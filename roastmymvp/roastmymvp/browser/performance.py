"""Performance metrics collection from browser pages."""

from playwright.async_api import Page

from roastmymvp.browser.models import PerformanceMetrics


async def collect_performance(page: Page) -> PerformanceMetrics:
    """Collect performance timing and resource metrics from the page."""
    timing = await page.evaluate("""() => {
        const t = performance.timing;
        return {
            load_time: t.loadEventEnd - t.navigationStart,
            dom_content_loaded: t.domContentLoadedEventEnd - t.navigationStart,
        };
    }""")

    resources = await page.evaluate("""() => {
        const entries = performance.getEntriesByType('resource');
        return {
            count: entries.length,
            total_size: entries.reduce((sum, e) => sum + (e.transferSize || 0), 0),
        };
    }""")

    js_errors = await page.evaluate("""() => {
        return window.__roastmymvp_errors || [];
    }""")

    return PerformanceMetrics(
        load_time_ms=max(0, timing["load_time"]),
        dom_content_loaded_ms=max(0, timing["dom_content_loaded"]),
        resource_count=resources["count"],
        total_resource_size_bytes=resources["total_size"],
        js_errors=tuple(js_errors),
    )


def setup_error_listener(page: Page) -> None:
    """Inject JS error collector into the page."""
    page.on("pageerror", lambda _: None)
    page.evaluate_handle("""() => {
        window.__roastmymvp_errors = [];
        window.addEventListener('error', (e) => {
            window.__roastmymvp_errors.push(e.message);
        });
    }""")
