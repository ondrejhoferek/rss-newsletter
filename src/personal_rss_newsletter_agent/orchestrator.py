"""Pipeline orchestrator.

Coordinates the full newsletter generation workflow:
fetch → dedupe → score → summarize → edit → render.
"""

import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path

from personal_rss_newsletter_agent.agent_prompts import (
    build_editor_prompt,
    build_relevance_prompt,
    build_summary_prompt,
)
from personal_rss_newsletter_agent.dedupe import deduplicate
from personal_rss_newsletter_agent.models import (
    AppConfig,
    EditorResponse,
    NewsletterArtifact,
    NewsletterDraft,
    RelevanceResponse,
    RunReport,
    SummaryResponse,
)
from personal_rss_newsletter_agent.render import write_outputs
from personal_rss_newsletter_agent.rss_ingestion import fetch_all_feeds
from personal_rss_newsletter_agent.sdk_runner import run_agent
from personal_rss_newsletter_agent.storage import (
    filter_unseen,
    load_seen_articles,
    mark_seen,
    save_seen_articles,
)

logger = logging.getLogger(__name__)


async def run_pipeline(
    config: AppConfig,
    days: int,
    max_items: int,
    output_dir: Path,
    state_dir: Path | None = None,
) -> tuple[NewsletterDraft, RunReport]:
    """Execute the full newsletter generation pipeline."""
    today = datetime.now(tz=UTC).strftime("%Y-%m-%d")
    warnings: list[str] = []

    # 1. Fetch RSS feeds
    cutoff = datetime.now(tz=UTC) - timedelta(days=days)
    logger.info("Fetching feeds (cutoff: %s)", cutoff.strftime("%Y-%m-%d %H:%M UTC"))
    articles, fetch_warnings = await fetch_all_feeds(config.feeds, cutoff)
    warnings.extend(fetch_warnings)
    raw_count = len(articles)
    enabled_count = len([f for f in config.feeds if f.enabled])
    logger.info("Fetched %d articles from %d feeds", raw_count, enabled_count)
    if fetch_warnings:
        for w in fetch_warnings:
            logger.warning("Feed warning: %s", w)

    # 2. Basic deduplication
    articles, dupe_count = deduplicate(articles)
    logger.info("After deduplication: %d articles (%d dupes removed)", len(articles), dupe_count)

    # 3. Optional history filtering
    seen_urls: dict[str, str] = {}
    if state_dir:
        state_path = state_dir / "seen_articles.json"
        seen_urls = load_seen_articles(state_path)
        articles = filter_unseen(articles, seen_urls)
        logger.info("After history filter: %d unseen articles", len(articles))

    after_dedupe_count = len(articles)

    if not articles:
        draft = NewsletterDraft(
            title="No New Articles",
            date=today,
            profile_name=config.profile.name,
            items=[],
            skipped_count=0,
            duplicate_count=dupe_count,
            warnings=warnings + ["No articles found after filtering."],
        )
        report = RunReport(
            date=today,
            feeds_attempted=len([f for f in config.feeds if f.enabled]),
            feed_failures=fetch_warnings,
            raw_entries=raw_count,
            after_dedupe=after_dedupe_count,
            scored=0,
            selected=0,
            warnings=warnings,
        )
        return draft, report

    # 4. Relevance scoring (agent phase 1)
    logger.info("Phase 1: relevance scoring (%d articles)", len(articles))
    relevance_result = await run_agent(
        prompt=build_relevance_prompt(articles, config.profile),
        output_schema=RelevanceResponse,
    )
    scored_articles = relevance_result.scored_articles
    logger.info("Phase 1 done: %d articles scored", len(scored_articles))

    # 5. Filter top candidates (take top N*2 for summarization)
    scored_articles.sort(key=lambda x: x.score, reverse=True)
    candidates = scored_articles[: max_items * 2]
    logger.info("Top %d candidates selected for summarization", len(candidates))

    # 6. Summarization (agent phase 2)
    logger.info("Phase 2: summarization (%d candidates)", len(candidates))
    summary_result = await run_agent(
        prompt=build_summary_prompt(candidates, articles, config.profile),
        output_schema=SummaryResponse,
    )
    logger.info("Phase 2 done: %d summaries generated", len(summary_result.summaries))

    # 7. Newsletter editing (agent phase 3)
    logger.info("Phase 3: newsletter editing (max %d items)", max_items)
    editor_result = await run_agent(
        prompt=build_editor_prompt(summary_result.summaries, config.profile, max_items),
        output_schema=EditorResponse,
    )
    draft = editor_result.draft
    draft.duplicate_count = dupe_count
    logger.info("Phase 3 done: newsletter '%s' with %d items", draft.title, len(draft.items))

    # 8. Persist history
    if state_dir:
        state_path = state_dir / "seen_articles.json"
        updated_seen = mark_seen(articles, seen_urls)
        save_seen_articles(state_path, updated_seen)

    # 9. Build report
    report = RunReport(
        date=today,
        feeds_attempted=len([f for f in config.feeds if f.enabled]),
        feed_failures=fetch_warnings,
        raw_entries=raw_count,
        after_dedupe=after_dedupe_count,
        scored=len(scored_articles),
        selected=len(draft.items),
        warnings=warnings,
    )

    # 10. Write outputs
    artifact = NewsletterArtifact(
        newsletter=draft,
        report=report,
        scored_articles=scored_articles,
        summaries=summary_result.summaries,
    )
    output_paths = write_outputs(draft, artifact, report, output_dir)
    report.output_paths = {k: str(v) for k, v in output_paths.items()}
    for name, path in output_paths.items():
        logger.info("Output written: %s → %s", name, path)

    return draft, report
