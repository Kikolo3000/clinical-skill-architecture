"""
ScaleAgent — orchestrates the two-stage (screening → detail) Clinical Skill
Architecture pipeline.

In v0.1 the agent is wired to the Gottschalk-Gleser depression scale by default.
The class is also re-exported as ``GGAgent`` because that scale is the only one
bundled at this version; both names refer to the same underlying implementation.

Public entrypoints:

    score(transcript, *, model="claude-sonnet-4-6", **kwargs) -> ScoringResult
    score_async(transcript, ...)
    ScaleAgent(model=..., backend="anthropic", max_concurrent=5)
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

from csa._version import PROMPT_VERSION
from csa.backends import Backend, get_backend
from csa.cost import estimate_cost_usd
from csa.fragmenter import fragment as fragment_text
from csa.prompts import (
    build_detail_system_prompt,
    build_detail_user_prompt,
    build_screening_system_prompt,
    build_screening_user_prompt,
)
from csa.schemas import (
    SUBSCALES,
    Coding,
    Fragment,
    FragmentResult,
    ScoringResult,
    Screening,
    Subscale,
)
from csa.scorer import aggregate
from csa.validator import validate_record

log = logging.getLogger("csa")

DEFAULT_MODEL = "claude-sonnet-4-6"
"""Lower-cost Anthropic default for public use. See MODEL_CARD.md."""


# ---------------------------------------------------------------------------
# JSON extraction
# ---------------------------------------------------------------------------

_FENCE_PATTERN = re.compile(r"```(?:json)?\s*\n?(.*?)\n?```", re.DOTALL)


def _extract_json(text: str) -> dict | None:
    """Best-effort JSON extraction from a model response."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = _FENCE_PATTERN.search(text)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            pass
    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start:i + 1])
                except json.JSONDecodeError:
                    return None
    return None


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------


@dataclass
class GGAgent:
    """
    Stateful agent that scores one or many transcripts.

    For one-off use, just call the module-level `score(...)`. Use this class
    when you want to re-use a configured backend across multiple transcripts
    or batches.
    """

    model: str = DEFAULT_MODEL
    backend: str | Backend = "anthropic"
    max_concurrent: int = 5
    max_retries: int = 3
    target_speakers: str | list[str] | None = None
    context_turns: int = 5

    def __post_init__(self) -> None:
        if isinstance(self.backend, str):
            self._backend: Backend = get_backend(self.backend)
        else:
            self._backend = self.backend

    # ---------------------------- public API ------------------------------

    def score(self, transcript: str, *, id_prefix: str = "frag") -> ScoringResult:
        """Score one transcript synchronously. Convenience wrapper around `score_async`.

        Works both at the top level and inside an existing event loop (e.g. a
        Jupyter or Colab kernel) — in the latter case it runs the coroutine in
        a worker thread so we do not collide with the kernel's loop.
        """
        return _run_sync(self.score_async(transcript, id_prefix=id_prefix))

    async def score_async(self, transcript: str, *, id_prefix: str = "frag") -> ScoringResult:
        fragments = fragment_text(
            transcript,
            target_speakers=self.target_speakers,
            context_turns=self.context_turns,
            id_prefix=id_prefix,
        )
        return await self.score_fragments_async(fragments)

    async def score_fragments_async(
        self, fragments: Iterable[Fragment]
    ) -> ScoringResult:
        fragments = list(fragments)
        sem = asyncio.Semaphore(self.max_concurrent)
        screening_system = build_screening_system_prompt()

        async def one(frag: Fragment) -> FragmentResult:
            async with sem:
                return await self._process_fragment(frag, screening_system)

        results = await asyncio.gather(*(one(f) for f in fragments))
        return self._assemble(results)

    # --------------------------- orchestration ----------------------------

    async def _process_fragment(
        self,
        frag: Fragment,
        screening_system: str,
    ) -> FragmentResult:
        # Stage 1: screening
        screening_user = build_screening_user_prompt(
            study_excerpt=frag.study_excerpt,
            close_context=frag.close_context,
        )
        screening = await self._call_with_retry(
            system=screening_system, user=screening_user, cache_system=True
        )
        if screening is None:
            log.warning("Screening failed for %s; returning empty result.", frag.id)
            return self._empty_result(frag, word_count=len(frag.study_excerpt.split()))

        s_text, s_tokens = screening
        s_data = _extract_json(s_text) or {}

        decision = s_data.get("decision", "no_depressive_content")
        flagged = [s for s in s_data.get("flagged_subscales", []) if s in SUBSCALES]
        rationale = s_data.get("screening_rationale", "")
        word_count = s_data.get("word_count")
        if not isinstance(word_count, int) or word_count <= 0:
            word_count = len(frag.study_excerpt.split())
        if flagged and decision == "no_depressive_content":
            decision = "needs_analysis"

        in_tok = s_tokens["input"]
        out_tok = s_tokens["output"]
        cached_tok = s_tokens["cached"]
        codings: list[Coding] = []

        # Stage 2: per flagged subscale
        if decision == "needs_analysis" and flagged:
            detail_user = build_detail_user_prompt(
                study_excerpt=frag.study_excerpt,
                close_context=frag.close_context,
                screening_rationale=rationale,
            )
            detail_tasks = [
                self._call_with_retry(
                    system=build_detail_system_prompt(sub),
                    user=detail_user,
                    cache_system=True,
                )
                for sub in flagged
            ]
            detail_results = await asyncio.gather(*detail_tasks)
            for sub, dres in zip(flagged, detail_results):
                if dres is None:
                    continue
                d_text, d_tokens = dres
                in_tok += d_tokens["input"]
                out_tok += d_tokens["output"]
                cached_tok += d_tokens["cached"]
                d_data = _extract_json(d_text) or {}
                for raw in d_data.get("codings", []) or []:
                    if not isinstance(raw, dict):
                        continue
                    coding = self._coerce_coding(raw, default_subscale=sub)
                    if coding is not None:
                        codings.append(coding)

        record = self._build_record(
            frag=frag,
            decision=decision,
            flagged=flagged,
            rationale=rationale,
            codings=codings,
            word_count=word_count,
        )
        # Validate (non-strict — keep best-effort, log issues)
        for issue in validate_record(record, strict=False):
            log.debug("[%s] schema issue: %s", frag.id, issue)

        return FragmentResult(
            fragment=frag,
            screening=Screening(
                decision=decision,  # type: ignore[arg-type]
                flagged_subscales=tuple(flagged),
                rationale=rationale,
            ),
            codings=tuple(codings),
            word_count=word_count,
            analyzed_at=datetime.now(timezone.utc).isoformat(),
            prompt_version=PROMPT_VERSION,
            input_tokens=in_tok,
            output_tokens=out_tok,
            cached_tokens=cached_tok,
        )

    async def _call_with_retry(
        self, *, system: str, user: str, cache_system: bool
    ) -> tuple[str, dict[str, int]] | None:
        last_err: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = await self._backend.complete(
                    system=system, user=user, model=self.model, cache_system=cache_system,
                )
                return resp.text, {
                    "input": resp.input_tokens,
                    "output": resp.output_tokens,
                    "cached": resp.cached_tokens,
                }
            except Exception as e:  # noqa: BLE001 — backend errors vary
                last_err = e
                if attempt < self.max_retries:
                    await asyncio.sleep(2 * attempt)
        log.warning("Backend call failed after %d retries: %s", self.max_retries, last_err)
        return None

    # ----------------------------- helpers --------------------------------

    @staticmethod
    def _coerce_coding(raw: dict, default_subscale: Subscale) -> Coding | None:
        try:
            sub = raw.get("subscale", default_subscale)
            if sub not in SUBSCALES:
                sub = default_subscale
            persp = raw.get("perspective", "self")
            if persp not in ("self", "others", "inanimate", "denial"):
                persp = "self"
            weight = int(raw.get("weight", 1))
            return Coding(
                clause=str(raw.get("clause", "")),
                subscale=sub,  # type: ignore[arg-type]
                sub_item=str(raw.get("sub_item", sub)),
                perspective=persp,  # type: ignore[arg-type]
                weight=weight,
                rationale=str(raw.get("rationale", "")),
            )
        except (TypeError, ValueError) as e:
            log.debug("Skipping malformed coding: %s (%s)", raw, e)
            return None

    @staticmethod
    def _build_record(
        *,
        frag: Fragment,
        decision: str,
        flagged: list[str],
        rationale: str,
        codings: list[Coding],
        word_count: int,
    ) -> dict:
        summaries = {
            sub: {
                "count": sum(1 for c in codings if c.subscale == sub),
                "weighted_sum": sum(c.weight for c in codings if c.subscale == sub),
                "items_found": sorted({c.sub_item for c in codings if c.subscale == sub}),
            }
            for sub in SUBSCALES
        }
        return {
            "id": frag.id,
            "screening": {
                "decision": decision,
                "flagged_subscales": flagged,
                "screening_rationale": rationale,
            },
            "codings": [c.to_dict() for c in codings],
            "subscale_summaries": summaries,
            "word_count": word_count,
        }

    @staticmethod
    def _empty_result(frag: Fragment, *, word_count: int) -> FragmentResult:
        return FragmentResult(
            fragment=frag,
            screening=Screening(
                decision="no_depressive_content",
                flagged_subscales=tuple(),
                rationale="(call failed)",
            ),
            codings=tuple(),
            word_count=word_count,
            analyzed_at=datetime.now(timezone.utc).isoformat(),
            prompt_version=PROMPT_VERSION,
        )

    def _assemble(self, results: list[FragmentResult]) -> ScoringResult:
        scores, total, total_words = aggregate(results)
        cost = sum(
            estimate_cost_usd(
                model=self.model,
                input_tokens=fr.input_tokens,
                cached_tokens=fr.cached_tokens,
                output_tokens=fr.output_tokens,
            )
            for fr in results
        )
        return ScoringResult(
            fragments=tuple(results),
            subscales=scores,
            total_depression=total,
            word_count=total_words,
            model=self.model,
            prompt_version=PROMPT_VERSION,
            estimated_cost_usd=cost,
        )


# ---------------------------------------------------------------------------
# Module-level helpers (the headline API)
# ---------------------------------------------------------------------------


def score(
    transcript: str,
    *,
    model: str = DEFAULT_MODEL,
    backend: str | Backend = "anthropic",
    max_concurrent: int = 5,
    target_speakers: str | list[str] | None = None,
) -> ScoringResult:
    """
    Score a single transcript synchronously and return a `ScoringResult`.

    `transcript` may be either a multi-turn dialogue with `LABEL: text` lines
    (e.g. `S: I just don't see the point.\\nI: Tell me more.`), or a single
    free-form utterance. Free-form input is wrapped as a one-turn `S:` line.

    See `MODEL_CARD.md` for the validated default model and prompt version.
    """
    if not _looks_like_dialogue(transcript):
        transcript = f"I: please describe how you have been feeling.\nS: {transcript.strip()}"
    agent = GGAgent(
        model=model,
        backend=backend,
        max_concurrent=max_concurrent,
        target_speakers=target_speakers,
    )
    return agent.score(transcript)


async def score_async(
    transcript: str,
    *,
    model: str = DEFAULT_MODEL,
    backend: str | Backend = "anthropic",
    max_concurrent: int = 5,
    target_speakers: str | list[str] | None = None,
) -> ScoringResult:
    """Async variant of `score()` for use inside event loops or notebooks with `await`."""
    if not _looks_like_dialogue(transcript):
        transcript = f"I: please describe how you have been feeling.\nS: {transcript.strip()}"
    agent = GGAgent(
        model=model,
        backend=backend,
        max_concurrent=max_concurrent,
        target_speakers=target_speakers,
    )
    return await agent.score_async(transcript)


def _run_sync(coro):
    """Run a coroutine to completion from a sync caller, even if a loop is already running.

    Plain `asyncio.run` raises `RuntimeError` when invoked inside Jupyter,
    Colab, or any other host that already drives an event loop. We detect that
    case and execute the coroutine on a fresh loop in a worker thread, which
    keeps `score()` ergonomic in notebooks without pulling `nest_asyncio` in.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


ScaleAgent = GGAgent
"""Framework-level alias for :class:`GGAgent`. Use this name when writing code
that should generalise to other rating scales once they are ported."""


def _looks_like_dialogue(text: str) -> bool:
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if re.match(r"^(?:Speaker\s+)?\w+:\s", line):
            return True
        return False
    return False
