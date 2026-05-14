"""Shared test fixtures."""

from datetime import UTC, datetime
from pathlib import Path

import pytest

from personal_rss_newsletter_agent.models import (
    Article,
    ArticleSummary,
    FeedConfig,
    NewsletterDraft,
    NewsletterItem,
    ProfileConfig,
    RunReport,
    ScoredArticle,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_profile() -> ProfileConfig:
    return ProfileConfig(
        name="Test Newsletter",
        language="en",
        interests=["AI agents", "Python", "developer tools"],
        avoid_terms=["cryptocurrency", "NFT"],
        max_items=5,
        style="concise",
    )


@pytest.fixture
def sample_feeds() -> list[FeedConfig]:
    return [
        FeedConfig(
            name="Test Feed",
            url="https://example.com/feed.xml",  # type: ignore[arg-type]
            enabled=True,
            category_hints=["tech", "ai"],
        ),
        FeedConfig(
            name="Disabled Feed",
            url="https://example.com/disabled.xml",  # type: ignore[arg-type]
            enabled=False,
            category_hints=["other"],
        ),
    ]


@pytest.fixture
def sample_articles() -> list[Article]:
    return [
        Article(
            id="abc123",
            title="Claude Agent SDK Released",
            url="https://anthropic.com/news/agent-sdk",
            published=datetime(2026, 5, 13, 10, 0, tzinfo=UTC),
            source="Anthropic News",
            excerpt="Anthropic releases the Claude Agent SDK for building AI agents.",
            tags=["ai", "sdk"],
            category_hints=["ai", "agents"],
        ),
        Article(
            id="def456",
            title="Python 3.14 Beta Available",
            url="https://blog.python.org/python-314-beta",
            published=datetime(2026, 5, 12, 8, 0, tzinfo=UTC),
            source="Python Insider",
            excerpt="The first beta of Python 3.14 is now available for testing.",
            tags=["python"],
            category_hints=["python", "programming"],
        ),
        Article(
            id="ghi789",
            title="NFT Market Rebounds",
            url="https://example.com/nft-rebound",
            published=datetime(2026, 5, 13, 12, 0, tzinfo=UTC),
            source="Crypto News",
            excerpt="NFT trading volume increased by 50% this week.",
            tags=["nft", "crypto"],
            category_hints=["cryptocurrency"],
        ),
    ]


@pytest.fixture
def sample_scored_articles() -> list[ScoredArticle]:
    return [
        ScoredArticle(
            article_id="abc123",
            title="Claude Agent SDK Released",
            url="https://anthropic.com/news/agent-sdk",
            source="Anthropic News",
            score=9,
            reasoning="Directly relevant to AI agents interest.",
        ),
        ScoredArticle(
            article_id="def456",
            title="Python 3.14 Beta Available",
            url="https://blog.python.org/python-314-beta",
            source="Python Insider",
            score=7,
            reasoning="Relevant to Python interest.",
        ),
    ]


@pytest.fixture
def sample_summaries() -> list[ArticleSummary]:
    return [
        ArticleSummary(
            article_id="abc123",
            title="Claude Agent SDK Released",
            source="Anthropic News",
            url="https://anthropic.com/news/agent-sdk",
            score=9,
            summary="Anthropic released a Python SDK for building AI agents with Claude.",
            why_it_matters="Directly enables building agentic applications with Claude.",
        ),
        ArticleSummary(
            article_id="def456",
            title="Python 3.14 Beta Available",
            source="Python Insider",
            url="https://blog.python.org/python-314-beta",
            score=7,
            summary="Python 3.14 beta introduces new pattern matching features.",
            why_it_matters="New Python features relevant to daily development workflow.",
        ),
    ]


@pytest.fixture
def sample_draft() -> NewsletterDraft:
    return NewsletterDraft(
        title="AI & Dev Tools Digest",
        date="2026-05-14",
        profile_name="Test Newsletter",
        items=[
            NewsletterItem(
                rank=1,
                title="Claude Agent SDK Released",
                source="Anthropic News",
                url="https://anthropic.com/news/agent-sdk",
                score=9,
                summary="Anthropic released a Python SDK for building AI agents.",
                why_it_matters="Enables agentic applications with Claude.",
            ),
            NewsletterItem(
                rank=2,
                title="Python 3.14 Beta Available",
                source="Python Insider",
                url="https://blog.python.org/python-314-beta",
                score=7,
                summary="Python 3.14 beta introduces new features.",
                why_it_matters="New Python features for daily development.",
            ),
        ],
        skipped_count=1,
        duplicate_count=2,
        warnings=["Short excerpt for one article."],
    )


@pytest.fixture
def sample_report() -> RunReport:
    return RunReport(
        date="2026-05-14",
        feeds_attempted=7,
        feed_failures=["Failed to fetch Broken Feed: timeout"],
        raw_entries=42,
        after_dedupe=38,
        scored=38,
        selected=5,
        warnings=["Short excerpt for one article."],
    )
