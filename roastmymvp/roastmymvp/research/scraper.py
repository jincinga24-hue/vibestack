"""Social media research scraper — pulls real user feedback from Reddit, HN, Twitter.

Uses public JSON APIs (no auth required for Reddit/HN).
Extracts real pain points, praise, and churn reasons to ground personas in reality.
"""

import asyncio
import json
import logging
import re
from urllib.parse import quote_plus

import httpx

from roastmymvp.research.models import (
    CompetitorIntel,
    MarketResearch,
    SignalSource,
    SignalType,
    UserSignal,
)

logger = logging.getLogger(__name__)

_REDDIT_SEARCH_URL = "https://www.reddit.com/search.json"
_HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search"
_USER_AGENT = "ai-beta-test/0.1 (research bot)"

# Keywords that indicate signal types
_COMPLAINT_KEYWORDS = (
    "hate", "annoying", "frustrating", "broken", "terrible", "worst",
    "can't believe", "deal breaker", "switched from", "left because",
    "gave up", "uninstalled", "cancelled", "refund", "bug", "slow",
    "unusable", "disappointed", "regret",
)
_PRAISE_KEYWORDS = (
    "love", "amazing", "best", "perfect", "finally", "game changer",
    "switched to", "recommend", "impressed", "beautiful", "fast",
    "intuitive", "elegant", "delightful",
)
_FEATURE_REQUEST_KEYWORDS = (
    "wish", "would be nice", "missing", "need", "should have",
    "feature request", "please add", "if only", "hoping for",
)
_CHURN_KEYWORDS = (
    "switched from", "left", "cancelled", "moved to", "dropped",
    "stopped using", "gave up on", "abandoned", "migrated from",
)


def _classify_signal(text: str) -> SignalType:
    """Classify a text snippet by signal type using keyword matching."""
    lower = text.lower()

    churn_score = sum(1 for kw in _CHURN_KEYWORDS if kw in lower)
    if churn_score > 0:
        return SignalType.CHURN_REASON

    complaint_score = sum(1 for kw in _COMPLAINT_KEYWORDS if kw in lower)
    praise_score = sum(1 for kw in _PRAISE_KEYWORDS if kw in lower)
    feature_score = sum(1 for kw in _FEATURE_REQUEST_KEYWORDS if kw in lower)

    scores = {
        SignalType.COMPLAINT: complaint_score,
        SignalType.PRAISE: praise_score,
        SignalType.FEATURE_REQUEST: feature_score,
    }

    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return SignalType.COMPLAINT  # default to complaint for unknown

    return best


async def search_reddit(
    query: str,
    subreddits: tuple[str, ...] = (),
    limit: int = 50,
) -> tuple[UserSignal, ...]:
    """Search Reddit for posts and comments about a product/topic."""
    signals: list[UserSignal] = []

    search_queries = [query]
    for sub in subreddits:
        search_queries.append(f"{query} subreddit:{sub}")

    async with httpx.AsyncClient(timeout=15.0) as client:
        for sq in search_queries:
            try:
                params = {
                    "q": sq,
                    "sort": "relevance",
                    "limit": min(limit, 25),
                    "type": "comment",
                }
                headers = {"User-Agent": _USER_AGENT}
                resp = await client.get(_REDDIT_SEARCH_URL, params=params, headers=headers)

                if resp.status_code != 200:
                    logger.warning("Reddit search returned %d for '%s'", resp.status_code, sq)
                    continue

                data = resp.json()
                children = data.get("data", {}).get("children", [])

                for child in children:
                    comment = child.get("data", {})
                    body = comment.get("body", "")
                    if len(body) < 20 or len(body) > 2000:
                        continue

                    # Clean markdown
                    body = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', body)
                    body = body.replace("&amp;", "&").replace("&gt;", ">").replace("&lt;", "<")

                    signals.append(
                        UserSignal(
                            text=body.strip(),
                            source=SignalSource.REDDIT,
                            signal_type=_classify_signal(body),
                            url=f"https://reddit.com{comment.get('permalink', '')}",
                            score=comment.get("score", 0),
                            subreddit=comment.get("subreddit", ""),
                        )
                    )
            except Exception as e:
                logger.warning("Reddit search failed for '%s': %s", sq, e)

    # Deduplicate and sort by score
    seen: set[str] = set()
    unique: list[UserSignal] = []
    for s in sorted(signals, key=lambda x: x.score, reverse=True):
        key = s.text[:100]
        if key not in seen:
            seen.add(key)
            unique.append(s)

    return tuple(unique[:limit])


async def search_hacker_news(
    query: str,
    limit: int = 30,
) -> tuple[UserSignal, ...]:
    """Search Hacker News comments for product discussions."""
    signals: list[UserSignal] = []

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            params = {
                "query": query,
                "tags": "comment",
                "hitsPerPage": min(limit, 30),
            }
            resp = await client.get(_HN_SEARCH_URL, params=params)

            if resp.status_code != 200:
                logger.warning("HN search returned %d", resp.status_code)
                return ()

            data = resp.json()
            for hit in data.get("hits", []):
                text = hit.get("comment_text", "")
                # Strip HTML tags
                text = re.sub(r'<[^>]+>', ' ', text).strip()
                text = re.sub(r'\s+', ' ', text)

                if len(text) < 20 or len(text) > 2000:
                    continue

                signals.append(
                    UserSignal(
                        text=text,
                        source=SignalSource.HACKER_NEWS,
                        signal_type=_classify_signal(text),
                        url=f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}",
                        score=hit.get("points", 0) or 0,
                    )
                )
        except Exception as e:
            logger.warning("HN search failed: %s", e)

    return tuple(signals[:limit])


async def research_product(
    product_name: str,
    competitors: tuple[str, ...] = (),
    subreddits: tuple[str, ...] = ("SaaS", "webdev", "startups", "ProductHunt", "selfhosted"),
) -> MarketResearch:
    """Run full market research: Reddit + HN search, signal classification, competitor intel."""

    # Run searches in parallel
    reddit_task = search_reddit(product_name, subreddits)
    hn_task = search_hacker_news(product_name)

    competitor_tasks = []
    for comp in competitors:
        competitor_tasks.append(search_reddit(comp, subreddits, limit=20))

    all_results = await asyncio.gather(
        reddit_task, hn_task, *competitor_tasks,
        return_exceptions=True,
    )

    # Collect product signals
    product_signals: list[UserSignal] = []
    for result in all_results[:2]:
        if isinstance(result, tuple):
            product_signals.extend(result)

    # Build competitor intel
    competitor_intel: list[CompetitorIntel] = []
    for i, comp in enumerate(competitors):
        comp_result = all_results[2 + i]
        if isinstance(comp_result, tuple):
            complaints = tuple(
                s.text for s in comp_result if s.signal_type == SignalType.COMPLAINT
            )[:5]
            praise = tuple(
                s.text for s in comp_result if s.signal_type == SignalType.PRAISE
            )[:5]
            churn = tuple(
                s.text for s in comp_result if s.signal_type == SignalType.CHURN_REASON
            )[:5]
            competitor_intel.append(
                CompetitorIntel(
                    name=comp,
                    complaints=complaints,
                    praise=praise,
                    churn_reasons=churn,
                )
            )

    # Aggregate top signals
    all_signals = tuple(product_signals)
    top_complaints = tuple(
        s.text for s in all_signals if s.signal_type == SignalType.COMPLAINT
    )[:10]
    top_praise = tuple(
        s.text for s in all_signals if s.signal_type == SignalType.PRAISE
    )[:10]
    top_features = tuple(
        s.text for s in all_signals if s.signal_type == SignalType.FEATURE_REQUEST
    )[:10]

    return MarketResearch(
        query=product_name,
        signals=all_signals,
        competitors=tuple(competitor_intel),
        top_complaints=top_complaints,
        top_praise=top_praise,
        top_feature_requests=top_features,
    )
