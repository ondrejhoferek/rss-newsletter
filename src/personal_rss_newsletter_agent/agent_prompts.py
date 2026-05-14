"""Prompt builders for each agent phase.

Each function constructs a complete prompt that includes the data to analyze
and instructions for the expected output format.
"""

import json

from personal_rss_newsletter_agent.models import (
    Article,
    ArticleSummary,
    ProfileConfig,
    ScoredArticle,
)


def _profile_section(profile: ProfileConfig) -> str:
    return (
        f"## User Profile\n"
        f"- Name: {profile.name}\n"
        f"- Language: {profile.language}\n"
        f"- Interests: {', '.join(profile.interests)}\n"
        f"- Avoid: {', '.join(profile.avoid_terms) if profile.avoid_terms else 'none'}\n"
        f"- Style: {profile.style}\n"
    )


def _articles_as_json(articles: list[Article]) -> str:
    data = [
        {
            "article_id": a.id,
            "title": a.title,
            "url": a.url,
            "source": a.source,
            "published": a.published.isoformat() if a.published else None,
            "excerpt": a.excerpt,
            "tags": a.tags,
            "category_hints": a.category_hints,
        }
        for a in articles
    ]
    return json.dumps(data, indent=2)


def build_relevance_prompt(articles: list[Article], profile: ProfileConfig) -> str:
    return (
        "# Relevance Scoring Task\n\n"
        "Score each article from 0 to 10 based on relevance to the user profile.\n\n"
        f"{_profile_section(profile)}\n"
        f"## Articles to Score ({len(articles)} items)\n\n"
        f"```json\n{_articles_as_json(articles)}\n```\n\n"
        "## Instructions\n\n"
        "Return a JSON object with a single key `scored_articles` containing an array.\n"
        "Each item must have: article_id, title, url, source, score (0-10 integer), reasoning.\n"
        "The article_id must exactly match the article_id from the input.\n"
    )


def build_summary_prompt(
    scored_articles: list[ScoredArticle],
    articles: list[Article],
    profile: ProfileConfig,
) -> str:
    articles_by_id = {a.id: a for a in articles}
    data = []
    for sa in scored_articles:
        article = articles_by_id.get(sa.article_id)
        excerpt = article.excerpt if article else ""
        data.append(
            {
                "article_id": sa.article_id,
                "title": sa.title,
                "url": sa.url,
                "source": sa.source,
                "score": sa.score,
                "excerpt": excerpt,
            }
        )

    return (
        "# Article Summarization Task\n\n"
        "Summarize each article and explain why it matters to this reader.\n\n"
        f"{_profile_section(profile)}\n"
        f"## Articles to Summarize ({len(data)} items)\n\n"
        f"```json\n{json.dumps(data, indent=2)}\n```\n\n"
        "## Instructions\n\n"
        "Return a JSON object with a single key `summaries` containing an array.\n"
        "Each item must have: article_id, title, source, url, score, summary, why_it_matters.\n"
        "- summary: 1-2 sentences about what's new or notable.\n"
        "- why_it_matters: 1 sentence connecting to the reader's interests.\n"
        "- If the excerpt is too short, note this limitation in the summary.\n"
        "- Preserve the score from the input.\n"
    )


def build_editor_prompt(
    summaries: list[ArticleSummary],
    profile: ProfileConfig,
    max_items: int,
) -> str:
    data = [s.model_dump() for s in summaries]
    return (
        "# Newsletter Editor Task\n\n"
        f"Select the top {max_items} items for the newsletter and assign final rankings.\n\n"
        f"{_profile_section(profile)}\n"
        f"## Available Summaries ({len(data)} items)\n\n"
        f"```json\n{json.dumps(data, indent=2)}\n```\n\n"
        "## Instructions\n\n"
        "Return a JSON object with a single key `draft` containing:\n"
        f"- title: a newsletter title reflecting today's top theme\n"
        f"- date: today's date in YYYY-MM-DD format\n"
        f'- profile_name: "{profile.name}"\n'
        f"- items: array of up to {max_items} items, each with: "
        "rank (1-based), title, source, url, score, summary, why_it_matters\n"
        "- skipped_count: number of articles not selected\n"
        "- duplicate_count: 0 (already handled)\n"
        "- warnings: array of any data quality warnings\n\n"
        "Editorial guidelines:\n"
        "- Prefer source diversity (max 2 items from the same source).\n"
        "- Rank by relevance score and editorial judgment.\n"
        "- Assign sequential ranks starting from 1.\n"
    )
