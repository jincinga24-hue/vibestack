"""Data models for the persona engine."""

from dataclasses import dataclass, field
from enum import Enum


class Archetype(Enum):
    """Behavioral archetype — how a persona approaches new products."""
    POWER_USER = "power_user"       # Explores everything, pushes limits
    SKEPTIC = "skeptic"             # Hard to impress, compares to alternatives
    ADVOCATE = "advocate"           # Enthusiastic early adopter, forgiving
    CONFUSED = "confused"           # Low context, easily lost
    CHURNER = "churner"             # Tried similar tools, left them all
    PRAGMATIST = "pragmatist"       # Only cares if it solves their problem
    ACCESSIBILITY = "accessibility" # Evaluates from disability/a11y perspective


class EvaluationStyle(Enum):
    """How the persona processes and judges a product."""
    TASK_DRIVEN = "task_driven"     # "Can I do X?" — judges by task success
    EXPLORATORY = "exploratory"     # Wanders, discovers, forms impressions
    COMPARISON = "comparison"       # Benchmarks against a known alternative
    FIRST_IMPRESSION = "first_impression"  # Snap judgment, leaves fast if unimpressed


@dataclass(frozen=True)
class PersonaProfile:
    name: str
    age: int
    background: str
    tech_savvy: float               # 0.0 - 1.0
    patience_seconds: int           # how long before they leave
    language: str                   # primary language
    has_alternative: bool           # already using a competitor?
    alternative_name: str | None = None
    irrationality_mod: str | None = None

    # Deep traits
    archetype: Archetype = Archetype.PRAGMATIST
    evaluation_style: EvaluationStyle = EvaluationStyle.TASK_DRIVEN
    goals: tuple[str, ...] = field(default_factory=tuple)
    frustrations: tuple[str, ...] = field(default_factory=tuple)
    context_of_use: str = ""        # When/where/why they'd use this
    emotional_state: str = "neutral" # Current mood affecting evaluation
    accessibility_needs: str | None = None


@dataclass(frozen=True)
class UXScore:
    time_to_value: int              # 1-10
    navigation_clarity: int         # 1-10
    visual_design: int              # 1-10
    error_handling: int             # 1-10
    mobile_experience: int          # 1-10
    overall: float                  # weighted average


@dataclass(frozen=True)
class PersonaFeedback:
    persona: PersonaProfile
    would_download: bool
    would_pay: bool
    would_return: bool
    ux_scores: UXScore
    friction_points: tuple[str, ...]
    bugs_found: tuple[str, ...]
    praise: tuple[str, ...]
    narrative: str                  # full written feedback (deep only)
    suggestions: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class PMFSignals:
    download_rate: float            # 0.0 - 1.0
    pay_rate: float                 # 0.0 - 1.0
    return_rate: float              # 0.0 - 1.0
    avg_ux_score: float
    verdict: str                    # GO / CONDITIONAL GO / NO-GO
