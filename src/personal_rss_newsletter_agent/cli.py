"""CLI entry point for the newsletter generator."""

import asyncio
from pathlib import Path

import click

from personal_rss_newsletter_agent.config import load_config
from personal_rss_newsletter_agent.logging_setup import configure_logging
from personal_rss_newsletter_agent.orchestrator import run_pipeline
from personal_rss_newsletter_agent.render import render_run_report


@click.group()
def cli() -> None:
    """Personal RSS Newsletter Agent."""


@cli.command()
@click.option(
    "--profile",
    type=click.Path(exists=True, path_type=Path),
    default="config/profile.yml",
    help="Path to profile YAML config.",
)
@click.option(
    "--feeds",
    type=click.Path(exists=True, path_type=Path),
    default="config/feeds.yml",
    help="Path to feeds YAML config.",
)
@click.option("--days", type=int, default=1, help="Look back N days for articles.")
@click.option("--max-items", type=int, default=8, help="Maximum newsletter items.")
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default="output",
    help="Output directory for generated files.",
)
@click.option(
    "--state-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="State directory for history tracking. Pass 'state' to enable.",
)
@click.option(
    "--log",
    "log_file",
    type=click.Path(dir_okay=False, writable=True, path_type=Path),
    default=None,
    help="Write progress log to FILE.",
)
def generate(
    profile: Path,
    feeds: Path,
    days: int,
    max_items: int,
    output_dir: Path,
    state_dir: Path | None,
    log_file: Path | None,
) -> None:
    """Generate a newsletter from RSS feeds."""
    configure_logging(log_file)
    config = load_config(feeds_path=feeds, profile_path=profile)

    click.echo(f"Generating newsletter: {config.profile.name}")
    click.echo(f"  Feeds: {len([f for f in config.feeds if f.enabled])} enabled")
    click.echo(f"  Look back: {days} day(s)")
    click.echo(f"  Max items: {max_items}")
    click.echo()

    draft, report = asyncio.run(
        run_pipeline(
            config=config,
            days=days,
            max_items=max_items,
            output_dir=output_dir,
            state_dir=state_dir,
        )
    )

    click.echo(render_run_report(report))
    click.echo()

    if report.output_paths:
        click.echo("Done! Newsletter generated successfully.")
    else:
        click.echo("Done. No output files written (no articles matched).")


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
