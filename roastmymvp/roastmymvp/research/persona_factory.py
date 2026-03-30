"""Build personas FROM real social media users — not default templates.

Scrapes Reddit/HN for real people discussing a topic, then uses LLM
to synthesize each real comment into a full persona with their actual
frustrations, language, and perspective.
"""

import asyncio
import logging
import random

from roastmymvp.llm.client import LLMClient
from roastmymvp.llm.models import LLMRequest, LLMResponse, ModelTier
from roastmymvp.personas.models import (
    Archetype,
    EvaluationStyle,
    PersonaProfile,
)
from roastmymvp.research.models import (
    MarketResearch,
    SignalType,
    UserSignal,
)
from roastmymvp.research.scraper import research_product, search_reddit, search_hacker_news

logger = logging.getLogger(__name__)

# Map signal types to likely archetypes
_SIGNAL_TO_ARCHETYPE = {
    SignalType.COMPLAINT: Archetype.CHURNER,
    SignalType.PRAISE: Archetype.ADVOCATE,
    SignalType.FEATURE_REQUEST: Archetype.POWER_USER,
    SignalType.CHURN_REASON: Archetype.CHURNER,
    SignalType.COMPARISON: Archetype.SKEPTIC,
}

_ARCHETYPE_TO_EVAL = {
    Archetype.POWER_USER: EvaluationStyle.TASK_DRIVEN,
    Archetype.SKEPTIC: EvaluationStyle.COMPARISON,
    Archetype.ADVOCATE: EvaluationStyle.EXPLORATORY,
    Archetype.CONFUSED: EvaluationStyle.FIRST_IMPRESSION,
    Archetype.CHURNER: EvaluationStyle.COMPARISON,
    Archetype.PRAGMATIST: EvaluationStyle.TASK_DRIVEN,
    Archetype.ACCESSIBILITY: EvaluationStyle.EXPLORATORY,
}

# Name pools for generating persona names
_FIRST_NAMES = [
    "Alex", "Jordan", "Sam", "Casey", "Robin", "Taylor", "Morgan", "Quinn",
    "Mia", "Ethan", "Zara", "Leo", "Nora", "Kai", "Luna", "Finn",
    "Iris", "Oscar", "Maya", "Theo", "Ava", "Liam", "Ella", "Noah",
    "Sophie", "James", "Olivia", "William", "Emma", "Ben", "Chloe", "Dan",
    "Grace", "Henry", "Ivy", "Jack", "Kate", "Luke", "Nina", "Owen",
    "Priya", "Raj", "Sarah", "Tom", "Uma", "Victor", "Wendy", "Xavier",
    "Yuki", "Zoe", "Aisha", "Carlos", "Diana", "Felix", "Hana", "Igor",
    "Julia", "Kevin", "Leila", "Marco", "Nadia", "Omar", "Petra", "Ravi",
]

_LAST_NAMES = [
    "Chen", "Park", "Smith", "Kumar", "Garcia", "Kim", "Brown", "Lee",
    "Wang", "Singh", "Jones", "Nakamura", "Silva", "Petrov", "Muller",
    "Dubois", "Hansen", "Ali", "Costa", "Nguyen", "Schmidt", "Liu",
    "Patel", "Johnson", "Williams", "Martinez", "Anderson", "Taylor",
    "Thomas", "Jackson", "White", "Harris", "Clark", "Lewis", "Young",
]


def _signal_to_persona(
    signal: UserSignal,
    index: int,
    rng: random.Random,
) -> PersonaProfile:
    """Convert a real social media signal into a persona."""
    archetype = _SIGNAL_TO_ARCHETYPE.get(signal.signal_type, Archetype.PRAGMATIST)
    eval_style = _ARCHETYPE_TO_EVAL.get(archetype, EvaluationStyle.TASK_DRIVEN)

    # Build background from the real comment
    source_label = signal.source.value.replace("_", " ").title()
    subreddit_ctx = f" on r/{signal.subreddit}" if signal.subreddit else ""

    name = f"{rng.choice(_FIRST_NAMES)} {rng.choice(_LAST_NAMES)}"
    age = rng.randint(18, 55)
    tech_savvy = rng.uniform(0.3, 1.0)
    patience = rng.randint(15, 90)

    # Extract the real user's voice as frustrations/goals
    text = signal.text[:500]  # Cap length

    if signal.signal_type == SignalType.COMPLAINT:
        frustrations = (text,)
        goals = ("Check if this product has the same problem I complained about",)
        emotional_state = "frustrated from past experience"
    elif signal.signal_type == SignalType.CHURN_REASON:
        frustrations = (text,)
        goals = ("See if this is better than what I left",)
        emotional_state = "cautious, been burned before"
    elif signal.signal_type == SignalType.PRAISE:
        frustrations = ()
        goals = ("See if this lives up to the hype I've heard",)
        emotional_state = "optimistic but will verify"
    elif signal.signal_type == SignalType.FEATURE_REQUEST:
        frustrations = ()
        goals = (f"Check if this has: {text[:150]}",)
        emotional_state = "hopeful, looking for a specific feature"
    else:
        frustrations = ()
        goals = ("Evaluate this product",)
        emotional_state = "neutral"

    return PersonaProfile(
        name=name,
        age=age,
        background=f"Real user from {source_label}{subreddit_ctx}. "
                   f"Their words: \"{text[:200]}{'...' if len(text) > 200 else ''}\"",
        tech_savvy=round(tech_savvy, 2),
        patience_seconds=patience,
        language="en",
        has_alternative=signal.signal_type in (SignalType.CHURN_REASON, SignalType.COMPARISON),
        alternative_name=None,
        archetype=archetype,
        evaluation_style=eval_style,
        goals=goals,
        frustrations=frustrations,
        context_of_use=f"Found via {source_label}{subreddit_ctx} (score: {signal.score})",
        emotional_state=emotional_state,
    )


async def build_personas_from_research(
    product_name: str,
    count: int = 20,
    competitors: tuple[str, ...] = (),
    subreddits: tuple[str, ...] = (),
    topics: tuple[str, ...] = (),
) -> tuple[PersonaProfile, ...]:
    """Scrape social media and build personas from real users.

    Returns up to `count` personas derived from actual Reddit/HN comments.
    Falls back to fewer if not enough signals found.
    """
    if not subreddits:
        subreddits = (
            "SaaS", "webdev", "startups", "ProductHunt", "selfhosted",
            "sideproject", "programming", "software", "apps",
        )

    # Search with product name first
    research = await research_product(product_name, competitors, subreddits)

    # If not enough signals, also search with topic keywords and subreddit names
    if len(research.signals) < count:
        extra_queries = list(topics)
        # Use subreddit names as search terms too (e.g., "actuary" → search for actuarial content)
        for sub in subreddits:
            if sub.lower() not in ("saas", "webdev", "startups", "producthunt", "selfhosted",
                                    "sideproject", "programming", "software", "apps"):
                extra_queries.append(sub)

        for query in extra_queries:
            if len(research.signals) >= count * 2:
                break
            extra = await research_product(query, (), subreddits)
            if extra.signals:
                # Merge signals
                combined = list(research.signals) + list(extra.signals)
                # Dedupe by first 100 chars
                seen: set[str] = set()
                unique = []
                for s in combined:
                    key = s.text[:100]
                    if key not in seen:
                        seen.add(key)
                        unique.append(s)
                research = MarketResearch(
                    query=product_name,
                    signals=tuple(unique),
                    competitors=research.competitors,
                    top_complaints=research.top_complaints,
                    top_praise=research.top_praise,
                    top_feature_requests=research.top_feature_requests,
                )

    if not research.signals:
        logger.warning("No signals found for '%s' — returning empty", product_name)
        return ()

    rng = random.Random(42)
    personas: list[PersonaProfile] = []
    used_names: set[str] = set()

    # Sort by score (highest upvoted = most representative voice)
    sorted_signals = sorted(research.signals, key=lambda s: s.score, reverse=True)

    for i, signal in enumerate(sorted_signals):
        if len(personas) >= count:
            break

        persona = _signal_to_persona(signal, i, rng)

        # Ensure unique names
        while persona.name in used_names:
            persona = PersonaProfile(
                name=f"{rng.choice(_FIRST_NAMES)} {rng.choice(_LAST_NAMES)}",
                age=persona.age,
                background=persona.background,
                tech_savvy=persona.tech_savvy,
                patience_seconds=persona.patience_seconds,
                language=persona.language,
                has_alternative=persona.has_alternative,
                alternative_name=persona.alternative_name,
                archetype=persona.archetype,
                evaluation_style=persona.evaluation_style,
                goals=persona.goals,
                frustrations=persona.frustrations,
                context_of_use=persona.context_of_use,
                emotional_state=persona.emotional_state,
            )
        used_names.add(persona.name)
        personas.append(persona)

    # If we don't have enough signals, duplicate with varied archetypes
    if len(personas) < count and personas:
        archetype_cycle = list(Archetype)
        while len(personas) < count:
            base = rng.choice(personas)
            arch = archetype_cycle[len(personas) % len(archetype_cycle)]
            new_name = f"{rng.choice(_FIRST_NAMES)} {rng.choice(_LAST_NAMES)}"
            while new_name in used_names:
                new_name = f"{rng.choice(_FIRST_NAMES)} {rng.choice(_LAST_NAMES)}"
            used_names.add(new_name)

            personas.append(
                PersonaProfile(
                    name=new_name,
                    age=rng.randint(18, 55),
                    background=base.background,
                    tech_savvy=max(0.1, min(1.0, base.tech_savvy + rng.uniform(-0.3, 0.3))),
                    patience_seconds=rng.randint(10, 90),
                    language=base.language,
                    has_alternative=base.has_alternative,
                    archetype=arch,
                    evaluation_style=_ARCHETYPE_TO_EVAL.get(arch, EvaluationStyle.TASK_DRIVEN),
                    goals=base.goals,
                    frustrations=base.frustrations,
                    context_of_use=base.context_of_use,
                    emotional_state=rng.choice([
                        "frustrated", "curious", "skeptical", "rushed",
                        "hopeful", "bored", "analytical", "impatient",
                    ]),
                )
            )

    return tuple(personas[:count])
