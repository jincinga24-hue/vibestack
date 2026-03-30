"""Screenshot capture for desktop and mobile viewports."""

import os
import time

from playwright.async_api import Page

from roastmymvp.browser.models import Screenshot

VIEWPORTS = {
    "desktop": {"width": 1920, "height": 1080},
    "tablet": {"width": 768, "height": 1024},
    "mobile": {"width": 375, "height": 812},
}


async def capture_all_viewports(
    page: Page, session_dir: str, label: str = "page"
) -> tuple[Screenshot, ...]:
    """Capture screenshots at desktop, tablet, and mobile viewports."""
    screenshots: list[Screenshot] = []
    original_viewport = page.viewport_size

    for name, size in VIEWPORTS.items():
        await page.set_viewport_size(size)
        await page.wait_for_timeout(300)

        filename = f"{label}_{name}_{int(time.time())}.png"
        path = os.path.join(session_dir, filename)
        await page.screenshot(path=path, full_page=True)

        screenshots.append(
            Screenshot(
                path=path,
                description=f"{label} ({name})",
                viewport_width=size["width"],
                viewport_height=size["height"],
                timestamp=time.time(),
            )
        )

    if original_viewport:
        await page.set_viewport_size(original_viewport)

    return tuple(screenshots)
