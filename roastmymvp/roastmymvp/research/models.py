"""Data models for market research signals."""

from dataclasses import dataclass, field
from enum import Enum


class SignalSource(Enum):
    REDDIT = "reddit"
    HACKER_NEWS = "hacker_news"
    TWITTER = "twitter"
    PRODUCT_HUNT = "product_hunt"


class SignalType(Enum):
    COMPLAINT = "complaint"     # User pain point
    PRAISE = "praise"           # What users love
    FEATURE_REQUEST = "feature_request"  # What's missing
    COMPARISON = "comparison"   # "X is better/worse than Y"
    CHURN_REASON = "churn_reason"  # Why someone left


@dataclass(frozen=True)
class UserSignal:
    text: str
    source: SignalSource
    signal_type: SignalType
    url: str = ""
    score: int = 0              # upvotes/likes
    subreddit: str = ""         # r/SaaS, r/webdev, etc.


@dataclass(frozen=True)
class CompetitorIntel:
    name: str
    complaints: tuple[str, ...] = field(default_factory=tuple)
    praise: tuple[str, ...] = field(default_factory=tuple)
    churn_reasons: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class MarketResearch:
    """Aggregated research from social media for a product/domain."""
    query: str
    signals: tuple[UserSignal, ...] = field(default_factory=tuple)
    competitors: tuple[CompetitorIntel, ...] = field(default_factory=tuple)
    top_complaints: tuple[str, ...] = field(default_factory=tuple)
    top_praise: tuple[str, ...] = field(default_factory=tuple)
    top_feature_requests: tuple[str, ...] = field(default_factory=tuple)
