"""Tests for rendering output."""

from pathlib import Path

from personal_rss_newsletter_agent.models import (
    NewsletterArtifact,
    NewsletterDraft,
    RunReport,
)
from personal_rss_newsletter_agent.render import (
    render_markdown,
    render_run_report,
    write_outputs,
)


class TestRenderMarkdown:
    def test_includes_title(self, sample_draft: NewsletterDraft) -> None:
        md = render_markdown(sample_draft)
        assert "# AI & Dev Tools Digest" in md

    def test_includes_date(self, sample_draft: NewsletterDraft) -> None:
        md = render_markdown(sample_draft)
        assert "2026-05-14" in md

    def test_includes_items(self, sample_draft: NewsletterDraft) -> None:
        md = render_markdown(sample_draft)
        assert "Claude Agent SDK Released" in md
        assert "Python 3.14 Beta Available" in md

    def test_includes_scores(self, sample_draft: NewsletterDraft) -> None:
        md = render_markdown(sample_draft)
        assert "9/10" in md
        assert "7/10" in md

    def test_includes_urls(self, sample_draft: NewsletterDraft) -> None:
        md = render_markdown(sample_draft)
        assert "https://anthropic.com/news/agent-sdk" in md

    def test_includes_warnings(self, sample_draft: NewsletterDraft) -> None:
        md = render_markdown(sample_draft)
        assert "Short excerpt" in md

    def test_includes_statistics(self, sample_draft: NewsletterDraft) -> None:
        md = render_markdown(sample_draft)
        assert "Duplicates removed: 2" in md
        assert "skipped: 1" in md

    def test_empty_draft(self) -> None:
        draft = NewsletterDraft(title="Empty", date="2026-05-14", profile_name="Test", items=[])
        md = render_markdown(draft)
        assert "No articles matched" in md


class TestRenderRunReport:
    def test_includes_stats(self, sample_report: RunReport) -> None:
        text = render_run_report(sample_report)
        assert "Feeds attempted: 7" in text
        assert "Raw entries: 42" in text
        assert "Selected: 5" in text

    def test_includes_failures(self, sample_report: RunReport) -> None:
        text = render_run_report(sample_report)
        assert "Broken Feed" in text


class TestWriteOutputs:
    def test_creates_output_files(
        self, tmp_path: Path, sample_draft: NewsletterDraft, sample_report: RunReport
    ) -> None:
        artifact = NewsletterArtifact(newsletter=sample_draft, report=sample_report)
        paths = write_outputs(sample_draft, artifact, sample_report, tmp_path)

        assert "markdown" in paths
        assert "json" in paths
        assert "log" in paths
        assert paths["markdown"].exists()
        assert paths["json"].exists()
        assert paths["log"].exists()

    def test_markdown_content(
        self, tmp_path: Path, sample_draft: NewsletterDraft, sample_report: RunReport
    ) -> None:
        artifact = NewsletterArtifact(newsletter=sample_draft, report=sample_report)
        paths = write_outputs(sample_draft, artifact, sample_report, tmp_path)
        content = paths["markdown"].read_text()
        assert "AI & Dev Tools Digest" in content
