"""Version + prompt-set version constants."""

__version__ = "0.1.0"

PROMPT_VERSION = "1.0.0"
"""
Version of the prompt set (skills + screening/detail templates + config).

Bump on any change to skills/, prompts/, or config/. Output records carry this
string so downstream analysis can detect runs produced under different prompt
sets and refuse to mix them. The validated metrics in MODEL_CARD.md correspond
to a specific PROMPT_VERSION.
"""
