"""Data models for the browser agent module.

All dataclasses are frozen (immutable) by design.
"""

from dataclasses import dataclass, field
from enum import Enum


class ElementType(Enum):
    BUTTON = "button"
    LINK = "link"
    INPUT = "input"
    SELECT = "select"
    TEXTAREA = "textarea"
    OTHER = "other"


class ErrorSeverity(Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True)
class Screenshot:
    path: str
    description: str
    viewport_width: int
    viewport_height: int
    timestamp: float


@dataclass(frozen=True)
class InteractiveElement:
    selector: str
    element_type: ElementType
    text: str
    is_visible: bool
    href: str | None = None


@dataclass(frozen=True)
class Interaction:
    element: InteractiveElement
    action: str
    result: str
    timestamp: float
    success: bool


@dataclass(frozen=True)
class BrowserError:
    message: str
    severity: ErrorSeverity
    url: str
    timestamp: float
    source: str = "unknown"


@dataclass(frozen=True)
class PerformanceMetrics:
    load_time_ms: float
    dom_content_loaded_ms: float
    resource_count: int
    total_resource_size_bytes: int
    js_errors: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class PageContent:
    title: str
    meta_description: str
    headings: tuple[str, ...]          # All h1-h3 text
    visible_text: str                   # First ~3000 chars of visible text
    above_fold_text: str                # Text visible without scrolling


@dataclass(frozen=True)
class BrowserContext:
    url: str
    screenshots: tuple[Screenshot, ...] = field(default_factory=tuple)
    interactions: tuple[Interaction, ...] = field(default_factory=tuple)
    errors: tuple[BrowserError, ...] = field(default_factory=tuple)
    performance: PerformanceMetrics | None = None
    elements: tuple[InteractiveElement, ...] = field(default_factory=tuple)
    page_content: PageContent | None = None
