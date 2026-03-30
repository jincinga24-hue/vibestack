"""Structured interaction recording for browser sessions."""

import time

from playwright.async_api import Page, Error as PlaywrightError

from roastmymvp.browser.models import (
    ElementType,
    InteractiveElement,
    Interaction,
)


async def click_element(
    page: Page, element: InteractiveElement
) -> Interaction:
    """Click an interactive element and record the result."""
    timestamp = time.time()
    try:
        await page.click(element.selector, timeout=5000)
        result = f"navigated to {page.url}"
        success = True
    except PlaywrightError as e:
        result = str(e)
        success = False

    return Interaction(
        element=element,
        action="click",
        result=result,
        timestamp=timestamp,
        success=success,
    )


async def explore_interactions(
    page: Page, elements: tuple[InteractiveElement, ...], max_clicks: int = 10
) -> tuple[Interaction, ...]:
    """Click through visible, safe elements and record outcomes."""
    interactions: list[Interaction] = []
    clicked = 0

    for element in elements:
        if clicked >= max_clicks:
            break

        if not element.is_visible:
            continue

        # Skip external links to avoid navigating away
        if element.element_type == ElementType.LINK and element.href:
            if element.href.startswith("http") and page.url not in element.href:
                continue

        interaction = await click_element(page, element)
        interactions.append(interaction)
        clicked += 1

        # Navigate back if we left the page
        if interaction.success and page.url != element.href:
            try:
                await page.go_back(timeout=5000)
            except PlaywrightError:
                pass

    return tuple(interactions)
