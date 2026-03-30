"""Data models for LLM interactions."""

from dataclasses import dataclass
from enum import Enum


class ModelTier(Enum):
    DEEP = "deep"       # Sonnet — rich narrative analysis
    FAST = "fast"       # Haiku — JSON-only quantified ratings


@dataclass(frozen=True)
class LLMRequest:
    prompt: str
    system: str = ""
    model_tier: ModelTier = ModelTier.DEEP
    max_tokens: int = 4096
    temperature: float = 0.7


@dataclass(frozen=True)
class LLMResponse:
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
