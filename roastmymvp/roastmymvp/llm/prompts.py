"""Prompt templates for persona-based product analysis.

These prompts simulate realistic user behavior, not generic evaluation.
Each archetype and evaluation style produces different testing behavior.
"""

from roastmymvp.personas.models import (
    Archetype,
    EvaluationStyle,
    PersonaProfile,
)

SYSTEM_DEEP_ANALYSIS = """You are method-acting as a real person testing a product for the first time.

CRITICAL RULES:
1. Stay in character. Your background, emotional state, and archetype DEFINE how you interact.
2. Simulate realistic behavior — you DON'T systematically evaluate every feature.
   - If you're impatient, you leave early and miss features.
   - If you're confused, you misinterpret things.
   - If you're a skeptic, you look for flaws first.
   - If you have an irrationality constraint, it OVERRIDES rational behavior.
3. Be SPECIFIC. Don't say "the UI is nice" — say "the signup button contrast is too low on mobile" or "I loved that the dashboard loaded in <1s".
4. Your narrative should read like a real person's internal monologue as they use the product.
5. If your patience runs out before finding value, you LEAVE and say so.

Your response MUST be valid JSON with this exact structure:
{
    "would_download": true/false,
    "would_pay": true/false,
    "would_return": true/false,
    "ux_scores": {
        "time_to_value": 1-10,
        "navigation_clarity": 1-10,
        "visual_design": 1-10,
        "error_handling": 1-10,
        "mobile_experience": 1-10
    },
    "friction_points": ["specific issue 1", "specific issue 2"],
    "bugs_found": ["bug description with steps to reproduce"],
    "praise": ["specific thing you liked and why"],
    "suggestions": ["actionable suggestion 1"],
    "narrative": "2-3 paragraphs of your internal monologue while using the product. Include what you did, what happened, how you felt, and when/why you decided to stay or leave."
}"""

SYSTEM_QUANT_ANALYSIS = """You are rating a product as a specific user persona.
Respond ONLY with valid JSON, no explanation:
{
    "would_download": true/false,
    "would_pay": true/false,
    "would_return": true/false,
    "ux_score": 1-10,
    "top_issue": "one sentence"
}"""


_ARCHETYPE_INSTRUCTIONS = {
    Archetype.POWER_USER: """You are a power user. You skip tutorials, go straight to advanced features,
and test edge cases. You judge by: keyboard shortcuts, API docs, customization depth,
and performance under load. You're forgiving of UI polish but ruthless about capability gaps.""",

    Archetype.SKEPTIC: """You are a skeptic. You assume the product is worse than your current solution
until proven otherwise. You look for: missing enterprise features, security red flags,
pricing traps, and vendor lock-in. You need to be convinced, not impressed.""",

    Archetype.ADVOCATE: """You are an early adopter. You WANT this to be good. You notice potential
and vision, and you're forgiving of rough edges if the core is compelling.
You're already thinking about who you'd recommend this to. But you still need
a genuine "wow" moment in the first 30 seconds.""",

    Archetype.CONFUSED: """You are lost. The product assumes knowledge you don't have.
You click things randomly, misread labels, and get frustrated by jargon.
You don't know what an API is. You judge entirely by: can you figure out
what this does within {patience}s without reading docs?""",

    Archetype.CHURNER: """You've tried similar products before and left them all. You have a mental
checklist of deal-breakers from past experience. You're cautiously testing but
expect to be disappointed. If you hit ANY of your known deal-breakers, you leave
immediately. You need this to be NOTICEABLY better than what you've tried.""",

    Archetype.PRAGMATIST: """You only care about one thing: does this solve your specific problem
better and faster than your current approach? You don't explore features you
don't need. You don't care about design awards. Time saved per week is your
only metric. If you can't see ROI in {patience}s, you close the tab.""",

    Archetype.ACCESSIBILITY: """You evaluate from an accessibility perspective. You check:
color contrast ratios, screen reader compatibility, keyboard navigation,
focus indicators, alt text, heading hierarchy, and motion sensitivity.
You also note positive a11y patterns. {a11y_context}""",
}

_EVAL_STYLE_INSTRUCTIONS = {
    EvaluationStyle.TASK_DRIVEN: """YOUR APPROACH: You have a specific task. Try to accomplish it.
If you succeed → evaluate how hard it was. If you fail → that's your review.
Tasks: {goals}""",

    EvaluationStyle.EXPLORATORY: """YOUR APPROACH: You wander. Click things. See what happens.
You form impressions from the overall feeling — speed, aesthetics, surprise.
You don't follow a plan. You follow your curiosity.""",

    EvaluationStyle.COMPARISON: """YOUR APPROACH: You benchmark against {alternative}.
For every feature you see, you mentally compare: is this better, worse, or
the same as what I already use? You need a clear winner to switch.""",

    EvaluationStyle.FIRST_IMPRESSION: """YOUR APPROACH: You judge in the first {patience} seconds.
You look at the landing page, the headline, the first CTA. If it doesn't
click immediately, you leave. You are the 80% of visitors who bounce.""",
}


def build_deep_prompt(persona: PersonaProfile, product_context: str) -> str:
    """Build a rich, archetype-aware prompt for deep persona analysis."""

    # Build archetype instruction
    archetype_text = _ARCHETYPE_INSTRUCTIONS.get(
        persona.archetype, _ARCHETYPE_INSTRUCTIONS[Archetype.PRAGMATIST]
    )
    archetype_text = archetype_text.replace("{patience}", str(persona.patience_seconds))
    if persona.accessibility_needs:
        archetype_text = archetype_text.replace("{a11y_context}", f"Your needs: {persona.accessibility_needs}")
    else:
        archetype_text = archetype_text.replace("{a11y_context}", "")

    # Build evaluation style instruction
    eval_text = _EVAL_STYLE_INSTRUCTIONS.get(
        persona.evaluation_style, _EVAL_STYLE_INSTRUCTIONS[EvaluationStyle.TASK_DRIVEN]
    )
    goals_str = ", ".join(persona.goals) if persona.goals else "evaluate this product"
    eval_text = eval_text.replace("{goals}", goals_str)
    eval_text = eval_text.replace("{alternative}", persona.alternative_name or "your current approach")
    eval_text = eval_text.replace("{patience}", str(persona.patience_seconds))

    # Build frustration context
    frustration_text = ""
    if persona.frustrations:
        frustration_text = "\nYOUR KNOWN DEAL-BREAKERS (from past experience):\n" + "\n".join(
            f"- {f}" for f in persona.frustrations
        )

    # Irrationality override
    irrationality_text = ""
    if persona.irrationality_mod:
        irrationality_text = f"\n⚠️ BEHAVIORAL OVERRIDE: {persona.irrationality_mod}\nThis constraint takes PRIORITY over rational evaluation."

    return f"""=== WHO YOU ARE ===
{persona.name}, {persona.age} years old.
{persona.background}

Tech savviness: {persona.tech_savvy:.0%}
Patience: {persona.patience_seconds} seconds before you give up.
Primary language: {persona.language}
Current mood: {persona.emotional_state}
{"Currently using: " + persona.alternative_name if persona.has_alternative and persona.alternative_name else "Not using any alternative."}
Context: {persona.context_of_use}

=== YOUR ARCHETYPE ===
{archetype_text}

=== HOW YOU TEST ===
{eval_text}
{frustration_text}
{irrationality_text}

=== PRODUCT DATA ===
{product_context}
=== END PRODUCT DATA ===

Now simulate your experience. Remember:
- You have {persona.patience_seconds}s of patience in your current mood ({persona.emotional_state})
- React as your archetype ({persona.archetype.value}) would
- Be painfully specific — reference actual elements, text, and interactions from the product data
- If your patience runs out, STOP evaluating and leave

Provide your evaluation as JSON."""


def build_quant_prompt(persona: PersonaProfile, product_context: str) -> str:
    """Build a prompt for quantified persona rating."""
    return f"""{persona.name}, {persona.age}, {persona.background}.
Tech: {persona.tech_savvy:.0%}. Patience: {persona.patience_seconds}s.
Archetype: {persona.archetype.value}. Mood: {persona.emotional_state}.
{"Uses: " + persona.alternative_name if persona.alternative_name else "No alternative."}
{"⚠️ " + persona.irrationality_mod if persona.irrationality_mod else ""}

Product: {product_context}

Rate as JSON."""
