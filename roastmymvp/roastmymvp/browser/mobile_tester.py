"""Responsive / mobile testing — detect overflow, tap target, and visibility issues."""

from dataclasses import dataclass

from playwright.async_api import Page

from roastmymvp.browser.models import BrowserError, ErrorSeverity

import time

MOBILE_VIEWPORT = {"width": 375, "height": 812}


@dataclass(frozen=True)
class MobileIssue:
    description: str
    selector: str
    severity: ErrorSeverity


async def check_horizontal_overflow(page: Page) -> tuple[MobileIssue, ...]:
    """Detect elements that overflow the mobile viewport horizontally."""
    overflows = await page.evaluate("""() => {
        const vw = window.innerWidth;
        const results = [];
        document.querySelectorAll('*').forEach(el => {
            const rect = el.getBoundingClientRect();
            if (rect.right > vw + 5 && rect.width > 0) {
                const tag = el.tagName.toLowerCase();
                const cls = el.className ? '.' + el.className.split(' ')[0] : '';
                results.push({
                    selector: tag + cls,
                    right: rect.right,
                    width: rect.width,
                });
            }
        });
        return results.slice(0, 20);
    }""")

    return tuple(
        MobileIssue(
            description=f"Element overflows viewport (right={o['right']:.0f}px, width={o['width']:.0f}px)",
            selector=o["selector"],
            severity=ErrorSeverity.WARNING,
        )
        for o in overflows
    )


async def check_tap_targets(page: Page) -> tuple[MobileIssue, ...]:
    """Find tap targets smaller than 44x44px (Apple HIG minimum)."""
    small_targets = await page.evaluate("""() => {
        const results = [];
        const interactive = document.querySelectorAll('a, button, input, select, textarea, [role="button"]');
        interactive.forEach(el => {
            const rect = el.getBoundingClientRect();
            if (rect.width > 0 && rect.height > 0 && (rect.width < 44 || rect.height < 44)) {
                const tag = el.tagName.toLowerCase();
                const cls = el.className ? '.' + el.className.split(' ')[0] : '';
                results.push({
                    selector: tag + cls,
                    width: rect.width,
                    height: rect.height,
                });
            }
        });
        return results.slice(0, 20);
    }""")

    return tuple(
        MobileIssue(
            description=f"Tap target too small ({t['width']:.0f}x{t['height']:.0f}px, min 44x44)",
            selector=t["selector"],
            severity=ErrorSeverity.INFO,
        )
        for t in small_targets
    )


async def run_mobile_checks(page: Page) -> tuple[BrowserError, ...]:
    """Run all mobile checks and return as BrowserError entries."""
    original_viewport = page.viewport_size
    await page.set_viewport_size(MOBILE_VIEWPORT)
    await page.wait_for_timeout(500)

    overflow_issues = await check_horizontal_overflow(page)
    tap_issues = await check_tap_targets(page)

    if original_viewport:
        await page.set_viewport_size(original_viewport)

    errors: list[BrowserError] = []
    for issue in (*overflow_issues, *tap_issues):
        errors.append(
            BrowserError(
                message=f"[Mobile] {issue.description} — {issue.selector}",
                severity=issue.severity,
                url=page.url,
                timestamp=time.time(),
                source="mobile_tester",
            )
        )

    return tuple(errors)
