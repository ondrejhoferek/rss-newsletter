"""Tests for deduplication logic."""

from datetime import UTC, datetime

from personal_rss_newsletter_agent.dedupe import (
    canonicalize_url,
    deduplicate,
    normalize_title,
)
from personal_rss_newsletter_agent.models import Article


class TestCanonicalizeUrl:
    def test_strip_tracking_params(self) -> None:
        url = "https://example.com/article?utm_source=twitter&utm_medium=social&id=123"
        canonical = canonicalize_url(url)
        assert "utm_source" not in canonical
        assert "utm_medium" not in canonical
        assert "id=123" in canonical

    def test_strip_trailing_slash(self) -> None:
        assert canonicalize_url("https://example.com/path/") == canonicalize_url(
            "https://example.com/path"
        )

    def test_lowercase_scheme_and_host(self) -> None:
        assert canonicalize_url("HTTPS://Example.COM/Path") == "https://example.com/Path"

    def test_strip_www(self) -> None:
        assert canonicalize_url("https://www.example.com/page") == canonicalize_url(
            "https://example.com/page"
        )

    def test_preserve_path_case(self) -> None:
        canonical = canonicalize_url("https://example.com/CamelCase")
        assert "/CamelCase" in canonical

    def test_empty_path_becomes_slash(self) -> None:
        canonical = canonicalize_url("https://example.com")
        assert canonical.endswith("/")


class TestNormalizeTitle:
    def test_basic_normalization(self) -> None:
        assert normalize_title("  Hello, World!  ") == "hello world"

    def test_collapse_whitespace(self) -> None:
        assert normalize_title("multiple   spaces   here") == "multiple spaces here"

    def test_strip_punctuation(self) -> None:
        assert normalize_title("What's New? (2026)") == "whats new 2026"

    def test_identical_after_normalization(self) -> None:
        assert normalize_title("AI is Great!") == normalize_title("ai is great")


class TestDeduplicate:
    def _make_article(self, id: str, title: str, url: str) -> Article:
        return Article(
            id=id,
            title=title,
            url=url,
            published=datetime(2026, 5, 14, tzinfo=UTC),
            source="Test",
        )

    def test_remove_url_duplicates(self) -> None:
        articles = [
            self._make_article("a", "Article One", "https://example.com/post"),
            self._make_article("b", "Article Two", "https://example.com/post"),
        ]
        unique, removed = deduplicate(articles)
        assert len(unique) == 1
        assert removed == 1

    def test_remove_url_duplicates_with_tracking(self) -> None:
        articles = [
            self._make_article("a", "Article One", "https://example.com/post"),
            self._make_article("b", "Article Two", "https://example.com/post?utm_source=twitter"),
        ]
        unique, removed = deduplicate(articles)
        assert len(unique) == 1
        assert removed == 1

    def test_remove_title_duplicates(self) -> None:
        articles = [
            self._make_article("a", "Big Announcement!", "https://site1.com/post"),
            self._make_article("b", "big announcement", "https://site2.com/post"),
        ]
        unique, removed = deduplicate(articles)
        assert len(unique) == 1
        assert removed == 1

    def test_no_duplicates(self) -> None:
        articles = [
            self._make_article("a", "First Article", "https://example.com/1"),
            self._make_article("b", "Second Article", "https://example.com/2"),
        ]
        unique, removed = deduplicate(articles)
        assert len(unique) == 2
        assert removed == 0

    def test_empty_input(self) -> None:
        unique, removed = deduplicate([])
        assert unique == []
        assert removed == 0
