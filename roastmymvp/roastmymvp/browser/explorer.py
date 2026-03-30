"""Browser explorer — navigates a URL and collects page data using Playwright."""

import time
import tempfile
import os

from playwright.async_api import async_playwright, Page, Error as PlaywrightError

from roastmymvp.browser.models import (
    BrowserContext,
    BrowserError,
    ElementType,
    ErrorSeverity,
    InteractiveElement,
    PageContent,
    PerformanceMetrics,
    Screenshot,
)

_DESKTOP_VIEWPORT = {"width": 1920, "height": 1080}
_ELEMENT_TYPE_MAP = {
    "a": ElementType.LINK,
    "button": ElementType.BUTTON,
    "input": ElementType.INPUT,
    "select": ElementType.SELECT,
    "textarea": ElementType.TEXTAREA,
}


async def discover_elements(page: Page) -> tuple[InteractiveElement, ...]:
    """Find all interactive elements on the current page."""
    selectors = {
        "a": ElementType.LINK,
        "button": ElementType.BUTTON,
        "input": ElementType.INPUT,
        "select": ElementType.SELECT,
        "textarea": ElementType.TEXTAREA,
    }

    elements: list[InteractiveElement] = []

    for tag, el_type in selectors.items():
        handles = await page.query_selector_all(tag)
        for handle in handles:
            text = (await handle.inner_text()).strip() if el_type != ElementType.INPUT else ""
            if el_type == ElementType.INPUT:
                text = await handle.get_attribute("placeholder") or ""

            is_visible = await handle.is_visible()
            href = await handle.get_attribute("href") if el_type == ElementType.LINK else None

            tag_name = await handle.evaluate("el => el.tagName.toLowerCase()")
            classes = await handle.get_attribute("class") or ""
            selector = f"{tag_name}.{classes.split()[0]}" if classes.strip() else tag_name

            elements.append(
                InteractiveElement(
                    selector=selector,
                    element_type=el_type,
                    text=text,
                    is_visible=is_visible,
                    href=href,
                )
            )

    return tuple(elements)


async def _capture_screenshot(page: Page, description: str, session_dir: str) -> Screenshot:
    """Take a screenshot and return a Screenshot dataclass."""
    filename = f"{description.replace(' ', '_')}_{int(time.time())}.png"
    path = os.path.join(session_dir, filename)
    viewport = page.viewport_size or _DESKTOP_VIEWPORT
    await page.screenshot(path=path)
    return Screenshot(
        path=path,
        description=description,
        viewport_width=viewport["width"],
        viewport_height=viewport["height"],
        timestamp=time.time(),
    )


async def _collect_performance(page: Page) -> PerformanceMetrics:
    """Collect performance timing from the page."""
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

    return PerformanceMetrics(
        load_time_ms=max(0, timing["load_time"]),
        dom_content_loaded_ms=max(0, timing["dom_content_loaded"]),
        resource_count=resources["count"],
        total_resource_size_bytes=resources["total_size"],
    )


async def _extract_page_content(page: Page) -> PageContent:
    """Extract visible text content, headings, title, and meta description."""
    data = await page.evaluate("""() => {
        // Title
        const title = document.title || '';

        // Meta description
        const metaDesc = document.querySelector('meta[name="description"]');
        const meta_description = metaDesc ? metaDesc.getAttribute('content') || '' : '';

        // Headings (h1-h3, truly visible only)
        const headings = [];
        document.querySelectorAll('h1, h2, h3').forEach(h => {
            const text = h.innerText.trim();
            if (!text) return;
            const style = window.getComputedStyle(h);
            if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') return;
            const rect = h.getBoundingClientRect();
            if (rect.width === 0 || rect.height === 0) return;
            headings.push(h.tagName.toLowerCase() + ': ' + text);
        });

        // Helper: check if element is truly visible to a user
        function isReallyVisible(el) {
            if (!el || !el.getBoundingClientRect) return false;
            const rect = el.getBoundingClientRect();
            if (rect.width === 0 || rect.height === 0) return false;
            const style = window.getComputedStyle(el);
            if (style.display === 'none') return false;
            if (style.visibility === 'hidden') return false;
            if (style.opacity === '0') return false;
            // Check parent chain for hidden containers
            let parent = el.parentElement;
            while (parent) {
                const ps = window.getComputedStyle(parent);
                if (ps.display === 'none' || ps.visibility === 'hidden' || ps.opacity === '0') return false;
                parent = parent.parentElement;
            }
            return true;
        }

        // Above-the-fold text (elements in first viewport, truly visible only)
        const viewportHeight = window.innerHeight;
        const aboveFold = [];
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        while (walker.nextNode()) {
            const node = walker.currentNode;
            const el = node.parentElement;
            if (!isReallyVisible(el)) continue;
            const rect = el.getBoundingClientRect();
            if (rect.top < viewportHeight && rect.bottom > 0) {
                const text = node.textContent.trim();
                if (text.length > 2) aboveFold.push(text);
            }
        }

        // All visible text (first 3000 chars, truly visible only)
        const allVisible = [];
        const walker2 = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        let charCount = 0;
        while (walker2.nextNode() && charCount < 3000) {
            const node = walker2.currentNode;
            const el = node.parentElement;
            if (!isReallyVisible(el)) continue;
            const text = node.textContent.trim();
            if (text.length > 2) {
                allVisible.push(text);
                charCount += text.length;
            }
        }

        return {
            title,
            meta_description,
            headings: headings.slice(0, 20),
            above_fold_text: aboveFold.join(' ').slice(0, 2000),
            visible_text: allVisible.join(' ').slice(0, 3000),
        };
    }""")

    return PageContent(
        title=data["title"],
        meta_description=data["meta_description"],
        headings=tuple(data["headings"]),
        visible_text=data["visible_text"],
        above_fold_text=data["above_fold_text"],
    )


async def explore_url(url: str) -> BrowserContext:
    """Navigate to a URL, explore the page, and return collected data."""
    session_dir = tempfile.mkdtemp(prefix="ai-beta-test-")
    errors: list[BrowserError] = []
    screenshots: list[Screenshot] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport=_DESKTOP_VIEWPORT)

        # Collect JS console errors
        page.on("pageerror", lambda err: errors.append(
            BrowserError(
                message=str(err),
                severity=ErrorSeverity.CRITICAL,
                url=url,
                timestamp=time.time(),
                source="console",
            )
        ))

        try:
            response = await page.goto(url, wait_until="load", timeout=30000)

            if response and response.status >= 400:
                errors.append(
                    BrowserError(
                        message=f"HTTP {response.status}",
                        severity=ErrorSeverity.WARNING,
                        url=url,
                        timestamp=time.time(),
                        source="network",
                    )
                )

            screenshot = await _capture_screenshot(page, "initial_load", session_dir)
            screenshots.append(screenshot)

            elements = await discover_elements(page)
            performance = await _collect_performance(page)
            page_content = await _extract_page_content(page)

        except PlaywrightError as e:
            errors.append(
                BrowserError(
                    message=str(e),
                    severity=ErrorSeverity.CRITICAL,
                    url=url,
                    timestamp=time.time(),
                    source="playwright",
                )
            )
            elements = ()
            performance = None
            page_content = None

        await browser.close()

    return BrowserContext(
        url=url,
        screenshots=tuple(screenshots),
        interactions=(),
        errors=tuple(errors),
        performance=performance,
        elements=elements,
        page_content=page_content,
    )
