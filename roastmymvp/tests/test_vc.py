"""Tests for VC roast mode and gauntlet pipeline."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock

from roastmymvp.llm.models import LLMResponse
from roastmymvp.vc.models import (
    InvestmentDecision,
    RoastVerdict,
    VCArchetype,
    VCGateResult,
    VCPersona,
)
from roastmymvp.vc.personas import DEFAULT_VC_PANEL
from roastmymvp.vc.analyst import run_vc_panel, _parse_verdict, PASS_THRESHOLD
from roastmymvp.vc.prompts import build_vc_roast_prompt, SYSTEM_VC_ROAST
from roastmymvp.vc.report import build_vc_report
from roastmymvp.gauntlet import (
    CertificationLevel,
    GauntletStage,
    determine_certification,
    build_gauntlet_report,
)
from roastmymvp.personas.models import PMFSignals


MOCK_VC_JSON = json.dumps({
    "decision": "maybe",
    "score": 55,
    "would_take_meeting": True,
    "roast": "Your product has potential but your TAM is a fantasy. The UI is decent but I've seen 30 of these fail.",
    "kill_shot": "You have zero paying customers and you're asking me for $2M.",
    "questions_that_destroyed": [
        "What's your CAC? You don't know? That's a red flag.",
        "Who are your paying customers? 'Beta users' don't count.",
    ],
    "grudging_praise": "At least you shipped something. Most founders just talk.",
    "must_fix": ["Get paying customers", "Fix the TAM calculation"],
})


class TestVCPersonas:
    def test_default_panel_has_5_vcs(self):
        assert len(DEFAULT_VC_PANEL) == 5

    def test_all_have_kill_questions(self):
        for vc in DEFAULT_VC_PANEL:
            assert len(vc.kill_questions) >= 3

    def test_all_have_pet_peeves(self):
        for vc in DEFAULT_VC_PANEL:
            assert len(vc.pet_peeves) >= 3

    def test_diverse_archetypes(self):
        archetypes = {vc.archetype for vc in DEFAULT_VC_PANEL}
        assert len(archetypes) >= 4

    def test_all_frozen(self):
        for vc in DEFAULT_VC_PANEL:
            with pytest.raises(AttributeError):
                vc.name = "Changed"


class TestParseVerdict:
    def test_parses_valid_json(self):
        vc = DEFAULT_VC_PANEL[0]
        verdict = _parse_verdict(vc, MOCK_VC_JSON)
        assert isinstance(verdict, RoastVerdict)
        assert verdict.decision == InvestmentDecision.MAYBE
        assert verdict.score == 55
        assert verdict.would_take_meeting is True
        assert len(verdict.kill_shot) > 0

    def test_frozen(self):
        vc = DEFAULT_VC_PANEL[0]
        verdict = _parse_verdict(vc, MOCK_VC_JSON)
        with pytest.raises(AttributeError):
            verdict.score = 100


class TestRunVCPanel:
    @pytest.mark.asyncio
    async def test_runs_all_vcs(self):
        mock_client = MagicMock()
        mock_client.send = AsyncMock(return_value=LLMResponse(
            content=MOCK_VC_JSON,
            model="claude-sonnet-4-6",
            input_tokens=500,
            output_tokens=500,
            cost_usd=0.05,
        ))

        gate = await run_vc_panel(
            product_context="A todo app with nice UI",
            llm_client=mock_client,
        )

        assert isinstance(gate, VCGateResult)
        assert len(gate.verdicts) == 5
        assert gate.score > 0
        assert gate.certification in ("DESTROYED", "SURVIVED", "IMPRESSED")

    @pytest.mark.asyncio
    async def test_pass_with_high_scores(self):
        high_score_json = json.dumps({
            "decision": "invest",
            "score": 75,
            "would_take_meeting": True,
            "roast": "Impressive.",
            "kill_shot": "Scale is your only risk.",
            "questions_that_destroyed": [],
            "grudging_praise": "Great execution.",
            "must_fix": [],
        })
        mock_client = MagicMock()
        mock_client.send = AsyncMock(return_value=LLMResponse(
            content=high_score_json,
            model="claude-sonnet-4-6",
            input_tokens=500, output_tokens=500, cost_usd=0.05,
        ))

        gate = await run_vc_panel("Great product", llm_client=mock_client)
        assert gate.passed is True
        assert gate.certification == "IMPRESSED"

    @pytest.mark.asyncio
    async def test_fail_with_low_scores(self):
        low_score_json = json.dumps({
            "decision": "pass",
            "score": 15,
            "would_take_meeting": False,
            "roast": "Terrible.",
            "kill_shot": "This is a feature, not a product.",
            "questions_that_destroyed": ["Everything"],
            "grudging_praise": "Nice logo.",
            "must_fix": ["Everything"],
        })
        mock_client = MagicMock()
        mock_client.send = AsyncMock(return_value=LLMResponse(
            content=low_score_json,
            model="claude-sonnet-4-6",
            input_tokens=500, output_tokens=500, cost_usd=0.05,
        ))

        gate = await run_vc_panel("Bad product", llm_client=mock_client)
        assert gate.passed is False
        assert gate.certification == "DESTROYED"

    @pytest.mark.asyncio
    async def test_handles_llm_error(self):
        mock_client = MagicMock()
        mock_client.send = AsyncMock(side_effect=Exception("API error"))

        gate = await run_vc_panel("Product", llm_client=mock_client)
        assert gate.passed is False
        assert len(gate.verdicts) == 5


class TestVCPrompts:
    def test_prompt_includes_vc_identity(self):
        vc = DEFAULT_VC_PANEL[0]
        prompt = build_vc_roast_prompt(vc, "A todo app")
        assert vc.name in prompt
        assert vc.fund in prompt

    def test_prompt_includes_kill_questions(self):
        vc = DEFAULT_VC_PANEL[0]
        prompt = build_vc_roast_prompt(vc, "A todo app")
        assert vc.kill_questions[0] in prompt

    def test_prompt_includes_pitch(self):
        vc = DEFAULT_VC_PANEL[0]
        prompt = build_vc_roast_prompt(vc, "A todo app", pitch_text="Uber for dogs")
        assert "Uber for dogs" in prompt

    def test_system_prompt_mentions_json(self):
        assert "JSON" in SYSTEM_VC_ROAST


class TestVCReport:
    def test_report_contains_url(self):
        gate = VCGateResult(
            passed=False, score=30,
            verdicts=(), summary_roast="Bad.", must_fix=("Fix everything",),
            certification="DESTROYED",
        )
        report = build_vc_report("https://example.com", gate)
        assert "https://example.com" in report

    def test_report_contains_certification(self):
        gate = VCGateResult(
            passed=True, score=55,
            verdicts=(), summary_roast="OK.", must_fix=(),
            certification="SURVIVED",
        )
        report = build_vc_report("https://example.com", gate)
        assert "SURVIVED" in report


class TestGauntlet:
    def _make_vc_result(self, passed: bool, score: int) -> VCGateResult:
        return VCGateResult(
            passed=passed, score=score,
            verdicts=(), summary_roast="Test.",
            must_fix=(), certification="SURVIVED" if passed else "DESTROYED",
        )

    def _make_pmf(self, verdict: str, ux: float) -> PMFSignals:
        return PMFSignals(
            download_rate=0.8, pay_rate=0.4,
            return_rate=0.7, avg_ux_score=ux, verdict=verdict,
        )

    def test_failed_vc(self):
        result = determine_certification(self._make_vc_result(False, 25))
        assert result.certification == CertificationLevel.FAILED_VC
        assert result.stage_reached == GauntletStage.VC_GATE

    def test_passed_vc_failed_community(self):
        result = determine_certification(
            self._make_vc_result(True, 50),
            self._make_pmf("NO-GO", 4.0),
        )
        assert result.certification == CertificationLevel.FAILED_COMMUNITY
        assert result.stage_reached == GauntletStage.COMMUNITY_GATE

    def test_certified_good(self):
        result = determine_certification(
            self._make_vc_result(True, 50),
            self._make_pmf("CONDITIONAL GO", 6.0),
        )
        assert result.certification == CertificationLevel.CERTIFIED_GOOD
        assert result.stage_reached == GauntletStage.CERTIFIED

    def test_certified_great(self):
        result = determine_certification(
            self._make_vc_result(True, 80),
            self._make_pmf("GO", 8.0),
        )
        assert result.certification == CertificationLevel.CERTIFIED_GREAT

    def test_gauntlet_report_contains_badge(self):
        result = determine_certification(
            self._make_vc_result(True, 80),
            self._make_pmf("GO", 8.0),
        )
        report = build_gauntlet_report(result, "https://example.com")
        assert "CERTIFIED GREAT" in report

    def test_gauntlet_report_failed(self):
        result = determine_certification(self._make_vc_result(False, 20))
        report = build_gauntlet_report(result, "https://example.com")
        assert "DESTROYED" in report

    def test_final_score_combined(self):
        result = determine_certification(
            self._make_vc_result(True, 60),
            self._make_pmf("GO", 7.0),
        )
        # (60 + 70) / 2 = 65
        assert result.final_score == 65
