"""Tests for interaction logging module."""

import pytest
from playwright.async_api import async_playwright

from roastmymvp.browser.interaction_log import click_element, explore_interactions
from roastmymvp.browser.models import ElementType, InteractiveElement


class TestClickElement:
    @pytest.mark.asyncio
    async def test_click_success(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_content(
                '<html><body><button id="btn" onclick="document.title=\'clicked\'">Go</button></body></html>'
            )
            element = InteractiveElement(
                selector="#btn",
                element_type=ElementType.BUTTON,
                text="Go",
                is_visible=True,
            )
            interaction = await click_element(page, element)
            await browser.close()

        assert interaction.success is True
        assert interaction.action == "click"

    @pytest.mark.asyncio
    async def test_click_nonexistent_element(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_content("<html><body></body></html>")
            element = InteractiveElement(
                selector="#nonexistent",
                element_type=ElementType.BUTTON,
                text="Missing",
                is_visible=True,
            )
            interaction = await click_element(page, element)
            await browser.close()

        assert interaction.success is False


class TestExploreInteractions:
    @pytest.mark.asyncio
    async def test_respects_max_clicks(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_content("""<html><body>
                <button>A</button><button>B</button><button>C</button>
                <button>D</button><button>E</button>
            </body></html>""")
            elements = tuple(
                InteractiveElement(
                    selector=f"button >> nth={i}",
                    element_type=ElementType.BUTTON,
                    text=name,
                    is_visible=True,
                )
                for i, name in enumerate(["A", "B", "C", "D", "E"])
            )
            interactions = await explore_interactions(page, elements, max_clicks=2)
            await browser.close()

        assert len(interactions) <= 2

    @pytest.mark.asyncio
    async def test_skips_invisible_elements(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_content(
                '<html><body><button style="display:none">Hidden</button></body></html>'
            )
            elements = (
                InteractiveElement(
                    selector="button",
                    element_type=ElementType.BUTTON,
                    text="Hidden",
                    is_visible=False,
                ),
            )
            interactions = await explore_interactions(page, elements)
            await browser.close()

        assert len(interactions) == 0
