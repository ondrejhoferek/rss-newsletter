"""Deterministic deduplication of articles.

Runs before agent phases to reduce noise without using AI.
"""

import re
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from personal_rss_newsletter_agent.models import Article

TRACKING_PARAMS = frozenset(
    {
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_content",
        "utm_term",
        "ref",
        "source",
        "fbclid",
        "gclid",
        "mc_cid",
        "mc_eid",
    }
)


def canonicalize_url(url: str) -> str:
    """Normalize a URL for deduplication purposes."""
    parsed = urlparse(url)

    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower().removeprefix("www.")
    path = parsed.path.rstrip("/") or "/"

    params = parse_qs(parsed.query, keep_blank_values=False)
    filtered_params = {k: v for k, v in params.items() if k.lower() not in TRACKING_PARAMS}
    query = urlencode(filtered_params, doseq=True) if filtered_params else ""

    return urlunparse((scheme, netloc, path, "", query, ""))


def normalize_title(title: str) -> str:
    """Normalize a title for comparison."""
    text = title.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def deduplicate(articles: list[Article]) -> tuple[list[Article], int]:
    """Remove duplicate articles by URL and title. Returns (unique, removed_count)."""
    seen_urls: set[str] = set()
    seen_titles: set[str] = set()
    unique: list[Article] = []

    for article in articles:
        canonical_url = canonicalize_url(article.url)
        norm_title = normalize_title(article.title)

        if canonical_url in seen_urls:
            continue
        if norm_title in seen_titles:
            continue

        seen_urls.add(canonical_url)
        seen_titles.add(norm_title)
        unique.append(article)

    removed = len(articles) - len(unique)
    return unique, removed
