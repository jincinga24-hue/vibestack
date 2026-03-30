"""Data models for VC roast mode."""

from dataclasses import dataclass, field
from enum import Enum


class VCArchetype(Enum):
    SHARK = "shark"                 # Ruthless, numbers-only, will destroy your TAM
    DOMAIN_EXPERT = "domain_expert" # Knows the space, will expose your ignorance
    PATTERN_MATCHER = "pattern_matcher"  # "I've seen 50 of these fail"
    DEVIL_ADVOCATE = "devil_advocate"    # Argues the opposite of everything
    COLD_CALLER = "cold_caller"    # Treats you like a cold email — 10 seconds to impress


class InvestmentDecision(Enum):
    PASS = "pass"                   # Would not invest
    MAYBE = "maybe"                 # Interested but concerns
    INVEST = "invest"               # Would take a meeting


@dataclass(frozen=True)
class VCPersona:
    name: str
    title: str
    fund: str
    archetype: VCArchetype
    background: str
    check_size: str                 # "$50K-$200K angel" or "$5M-$15M Series A"
    portfolio: tuple[str, ...]      # Types of companies they've invested in
    pet_peeves: tuple[str, ...]     # Instant turn-offs
    kill_questions: tuple[str, ...]  # Questions designed to destroy weak pitches
    tone: str                       # "brutal", "condescending", "ice cold"


@dataclass(frozen=True)
class RoastVerdict:
    vc: VCPersona
    decision: InvestmentDecision
    roast: str                      # The brutal feedback
    kill_shot: str                  # The single most devastating critique
    score: int                      # 0-100 investability score
    would_take_meeting: bool
    questions_that_destroyed: tuple[str, ...]  # Questions founder couldn't answer
    grudging_praise: str            # Even sharks respect something


@dataclass(frozen=True)
class VCGateResult:
    passed: bool
    score: int                      # 0-100 average
    verdicts: tuple[RoastVerdict, ...]
    summary_roast: str              # Aggregate brutal summary
    must_fix: tuple[str, ...]       # Non-negotiable issues before community test
    certification: str              # "DESTROYED" / "SURVIVED" / "IMPRESSED"
