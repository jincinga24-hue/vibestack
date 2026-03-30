"""VC roast report generator."""

from datetime import datetime, timezone

from roastmymvp.vc.models import InvestmentDecision, VCGateResult


def build_vc_report(url: str, gate: VCGateResult) -> str:
    """Generate the VC roast report markdown."""
    sections: list[str] = []

    # Header
    status = "PASSED ✅" if gate.passed else "FAILED ❌"
    sections.append(
        f"# VC Roast Report — {gate.certification}\n\n"
        f"**URL:** {url}\n"
        f"**Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n"
        f"**Gate Status:** {status}\n"
        f"**Average Score:** {gate.score}/100\n"
        f"**Panel Size:** {len(gate.verdicts)} VCs"
    )

    # Summary
    sections.append(gate.summary_roast)

    # Must fix (if failed)
    if gate.must_fix:
        fix_lines = ["## Must Fix Before Community Test\n"]
        for i, fix in enumerate(gate.must_fix, 1):
            fix_lines.append(f"{i}. {fix}")
        sections.append("\n".join(fix_lines))

    # Individual roasts
    roast_lines = ["## Full Roasts\n"]
    for v in gate.verdicts:
        emoji = "❌" if v.decision == InvestmentDecision.PASS else "🤔" if v.decision == InvestmentDecision.MAYBE else "✅"
        roast_lines.append(f"### {emoji} {v.vc.name} — {v.vc.title}, {v.vc.fund}")
        roast_lines.append(f"**Score:** {v.score}/100 | **Decision:** {v.decision.value.upper()} | "
                          f"**Meeting:** {'Yes' if v.would_take_meeting else 'No'}\n")
        roast_lines.append(v.roast)
        roast_lines.append(f"\n**Kill Shot:** *\"{v.kill_shot}\"*\n")

        if v.questions_that_destroyed:
            roast_lines.append("**Questions That Destroyed You:**")
            for q in v.questions_that_destroyed:
                roast_lines.append(f"- {q}")

        roast_lines.append(f"\n**Grudging Praise:** \"{v.grudging_praise}\"\n")
        roast_lines.append("---\n")

    sections.append("\n".join(roast_lines))

    # Next steps
    if gate.passed:
        sections.append(
            "## Next Steps\n\n"
            "You survived the VC panel. Proceeding to **Community Testing**.\n"
            "Fix the issues above first — community testers will find them too."
        )
    else:
        sections.append(
            "## Next Steps\n\n"
            "You did not pass the VC gate. Community testing is **LOCKED**.\n\n"
            "Fix the must-fix issues above and run `ai-beta-test --mode vc` again.\n"
            "When you pass, you'll unlock community testing with `--mode gauntlet`."
        )

    return "\n\n---\n\n".join(sections)
