"""End-to-end integration test: URL → Report (with mocked LLM)."""

import json
import os
import tempfile

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from roastmymvp.browser.explorer import explore_url
from roastmymvp.context.builder import build_product_context
from roastmymvp.llm.client import LLMClient
from roastmymvp.llm.models import LLMResponse
from roastmymvp.personas.depth_analyst import run_deep_analysis
from roastmymvp.personas.generator import generate_default_personas
from roastmymvp.report.builder import build_report
from roastmymvp.report.stats import calculate_pmf_signals


MOCK_FEEDBACK_JSON = json.dumps({
    "would_download": True,
    "would_pay": False,
    "would_return": True,
    "ux_scores": {
        "time_to_value": 8,
        "navigation_clarity": 7,
        "visual_design": 6,
        "error_handling": 5,
        "mobile_experience": 7,
    },
    "friction_points": ["No search functionality"],
    "bugs_found": [],
    "praise": ["Simple and clean"],
    "suggestions": ["Add a search bar"],
    "narrative": "The site loads quickly and is easy to understand.",
})


class TestFullPipeline:
    @pytest.mark.asyncio
    async def test_url_to_report(self):
        """Full pipeline: explore URL → build context → analyze → report."""
        # Step 1: Explore a real URL
        browser_ctx = await explore_url("https://example.com")

        assert browser_ctx.url == "https://example.com"
        assert len(browser_ctx.screenshots) >= 1

        # Step 2: Build product context
        product_context = build_product_context(browser_ctx)
        assert "example.com" in product_context

        # Step 3: Generate personas (use just 3 for speed)
        personas = generate_default_personas()[:3]

        # Step 4: Run analysis with mocked LLM
        mock_client = MagicMock(spec=LLMClient)
        mock_client.send = AsyncMock(return_value=LLMResponse(
            content=MOCK_FEEDBACK_JSON,
            model="claude-sonnet-4-6",
            input_tokens=500,
            output_tokens=300,
            cost_usd=0.02,
        ))

        feedbacks = await run_deep_analysis(
            personas=personas,
            product_context=product_context,
            llm_client=mock_client,
        )

        assert len(feedbacks) == 3
        assert all(f.would_download for f in feedbacks)

        # Step 5: Calculate PMF
        pmf = calculate_pmf_signals(feedbacks)
        assert pmf.download_rate == 1.0

        # Step 6: Build report
        browser_errors = tuple(e.message for e in browser_ctx.errors)
        report = build_report("https://example.com", feedbacks, pmf, browser_errors)

        assert "example.com" in report
        assert pmf.verdict in report
        assert "No search functionality" in report
        assert "Simple and clean" in report

        # Step 7: Write to file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(report)
            path = f.name

        assert os.path.exists(path)
        assert os.path.getsize(path) > 100
        os.unlink(path)

    @pytest.mark.asyncio
    async def test_pipeline_handles_bad_url(self):
        """Pipeline should not crash on unreachable URLs."""
        browser_ctx = await explore_url("https://thisdomaindoesnotexist99999.com")

        assert len(browser_ctx.errors) >= 1

        product_context = build_product_context(browser_ctx)
        personas = generate_default_personas()[:2]

        mock_client = MagicMock(spec=LLMClient)
        mock_client.send = AsyncMock(return_value=LLMResponse(
            content=MOCK_FEEDBACK_JSON,
            model="claude-sonnet-4-6",
            input_tokens=100,
            output_tokens=100,
            cost_usd=0.01,
        ))

        feedbacks = await run_deep_analysis(
            personas=personas,
            product_context=product_context,
            llm_client=mock_client,
        )

        pmf = calculate_pmf_signals(feedbacks)
        browser_errors = tuple(e.message for e in browser_ctx.errors)
        report = build_report(
            "https://thisdomaindoesnotexist99999.com",
            feedbacks, pmf, browser_errors,
        )

        assert len(report) > 100
        assert "Technical Errors" in report
