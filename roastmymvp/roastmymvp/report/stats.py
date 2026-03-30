"""Aggregate statistics from persona feedback."""

from roastmymvp.personas.models import PersonaFeedback, PMFSignals


def calculate_pmf_signals(
    feedbacks: tuple[PersonaFeedback, ...],
) -> PMFSignals:
    """Calculate PMF signals from all persona feedback."""
    if not feedbacks:
        return PMFSignals(
            download_rate=0.0,
            pay_rate=0.0,
            return_rate=0.0,
            avg_ux_score=0.0,
            verdict="NO-GO",
        )

    total = len(feedbacks)
    download_rate = sum(1 for f in feedbacks if f.would_download) / total
    pay_rate = sum(1 for f in feedbacks if f.would_pay) / total
    return_rate = sum(1 for f in feedbacks if f.would_return) / total
    avg_ux = sum(f.ux_scores.overall for f in feedbacks) / total

    verdict = _determine_verdict(download_rate, pay_rate, return_rate, avg_ux)

    return PMFSignals(
        download_rate=round(download_rate, 3),
        pay_rate=round(pay_rate, 3),
        return_rate=round(return_rate, 3),
        avg_ux_score=round(avg_ux, 2),
        verdict=verdict,
    )


def _determine_verdict(
    download_rate: float,
    pay_rate: float,
    return_rate: float,
    avg_ux: float,
) -> str:
    """Determine GO / CONDITIONAL GO / NO-GO."""
    score = 0
    if download_rate >= 0.7:
        score += 1
    if pay_rate >= 0.3:
        score += 1
    if return_rate >= 0.5:
        score += 1
    if avg_ux >= 6.0:
        score += 1

    if score >= 3:
        return "GO"
    elif score >= 2:
        return "CONDITIONAL GO"
    else:
        return "NO-GO"
