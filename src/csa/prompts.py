"""
Prompt loading + template substitution.

The generic screening / detail templates live at the framework level
(``csa/prompts/``) and contain placeholders. The scale-specific ontology and
skill files live under ``csa/scales/<SCALE_ID>/`` and are loaded via
:mod:`importlib.resources` so they ship inside the wheel.

For v0.1 this module defaults every loader to the Gottschalk-Gleser depression
scale (``SCALE_ID = "gg_depression"``); pass an explicit ``scale=...`` to read
from a different scale package once others are ported.
"""

from __future__ import annotations

from functools import lru_cache
from importlib import resources

from csa.schemas import SUBSCALES, Subscale

_PKG = "csa"
_DEFAULT_SCALE = "gg_depression"


def _read_scale(scale: str, *parts: str) -> str:
    """Read a text resource from ``csa/scales/<scale>/<parts...>``."""
    path = resources.files(_PKG) / "scales" / scale
    for part in parts:
        path = path / part
    return path.read_text(encoding="utf-8")


def _read_template(*parts: str) -> str:
    """Read a generic prompt template from ``csa/<parts...>``."""
    path = resources.files(_PKG)
    for part in parts:
        path = path / part
    return path.read_text(encoding="utf-8")


@lru_cache(maxsize=4)
def load_domains(scale: str = _DEFAULT_SCALE) -> str:
    """The construct-domain ontology for ``scale`` (shared by both stages)."""
    return _read_scale(scale, "config", "depression_domains.md")


@lru_cache(maxsize=1)
def load_screening_template() -> str:
    return _read_template("prompts", "screening.md")


@lru_cache(maxsize=1)
def load_detail_template() -> str:
    return _read_template("prompts", "detail.md")


@lru_cache(maxsize=32)
def load_skill(code: Subscale, scale: str = _DEFAULT_SCALE) -> str:
    """Load the ``SKILL.md`` for one construct of ``scale``."""
    if scale == _DEFAULT_SCALE and code not in SUBSCALES:
        raise ValueError(f"Unknown subscale: {code!r}")
    return _read_scale(scale, "skills", code, "SKILL.md")


def build_screening_system_prompt(scale: str = _DEFAULT_SCALE) -> str:
    return load_screening_template().format(domains_content=load_domains(scale))


def build_screening_user_prompt(study_excerpt: str, close_context: str = "") -> str:
    parts: list[str] = []
    if close_context:
        parts.append(
            f"## Close Context (preceding turns)\n\n<close_context>\n{close_context}\n</close_context>\n"
        )
    parts.append(
        f"## Study Excerpt (evaluate this for depressive content)\n\n"
        f"<study_excerpt>\n{study_excerpt}\n</study_excerpt>"
    )
    return "\n".join(parts)


def build_detail_system_prompt(subscale_code: Subscale, scale: str = _DEFAULT_SCALE) -> str:
    return load_detail_template().format(
        subscale_code=subscale_code,
        skill_content=load_skill(subscale_code, scale=scale),
    )


def build_detail_user_prompt(
    study_excerpt: str,
    close_context: str,
    screening_rationale: str,
) -> str:
    parts: list[str] = []
    if close_context:
        parts.append(
            f"## Close Context\n\n<close_context>\n{close_context}\n</close_context>\n"
        )
    parts.append(
        f"## Study Excerpt\n\n<study_excerpt>\n{study_excerpt}\n</study_excerpt>\n"
    )
    if screening_rationale:
        parts.append(
            f"## Screening Context\n\nThe screening stage flagged this excerpt. "
            f"Rationale: {screening_rationale}"
        )
    return "\n".join(parts)
