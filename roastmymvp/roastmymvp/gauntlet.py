"""Gauntlet pipeline — VC Gate → Community Gate → Certification."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from roastmymvp.personas.models import PMFSignals
from roastmymvp.vc.models import VCGateResult


class GauntletStage(Enum):
    VC_GATE = "vc_gate"
    COMMUNITY_GATE = "community_gate"
    CERTIFIED = "certified"


class CertificationLevel(Enum):
    FAILED_VC = "failed_vc"                 # Didn't pass VC gate
    FAILED_COMMUNITY = "failed_community"   # Passed VC, failed community
    CERTIFIED_GOOD = "certified_good"       # Passed both gates
    CERTIFIED_GREAT = "certified_great"     # Passed both with high scores


@dataclass(frozen=True)
class GauntletResult:
    stage_reached: GauntletStage
    certification: CertificationLevel
    vc_result: VCGateResult | None = None
    community_result: PMFSignals | None = None
    vc_report: str = ""
    community_report: str = ""
    final_score: int = 0            # 0-100 combined score


def determine_certification(
    vc_result: VCGateResult,
    community_result: PMFSignals | None = None,
) -> GauntletResult:
    """Determine final certification based on both gates."""

    # Stage 1: VC Gate
    if not vc_result.passed:
        return GauntletResult(
            stage_reached=GauntletStage.VC_GATE,
            certification=CertificationLevel.FAILED_VC,
            vc_result=vc_result,
            final_score=vc_result.score,
        )

    # Stage 2: Community Gate (only if VC passed)
    if community_result is None:
        # VC passed but community not run yet
        return GauntletResult(
            stage_reached=GauntletStage.VC_GATE,
            certification=CertificationLevel.FAILED_VC,  # Incomplete
            vc_result=vc_result,
            final_score=vc_result.score,
        )

    community_passed = community_result.verdict in ("GO", "CONDITIONAL GO")

    if not community_passed:
        return GauntletResult(
            stage_reached=GauntletStage.COMMUNITY_GATE,
            certification=CertificationLevel.FAILED_COMMUNITY,
            vc_result=vc_result,
            community_result=community_result,
            final_score=round((vc_result.score + community_result.avg_ux_score * 10) / 2),
        )

    # Both passed — determine level
    combined_score = round((vc_result.score + community_result.avg_ux_score * 10) / 2)

    if combined_score >= 70 and community_result.verdict == "GO":
        cert = CertificationLevel.CERTIFIED_GREAT
    else:
        cert = CertificationLevel.CERTIFIED_GOOD

    return GauntletResult(
        stage_reached=GauntletStage.CERTIFIED,
        certification=cert,
        vc_result=vc_result,
        community_result=community_result,
        final_score=combined_score,
    )


def build_gauntlet_report(result: GauntletResult, url: str) -> str:
    """Build the final gauntlet certification report."""
    lines: list[str] = []

    # Header art
    if result.certification == CertificationLevel.CERTIFIED_GREAT:
        badge = "🏆 CERTIFIED GREAT PROJECT 🏆"
    elif result.certification == CertificationLevel.CERTIFIED_GOOD:
        badge = "✅ CERTIFIED GOOD PROJECT ✅"
    elif result.certification == CertificationLevel.FAILED_COMMUNITY:
        badge = "😤 PASSED VC, FAILED COMMUNITY 😤"
    else:
        badge = "💀 DESTROYED BY VCS 💀"

    lines.append(f"# THE GAUNTLET — Final Report\n")
    lines.append(f"## {badge}\n")
    lines.append(f"**URL:** {url}")
    lines.append(f"**Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"**Final Score:** {result.final_score}/100")
    lines.append(f"**Stage Reached:** {result.stage_reached.value}\n")

    # Progress bar
    stages = ["VC GATE", "COMMUNITY", "CERTIFIED"]
    reached = {"vc_gate": 1, "community_gate": 2, "certified": 3}[result.stage_reached.value]
    progress = " → ".join(
        f"**[{s}]**" if i + 1 <= reached else f"~~{s}~~"
        for i, s in enumerate(stages)
    )
    lines.append(f"### Progress: {progress}\n")

    # VC Gate summary
    if result.vc_result:
        vc = result.vc_result
        vc_status = "PASSED ✅" if vc.passed else "FAILED ❌"
        lines.append(f"---\n\n## Stage 1: VC Gate — {vc_status} ({vc.score}/100)\n")
        lines.append(vc.summary_roast)

    # Community Gate summary
    if result.community_result:
        cr = result.community_result
        com_status = "PASSED ✅" if cr.verdict in ("GO", "CONDITIONAL GO") else "FAILED ❌"
        lines.append(f"\n---\n\n## Stage 2: Community Gate — {com_status}\n")
        lines.append(f"- Download rate: {cr.download_rate:.0%}")
        lines.append(f"- Pay rate: {cr.pay_rate:.0%}")
        lines.append(f"- Return rate: {cr.return_rate:.0%}")
        lines.append(f"- Avg UX: {cr.avg_ux_score:.1f}/10")
        lines.append(f"- Verdict: **{cr.verdict}**")

    # Final verdict
    lines.append(f"\n---\n\n## Final Verdict\n")
    if result.certification == CertificationLevel.CERTIFIED_GREAT:
        lines.append("This project passed both the VC panel AND community testing with high scores.")
        lines.append("**This is a good project. Ship it.**")
    elif result.certification == CertificationLevel.CERTIFIED_GOOD:
        lines.append("This project passed both gates. It has potential but room to improve.")
        lines.append("**Ship it, but keep iterating.**")
    elif result.certification == CertificationLevel.FAILED_COMMUNITY:
        lines.append("VCs saw potential, but real users didn't love it.")
        lines.append("**Fix UX issues and re-run community testing.**")
    else:
        lines.append("The VC panel destroyed this. Community testing is locked.")
        lines.append("**Go back. Fix fundamentals. Try again.**")

    return "\n".join(lines)
