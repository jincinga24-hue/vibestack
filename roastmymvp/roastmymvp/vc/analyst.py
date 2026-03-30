"""VC roast analyst — runs the VC panel and determines pass/fail gate."""

import asyncio
import json
import logging

from roastmymvp.llm.client import LLMClient
from roastmymvp.llm.models import LLMRequest, ModelTier
from roastmymvp.vc.models import (
    InvestmentDecision,
    RoastVerdict,
    VCGateResult,
    VCPersona,
)
from roastmymvp.vc.personas import DEFAULT_VC_PANEL
from roastmymvp.vc.prompts import SYSTEM_VC_ROAST, build_vc_roast_prompt

logger = logging.getLogger(__name__)

# Pass threshold: average score >= 40 AND at least one "maybe" or "invest"
PASS_THRESHOLD = 40


def _parse_verdict(vc: VCPersona, raw_json: str) -> RoastVerdict:
    """Parse LLM response into a RoastVerdict."""
    data = json.loads(raw_json)

    decision_map = {
        "pass": InvestmentDecision.PASS,
        "maybe": InvestmentDecision.MAYBE,
        "invest": InvestmentDecision.INVEST,
    }

    return RoastVerdict(
        vc=vc,
        decision=decision_map.get(data.get("decision", "pass"), InvestmentDecision.PASS),
        roast=data.get("roast", ""),
        kill_shot=data.get("kill_shot", ""),
        score=data.get("score", 0),
        would_take_meeting=data.get("would_take_meeting", False),
        questions_that_destroyed=tuple(data.get("questions_that_destroyed", ())),
        grudging_praise=data.get("grudging_praise", ""),
    )


def _error_verdict(vc: VCPersona, error_msg: str) -> RoastVerdict:
    """Fallback verdict when LLM call fails."""
    return RoastVerdict(
        vc=vc,
        decision=InvestmentDecision.PASS,
        roast=f"[Analysis failed: {error_msg}]",
        kill_shot="Couldn't even analyze this — that's a red flag.",
        score=0,
        would_take_meeting=False,
        questions_that_destroyed=(),
        grudging_praise="At least they tried.",
    )


async def _roast_one(
    vc: VCPersona,
    product_context: str,
    pitch_text: str,
    llm_client: LLMClient,
    founder_summary: str = "",
) -> RoastVerdict:
    """Run one VC's roast evaluation."""
    try:
        request = LLMRequest(
            prompt=build_vc_roast_prompt(vc, product_context, pitch_text, founder_summary),
            system=SYSTEM_VC_ROAST,
            model_tier=ModelTier.DEEP,
            max_tokens=4096,
            temperature=0.8,  # Higher temp for more creative roasts
        )
        response = await llm_client.send(request)
        return _parse_verdict(vc, response.content)
    except Exception as e:
        logger.warning("VC roast failed for %s: %s", vc.name, e)
        return _error_verdict(vc, str(e))


async def run_vc_panel(
    product_context: str,
    llm_client: LLMClient,
    pitch_text: str = "",
    panel: tuple[VCPersona, ...] = DEFAULT_VC_PANEL,
    founder_summary: str = "",
) -> VCGateResult:
    """Run the full VC panel and determine pass/fail."""
    tasks = [
        _roast_one(vc, product_context, pitch_text, llm_client, founder_summary)
        for vc in panel
    ]
    verdicts = tuple(await asyncio.gather(*tasks))

    # Calculate gate result
    avg_score = sum(v.score for v in verdicts) / len(verdicts) if verdicts else 0
    has_interest = any(
        v.decision in (InvestmentDecision.MAYBE, InvestmentDecision.INVEST)
        for v in verdicts
    )
    passed = avg_score >= PASS_THRESHOLD and has_interest

    # Aggregate must-fix issues
    all_kill_shots = [v.kill_shot for v in verdicts if v.kill_shot]
    must_fix = tuple(dict.fromkeys(all_kill_shots))[:5]  # dedupe, top 5

    # Certification
    if avg_score >= 70:
        certification = "IMPRESSED"
    elif avg_score >= PASS_THRESHOLD:
        certification = "SURVIVED"
    else:
        certification = "DESTROYED"

    # Build summary roast
    summary = _build_summary_roast(verdicts, avg_score, certification)

    return VCGateResult(
        passed=passed,
        score=round(avg_score),
        verdicts=verdicts,
        summary_roast=summary,
        must_fix=must_fix,
        certification=certification,
    )


def _build_summary_roast(
    verdicts: tuple[RoastVerdict, ...],
    avg_score: int,
    certification: str,
) -> str:
    """Build the aggregate summary of the VC panel."""
    lines = []

    if certification == "DESTROYED":
        lines.append("💀 **VERDICT: DESTROYED**")
        lines.append("The panel has spoken. This is not ready. Not even close.")
    elif certification == "SURVIVED":
        lines.append("😤 **VERDICT: SURVIVED**")
        lines.append("You didn't die, but you didn't impress either. Fix the issues below.")
    else:
        lines.append("🔥 **VERDICT: IMPRESSED**")
        lines.append("The panel sees something here. Don't let it go to your head.")

    lines.append(f"\n**Average Score: {avg_score}/100**\n")

    # Individual scores
    for v in verdicts:
        emoji = "❌" if v.decision == InvestmentDecision.PASS else "🤔" if v.decision == InvestmentDecision.MAYBE else "✅"
        lines.append(f"{emoji} **{v.vc.name}** ({v.vc.fund}): {v.score}/100 — {v.decision.value.upper()}")
        lines.append(f"   Kill shot: *\"{v.kill_shot}\"*")
        if v.grudging_praise:
            lines.append(f"   Grudging praise: \"{v.grudging_praise}\"")
        lines.append("")

    return "\n".join(lines)
