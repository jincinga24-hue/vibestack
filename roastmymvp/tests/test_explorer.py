"""Tests for the browser explorer module — TDD: written before implementation."""

import pytest

from roastmymvp.browser.models import BrowserContext, ElementType


class TestExplorer:
    """Tests for the explore_url function."""

    @pytest.mark.asyncio
    async def test_explore_returns_browser_context(self):
        from roastmymvp.browser.explorer import explore_url

        ctx = await explore_url("https://example.com")
        assert isinstance(ctx, BrowserContext)
        assert ctx.url == "https://example.com"

    @pytest.mark.asyncio
    async def test_explore_captures_screenshots(self):
        from roastmymvp.browser.explorer import explore_url

        ctx = await explore_url("https://example.com")
        assert len(ctx.screenshots) >= 1
        assert ctx.screenshots[0].viewport_width > 0

    @pytest.mark.asyncio
    async def test_explore_finds_interactive_elements(self):
        from roastmymvp.browser.explorer import explore_url

        ctx = await explore_url("https://example.com")
        # example.com has at least one link
        assert len(ctx.elements) >= 1

    @pytest.mark.asyncio
    async def test_explore_collects_performance_metrics(self):
        from roastmymvp.browser.explorer import explore_url

        ctx = await explore_url("https://example.com")
        assert ctx.performance is not None
        assert ctx.performance.load_time_ms >= 0

    @pytest.mark.asyncio
    async def test_explore_invalid_url_returns_errors(self):
        from roastmymvp.browser.explorer import explore_url

        ctx = await explore_url("https://thisdomaindoesnotexist12345.com")
        assert len(ctx.errors) >= 1


class TestElementDiscovery:
    """Tests for finding interactive elements on a page."""

    @pytest.mark.asyncio
    async def test_discovers_links(self):
        from roastmymvp.browser.explorer import discover_elements

        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_content(
                '<html><body><a href="/about">About</a></body></html>'
            )
            elements = await discover_elements(page)
            await browser.close()

        link_elements = [e for e in elements if e.element_type == ElementType.LINK]
        assert len(link_elements) >= 1
        assert link_elements[0].text == "About"

    @pytest.mark.asyncio
    async def test_discovers_buttons(self):
        from roastmymvp.browser.explorer import discover_elements

        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_content(
                "<html><body><button>Click me</button></body></html>"
            )
            elements = await discover_elements(page)
            await browser.close()

        button_elements = [e for e in elements if e.element_type == ElementType.BUTTON]
        assert len(button_elements) >= 1
        assert button_elements[0].text == "Click me"

    @pytest.mark.asyncio
    async def test_discovers_inputs(self):
        from roastmymvp.browser.explorer import discover_elements

        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_content(
                '<html><body><input type="text" placeholder="Email"></body></html>'
            )
            elements = await discover_elements(page)
            await browser.close()

        input_elements = [e for e in elements if e.element_type == ElementType.INPUT]
        assert len(input_elements) >= 1
