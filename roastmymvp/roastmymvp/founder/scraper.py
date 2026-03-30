"""Founder profiler — scrape LinkedIn, GitHub, Twitter to verify claims.

VCs don't just evaluate your product. They evaluate YOU.
This module researches the founder before the roast so VCs can
call out bluffs, verify experience, and judge founder-market fit.
"""

import asyncio
import logging
import re

import httpx

from roastmymvp.founder.models import (
    CredibilityCheck,
    CredibilityFlag,
    FounderProfile,
    GitHubProfile,
    LinkedInProfile,
    TwitterProfile,
)

logger = logging.getLogger(__name__)

_USER_AGENT = "roastmymvp/0.2 (founder-research)"


async def scrape_github(username: str) -> GitHubProfile | None:
    """Scrape public GitHub profile via API (no auth needed)."""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # User profile
            resp = await client.get(
                f"https://api.github.com/users/{username}",
                headers={"User-Agent": _USER_AGENT},
            )
            if resp.status_code != 200:
                logger.warning("GitHub user %s not found: %d", username, resp.status_code)
                return None

            user = resp.json()

            # Get repos for language stats + stars
            repos_resp = await client.get(
                f"https://api.github.com/users/{username}/repos?sort=stars&per_page=30",
                headers={"User-Agent": _USER_AGENT},
            )
            repos = repos_resp.json() if repos_resp.status_code == 200 else []

            # Calculate stats
            total_stars = sum(r.get("stargazers_count", 0) for r in repos)
            languages: dict[str, int] = {}
            for r in repos:
                lang = r.get("language")
                if lang:
                    languages[lang] = languages.get(lang, 0) + 1
            top_langs = tuple(
                k for k, _ in sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
            )
            pinned = tuple(r["name"] for r in repos[:6])

            # Account age
            from datetime import datetime, timezone
            created = datetime.fromisoformat(user["created_at"].replace("Z", "+00:00"))
            age_years = (datetime.now(timezone.utc) - created).days / 365.25

            # Recent activity (events)
            events_resp = await client.get(
                f"https://api.github.com/users/{username}/events?per_page=30",
                headers={"User-Agent": _USER_AGENT},
            )
            events = events_resp.json() if events_resp.status_code == 200 else []
            streak = len(set(
                e["created_at"][:10] for e in events
                if isinstance(e, dict) and "created_at" in e
            ))

            return GitHubProfile(
                username=username,
                public_repos=user.get("public_repos", 0),
                followers=user.get("followers", 0),
                total_stars=total_stars,
                top_languages=top_langs,
                contribution_streak=streak,
                account_age_years=round(age_years, 1),
                pinned_repos=pinned,
                profile_bio=user.get("bio", "") or "",
            )
    except Exception as e:
        logger.warning("GitHub scrape failed for %s: %s", username, e)
        return None


async def scrape_github_from_url(url: str) -> GitHubProfile | None:
    """Extract username from GitHub URL and scrape."""
    match = re.search(r'github\.com/([a-zA-Z0-9_-]+)', url)
    if match:
        return await scrape_github(match.group(1))
    return None


async def research_founder(
    github_url: str = "",
    linkedin_url: str = "",
    twitter_url: str = "",
    pitch_text: str = "",
) -> FounderProfile:
    """Research a founder across all available platforms."""
    github = None
    linkedin = None
    twitter = None

    # Scrape what we can
    tasks = []
    if github_url:
        github = await scrape_github_from_url(github_url)
    elif pitch_text:
        # Try to find GitHub URL in pitch text
        gh_match = re.search(r'github\.com/([a-zA-Z0-9_-]+)', pitch_text)
        if gh_match:
            github = await scrape_github(gh_match.group(1))

    # LinkedIn and Twitter need auth/scraping workarounds
    # For now, extract what we can from URLs
    if linkedin_url:
        linkedin = _parse_linkedin_url(linkedin_url)
    if twitter_url:
        twitter = _parse_twitter_url(twitter_url)

    # Run credibility checks
    checks = _run_credibility_checks(github, linkedin, twitter, pitch_text)

    # Calculate overall credibility
    if checks:
        verified = sum(1 for c in checks if c.flag == CredibilityFlag.VERIFIED)
        bluffs = sum(1 for c in checks if c.flag == CredibilityFlag.BLUFF)
        suspicious = sum(1 for c in checks if c.flag == CredibilityFlag.SUSPICIOUS)
        credibility = max(0.0, (verified - bluffs * 2 - suspicious) / max(len(checks), 1))
    else:
        credibility = 0.5  # No data = neutral
        bluffs = 0

    summary = _build_founder_summary(github, linkedin, twitter, checks)

    return FounderProfile(
        github=github,
        linkedin=linkedin,
        twitter=twitter,
        credibility_checks=tuple(checks),
        overall_credibility=round(credibility, 2),
        bluff_count=bluffs,
        summary=summary,
    )


def _parse_linkedin_url(url: str) -> LinkedInProfile | None:
    """Extract basic info from LinkedIn URL (limited without auth)."""
    match = re.search(r'linkedin\.com/in/([a-zA-Z0-9_-]+)', url)
    if not match:
        return None
    return LinkedInProfile(
        name="",
        headline="",
        current_role="",
        company="",
        years_experience=0,
        education=(),
        skills=(),
        connections_range="unknown",
        summary=f"LinkedIn profile: {url} (full scrape requires auth)",
    )


def _parse_twitter_url(url: str) -> TwitterProfile | None:
    """Extract basic info from Twitter/X URL."""
    match = re.search(r'(?:twitter|x)\.com/([a-zA-Z0-9_]+)', url)
    if not match:
        return None
    return TwitterProfile(
        username=match.group(1),
        bio="",
        followers=0,
        following=0,
        tweet_count=0,
        recent_topics=(),
        account_age_years=0,
    )


def _run_credibility_checks(
    github: GitHubProfile | None,
    linkedin: LinkedInProfile | None,
    twitter: TwitterProfile | None,
    pitch_text: str,
) -> list[CredibilityCheck]:
    """Cross-reference founder claims against scraped evidence."""
    checks: list[CredibilityCheck] = []
    pitch_lower = pitch_text.lower()

    if github:
        # Check: Do they actually code?
        if github.public_repos < 3:
            checks.append(CredibilityCheck(
                claim="Founder is technical / can code",
                evidence=f"GitHub has only {github.public_repos} public repos",
                flag=CredibilityFlag.SUSPICIOUS,
                source="github",
                roast_line=f"You have {github.public_repos} public repos on GitHub. My intern has more. Are you really the technical co-founder?",
            ))
        elif github.public_repos >= 10:
            checks.append(CredibilityCheck(
                claim="Founder is technical / can code",
                evidence=f"GitHub has {github.public_repos} repos, {github.total_stars} stars",
                flag=CredibilityFlag.VERIFIED,
                source="github",
                roast_line="",
            ))

        # Check: Recent activity
        if github.contribution_streak < 3:
            checks.append(CredibilityCheck(
                claim="Founder is actively building",
                evidence=f"Only {github.contribution_streak} days of activity in recent events",
                flag=CredibilityFlag.SUSPICIOUS,
                source="github",
                roast_line=f"Your GitHub shows {github.contribution_streak} days of recent activity. Are you building this or just talking about it?",
            ))
        elif github.contribution_streak >= 10:
            checks.append(CredibilityCheck(
                claim="Founder is actively building",
                evidence=f"{github.contribution_streak} days of recent activity",
                flag=CredibilityFlag.VERIFIED,
                source="github",
                roast_line="",
            ))

        # Check: Do they have followers / community?
        if github.followers < 5:
            checks.append(CredibilityCheck(
                claim="Founder has developer community presence",
                evidence=f"GitHub has {github.followers} followers",
                flag=CredibilityFlag.SUSPICIOUS,
                source="github",
                roast_line=f"{github.followers} GitHub followers. Nobody in the developer community knows you exist. That's not a crime, but don't pitch me 'community-driven' with those numbers.",
            ))

        # Check: Account age vs claimed experience
        if github.account_age_years < 1 and any(
            w in pitch_lower for w in ("years of experience", "senior", "experienced", "veteran")
        ):
            checks.append(CredibilityCheck(
                claim="Experienced developer",
                evidence=f"GitHub account is only {github.account_age_years:.1f} years old",
                flag=CredibilityFlag.BLUFF,
                source="github",
                roast_line=f"You claim years of experience but your GitHub account is {github.account_age_years:.1f} years old. Where were you coding before that — on paper?",
            ))

        # Check: Tech stack match
        if github.top_languages:
            lang_str = ", ".join(github.top_languages[:3])
            checks.append(CredibilityCheck(
                claim=f"Technical background in {lang_str}",
                evidence=f"Top GitHub languages: {lang_str}",
                flag=CredibilityFlag.VERIFIED,
                source="github",
                roast_line="",
            ))

        # Check: Stars = traction signal
        if github.total_stars > 100:
            checks.append(CredibilityCheck(
                claim="Has built something people use",
                evidence=f"{github.total_stars} total stars across repos",
                flag=CredibilityFlag.VERIFIED,
                source="github",
                roast_line="",
            ))
        elif github.total_stars < 5 and any(
            w in pitch_lower for w in ("popular", "traction", "users love", "community")
        ):
            checks.append(CredibilityCheck(
                claim="Product has traction/community",
                evidence=f"Total GitHub stars: {github.total_stars}",
                flag=CredibilityFlag.BLUFF,
                source="github",
                roast_line=f"You mention 'traction' but your repos have {github.total_stars} stars total. That's not traction, that's your mom and your roommate.",
            ))

    # Check: No GitHub at all but claims to be technical
    if not github and any(
        w in pitch_lower for w in ("built", "coded", "developed", "engineer", "technical")
    ):
        checks.append(CredibilityCheck(
            claim="Technical founder",
            evidence="No GitHub profile found or provided",
            flag=CredibilityFlag.UNVERIFIABLE,
            source="github",
            roast_line="You say you built this but I can't find your GitHub. In 2026, a technical founder without a GitHub is like a chef without a kitchen.",
        ))

    return checks


def _build_founder_summary(
    github: GitHubProfile | None,
    linkedin: LinkedInProfile | None,
    twitter: TwitterProfile | None,
    checks: list[CredibilityCheck],
) -> str:
    """Build a text summary of the founder for VC prompts."""
    parts: list[str] = []

    if github:
        parts.append(
            f"GitHub (@{github.username}): {github.public_repos} repos, "
            f"{github.total_stars} stars, {github.followers} followers, "
            f"account age {github.account_age_years}y, "
            f"languages: {', '.join(github.top_languages[:3]) or 'none'}, "
            f"recent activity: {github.contribution_streak} days, "
            f"bio: \"{github.profile_bio}\""
        )

    if linkedin:
        parts.append(f"LinkedIn: {linkedin.summary}")

    if twitter:
        parts.append(f"Twitter/X: @{twitter.username}")

    if checks:
        bluffs = [c for c in checks if c.flag == CredibilityFlag.BLUFF]
        suspicious = [c for c in checks if c.flag == CredibilityFlag.SUSPICIOUS]
        verified = [c for c in checks if c.flag == CredibilityFlag.VERIFIED]

        if bluffs:
            parts.append(f"BLUFFS DETECTED ({len(bluffs)}):")
            for c in bluffs:
                parts.append(f"  - {c.claim}: {c.evidence}")
        if suspicious:
            parts.append(f"SUSPICIOUS ({len(suspicious)}):")
            for c in suspicious:
                parts.append(f"  - {c.claim}: {c.evidence}")
        if verified:
            parts.append(f"VERIFIED ({len(verified)}):")
            for c in verified:
                parts.append(f"  - {c.claim}: {c.evidence}")

    return "\n".join(parts) if parts else "No founder data available."
