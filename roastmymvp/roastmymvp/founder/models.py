"""Data models for founder profiling — VCs research you before roasting."""

from dataclasses import dataclass, field
from enum import Enum


class CredibilityFlag(Enum):
    VERIFIED = "verified"           # Claim checks out
    SUSPICIOUS = "suspicious"       # Claim doesn't match evidence
    UNVERIFIABLE = "unverifiable"   # Can't confirm or deny
    BLUFF = "bluff"                 # Evidence directly contradicts claim


@dataclass(frozen=True)
class GitHubProfile:
    username: str
    public_repos: int
    followers: int
    total_stars: int
    top_languages: tuple[str, ...]
    contribution_streak: int        # Days of recent activity
    account_age_years: float
    pinned_repos: tuple[str, ...]
    profile_bio: str


@dataclass(frozen=True)
class LinkedInProfile:
    name: str
    headline: str
    current_role: str
    company: str
    years_experience: int
    education: tuple[str, ...]
    skills: tuple[str, ...]
    connections_range: str           # "500+", "1000+", etc.
    summary: str


@dataclass(frozen=True)
class TwitterProfile:
    username: str
    bio: str
    followers: int
    following: int
    tweet_count: int
    recent_topics: tuple[str, ...]  # What they talk about
    account_age_years: float


@dataclass(frozen=True)
class CredibilityCheck:
    claim: str                      # What the founder said/implied
    evidence: str                   # What we found
    flag: CredibilityFlag
    source: str                     # "github", "linkedin", "twitter"
    roast_line: str                 # The brutal callout if suspicious/bluff


@dataclass(frozen=True)
class FounderProfile:
    """Everything we know about the founder — scraped, not claimed."""
    github: GitHubProfile | None = None
    linkedin: LinkedInProfile | None = None
    twitter: TwitterProfile | None = None
    credibility_checks: tuple[CredibilityCheck, ...] = field(default_factory=tuple)
    overall_credibility: float = 0.0  # 0.0 - 1.0
    bluff_count: int = 0
    summary: str = ""
