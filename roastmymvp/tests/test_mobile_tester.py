"""Tests for mobile testing module."""

import pytest
from playwright.async_api import async_playwright

from roastmymvp.browser.mobile_tester import (
    check_horizontal_overflow,
    check_tap_targets,
    run_mobile_checks,
    MOBILE_VIEWPORT,
)


class TestHorizontalOverflow:
    @pytest.mark.asyncio
    async def test_detects_overflow(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport=MOBILE_VIEWPORT)
            await page.set_content(
                '<html><body><div style="width:800px;height:50px;background:red;">Wide</div></body></html>'
            )
            issues = await check_horizontal_overflow(page)
            await browser.close()

        assert len(issues) >= 1

    @pytest.mark.asyncio
    async def test_no_overflow_when_responsive(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport=MOBILE_VIEWPORT)
            await page.set_content(
                '<html><body><div style="width:100%;height:50px;">OK</div></body></html>'
            )
            issues = await check_horizontal_overflow(page)
            await browser.close()

        assert len(issues) == 0


class TestTapTargets:
    @pytest.mark.asyncio
    async def test_detects_small_tap_target(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport=MOBILE_VIEWPORT)
            await page.set_content(
                '<html><body><button style="width:20px;height:20px;">X</button></body></html>'
            )
            issues = await check_tap_targets(page)
            await browser.close()

        assert len(issues) >= 1
        assert "44x44" in issues[0].description

    @pytest.mark.asyncio
    async def test_passes_large_tap_target(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport=MOBILE_VIEWPORT)
            await page.set_content(
                '<html><body><button style="width:60px;height:60px;">OK</button></body></html>'
            )
            issues = await check_tap_targets(page)
            await browser.close()

        assert len(issues) == 0


class TestRunMobileChecks:
    @pytest.mark.asyncio
    async def test_returns_browser_errors(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_content(
                '<html><body><div style="width:800px;">Wide</div><button style="width:10px;height:10px;">X</button></body></html>'
            )
            errors = await run_mobile_checks(page)
            await browser.close()

        assert len(errors) >= 1
        assert all(e.source == "mobile_tester" for e in errors)
