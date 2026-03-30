"""Report builder — generates FEEDBACK-REPORT.md from analysis results."""

from datetime import datetime, timezone

from roastmymvp.personas.models import PersonaFeedback, PMFSignals


def build_report(
    url: str,
    feedbacks: tuple[PersonaFeedback, ...],
    pmf: PMFSignals,
    browser_errors: tuple[str, ...] = (),
) -> str:
    """Generate the full markdown feedback report."""
    sections: list[str] = []

    # Header
    sections.append(
        f"# AI Beta Test — Feedback Report\n\n"
        f"**URL:** {url}\n"
        f"**Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n"
        f"**Personas tested:** {len(feedbacks)}\n"
        f"**Verdict:** {pmf.verdict}"
    )

    # PMF Signals
    sections.append(_build_pmf_section(pmf))

    # UX Scores summary
    sections.append(_build_ux_summary(feedbacks))

    # Browser errors (Layer 1)
    if browser_errors:
        sections.append(_build_errors_section(browser_errors))

    # Top friction points
    sections.append(_build_friction_section(feedbacks))

    # Bugs found
    sections.append(_build_bugs_section(feedbacks))

    # Praise
    sections.append(_build_praise_section(feedbacks))

    # Suggestions
    sections.append(_build_suggestions_section(feedbacks))

    # Individual persona narratives
    sections.append(_build_narratives_section(feedbacks))

    return "\n\n---\n\n".join(sections)


def _build_pmf_section(pmf: PMFSignals) -> str:
    return (
        f"## PMF Signals\n\n"
        f"| Metric | Value |\n"
        f"|--------|-------|\n"
        f"| Would download | {pmf.download_rate:.0%} |\n"
        f"| Would pay | {pmf.pay_rate:.0%} |\n"
        f"| Would return | {pmf.return_rate:.0%} |\n"
        f"| Avg UX score | {pmf.avg_ux_score:.1f}/10 |\n"
        f"| **Verdict** | **{pmf.verdict}** |"
    )


def _build_ux_summary(feedbacks: tuple[PersonaFeedback, ...]) -> str:
    if not feedbacks:
        return "## UX Scores\n\nNo data."

    dims = ["time_to_value", "navigation_clarity", "visual_design", "error_handling", "mobile_experience"]
    lines = ["## UX Scores\n", "| Dimension | Avg Score |", "|-----------|-----------|"]

    for dim in dims:
        avg = sum(getattr(f.ux_scores, dim) for f in feedbacks) / len(feedbacks)
        label = dim.replace("_", " ").title()
        bar = "█" * int(avg) + "░" * (10 - int(avg))
        lines.append(f"| {label} | {bar} {avg:.1f}/10 |")

    return "\n".join(lines)


def _build_friction_section(feedbacks: tuple[PersonaFeedback, ...]) -> str:
    all_points: dict[str, int] = {}
    for f in feedbacks:
        for point in f.friction_points:
            all_points[point] = all_points.get(point, 0) + 1

    sorted_points = sorted(all_points.items(), key=lambda x: x[1], reverse=True)
    lines = ["## Top Friction Points\n"]
    for point, count in sorted_points[:10]:
        lines.append(f"- **({count}x)** {point}")

    return "\n".join(lines) if sorted_points else "## Top Friction Points\n\nNone reported."


def _build_bugs_section(feedbacks: tuple[PersonaFeedback, ...]) -> str:
    all_bugs: dict[str, int] = {}
    for f in feedbacks:
        for bug in f.bugs_found:
            all_bugs[bug] = all_bugs.get(bug, 0) + 1

    sorted_bugs = sorted(all_bugs.items(), key=lambda x: x[1], reverse=True)
    lines = ["## Bugs Found\n"]
    for bug, count in sorted_bugs:
        lines.append(f"- **({count}x)** {bug}")

    return "\n".join(lines) if sorted_bugs else "## Bugs Found\n\nNone reported."


def _build_praise_section(feedbacks: tuple[PersonaFeedback, ...]) -> str:
    all_praise: dict[str, int] = {}
    for f in feedbacks:
        for p in f.praise:
            all_praise[p] = all_praise.get(p, 0) + 1

    sorted_praise = sorted(all_praise.items(), key=lambda x: x[1], reverse=True)
    lines = ["## What Users Liked\n"]
    for praise, count in sorted_praise[:10]:
        lines.append(f"- **({count}x)** {praise}")

    return "\n".join(lines) if sorted_praise else "## What Users Liked\n\nNothing highlighted."


def _build_suggestions_section(feedbacks: tuple[PersonaFeedback, ...]) -> str:
    all_suggestions: dict[str, int] = {}
    for f in feedbacks:
        for s in f.suggestions:
            all_suggestions[s] = all_suggestions.get(s, 0) + 1

    sorted_sug = sorted(all_suggestions.items(), key=lambda x: x[1], reverse=True)
    lines = ["## Suggestions\n"]
    for sug, count in sorted_sug[:10]:
        lines.append(f"- **({count}x)** {sug}")

    return "\n".join(lines) if sorted_sug else "## Suggestions\n\nNone."


def _build_errors_section(errors: tuple[str, ...]) -> str:
    lines = ["## Technical Errors (Layer 1)\n"]
    for e in errors:
        lines.append(f"- {e}")
    return "\n".join(lines)


def _build_narratives_section(feedbacks: tuple[PersonaFeedback, ...]) -> str:
    lines = ["## Individual Persona Feedback\n"]
    for f in feedbacks:
        p = f.persona
        lines.append(f"### {p.name} ({p.age}, {p.background})")
        lines.append(f"Tech: {p.tech_savvy:.0%} | Patience: {p.patience_seconds}s | "
                     f"Download: {'✓' if f.would_download else '✗'} | "
                     f"Pay: {'✓' if f.would_pay else '✗'} | "
                     f"Return: {'✓' if f.would_return else '✗'}")
        lines.append(f"\n{f.narrative}\n")
    return "\n".join(lines)
