"""Pydantic models for the newsletter pipeline.

Defines structured contracts used between all pipeline phases:
configuration, ingestion, agent communication, and output rendering.
"""

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field, HttpUrl


class FeedConfig(BaseModel):
    name: str
    url: HttpUrl
    enabled: bool = True
    category_hints: list[str] = Field(default_factory=list)


class ProfileConfig(BaseModel):
    name: str
    language: str = "en"
    interests: list[str]
    avoid_terms: list[str] = Field(default_factory=list)
    max_items: int = 8
    style: str = "concise and practical"


class AppConfig(BaseModel):
    feeds: list[FeedConfig]
    profile: ProfileConfig


# --- Pipeline data models ---


class Article(BaseModel):
    id: str = Field(description="Stable identifier: hash of URL")
    title: str
    url: str
    published: datetime | None = None
    source: str
    excerpt: str = ""
    tags: list[str] = Field(default_factory=list)
    category_hints: list[str] = Field(default_factory=list)


class ScoredArticle(BaseModel):
    article_id: str
    title: str
    url: str
    source: str
    score: int = Field(ge=0, le=10)
    reasoning: str


class ArticleSummary(BaseModel):
    article_id: str
    title: str
    source: str
    url: str
    score: int = Field(ge=0, le=10)
    summary: str
    why_it_matters: str


class NewsletterItem(BaseModel):
    rank: int
    title: str
    source: str
    url: str
    score: int = Field(ge=0, le=10)
    summary: str
    why_it_matters: str


class NewsletterDraft(BaseModel):
    title: str
    date: str
    profile_name: str
    items: list[NewsletterItem]
    skipped_count: int = 0
    duplicate_count: int = 0
    warnings: list[str] = Field(default_factory=list)


class RunReport(BaseModel):
    date: str
    feeds_attempted: int
    feed_failures: list[str] = Field(default_factory=list)
    raw_entries: int
    after_dedupe: int
    scored: int
    selected: int
    warnings: list[str] = Field(default_factory=list)
    output_paths: dict[str, str] = Field(default_factory=dict)


# --- Agent response wrappers (for structured output validation) ---


class RelevanceResponse(BaseModel):
    scored_articles: list[ScoredArticle]


class SummaryResponse(BaseModel):
    summaries: list[ArticleSummary]


class EditorResponse(BaseModel):
    draft: NewsletterDraft


# --- Storage models ---


class SeenArticlesStore(BaseModel):
    seen_urls: dict[str, str] = Field(
        default_factory=dict, description="URL -> ISO timestamp when first seen"
    )


# --- Output artifact ---


class NewsletterArtifact(BaseModel):
    newsletter: NewsletterDraft
    report: RunReport
    scored_articles: list[ScoredArticle] = Field(default_factory=list)
    summaries: list[ArticleSummary] = Field(default_factory=list)
    output_paths: dict[str, Path] = Field(default_factory=dict)
