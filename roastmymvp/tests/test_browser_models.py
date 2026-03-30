"""Tests for browser data models — immutability and construction."""

import pytest

from roastmymvp.browser.models import (
    BrowserContext,
    BrowserError,
    ElementType,
    ErrorSeverity,
    InteractiveElement,
    Interaction,
    PerformanceMetrics,
    Screenshot,
)


class TestScreenshot:
    def test_create(self):
        s = Screenshot(
            path="/tmp/shot.png",
            description="Homepage",
            viewport_width=1920,
            viewport_height=1080,
            timestamp=1000.0,
        )
        assert s.path == "/tmp/shot.png"
        assert s.viewport_width == 1920

    def test_frozen(self):
        s = Screenshot(
            path="/tmp/shot.png",
            description="Homepage",
            viewport_width=1920,
            viewport_height=1080,
            timestamp=1000.0,
        )
        with pytest.raises(AttributeError):
            s.path = "/other"


class TestInteractiveElement:
    def test_create_with_defaults(self):
        el = InteractiveElement(
            selector="button.submit",
            element_type=ElementType.BUTTON,
            text="Submit",
            is_visible=True,
        )
        assert el.href is None
        assert el.element_type == ElementType.BUTTON

    def test_create_link_with_href(self):
        el = InteractiveElement(
            selector="a.nav",
            element_type=ElementType.LINK,
            text="Home",
            is_visible=True,
            href="https://example.com",
        )
        assert el.href == "https://example.com"


class TestInteraction:
    def test_create(self):
        el = InteractiveElement(
            selector="button",
            element_type=ElementType.BUTTON,
            text="Click me",
            is_visible=True,
        )
        interaction = Interaction(
            element=el,
            action="click",
            result="navigated to /dashboard",
            timestamp=1001.0,
            success=True,
        )
        assert interaction.success is True
        assert interaction.element.text == "Click me"


class TestBrowserError:
    def test_create_with_default_source(self):
        err = BrowserError(
            message="404 Not Found",
            severity=ErrorSeverity.WARNING,
            url="https://example.com/missing",
            timestamp=1002.0,
        )
        assert err.source == "unknown"

    def test_create_with_source(self):
        err = BrowserError(
            message="Uncaught TypeError",
            severity=ErrorSeverity.CRITICAL,
            url="https://example.com",
            timestamp=1003.0,
            source="console",
        )
        assert err.source == "console"


class TestPerformanceMetrics:
    def test_create_with_defaults(self):
        perf = PerformanceMetrics(
            load_time_ms=1200.0,
            dom_content_loaded_ms=800.0,
            resource_count=42,
            total_resource_size_bytes=1_500_000,
        )
        assert perf.js_errors == ()

    def test_create_with_errors(self):
        perf = PerformanceMetrics(
            load_time_ms=1200.0,
            dom_content_loaded_ms=800.0,
            resource_count=42,
            total_resource_size_bytes=1_500_000,
            js_errors=("TypeError: x is undefined",),
        )
        assert len(perf.js_errors) == 1


class TestBrowserContext:
    def test_create_minimal(self):
        ctx = BrowserContext(url="https://example.com")
        assert ctx.url == "https://example.com"
        assert ctx.screenshots == ()
        assert ctx.performance is None

    def test_create_full(self):
        shot = Screenshot(
            path="/tmp/s.png",
            description="home",
            viewport_width=1920,
            viewport_height=1080,
            timestamp=1000.0,
        )
        perf = PerformanceMetrics(
            load_time_ms=500.0,
            dom_content_loaded_ms=300.0,
            resource_count=10,
            total_resource_size_bytes=500_000,
        )
        ctx = BrowserContext(
            url="https://example.com",
            screenshots=(shot,),
            performance=perf,
        )
        assert len(ctx.screenshots) == 1
        assert ctx.performance.load_time_ms == 500.0

    def test_frozen(self):
        ctx = BrowserContext(url="https://example.com")
        with pytest.raises(AttributeError):
            ctx.url = "https://other.com"
