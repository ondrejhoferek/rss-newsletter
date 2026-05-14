"""RSS/Atom feed fetching and parsing.

Deterministic Python — no agent involvement. Handles broken feeds gracefully.
"""

import asyncio
import hashlib
from datetime import UTC, datetime
from time import mktime

import feedparser
import httpx

from personal_rss_newsletter_agent.models import Article, FeedConfig

FETCH_TIMEOUT = 15.0


def _make_article_id(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:16]


def _parse_published(entry: feedparser.FeedParserDict) -> datetime | None:
    for field in ("published_parsed", "updated_parsed"):
        parsed = getattr(entry, field, None)
        if parsed:
            return datetime.fromtimestamp(mktime(parsed), tz=UTC)
    return None


def _parse_excerpt(entry: feedparser.FeedParserDict) -> str:
    if hasattr(entry, "summary") and entry.summary:
        text: str = str(entry.summary)
        if len(text) > 500:
            text = text[:500] + "..."
        return text
    return ""


def _parse_tags(entry: feedparser.FeedParserDict) -> list[str]:
    if hasattr(entry, "tags") and entry.tags:
        return [t.get("term", "") for t in entry.tags if t.get("term")]
    return []


def parse_feed_content(
    content: bytes, feed_config: FeedConfig, cutoff: datetime | None = None
) -> list[Article]:
    """Parse raw feed bytes into Article models."""
    parsed = feedparser.parse(content)
    articles: list[Article] = []

    for entry in parsed.entries:
        link = getattr(entry, "link", "") or ""
        title = getattr(entry, "title", "") or ""
        if not link or not title:
            continue

        published = _parse_published(entry)
        if cutoff and published and published < cutoff:
            continue

        articles.append(
            Article(
                id=_make_article_id(link),
                title=title.strip(),
                url=link.strip(),
                published=published,
                source=feed_config.name,
                excerpt=_parse_excerpt(entry),
                tags=_parse_tags(entry),
                category_hints=feed_config.category_hints,
            )
        )

    return articles


async def fetch_feed(
    client: httpx.AsyncClient, feed_config: FeedConfig, cutoff: datetime | None = None
) -> tuple[list[Article], str | None]:
    """Fetch and parse a single feed. Returns (articles, warning_or_None)."""
    try:
        response = await client.get(str(feed_config.url), timeout=FETCH_TIMEOUT)
        response.raise_for_status()
    except (httpx.HTTPError, httpx.TimeoutException) as e:
        return [], f"Failed to fetch {feed_config.name}: {e}"

    try:
        articles = parse_feed_content(response.content, feed_config, cutoff)
    except Exception as e:
        return [], f"Failed to parse {feed_config.name}: {e}"

    return articles, None


async def fetch_all_feeds(
    feeds: list[FeedConfig], cutoff: datetime | None = None
) -> tuple[list[Article], list[str]]:
    """Fetch all enabled feeds concurrently. Returns (all_articles, warnings)."""
    enabled_feeds = [f for f in feeds if f.enabled]

    async with httpx.AsyncClient(
        follow_redirects=True,
        headers={"User-Agent": "PersonalRSSNewsletter/0.1"},
    ) as client:
        tasks = [fetch_feed(client, feed, cutoff) for feed in enabled_feeds]
        results = await asyncio.gather(*tasks)

    all_articles: list[Article] = []
    warnings: list[str] = []

    for articles, warning in results:
        all_articles.extend(articles)
        if warning:
            warnings.append(warning)

    return all_articles, warnings
