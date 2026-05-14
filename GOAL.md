# Personal RSS Newsletter Agent - Business Goal and Product Brief

## Executive summary

Build a practical, repeatable personal newsletter generator powered by the Claude Agent SDK for Python.

The application reads a curated list of RSS/Atom feeds, filters and ranks recent articles against a user profile, summarizes the selected items, and produces a concise newsletter in Markdown plus a machine-readable JSON artifact.

The project must demonstrate agentic orchestration without turning deterministic work into unnecessary agent work. RSS fetching, parsing, normalization, and basic deduplication should be implemented as ordinary Python code. Claude agents should be used where judgment is useful: relevance scoring, optional semantic grouping, summarization, and editorial selection.

## Problem statement

People often follow many information sources but do not want to manually scan every RSS feed every day. A useful assistant should answer:

- What changed since the last run?
- Which articles actually match my interests?
- What are the top items worth reading?
- Why should I care about each one?
- Which sources produced duplicates or low-value items?

The result should be a reusable command-line tool that can run daily or weekly and generate a consistent personal digest.

## Target users

Primary user: a technical professional who follows news across AI, developer tools, interoperability, databases, security, and selected industry domains.

Secondary users: anyone who wants a small personal research/news workflow from RSS sources without building a full email platform.

## Product goals

1. Generate a useful personal newsletter from RSS/Atom feeds.
2. Demonstrate a clean orchestrator-subagent architecture using the Claude Agent SDK for Python.
3. Use structured JSON contracts between orchestration phases.
4. Keep the system repeatable, testable, and easy to extend.
5. Include project-local Claude runtime configuration that the SDK application can load during agent execution.

## Non-goals for the MVP

- No web UI.
- No email sending integration.
- No full article scraping unless a later extension explicitly adds it.
- No database requirement; local JSON files are sufficient.
- No autonomous long-running background service.
- No agent teams for the MVP.
- No free-form unvalidated JSON parsing as a normal path.

## Expected user experience

A user configures RSS feeds and a personal profile, then runs a command similar to:

```bash
uv run personal-newsletter generate --profile config/profile.yml --feeds config/feeds.yml --days 1 --max-items 8
```

The application writes:

```text
output/newsletter_YYYY-MM-DD.md
output/newsletter_YYYY-MM-DD.json
output/run_YYYY-MM-DD.log
```

The Markdown newsletter should be immediately readable. The JSON file should preserve enough structured data for testing, debugging, and future UI/email rendering.

## MVP functional requirements

### 1. Configuration

Provide these user-editable files:

```text
config/feeds.yml
config/profile.yml
```

`feeds.yml` must support feed name, URL, enabled flag, and optional category hints.

`profile.yml` must support preferred language, interests, avoid terms, ranking weights, maximum newsletter items, and style preferences.

### 2. RSS ingestion

Implement deterministic Python ingestion:

- Fetch RSS/Atom feeds.
- Parse feed entries.
- Normalize entries into Pydantic models.
- Preserve source name, title, URL, published timestamp, excerpt, and optional tags.
- Handle broken feeds gracefully and report warnings.

### 3. Basic deduplication

Implement deterministic deduplication before invoking agents:

- Canonicalize URLs where reasonable.
- Remove exact URL duplicates.
- Remove exact normalized title duplicates.
- Keep track of discarded duplicates for the run report.

Optional extension: add semantic deduplication as an agentic step after basic dedupe.

### 4. Agentic orchestration

Use an orchestrator-subagent architecture.

The orchestrator may be Python code that calls Claude Agent SDK queries in sequence. It should coordinate the workflow and persist intermediate artifacts.

Required agentic phases:

1. Relevance scoring agent
2. Article summarization agent
3. Newsletter editor agent

Optional agentic phase:

4. Semantic deduplication or topic clustering agent

### 5. Structured JSON contracts

Agent phases must return validated structured data, not untrusted free-form text that is parsed with ad hoc regexes.

At minimum define typed models for:

- `Article`
- `ScoredArticle`
- `ArticleSummary`
- `NewsletterItem`
- `NewsletterDraft`
- `RunReport`

The application should fail clearly or retry with a bounded retry strategy if structured output validation fails.

### 6. Newsletter output

The Markdown newsletter must include:

- Title and generation date.
- Profile name or newsletter name.
- Top items section.
- Each item: title, source, URL, score, summary, and why it matters.
- Warnings or limitations when RSS excerpts are short or source metadata is incomplete.
- Optional skipped/duplicates summary.

### 7. Runtime Claude configuration as part of the application

The generated project must include a dedicated Claude configuration structure used by the application at runtime, not only by Claude Code during implementation.

The application must create and use a project-local runtime directory such as:

```text
runtime/
  CLAUDE.md
  .claude/
    settings.json
    rules/
      agent-runtime.md
      structured-output.md
      newsletter-quality.md
    agents/
      relevance-scorer.md
      article-summarizer.md
      newsletter-editor.md
    skills/
      newsletter-editorial-policy/SKILL.md
      rss-source-evaluation/SKILL.md
    hooks/
      block-dangerous-bash.py
```

The SDK runner must set an explicit `cwd` to this runtime directory and opt into project settings, for example conceptually:

```python
ClaudeAgentOptions(
    cwd=str(runtime_dir),
    setting_sources=["project"],
    allowed_tools=["Agent"],
)
```

The runtime configuration should be version-controlled and should not depend on a developer's personal `~/.claude` configuration. Tests should verify that the expected runtime configuration files exist and that the SDK runner points to the intended runtime directory.

### 8. Application-level tools

Prefer deterministic Python functions for ingestion and persistence. Use Claude Agent SDK custom tools only when the agent itself needs controlled access to application capabilities.

Possible custom tools:

- `get_candidate_articles`
- `get_user_profile`
- `save_newsletter_artifact`
- `get_seen_articles`
- `mark_articles_seen`

If custom tools are implemented, they must have explicit input schemas, structured results, narrow permissions, and tests.

### 9. Repeatability and history

The MVP should optionally support:

```text
state/seen_articles.json
```

This prevents repeating the same article across runs when the user enables history.

### 10. Observability

Each run should produce a concise run report:

- Feeds attempted.
- Feed failures.
- Number of raw entries.
- Number of entries after basic dedupe.
- Number scored.
- Number selected.
- Total warnings.
- Output paths.

## Recommended technical shape

Suggested repository structure for the generated application:

```text
personal-rss-newsletter-agent/
  pyproject.toml
  README.md
  .env.example
  CLAUDE.md
  runtime/
    CLAUDE.md
    .claude/
      settings.json
      rules/
      agents/
      skills/
      hooks/
  config/
    feeds.yml
    profile.yml
  src/
    personal_rss_newsletter_agent/
      __init__.py
      cli.py
      config.py
      models.py
      rss_ingestion.py
      dedupe.py
      orchestrator.py
      sdk_runner.py
      render.py
      storage.py
      agent_prompts.py
      agent_tools.py
  tests/
    test_config.py
    test_dedupe.py
    test_models.py
    test_render.py
    test_runtime_config.py
    test_orchestrator_contracts.py
  output/
    .gitkeep
  state/
    .gitkeep
```

## Suggested orchestration flow

```text
load config
  -> fetch RSS feeds
  -> normalize Article[]
  -> basic dedupe
  -> relevance scorer agent -> ScoredArticle[]
  -> filter top candidates
  -> summarizer agent -> ArticleSummary[]
  -> newsletter editor agent -> NewsletterDraft
  -> render Markdown and JSON
  -> write run report
```

## Acceptance criteria

The project is done when all of the following are true:

1. `uv run personal-newsletter generate ...` creates Markdown and JSON outputs from sample RSS feeds.
2. RSS fetching/parsing/basic dedupe are deterministic Python code.
3. At least three Claude agentic phases are present: relevance scoring, summarization, and newsletter editing.
4. Agent outputs are validated with typed structured contracts.
5. The project includes a runtime Claude configuration under a dedicated runtime directory.
6. The SDK runner uses the runtime directory as `cwd` and loads project settings from that directory.
7. The project includes tests for models, dedupe, rendering, runtime config presence, and at least one orchestration contract.
8. The README includes setup, configuration, and demo instructions.
9. The app handles feed failures without failing the whole run.
10. No secrets are committed; `.env.example` documents required variables.

## Demo script

A good demo should show:

1. The feed list.
2. The user profile.
3. The runtime Claude configuration directory.
4. A command-line run.
5. The run report.
6. The generated Markdown newsletter.
7. The JSON artifact containing structured intermediate data.
8. A short explanation of why deterministic steps are not implemented as agents.

## Future extensions

- Weekly digest mode.
- HTML export.
- Email delivery.
- Semantic deduplication agent.
- Topic clustering.
- Multiple profiles.
- Feed quality scoring.
- Calendar or task export for articles that require follow-up.
