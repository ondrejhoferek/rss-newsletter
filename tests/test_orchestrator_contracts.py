"""Tests for orchestrator contract validation.

These tests verify that the data flows correctly between pipeline phases
using mock agent responses, without making actual SDK calls.
"""

from unittest.mock import AsyncMock, patch

import pytest

from personal_rss_newsletter_agent.models import (
    AppConfig,
    Article,
    ArticleSummary,
    EditorResponse,
    FeedConfig,
    NewsletterDraft,
    NewsletterItem,
    ProfileConfig,
    RelevanceResponse,
    ScoredArticle,
    SummaryResponse,
)


@pytest.fixture
def mock_config(sample_profile: ProfileConfig, sample_feeds: list[FeedConfig]) -> AppConfig:
    return AppConfig(feeds=sample_feeds, profile=sample_profile)


@pytest.fixture
def mock_relevance_response() -> RelevanceResponse:
    return RelevanceResponse(
        scored_articles=[
            ScoredArticle(
                article_id="abc123",
                title="AI Article",
                url="https://example.com/ai",
                source="Test Feed",
                score=9,
                reasoning="Highly relevant to AI interests.",
            ),
            ScoredArticle(
                article_id="def456",
                title="Python Article",
                url="https://example.com/python",
                source="Test Feed",
                score=7,
                reasoning="Related to Python interest.",
            ),
        ]
    )


@pytest.fixture
def mock_summary_response() -> SummaryResponse:
    return SummaryResponse(
        summaries=[
            ArticleSummary(
                article_id="abc123",
                title="AI Article",
                source="Test Feed",
                url="https://example.com/ai",
                score=9,
                summary="New AI framework released.",
                why_it_matters="Enables building agentic applications.",
            ),
            ArticleSummary(
                article_id="def456",
                title="Python Article",
                source="Test Feed",
                url="https://example.com/python",
                score=7,
                summary="Python update available.",
                why_it_matters="Improves daily development workflow.",
            ),
        ]
    )


@pytest.fixture
def mock_editor_response() -> EditorResponse:
    return EditorResponse(
        draft=NewsletterDraft(
            title="Weekly AI & Tools Digest",
            date="2026-05-14",
            profile_name="Test Newsletter",
            items=[
                NewsletterItem(
                    rank=1,
                    title="AI Article",
                    source="Test Feed",
                    url="https://example.com/ai",
                    score=9,
                    summary="New AI framework released.",
                    why_it_matters="Enables building agentic applications.",
                ),
            ],
            skipped_count=1,
            duplicate_count=0,
            warnings=[],
        )
    )


class TestContractValidation:
    def test_relevance_response_validates(self, mock_relevance_response: RelevanceResponse) -> None:
        data = mock_relevance_response.model_dump()
        restored = RelevanceResponse.model_validate(data)
        assert len(restored.scored_articles) == 2
        assert all(0 <= sa.score <= 10 for sa in restored.scored_articles)

    def test_summary_response_validates(self, mock_summary_response: SummaryResponse) -> None:
        data = mock_summary_response.model_dump()
        restored = SummaryResponse.model_validate(data)
        assert len(restored.summaries) == 2
        assert all(s.summary for s in restored.summaries)

    def test_editor_response_validates(self, mock_editor_response: EditorResponse) -> None:
        data = mock_editor_response.model_dump()
        restored = EditorResponse.model_validate(data)
        assert restored.draft.title == "Weekly AI & Tools Digest"
        assert len(restored.draft.items) == 1

    def test_article_ids_flow_through_phases(
        self,
        mock_relevance_response: RelevanceResponse,
        mock_summary_response: SummaryResponse,
    ) -> None:
        scored_ids = {sa.article_id for sa in mock_relevance_response.scored_articles}
        summary_ids = {s.article_id for s in mock_summary_response.summaries}
        assert summary_ids.issubset(scored_ids)


class TestOrchestratorWithMocks:
    @pytest.mark.asyncio
    async def test_pipeline_with_mocked_agents(
        self,
        tmp_path,
        mock_config: AppConfig,
        sample_articles: list[Article],
        mock_relevance_response: RelevanceResponse,
        mock_summary_response: SummaryResponse,
        mock_editor_response: EditorResponse,
    ) -> None:
        from personal_rss_newsletter_agent.orchestrator import run_pipeline

        mock_run_agent = AsyncMock(
            side_effect=[
                mock_relevance_response,
                mock_summary_response,
                mock_editor_response,
            ]
        )

        with (
            patch(
                "personal_rss_newsletter_agent.orchestrator.fetch_all_feeds",
                new=AsyncMock(return_value=(sample_articles, [])),
            ),
            patch(
                "personal_rss_newsletter_agent.orchestrator.run_agent",
                new=mock_run_agent,
            ),
        ):
            output_dir = tmp_path / "output"
            draft, report = await run_pipeline(
                config=mock_config,
                days=1,
                max_items=5,
                output_dir=output_dir,
            )

        assert draft.title == "Weekly AI & Tools Digest"
        assert report.feeds_attempted == 1
        assert report.raw_entries == 3
        assert mock_run_agent.call_count == 3

    @pytest.mark.asyncio
    async def test_pipeline_no_articles(
        self,
        tmp_path,
        mock_config: AppConfig,
    ) -> None:
        from personal_rss_newsletter_agent.orchestrator import run_pipeline

        with patch(
            "personal_rss_newsletter_agent.orchestrator.fetch_all_feeds",
            new=AsyncMock(return_value=([], ["Feed failed: timeout"])),
        ):
            output_dir = tmp_path / "output"
            draft, report = await run_pipeline(
                config=mock_config,
                days=1,
                max_items=5,
                output_dir=output_dir,
            )

        assert draft.items == []
        assert any("No articles found" in w for w in draft.warnings)
        assert report.feed_failures == ["Feed failed: timeout"]
