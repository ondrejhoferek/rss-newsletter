"""Configuration loading and validation."""

from pathlib import Path

import yaml
from dotenv import load_dotenv

from personal_rss_newsletter_agent.models import AppConfig, FeedConfig, ProfileConfig


def load_env() -> None:
    """Load .env.local if it exists, for optional API key overrides."""
    env_local = Path(".env.local")
    if env_local.exists():
        load_dotenv(env_local)


def load_feeds(path: Path) -> list[FeedConfig]:
    """Load and validate feed configuration from YAML."""
    if not path.exists():
        raise FileNotFoundError(f"Feeds config not found: {path}")
    raw = yaml.safe_load(path.read_text())
    if not raw or "feeds" not in raw:
        raise ValueError(f"Invalid feeds config: missing 'feeds' key in {path}")
    return [FeedConfig.model_validate(f) for f in raw["feeds"]]


def load_profile(path: Path) -> ProfileConfig:
    """Load and validate profile configuration from YAML."""
    if not path.exists():
        raise FileNotFoundError(f"Profile config not found: {path}")
    raw = yaml.safe_load(path.read_text())
    if not raw:
        raise ValueError(f"Invalid profile config: empty file {path}")
    return ProfileConfig.model_validate(raw)


def load_config(feeds_path: Path, profile_path: Path) -> AppConfig:
    """Load full application configuration."""
    load_env()
    feeds = load_feeds(feeds_path)
    profile = load_profile(profile_path)
    return AppConfig(feeds=feeds, profile=profile)
