"""Enrich personas with real market research data.

Takes research signals from Reddit/HN and injects real frustrations,
competitor context, and user language into persona profiles.
"""

import random

from roastmymvp.personas.models import (
    Archetype,
    PersonaProfile,
)
from roastmymvp.research.models import (
    CompetitorIntel,
    MarketResearch,
    SignalType,
)


def enrich_personas(
    personas: tuple[PersonaProfile, ...],
    research: MarketResearch,
    seed: int = 42,
) -> tuple[PersonaProfile, ...]:
    """Inject real market research signals into existing personas.

    - Skeptics/churners get real complaints as frustrations
    - Personas with alternatives get real competitor context
    - All personas get frustrations grounded in real user language
    """
    rng = random.Random(seed)
    enriched: list[PersonaProfile] = []

    real_complaints = _extract_short_signals(research.top_complaints)
    real_praise = _extract_short_signals(research.top_praise)
    real_feature_requests = _extract_short_signals(research.top_feature_requests)
    competitor_data = {c.name.lower(): c for c in research.competitors}

    for persona in personas:
        new_frustrations = list(persona.frustrations)
        new_goals = list(persona.goals)
        new_context = persona.context_of_use
        new_background = persona.background

        # Inject real complaints as frustrations for skeptics/churners
        if persona.archetype in (Archetype.SKEPTIC, Archetype.CHURNER) and real_complaints:
            sampled = rng.sample(real_complaints, min(3, len(real_complaints)))
            new_frustrations.extend(f"[Real user said] {c}" for c in sampled)

        # Inject real frustrations for pragmatists too (they care about real issues)
        if persona.archetype == Archetype.PRAGMATIST and real_complaints:
            sampled = rng.sample(real_complaints, min(2, len(real_complaints)))
            new_frustrations.extend(f"[Real user said] {c}" for c in sampled)

        # Add real feature requests as goals for power users
        if persona.archetype == Archetype.POWER_USER and real_feature_requests:
            sampled = rng.sample(real_feature_requests, min(2, len(real_feature_requests)))
            new_goals.extend(f"Check if: {fr}" for fr in sampled)

        # Enrich competitor context with real competitor intel
        if persona.has_alternative and persona.alternative_name:
            comp_key = persona.alternative_name.lower()
            for key, intel in competitor_data.items():
                if key in comp_key or comp_key in key:
                    if intel.churn_reasons:
                        reason = rng.choice(intel.churn_reasons)
                        new_context += f" [Real users left {intel.name} because: {_truncate(reason)}]"
                    if intel.complaints:
                        complaint = rng.choice(intel.complaints)
                        new_frustrations.append(f"[{intel.name} users hate] {_truncate(complaint)}")
                    break

        # For advocates, add real praise so they can compare
        if persona.archetype == Archetype.ADVOCATE and real_praise:
            sampled = rng.sample(real_praise, min(2, len(real_praise)))
            new_background += " [Real users praised similar products for: " + "; ".join(sampled) + "]"

        enriched.append(
            PersonaProfile(
                name=persona.name,
                age=persona.age,
                background=new_background,
                tech_savvy=persona.tech_savvy,
                patience_seconds=persona.patience_seconds,
                language=persona.language,
                has_alternative=persona.has_alternative,
                alternative_name=persona.alternative_name,
                irrationality_mod=persona.irrationality_mod,
                archetype=persona.archetype,
                evaluation_style=persona.evaluation_style,
                goals=tuple(new_goals),
                frustrations=tuple(new_frustrations),
                context_of_use=new_context,
                emotional_state=persona.emotional_state,
                accessibility_needs=persona.accessibility_needs,
            )
        )

    return tuple(enriched)


def _extract_short_signals(texts: tuple[str, ...], max_len: int = 150) -> list[str]:
    """Extract short, usable signal snippets from raw text."""
    result: list[str] = []
    for text in texts:
        truncated = _truncate(text, max_len)
        if len(truncated) >= 15:  # skip very short noise
            result.append(truncated)
    return result


def _truncate(text: str, max_len: int = 150) -> str:
    """Truncate text to max_len, breaking at word boundary."""
    if len(text) <= max_len:
        return text
    truncated = text[:max_len].rsplit(" ", 1)[0]
    return truncated + "..."
