"""
Gottschalk-Gleser Depression Scale — the v0.1 worked example of the
Clinical Skill Architecture.

The skill files, ontology, and demo data for this scale are bundled here as
package resources. The framework code (agent, fragmenter, scorer, eval) lives
under :mod:`csa` and is scale-agnostic.

Convenience re-exports
----------------------

>>> from csa.scales.gg_depression import score, GGAgent
>>> result = score("I just don't see the point anymore.")

Lower-level resource access uses :mod:`importlib.resources` against the package
``csa.scales.gg_depression``; see :func:`csa.prompts.load_skill` for the
canonical loader.
"""

from csa.agent import DEFAULT_MODEL, GGAgent, score, score_async

SCALE_ID = "gg_depression"
"""Resource sub-path under ``csa/scales/`` where this scale's files live."""

SUBSCALES: tuple[str, ...] = ("HOP", "SAC", "PMR", "SOM", "DAM", "SEP", "HOS")
"""The seven Gottschalk-Gleser depression subscales."""

__all__ = [
    "SCALE_ID",
    "SUBSCALES",
    "GGAgent",
    "score",
    "score_async",
    "DEFAULT_MODEL",
]
