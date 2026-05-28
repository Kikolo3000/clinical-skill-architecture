"""
Aggregate per-fragment results into the 7 G-G subscale scores plus the total
depression score.
"""

from __future__ import annotations

from collections.abc import Iterable

from csa.schemas import (
    SUBSCALES,
    FragmentResult,
    Subscale,
    SubscaleScore,
    gg_formula,
)


def aggregate(
    fragment_results: Iterable[FragmentResult],
) -> tuple[dict[Subscale, SubscaleScore], float, int]:
    """
    Aggregate one or more `FragmentResult`s into per-subscale scores and a
    total depression score.

    Returns:
        (subscale_scores, total_depression, total_word_count)
    """
    fr_list = list(fragment_results)
    total_words = sum(fr.word_count for fr in fr_list)

    scores: dict[Subscale, SubscaleScore] = {}
    total = 0.0
    for sub in SUBSCALES:
        weighted_sum = sum(fr.weighted_sum(sub) for fr in fr_list)
        count = sum(1 for fr in fr_list for c in fr.codings if c.subscale == sub)
        items = sorted({c.sub_item for fr in fr_list for c in fr.codings if c.subscale == sub})
        score = gg_formula(weighted_sum, total_words)
        scores[sub] = SubscaleScore(
            subscale=sub,
            score=score,
            count=count,
            weighted_sum=weighted_sum,
            word_count=total_words,
            items_found=tuple(items),
        )
        total += score
    return scores, total, total_words
