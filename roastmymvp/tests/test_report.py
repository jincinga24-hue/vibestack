"""Tests for report builder and stats modules."""

import pytest

from roastmymvp.personas.models import (
    PersonaFeedback,
    PersonaProfile,
    PMFSignals,
    UXScore,
)
from roastmymvp.report.builder import build_report
from roastmymvp.report.stats import calculate_pmf_signals


def _make_feedback(
    download: bool = True,
    pay: bool = False,
    ret: bool = True,
    ux_overall: float = 7.0,
    name: str = "Test User",
) -> PersonaFeedback:
    return PersonaFeedback(
        persona=PersonaProfile(
            name=name, age=25, background="Developer",
            tech_savvy=0.8, patience_seconds=30,
            language="en", has_alternative=False,
        ),
        would_download=download,
        would_pay=pay,
        would_return=ret,
        ux_scores=UXScore(
            time_to_value=7, navigation_clarity=7,
            visual_design=7, error_handling=7,
            mobile_experience=7, overall=ux_overall,
        ),
        friction_points=("Slow login",),
        bugs_found=("404 on /settings",),
        praise=("Clean design",),
        narrative="Good product overall.",
        suggestions=("Add dark mode",),
    )


class TestCalculatePMFSignals:
    def test_empty_feedbacks(self):
        pmf = calculate_pmf_signals(())
        assert pmf.verdict == "NO-GO"
        assert pmf.download_rate == 0.0

    def test_all_positive(self):
        feedbacks = tuple(_make_feedback(True, True, True, 8.0) for _ in range(10))
        pmf = calculate_pmf_signals(feedbacks)
        assert pmf.verdict == "GO"
        assert pmf.download_rate == 1.0
        assert pmf.pay_rate == 1.0

    def test_mixed_signals(self):
        feedbacks = (
            _make_feedback(True, False, True, 7.0),
            _make_feedback(True, False, False, 5.0),
            _make_feedback(False, False, False, 3.0),
        )
        pmf = calculate_pmf_signals(feedbacks)
        assert pmf.verdict in ("CONDITIONAL GO", "NO-GO")

    def test_conditional_go(self):
        feedbacks = tuple(
            _make_feedback(True, True, True, 7.0) if i < 7
            else _make_feedback(False, False, False, 3.0)
            for i in range(10)
        )
        pmf = calculate_pmf_signals(feedbacks)
        assert pmf.verdict in ("GO", "CONDITIONAL GO")

    def test_rates_are_rounded(self):
        feedbacks = (_make_feedback(True, False, True),) * 3
        pmf = calculate_pmf_signals(feedbacks)
        assert isinstance(pmf.download_rate, float)
        assert len(str(pmf.download_rate).split(".")[-1]) <= 3


class TestBuildReport:
    def test_contains_url(self):
        feedbacks = (_make_feedback(),)
        pmf = calculate_pmf_signals(feedbacks)
        report = build_report("https://example.com", feedbacks, pmf)
        assert "https://example.com" in report

    def test_contains_verdict(self):
        feedbacks = (_make_feedback(),)
        pmf = calculate_pmf_signals(feedbacks)
        report = build_report("https://example.com", feedbacks, pmf)
        assert pmf.verdict in report

    def test_contains_friction_points(self):
        feedbacks = (_make_feedback(),)
        pmf = calculate_pmf_signals(feedbacks)
        report = build_report("https://example.com", feedbacks, pmf)
        assert "Slow login" in report

    def test_contains_bugs(self):
        feedbacks = (_make_feedback(),)
        pmf = calculate_pmf_signals(feedbacks)
        report = build_report("https://example.com", feedbacks, pmf)
        assert "404 on /settings" in report

    def test_contains_persona_narratives(self):
        feedbacks = (_make_feedback(name="Alice Test"),)
        pmf = calculate_pmf_signals(feedbacks)
        report = build_report("https://example.com", feedbacks, pmf)
        assert "Alice Test" in report
        assert "Good product overall." in report

    def test_contains_browser_errors(self):
        feedbacks = (_make_feedback(),)
        pmf = calculate_pmf_signals(feedbacks)
        report = build_report(
            "https://example.com", feedbacks, pmf,
            browser_errors=("JS Error: undefined is not a function",),
        )
        assert "undefined is not a function" in report

    def test_aggregates_duplicate_friction(self):
        feedbacks = (_make_feedback(), _make_feedback())
        pmf = calculate_pmf_signals(feedbacks)
        report = build_report("https://example.com", feedbacks, pmf)
        assert "(2x)" in report

    def test_returns_string(self):
        feedbacks = (_make_feedback(),)
        pmf = calculate_pmf_signals(feedbacks)
        report = build_report("https://example.com", feedbacks, pmf)
        assert isinstance(report, str)
        assert len(report) > 100
