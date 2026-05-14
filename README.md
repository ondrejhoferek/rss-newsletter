# Personal RSS Newsletter Agent

A CLI tool that generates a curated personal newsletter from RSS/Atom feeds. Uses deterministic Python for data processing and the Claude Agent SDK for relevance scoring, summarization, and editorial selection.

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) for dependency management
- Claude Code CLI installed and authenticated (for local development), or an `ANTHROPIC_API_KEY`

## Installation

```bash
git clone <this-repo>
cd rss-newsletter
uv sync
```

## Authentication

The application supports multiple authentication modes:

1. **Claude Code login (recommended for local dev):** If you have `claude` CLI authenticated, no additional setup is needed.
2. **API key:** Set `ANTHROPIC_API_KEY` in `.env.local` or your shell environment.

```bash
# Optional: create .env.local for API key auth
cp .env.example .env.local
# Edit .env.local and set ANTHROPIC_API_KEY=sk-ant-...
```

## Configuration

### Feeds (`config/feeds.yml`)

Define RSS/Atom feeds to monitor:

```yaml
feeds:
  - name: Hacker News
    url: https://news.ycombinator.com/rss
    enabled: true
    category_hints: [technology, startups]
```

### Profile (`config/profile.yml`)

Define your interests and preferences:

```yaml
name: "AI & Developer Tools Weekly"
language: en
interests:
  - AI agents
  - Python
  - developer tools
avoid_terms:
  - cryptocurrency
max_items: 8
style: "concise and practical"
```

## Usage

```bash
# Generate newsletter (default: last 1 day, max 8 items)
uv run personal-newsletter generate

# Custom options
uv run personal-newsletter generate --days 3 --max-items 5

# With history tracking (avoids repeating articles across runs)
uv run personal-newsletter generate --state-dir state

# Custom config paths
uv run personal-newsletter generate \
  --profile config/profile.yml \
  --feeds config/feeds.yml \
  --output-dir output
```

## Generated Outputs

Each run produces three files in `output/`:

| File | Description |
|------|-------------|
| `newsletter_YYYY-MM-DD.md` | Readable Markdown newsletter |
| `newsletter_YYYY-MM-DD.json` | Structured JSON artifact with all intermediate data |
| `run_YYYY-MM-DD.log` | Run report with statistics |

## Architecture

The pipeline runs in this order:

1. **Load config** — Parse feeds.yml and profile.yml
2. **Fetch RSS** — Concurrent HTTP fetching with httpx + feedparser
3. **Deduplicate** — URL canonicalization + title normalization
4. **Score** (Claude agent) — Relevance scoring against user profile
5. **Summarize** (Claude agent) — Concise summaries with "why it matters"
6. **Edit** (Claude agent) — Final selection, ranking, and newsletter assembly
7. **Render** — Markdown + JSON output generation

Deterministic steps (1-3) use plain Python. Agent steps (4-6) use the Claude Agent SDK with structured output validation.

For deeper technical details, see [specs/architecture.md](specs/architecture.md) and [specs/runtime-agent-config.md](specs/runtime-agent-config.md).

## Testing & Linting

```bash
# Run tests
uv run pytest

# Lint
uv run ruff check .

# Format check
uv run ruff format --check .

# Type check
uv run mypy src
```

## Troubleshooting

### "No ResultMessage received from agent"
- Verify Claude Code authentication: run `claude --version` in your terminal.
- Or set `ANTHROPIC_API_KEY` in `.env.local`.

### Feed failures
- The app handles broken feeds gracefully — it skips them and includes warnings.
- Check `output/run_YYYY-MM-DD.log` for details on which feeds failed.

### Structured output validation failures
- The SDK retries up to 2 times on validation failure.
- If persistent, check that the model supports structured outputs (claude-sonnet-4-6 recommended).
- Override the model with `NEWSLETTER_MODEL` environment variable.

### No articles found
- Increase `--days` to look further back.
- Check that feeds in `config/feeds.yml` are enabled and URLs are reachable.

## License

MIT
