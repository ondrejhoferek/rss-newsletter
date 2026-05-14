# Runtime Agent Configuration

## Purpose

The `runtime/` directory contains project-local Claude configuration that the application loads at runtime through the Claude Agent SDK. This is separate from the development-time `.claude/` configuration used by Claude Code during implementation.

## Directory Structure

```
runtime/
├── CLAUDE.md                     # Agent instructions loaded into context
└── .claude/
    ├── settings.json             # Permission and tool restrictions
    ├── rules/
    │   ├── agent-runtime.md      # Behavioral constraints
    │   ├── structured-output.md  # JSON output formatting rules
    │   └── newsletter-quality.md # Editorial quality standards
    ├── agents/
    │   ├── relevance-scorer.md   # Scoring agent definition
    │   ├── article-summarizer.md # Summarization agent definition
    │   └── newsletter-editor.md  # Editor agent definition
    ├── skills/
    │   ├── newsletter-editorial-policy/SKILL.md
    │   └── rss-source-evaluation/SKILL.md
    └── hooks/
        └── block-dangerous-bash.py  # Defense-in-depth safety hook
```

## How the Application Loads Configuration

The SDK runner in `src/personal_rss_newsletter_agent/sdk_runner.py` sets:

```python
ClaudeAgentOptions(
    cwd=str(runtime_dir),           # Points to runtime/
    setting_sources=["project"],    # Loads .claude/ from cwd only
    allowed_tools=[],               # No filesystem tools needed
    permission_mode="bypassPermissions",
    output_format={"type": "json_schema", "schema": ...},
)
```

When `setting_sources=["project"]` is set with `cwd` pointing to `runtime/`:
- `runtime/CLAUDE.md` is loaded as project instructions
- `runtime/.claude/settings.json` defines permissions
- `runtime/.claude/rules/*.md` provide behavioral rules
- `runtime/.claude/agents/*.md` define available subagents
- `runtime/.claude/skills/*/SKILL.md` provide on-demand knowledge

## Runtime Agents

### relevance-scorer
Scores articles 0-10 based on user profile relevance. Receives article data in the prompt, returns `RelevanceResponse` JSON.

### article-summarizer
Produces 1-2 sentence summaries with "why it matters" explanations. Receives scored articles, returns `SummaryResponse` JSON.

### newsletter-editor
Selects top items, assigns ranks, generates newsletter title. Receives summaries, returns `EditorResponse` JSON.

## Security Constraints

1. **No tools allowed**: `allowed_tools=[]` prevents agents from using Read, Write, Bash, or any filesystem tools.
2. **Deny list**: `settings.json` explicitly denies Bash, Write, Edit, WebFetch, and WebSearch.
3. **Defense-in-depth hook**: `block-dangerous-bash.py` blocks dangerous patterns even if tool restrictions are bypassed.
4. **Data-in/data-out**: Agents receive all data in the prompt and return structured JSON. No file access needed.

## Separation from Development Configuration

| Aspect | Development (`.claude/`) | Runtime (`runtime/.claude/`) |
|---|---|---|
| Purpose | Guide Claude Code during implementation | Configure agents at application runtime |
| Loaded by | Claude Code CLI | Claude Agent SDK via `query()` |
| Contains | Dev rules, hooks, skills for code review | Agent definitions, quality rules |
| Location | Repository root `.claude/` | `runtime/` subdirectory |

## Supported Authentication

The runtime agents authenticate using whatever credentials are available:
1. **Claude Code login** — Existing `claude` CLI authentication (local development)
2. **ANTHROPIC_API_KEY** — Environment variable (CI, containers, API-key based)

No secrets are stored in the runtime configuration directory.
