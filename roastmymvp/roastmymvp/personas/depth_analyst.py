"""Deep persona analysis — 20 personas with full narrative feedback."""

import asyncio
import json
import logging

from roastmymvp.llm.client import LLMClient
from roastmymvp.llm.models import LLMRequest, ModelTier
from roastmymvp.llm.prompts import SYSTEM_DEEP_ANALYSIS, build_deep_prompt
from roastmymvp.personas.models import (
    PersonaFeedback,
    PersonaProfile,
    UXScore,
)

logger = logging.getLogger(__name__)


def parse_feedback(persona: PersonaProfile, raw_json: str) -> PersonaFeedback:
    """Parse LLM JSON response into a PersonaFeedback dataclass."""
    data = json.loads(raw_json)

    scores = data["ux_scores"]
    ux = UXScore(
        time_to_value=scores["time_to_value"],
        navigation_clarity=scores["navigation_clarity"],
        visual_design=scores["visual_design"],
        error_handling=scores["error_handling"],
        mobile_experience=scores["mobile_experience"],
        overall=sum(scores.values()) / len(scores),
    )

    return PersonaFeedback(
        persona=persona,
        would_download=data["would_download"],
        would_pay=data["would_pay"],
        would_return=data["would_return"],
        ux_scores=ux,
        friction_points=tuple(data.get("friction_points", ())),
        bugs_found=tuple(data.get("bugs_found", ())),
        praise=tuple(data.get("praise", ())),
        narrative=data.get("narrative", ""),
        suggestions=tuple(data.get("suggestions", ())),
    )


def _error_feedback(persona: PersonaProfile, error_msg: str) -> PersonaFeedback:
    """Create a fallback feedback entry when LLM call fails."""
    return PersonaFeedback(
        persona=persona,
        would_download=False,
        would_pay=False,
        would_return=False,
        ux_scores=UXScore(
            time_to_value=0,
            navigation_clarity=0,
            visual_design=0,
            error_handling=0,
            mobile_experience=0,
            overall=0.0,
        ),
        friction_points=(),
        bugs_found=(),
        praise=(),
        narrative=f"[Analysis failed: {error_msg}]",
    )


async def _analyze_one(
    persona: PersonaProfile,
    product_context: str,
    llm_client: LLMClient,
) -> PersonaFeedback:
    """Run deep analysis for a single persona."""
    try:
        request = LLMRequest(
            prompt=build_deep_prompt(persona, product_context),
            system=SYSTEM_DEEP_ANALYSIS,
            model_tier=ModelTier.DEEP,
            max_tokens=4096,
            temperature=0.7,
        )
        response = await llm_client.send(request)
        return parse_feedback(persona, response.content)
    except Exception as e:
        logger.warning("Analysis failed for %s: %s", persona.name, e)
        return _error_feedback(persona, str(e))


async def run_deep_analysis(
    personas: tuple[PersonaProfile, ...],
    product_context: str,
    llm_client: LLMClient,
    max_concurrent: int = 5,
) -> tuple[PersonaFeedback, ...]:
    """Run deep analysis for all personas with concurrency control."""
    semaphore = asyncio.Semaphore(max_concurrent)

    async def bounded(persona: PersonaProfile) -> PersonaFeedback:
        async with semaphore:
            return await _analyze_one(persona, product_context, llm_client)

    tasks = [bounded(p) for p in personas]
    results = await asyncio.gather(*tasks)
    return tuple(results)
