"""Output rendering for newsletter Markdown and JSON artifacts."""

from datetime import UTC, datetime
from pathlib import Path

from personal_rss_newsletter_agent.models import (
    NewsletterArtifact,
    NewsletterDraft,
    RunReport,
)


def render_markdown(draft: NewsletterDraft) -> str:
    """Render a NewsletterDraft to readable Markdown."""
    lines: list[str] = []
    lines.append(f"# {draft.title}")
    lines.append("")
    lines.append(f"**Date:** {draft.date}  ")
    lines.append(f"**Profile:** {draft.profile_name}")
    lines.append("")
    lines.append("---")
    lines.append("")

    if draft.items:
        lines.append("## Top Stories")
        lines.append("")
        for item in draft.items:
            lines.append(f"### {item.rank}. {item.title}")
            lines.append("")
            lines.append(f"**Source:** {item.source} | **Score:** {item.score}/10  ")
            lines.append(f"**Link:** {item.url}")
            lines.append("")
            lines.append(item.summary)
            lines.append("")
            lines.append(f"*Why it matters:* {item.why_it_matters}")
            lines.append("")
            lines.append("---")
            lines.append("")
    else:
        lines.append("*No articles matched your interests in this period.*")
        lines.append("")

    if draft.warnings:
        lines.append("## Warnings")
        lines.append("")
        for warning in draft.warnings:
            lines.append(f"- {warning}")
        lines.append("")

    if draft.duplicate_count or draft.skipped_count:
        lines.append("## Statistics")
        lines.append("")
        if draft.duplicate_count:
            lines.append(f"- Duplicates removed: {draft.duplicate_count}")
        if draft.skipped_count:
            lines.append(f"- Low-relevance articles skipped: {draft.skipped_count}")
        lines.append("")

    return "\n".join(lines)


def render_json(artifact: NewsletterArtifact) -> str:
    """Render the full newsletter artifact as JSON."""
    return artifact.model_dump_json(indent=2)


def render_run_report(report: RunReport) -> str:
    """Render the run report as a log-friendly string."""
    lines: list[str] = []
    lines.append(f"=== Newsletter Run Report ({report.date}) ===")
    lines.append(f"Feeds attempted: {report.feeds_attempted}")
    if report.feed_failures:
        lines.append(f"Feed failures ({len(report.feed_failures)}):")
        for failure in report.feed_failures:
            lines.append(f"  - {failure}")
    lines.append(f"Raw entries: {report.raw_entries}")
    lines.append(f"After dedupe: {report.after_dedupe}")
    lines.append(f"Scored: {report.scored}")
    lines.append(f"Selected: {report.selected}")
    if report.warnings:
        lines.append(f"Warnings ({len(report.warnings)}):")
        for w in report.warnings:
            lines.append(f"  - {w}")
    if report.output_paths:
        lines.append("Output paths:")
        for key, path in report.output_paths.items():
            lines.append(f"  {key}: {path}")
    return "\n".join(lines)


def write_outputs(
    draft: NewsletterDraft,
    artifact: NewsletterArtifact,
    report: RunReport,
    output_dir: Path,
) -> dict[str, Path]:
    """Write all output files. Returns dict of output name -> path."""
    output_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now(tz=UTC).strftime("%Y-%m-%d")

    md_path = output_dir / f"newsletter_{today}.md"
    json_path = output_dir / f"newsletter_{today}.json"
    log_path = output_dir / f"run_{today}.log"

    md_path.write_text(render_markdown(draft))
    json_path.write_text(render_json(artifact))
    log_path.write_text(render_run_report(report))

    return {"markdown": md_path, "json": json_path, "log": log_path}
