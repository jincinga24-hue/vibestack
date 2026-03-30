"""Context builder — unifies browser data into a text summary for LLM consumption."""

from roastmymvp.browser.models import BrowserContext


def build_product_context(browser_ctx: BrowserContext) -> str:
    """Convert BrowserContext into a structured text summary for persona prompts."""
    sections: list[str] = []

    sections.append(f"## Product URL\n{browser_ctx.url}")

    # Page content — what the user actually sees
    if browser_ctx.page_content:
        pc = browser_ctx.page_content
        content_parts = []
        if pc.title:
            content_parts.append(f"**Page Title:** {pc.title}")
        if pc.meta_description:
            content_parts.append(f"**Meta Description:** {pc.meta_description}")
        if pc.headings:
            content_parts.append(
                "**Headings:**\n" +
                "\n".join(f"- {h}" for h in pc.headings)
            )
        if pc.above_fold_text:
            content_parts.append(
                f"**Text visible without scrolling (above the fold):**\n{pc.above_fold_text}"
            )
        if pc.visible_text:
            content_parts.append(
                f"**Full visible text on page:**\n{pc.visible_text}"
            )
        sections.append("## Page Content (what users see)\n" + "\n\n".join(content_parts))

    # Performance
    if browser_ctx.performance:
        p = browser_ctx.performance
        sections.append(
            f"## Performance\n"
            f"- Load time: {p.load_time_ms:.0f}ms\n"
            f"- DOM ready: {p.dom_content_loaded_ms:.0f}ms\n"
            f"- Resources: {p.resource_count} files ({p.total_resource_size_bytes:,} bytes)\n"
            f"- JS errors: {len(p.js_errors)}"
        )
        if p.js_errors:
            sections.append(
                "### JS Errors\n" +
                "\n".join(f"- {e}" for e in p.js_errors)
            )

    # Interactive elements
    if browser_ctx.elements:
        element_lines = []
        for el in browser_ctx.elements:
            href_part = f" → {el.href}" if el.href else ""
            vis = "visible" if el.is_visible else "hidden"
            element_lines.append(
                f"- [{el.element_type.value}] \"{el.text}\"{href_part} ({vis})"
            )
        sections.append(
            f"## Interactive Elements ({len(browser_ctx.elements)} found)\n" +
            "\n".join(element_lines)
        )

    # Errors
    if browser_ctx.errors:
        error_lines = [
            f"- [{e.severity.value}] {e.message} (source: {e.source})"
            for e in browser_ctx.errors
        ]
        sections.append(
            f"## Errors ({len(browser_ctx.errors)} found)\n" +
            "\n".join(error_lines)
        )

    # Screenshots
    if browser_ctx.screenshots:
        shot_lines = [
            f"- {s.description} ({s.viewport_width}x{s.viewport_height})"
            for s in browser_ctx.screenshots
        ]
        sections.append(
            f"## Screenshots ({len(browser_ctx.screenshots)} captured)\n" +
            "\n".join(shot_lines)
        )

    return "\n\n".join(sections)
