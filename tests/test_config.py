"""Tests for configuration loading."""

from pathlib import Path

import pytest

from personal_rss_newsletter_agent.config import load_config, load_feeds, load_profile


class TestLoadFeeds:
    def test_load_valid_feeds(self, tmp_path: Path) -> None:
        feeds_file = tmp_path / "feeds.yml"
        feeds_file.write_text(
            """
feeds:
  - name: Test Feed
    url: https://example.com/rss
    enabled: true
    category_hints: [ai, tools]
  - name: Another Feed
    url: https://example.com/other
    enabled: false
"""
        )
        feeds = load_feeds(feeds_file)
        assert len(feeds) == 2
        assert feeds[0].name == "Test Feed"
        assert feeds[1].enabled is False

    def test_load_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_feeds(tmp_path / "nonexistent.yml")

    def test_load_invalid_format(self, tmp_path: Path) -> None:
        feeds_file = tmp_path / "feeds.yml"
        feeds_file.write_text("not_feeds: []")
        with pytest.raises(ValueError, match="missing 'feeds' key"):
            load_feeds(feeds_file)


class TestLoadProfile:
    def test_load_valid_profile(self, tmp_path: Path) -> None:
        profile_file = tmp_path / "profile.yml"
        profile_file.write_text(
            """
name: Test Newsletter
language: en
interests:
  - AI
  - Python
avoid_terms:
  - crypto
max_items: 5
style: concise
"""
        )
        profile = load_profile(profile_file)
        assert profile.name == "Test Newsletter"
        assert "AI" in profile.interests
        assert profile.max_items == 5

    def test_load_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_profile(tmp_path / "nonexistent.yml")

    def test_load_empty_file(self, tmp_path: Path) -> None:
        profile_file = tmp_path / "profile.yml"
        profile_file.write_text("")
        with pytest.raises(ValueError, match="empty file"):
            load_profile(profile_file)


class TestLoadConfig:
    def test_load_full_config(self, tmp_path: Path) -> None:
        feeds_file = tmp_path / "feeds.yml"
        feeds_file.write_text(
            """
feeds:
  - name: Feed One
    url: https://example.com/one
    enabled: true
"""
        )
        profile_file = tmp_path / "profile.yml"
        profile_file.write_text(
            """
name: Test
interests: [AI]
"""
        )
        config = load_config(feeds_file, profile_file)
        assert len(config.feeds) == 1
        assert config.profile.name == "Test"
