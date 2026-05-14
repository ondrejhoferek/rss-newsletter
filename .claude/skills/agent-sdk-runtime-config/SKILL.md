---
name: agent-sdk-runtime-config
description: Create or review a project-local Claude runtime configuration for a Python Claude Agent SDK application.
---

# Agent SDK Runtime Configuration Skill

Use this skill when creating an application that should load Claude configuration at runtime through the Claude Agent SDK.

## Objective

Create a dedicated runtime directory that contains Claude configuration used by the application, not only by the developer using Claude Code.

## Required runtime structure

```text
runtime/
  CLAUDE.md
  .claude/
    settings.json
    rules/
    agents/
    skills/
    hooks/
```

## Implementation checklist

1. Create the runtime directory and configuration files.
2. Keep runtime `CLAUDE.md` technical and behavior-focused.
3. Do not duplicate product documentation into runtime instructions.
4. Add filesystem-based subagents only if the SDK runner intentionally exposes the `Agent` tool.
5. Add skills for reusable domain workflows that should load on demand.
6. Add hooks only for deterministic safety or validation behavior.
7. In the SDK runner, set an explicit `cwd` to the runtime directory.
8. Use project setting sources intentionally.
9. Avoid relying on user-level settings for application behavior.
10. Add tests that verify runtime files exist and the SDK runner resolves the expected path.

## Review checklist

- Can a clean checkout run without personal Claude configuration?
- Are permissions narrow?
- Are hooks safe and deterministic?
- Are runtime agents distinct from development-time reviewers?
- Is runtime configuration documented in README?
