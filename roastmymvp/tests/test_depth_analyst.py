"""Tests for deep persona analysis module."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock

from roastmymvp.personas.models import PersonaProfile, PersonaFeedback
from roastmymvp.personas.depth_analyst import run_deep_analysis, parse_feedback
from roastmymvp.llm.models import LLMResponse


MOCK_LLM_JSON = json.dumps({
    "would_download": True,
    "would_pay": False,
    "would_return": True,
    "ux_scores": {
        "time_to_value": 7,
        "navigation_clarity": 8,
        "visual_design": 6,
        "error_handling": 5,
        "mobile_experience": 4,
    },
    "friction_points": ["Login flow too long", "No dark mode"],
    "bugs_found": ["404 on /settings"],
    "praise": ["Clean homepage", "Fast load time"],
    "suggestions": ["Add SSO login"],
    "narrative": "As a developer, I found the product promising but rough around the edges.",
})

SAMPLE_PERSONA = PersonaProfile(
    name="Test User",
    age=25,
    background="Developer",
    tech_savvy=0.8,
    patience_seconds=30,
    language="en",
    has_alternative=False,
)


class TestParseFeedback:
    def test_parses_valid_json(self):
        feedback = parse_feedback(SAMPLE_PERSONA, MOCK_LLM_JSON)
        assert isinstance(feedback, PersonaFeedback)
        assert feedback.would_download is True
        assert feedback.would_pay is False
        assert feedback.ux_scores.time_to_value == 7
        assert len(feedback.friction_points) == 2
        assert feedback.narrative != ""

    def test_frozen(self):
        feedback = parse_feedback(SAMPLE_PERSONA, MOCK_LLM_JSON)
        with pytest.raises(AttributeError):
            feedback.would_download = False

    def test_handles_missing_optional_fields(self):
        minimal = json.dumps({
            "would_download": True,
            "would_pay": True,
            "would_return": True,
            "ux_scores": {
                "time_to_value": 5,
                "navigation_clarity": 5,
                "visual_design": 5,
                "error_handling": 5,
                "mobile_experience": 5,
            },
            "friction_points": [],
            "bugs_found": [],
            "praise": [],
            "narrative": "Fine.",
        })
        feedback = parse_feedback(SAMPLE_PERSONA, minimal)
        assert feedback.suggestions == ()


class TestRunDeepAnalysis:
    @pytest.mark.asyncio
    async def test_runs_all_personas(self):
        mock_client = MagicMock()
        mock_client.send = AsyncMock(return_value=LLMResponse(
            content=MOCK_LLM_JSON,
            model="claude-sonnet-4-6",
            input_tokens=100,
            output_tokens=200,
            cost_usd=0.01,
        ))

        personas = (SAMPLE_PERSONA,) * 3
        results = await run_deep_analysis(
            personas=personas,
            product_context="A todo app",
            llm_client=mock_client,
        )

        assert len(results) == 3
        assert all(isinstance(r, PersonaFeedback) for r in results)
        assert mock_client.send.call_count == 3

    @pytest.mark.asyncio
    async def test_handles_llm_error_gracefully(self):
        mock_client = MagicMock()
        mock_client.send = AsyncMock(side_effect=Exception("API error"))

        results = await run_deep_analysis(
            personas=(SAMPLE_PERSONA,),
            product_context="A todo app",
            llm_client=mock_client,
        )

        # Should not crash, returns empty or error feedback
        assert len(results) == 1
        assert results[0].narrative != ""
