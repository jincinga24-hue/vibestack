"""Tests for screenshotter module."""

import os
import tempfile

import pytest
from playwright.async_api import async_playwright

from roastmymvp.browser.screenshotter import VIEWPORTS, capture_all_viewports


class TestCaptureAllViewports:
    @pytest.mark.asyncio
    async def test_captures_three_viewports(self):
        session_dir = tempfile.mkdtemp(prefix="ai-beta-test-")
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_content("<html><body><h1>Hello</h1></body></html>")
            screenshots = await capture_all_viewports(page, session_dir)
            await browser.close()

        assert len(screenshots) == 3

    @pytest.mark.asyncio
    async def test_files_exist_on_disk(self):
        session_dir = tempfile.mkdtemp(prefix="ai-beta-test-")
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_content("<html><body><h1>Hello</h1></body></html>")
            screenshots = await capture_all_viewports(page, session_dir)
            await browser.close()

        for s in screenshots:
            assert os.path.exists(s.path)
            assert os.path.getsize(s.path) > 0

    @pytest.mark.asyncio
    async def test_viewport_dimensions_match(self):
        session_dir = tempfile.mkdtemp(prefix="ai-beta-test-")
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_content("<html><body><h1>Hello</h1></body></html>")
            screenshots = await capture_all_viewports(page, session_dir)
            await browser.close()

        widths = {s.viewport_width for s in screenshots}
        expected_widths = {v["width"] for v in VIEWPORTS.values()}
        assert widths == expected_widths

    @pytest.mark.asyncio
    async def test_restores_original_viewport(self):
        session_dir = tempfile.mkdtemp(prefix="ai-beta-test-")
        original = {"width": 1024, "height": 768}
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport=original)
            await page.set_content("<html><body><h1>Hello</h1></body></html>")
            await capture_all_viewports(page, session_dir)
            restored = page.viewport_size
            await browser.close()

        assert restored == original
