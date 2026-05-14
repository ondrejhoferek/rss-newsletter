"""Tests for Pydantic models."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from personal_rss_newsletter_agent.models import (
    Article,
    FeedConfig,
    NewsletterDraft,
    NewsletterItem,
    ProfileConfig,
    RelevanceResponse,
    RunReport,
    ScoredArticle,
)


class TestFeedConfig:
    def test_valid_feed(self) -> None:
        feed = FeedConfig(
            name="Test",
            url="https://example.com/feed.xml",
            enabled=True,  # type: ignore[arg-type]
        )
        assert feed.name == "Test"
        assert feed.enabled is True
        assert feed.category_hints == []

    def test_feed_with_hints(self) -> None:
        feed = FeedConfig(
            name="Test",
            url="https://example.com/feed.xml",  # type: ignore[arg-type]
            category_hints=["ai", "tools"],
        )
        assert feed.category_hints == ["ai", "tools"]


class TestProfileConfig:
    def test_valid_profile(self) -> None:
        profile = ProfileConfig(name="My Newsletter", interests=["AI", "Python"])
        assert profile.name == "My Newsletter"
        assert profile.language == "en"
        assert profile.max_items == 8

    def test_profile_missing_interests(self) -> None:
        with pytest.raises(ValidationError):
            ProfileConfig(name="Test")  # type: ignore[call-arg]


class TestArticle:
    def test_article_creation(self) -> None:
        article = Article(
            id="test123",
            title="Test Article",
            url="https://example.com/test",
            source="Test Feed",
        )
        assert article.id == "test123"
        assert article.published is None
        assert article.tags == []

    def test_article_with_all_fields(self) -> None:
        article = Article(
            id="test123",
            title="Test Article",
            url="https://example.com/test",
            published=datetime(2026, 5, 14, tzinfo=UTC),
            source="Test Feed",
            excerpt="A test excerpt.",
            tags=["python"],
            category_hints=["programming"],
        )
        assert article.published is not None
        assert article.excerpt == "A test excerpt."


class TestScoredArticle:
    def test_valid_score(self) -> None:
        sa = ScoredArticle(
            article_id="abc",
            title="Test",
            url="https://example.com",
            source="Feed",
            score=7,
            reasoning="Relevant.",
        )
        assert sa.score == 7

    def test_score_out_of_range(self) -> None:
        with pytest.raises(ValidationError):
            ScoredArticle(
                article_id="abc",
                title="Test",
                url="https://example.com",
                source="Feed",
                score=11,
                reasoning="Too high.",
            )

    def test_negative_score(self) -> None:
        with pytest.raises(ValidationError):
            ScoredArticle(
                article_id="abc",
                title="Test",
                url="https://example.com",
                source="Feed",
                score=-1,
                reasoning="Negative.",
            )


class TestRelevanceResponse:
    def test_valid_response(self, sample_scored_articles: list[ScoredArticle]) -> None:
        resp = RelevanceResponse(scored_articles=sample_scored_articles)
        assert len(resp.scored_articles) == 2


class TestNewsletterDraft:
    def test_draft_serialization(self, sample_draft: NewsletterDraft) -> None:
        data = sample_draft.model_dump()
        restored = NewsletterDraft.model_validate(data)
        assert restored.title == sample_draft.title
        assert len(restored.items) == 2

    def test_empty_draft(self) -> None:
        draft = NewsletterDraft(title="Empty", date="2026-05-14", profile_name="Test", items=[])
        assert draft.skipped_count == 0


class TestRunReport:
    def test_report_creation(self, sample_report: RunReport) -> None:
        assert sample_report.feeds_attempted == 7
        assert sample_report.selected == 5


class TestNewsletterItem:
    def test_item_score_range(self) -> None:
        item = NewsletterItem(
            rank=1,
            title="Test",
            source="Feed",
            url="https://example.com",
            score=10,
            summary="Summary",
            why_it_matters="Matters",
        )
        assert item.score == 10
