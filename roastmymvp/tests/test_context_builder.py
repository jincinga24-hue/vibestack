"""Tests for context builder module."""

import pytest

from roastmymvp.browser.models import (
    BrowserContext,
    BrowserError,
    ElementType,
    ErrorSeverity,
    InteractiveElement,
    PerformanceMetrics,
    Screenshot,
)
from roastmymvp.context.builder import build_product_context


class TestBuildProductContext:
    def test_includes_url(self):
        ctx = BrowserContext(url="https://example.com")
        result = build_product_context(ctx)
        assert "https://example.com" in result

    def test_includes_performance(self):
        ctx = BrowserContext(
            url="https://example.com",
            performance=PerformanceMetrics(
                load_time_ms=1200.0,
                dom_content_loaded_ms=800.0,
                resource_count=42,
                total_resource_size_bytes=1_500_000,
            ),
        )
        result = build_product_context(ctx)
        assert "1200" in result
        assert "42" in result

    def test_includes_elements(self):
        ctx = BrowserContext(
            url="https://example.com",
            elements=(
                InteractiveElement(
                    selector="button.submit",
                    element_type=ElementType.BUTTON,
                    text="Sign Up",
                    is_visible=True,
                ),
                InteractiveElement(
                    selector="a.nav",
                    element_type=ElementType.LINK,
                    text="About",
                    is_visible=True,
                    href="/about",
                ),
            ),
        )
        result = build_product_context(ctx)
        assert "Sign Up" in result
        assert "About" in result

    def test_includes_errors(self):
        ctx = BrowserContext(
            url="https://example.com",
            errors=(
                BrowserError(
                    message="404 Not Found",
                    severity=ErrorSeverity.WARNING,
                    url="https://example.com/missing",
                    timestamp=1000.0,
                ),
            ),
        )
        result = build_product_context(ctx)
        assert "404" in result

    def test_includes_screenshots_count(self):
        ctx = BrowserContext(
            url="https://example.com",
            screenshots=(
                Screenshot(path="/tmp/a.png", description="home", viewport_width=1920, viewport_height=1080, timestamp=1000.0),
                Screenshot(path="/tmp/b.png", description="mobile", viewport_width=375, viewport_height=812, timestamp=1001.0),
            ),
        )
        result = build_product_context(ctx)
        assert "2" in result

    def test_returns_string(self):
        ctx = BrowserContext(url="https://example.com")
        result = build_product_context(ctx)
        assert isinstance(result, str)
        assert len(result) > 0
