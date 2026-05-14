"""Persistent state for tracking previously seen articles."""

import json
from datetime import UTC, datetime
from pathlib import Path

from personal_rss_newsletter_agent.models import Article


def load_seen_articles(state_path: Path) -> dict[str, str]:
    """Load previously seen article URLs from state file."""
    if not state_path.exists():
        return {}
    data: dict[str, dict[str, str]] = json.loads(state_path.read_text())
    return data.get("seen_urls", {})


def save_seen_articles(state_path: Path, seen_urls: dict[str, str]) -> None:
    """Persist seen article URLs to state file."""
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps({"seen_urls": seen_urls}, indent=2))


def filter_unseen(articles: list[Article], seen_urls: dict[str, str]) -> list[Article]:
    """Return only articles not previously seen."""
    return [a for a in articles if a.url not in seen_urls]


def mark_seen(articles: list[Article], seen_urls: dict[str, str]) -> dict[str, str]:
    """Add articles to the seen set. Returns updated dict."""
    now = datetime.now(tz=UTC).isoformat()
    updated = dict(seen_urls)
    for article in articles:
        if article.url not in updated:
            updated[article.url] = now
    return updated
