"""
Token → USD cost estimation.

Prices are per 1M tokens, pulled from publicly listed Anthropic / OpenAI pricing
at the time of the 0.1.0 release. Override via `set_price()` to use a custom
provider's rates.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Price:
    """Per 1M tokens, in USD."""

    input: float
    cached_input: float
    output: float


_PRICES: dict[str, Price] = {
    # Anthropic — https://www.anthropic.com/pricing
    "claude-opus-4-6": Price(input=15.0, cached_input=1.50, output=75.0),
    "claude-opus-4-7": Price(input=15.0, cached_input=1.50, output=75.0),
    "claude-sonnet-4-6": Price(input=3.0, cached_input=0.30, output=15.0),
    "claude-haiku-4-5": Price(input=1.0, cached_input=0.10, output=5.0),
    # Generic fallbacks
    "gpt-5": Price(input=10.0, cached_input=2.50, output=40.0),
    "default": Price(input=3.0, cached_input=0.30, output=15.0),
}


def get_price(model: str) -> Price:
    if model in _PRICES:
        return _PRICES[model]
    for prefix, price in _PRICES.items():
        if model.startswith(prefix):
            return price
    return _PRICES["default"]


def set_price(model: str, *, input: float, cached_input: float, output: float) -> None:
    """Override pricing for a model name (useful for self-hosted or custom providers)."""
    _PRICES[model] = Price(input=input, cached_input=cached_input, output=output)


def estimate_cost_usd(
    *, model: str, input_tokens: int, cached_tokens: int, output_tokens: int
) -> float:
    p = get_price(model)
    fresh_input = max(0, input_tokens - cached_tokens)
    return (
        fresh_input * p.input / 1_000_000
        + cached_tokens * p.cached_input / 1_000_000
        + output_tokens * p.output / 1_000_000
    )
