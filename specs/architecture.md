# Architecture

## Overview

The Personal RSS Newsletter Agent is a CLI application that generates curated newsletters from RSS/Atom feeds. It uses an orchestrator pattern that separates deterministic data processing from AI-powered judgment tasks.

## Pipeline

```
CLI (cli.py)
  → load config (config.py)
  → orchestrator (orchestrator.py)
      → fetch RSS feeds (rss_ingestion.py) ─── deterministic
      → deduplicate (dedupe.py) ─────────────── deterministic
      → filter seen articles (storage.py) ───── deterministic
      → relevance scoring (sdk_runner.py) ───── Claude agent
      → summarization (sdk_runner.py) ────────── Claude agent
      → newsletter editing (sdk_runner.py) ──── Claude agent
      → render outputs (render.py) ──────────── deterministic
```

## Deterministic vs. Agentic Responsibilities

| Responsibility | Implementation | Rationale |
|---|---|---|
| RSS fetching | httpx + feedparser | Network I/O, no judgment needed |
| Feed parsing | feedparser + Pydantic | Structural transformation |
| URL canonicalization | Python string ops | Deterministic normalization |
| Deduplication | Set-based comparison | Exact matching, no ambiguity |
| History tracking | JSON file read/write | Simple persistence |
| Relevance scoring | Claude agent | Requires understanding user interests |
| Summarization | Claude agent | Requires reading comprehension |
| Editorial selection | Claude agent | Requires editorial judgment |
| Output rendering | Python string templates | Deterministic formatting |

## Structured JSON Contracts

All agent phases communicate via validated Pydantic models:

### Models

- **Article**: Raw parsed feed entry (id, title, url, published, source, excerpt, tags)
- **ScoredArticle**: Article scored for relevance (article_id, score 0-10, reasoning)
- **ArticleSummary**: Summarized article (article_id, summary, why_it_matters)
- **NewsletterItem**: Final newsletter entry (rank, title, summary, why_it_matters)
- **NewsletterDraft**: Complete newsletter (title, date, items, warnings)
- **RunReport**: Pipeline execution statistics

### Contract Flow

```
Article[] → RelevanceResponse{scored_articles: ScoredArticle[]}
ScoredArticle[] → SummaryResponse{summaries: ArticleSummary[]}
ArticleSummary[] → EditorResponse{draft: NewsletterDraft}
```

Each response is validated with Pydantic before being passed downstream. Failed validation triggers bounded retries (max 2 attempts).

## Data Flow

1. `fetch_all_feeds()` → `list[Article]` + warnings
2. `deduplicate()` → `list[Article]` (reduced) + removed count
3. `filter_unseen()` → `list[Article]` (history-filtered)
4. `run_agent(relevance_prompt)` → `RelevanceResponse`
5. Sort by score, take top N×2 candidates
6. `run_agent(summary_prompt)` → `SummaryResponse`
7. `run_agent(editor_prompt)` → `EditorResponse`
8. `write_outputs()` → Markdown + JSON + log files

## Observability

Each run produces a `RunReport` containing:
- Feeds attempted and failures
- Article counts at each stage (raw, after dedupe, scored, selected)
- Warnings (broken feeds, short excerpts, validation issues)
- Output file paths

The report is written to `output/run_YYYY-MM-DD.log`.

## Test Strategy

| Layer | Test approach |
|---|---|
| Models | Direct Pydantic validation (valid + invalid inputs) |
| Config | File I/O with tmp_path fixtures |
| Dedupe | Unit tests with crafted duplicates |
| Render | Output string assertions |
| Runtime config | File existence checks |
| Orchestrator | Mocked SDK calls, contract flow verification |
| Integration | Manual end-to-end run (requires auth) |

All tests run offline by default. Network-dependent tests are opt-in.

## MVP Boundaries

**Included:**
- Single-run CLI command
- Local file I/O (YAML config, JSON state, Markdown/JSON output)
- Three agent phases with structured output
- Basic URL + title deduplication
- Optional history tracking

**Future extensions:**
- Weekly digest mode
- HTML/email export
- Semantic deduplication agent
- Topic clustering
- Multiple profiles
- Feed quality scoring
