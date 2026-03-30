"""Tests for market research module."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from roastmymvp.research.models import (
    CompetitorIntel,
    MarketResearch,
    SignalSource,
    SignalType,
    UserSignal,
)
from roastmymvp.research.scraper import _classify_signal, search_reddit, search_hacker_news, research_product
from roastmymvp.research.persona_enricher import enrich_personas, _truncate
from roastmymvp.personas.models import Archetype, EvaluationStyle, PersonaProfile


class TestSignalClassification:
    def test_classifies_complaint(self):
        assert _classify_signal("This tool is broken and unusable") == SignalType.COMPLAINT

    def test_classifies_praise(self):
        assert _classify_signal("I love this product, it's amazing") == SignalType.PRAISE

    def test_classifies_feature_request(self):
        assert _classify_signal("I wish they would add dark mode") == SignalType.FEATURE_REQUEST

    def test_classifies_churn(self):
        assert _classify_signal("I switched from Notion because it was too slow") == SignalType.CHURN_REASON

    def test_churn_takes_priority(self):
        # Churn keywords should win over complaint keywords
        assert _classify_signal("I hate it so I switched from it to something else") == SignalType.CHURN_REASON

    def test_defaults_to_complaint(self):
        assert _classify_signal("Some neutral text about nothing") == SignalType.COMPLAINT


class TestModels:
    def test_user_signal_frozen(self):
        s = UserSignal(text="test", source=SignalSource.REDDIT, signal_type=SignalType.COMPLAINT)
        with pytest.raises(AttributeError):
            s.text = "changed"

    def test_market_research_defaults(self):
        r = MarketResearch(query="test")
        assert r.signals == ()
        assert r.competitors == ()

    def test_competitor_intel(self):
        c = CompetitorIntel(
            name="Notion",
            complaints=("slow", "expensive"),
            churn_reasons=("switched to Obsidian",),
        )
        assert len(c.complaints) == 2


class TestRedditSearch:
    @pytest.mark.asyncio
    async def test_returns_signals_from_mock(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "children": [
                    {
                        "data": {
                            "body": "I really hate how slow this tool is, it's frustrating to use every day",
                            "permalink": "/r/test/comments/abc",
                            "score": 42,
                            "subreddit": "SaaS",
                        }
                    },
                    {
                        "data": {
                            "body": "This is amazing, I love it and recommend it to everyone",
                            "permalink": "/r/test/comments/def",
                            "score": 15,
                            "subreddit": "webdev",
                        }
                    },
                ]
            }
        }

        with patch("roastmymvp.research.scraper.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            signals = await search_reddit("test product")

        assert len(signals) >= 1
        assert all(isinstance(s, UserSignal) for s in signals)
        assert signals[0].source == SignalSource.REDDIT

    @pytest.mark.asyncio
    async def test_handles_api_error(self):
        with patch("roastmymvp.research.scraper.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=Exception("Connection error"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            signals = await search_reddit("test")

        assert signals == ()


class TestHNSearch:
    @pytest.mark.asyncio
    async def test_returns_signals_from_mock(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "hits": [
                {
                    "comment_text": "I switched from this tool because it was too expensive and the support was terrible",
                    "objectID": "12345",
                    "points": 10,
                },
            ]
        }

        with patch("roastmymvp.research.scraper.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            signals = await search_hacker_news("test")

        assert len(signals) >= 1
        assert signals[0].source == SignalSource.HACKER_NEWS


class TestPersonaEnricher:
    def _make_research(self) -> MarketResearch:
        return MarketResearch(
            query="test product",
            signals=(
                UserSignal(text="The login flow takes forever", source=SignalSource.REDDIT, signal_type=SignalType.COMPLAINT, score=50),
                UserSignal(text="No dark mode is a deal breaker", source=SignalSource.REDDIT, signal_type=SignalType.COMPLAINT, score=30),
                UserSignal(text="The API is beautifully designed", source=SignalSource.REDDIT, signal_type=SignalType.PRAISE, score=25),
                UserSignal(text="I wish they had webhook support", source=SignalSource.REDDIT, signal_type=SignalType.FEATURE_REQUEST, score=20),
            ),
            competitors=(
                CompetitorIntel(
                    name="Notion",
                    complaints=("Notion is so slow on large docs",),
                    praise=("Great for collaboration",),
                    churn_reasons=("Switched to Obsidian because Notion was too bloated",),
                ),
            ),
            top_complaints=("The login flow takes forever", "No dark mode is a deal breaker"),
            top_praise=("The API is beautifully designed",),
            top_feature_requests=("I wish they had webhook support",),
        )

    def _make_persona(self, archetype: Archetype, alt_name: str | None = None) -> PersonaProfile:
        return PersonaProfile(
            name="Test", age=30, background="Test background",
            tech_savvy=0.8, patience_seconds=30, language="en",
            has_alternative=alt_name is not None, alternative_name=alt_name,
            archetype=archetype, evaluation_style=EvaluationStyle.TASK_DRIVEN,
            goals=("Test goal",), frustrations=("Existing frustration",),
            context_of_use="Testing", emotional_state="neutral",
        )

    def test_skeptics_get_real_complaints(self):
        research = self._make_research()
        persona = self._make_persona(Archetype.SKEPTIC)
        enriched = enrich_personas((persona,), research)

        assert len(enriched[0].frustrations) > len(persona.frustrations)
        assert any("[Real user said]" in f for f in enriched[0].frustrations)

    def test_churners_get_real_complaints(self):
        research = self._make_research()
        persona = self._make_persona(Archetype.CHURNER)
        enriched = enrich_personas((persona,), research)

        assert any("[Real user said]" in f for f in enriched[0].frustrations)

    def test_power_users_get_feature_requests(self):
        research = self._make_research()
        persona = self._make_persona(Archetype.POWER_USER)
        enriched = enrich_personas((persona,), research)

        assert any("Check if:" in g for g in enriched[0].goals)

    def test_competitor_context_injected(self):
        research = self._make_research()
        persona = self._make_persona(Archetype.SKEPTIC, alt_name="Notion")
        enriched = enrich_personas((persona,), research)

        assert "Notion" in enriched[0].context_of_use

    def test_advocates_get_real_praise(self):
        research = self._make_research()
        persona = self._make_persona(Archetype.ADVOCATE)
        enriched = enrich_personas((persona,), research)

        assert "Real users praised" in enriched[0].background

    def test_enrichment_preserves_immutability(self):
        research = self._make_research()
        persona = self._make_persona(Archetype.SKEPTIC)
        enriched = enrich_personas((persona,), research)

        with pytest.raises(AttributeError):
            enriched[0].name = "Changed"

    def test_enrichment_preserves_original_data(self):
        research = self._make_research()
        persona = self._make_persona(Archetype.SKEPTIC)
        enriched = enrich_personas((persona,), research)

        # Original frustrations should still be there
        assert "Existing frustration" in enriched[0].frustrations


class TestTruncate:
    def test_short_text_unchanged(self):
        assert _truncate("short") == "short"

    def test_long_text_truncated(self):
        result = _truncate("a " * 100, max_len=20)
        assert len(result) <= 25  # some room for "..."
        assert result.endswith("...")
