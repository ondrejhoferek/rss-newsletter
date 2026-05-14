# General Instructions for Python Agentic Projects

## Scope

These instructions apply to Python projects that build agentic applications with the Claude Agent SDK. Keep this file short, technical, and broadly reusable. Do not put product-specific business requirements here.

## Working style

- Explore before implementing when the change touches multiple files.
- Write a short implementation plan before broad refactors.
- Prefer small, reviewable changes.
- Verify with tests or a concrete command before considering work complete.
- Do not hide failures. Explain what failed and what remains.

## Python engineering standards

- Use `uv` for dependency and command execution when the project supports it.
- Use a `src/` layout for importable packages.
- Use Pydantic models at data boundaries.
- Keep I/O, orchestration, rendering, and data models in separate modules.
- Prefer pure functions for deterministic transformations.
- Avoid global mutable state except for explicit configuration objects.
- Do not read secrets from source files. Use environment variables and `.env.example` only.

## Agentic architecture standards

- Use deterministic Python code for deterministic work.
- Use agents only for judgment-heavy tasks such as ranking, summarization, critique, synthesis, or semantic grouping.
- Prefer orchestrator-subagent workflows over autonomous agent teams unless peer-to-peer coordination is explicitly needed.
- Keep each agent role narrow and testable.
- Pass compact, explicit inputs to agents. Do not pass entire repositories or unbounded logs unless necessary.
- Use structured output contracts for machine-consumed agent results.
- Validate every agent result before using it downstream.
- Bound retries. Do not loop indefinitely on malformed output.

## Claude Agent SDK runtime standards

- Use the Python Claude Agent SDK as the orchestration layer for Claude-powered work.
- Set an explicit runtime `cwd` for SDK calls.
- For applications that rely on project-local Claude configuration, use project setting sources intentionally.
- Do not rely on a developer's personal user-level Claude configuration for application behavior.
- Keep runtime Claude configuration version-controlled when it affects application behavior.
- Give subagents only the tools they actually need.
- Do not include the `Agent` tool inside subagents unless the SDK documentation explicitly supports nested agent delegation for the selected version.
- Prefer programmatic subagent definitions for application logic when runtime behavior must be fully controlled in code.
- Filesystem-based subagents, skills, hooks, and rules are appropriate when the application intentionally loads project-local Claude configuration at runtime.

## Structured JSON contracts

- Define input and output schemas before implementing an agent step.
- Use Pydantic for Python-side validation.
- Keep IDs stable across phases so outputs can be joined without fuzzy matching.
- Store raw agent outputs only for debugging; downstream logic must use validated objects.
- Include warnings and confidence where source data may be incomplete.

## Testing and quality gates

Prefer these commands when available:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```

When adding new behavior:

- Add or update tests.
- Test normal and failure paths.
- Include a small fixture instead of live network calls when practical.
- Keep network-dependent tests opt-in.

## Security and safety

- Never commit API keys, tokens, cookies, private keys, or real `.env` files.
- Never print secrets in logs.
- Block or ask before destructive shell commands.
- Treat downloaded feed content as untrusted input.
- Keep rendered Markdown safe: do not execute embedded content.
- Do not add telemetry, external posting, email sending, or network writes without explicit user request.

## Review checklist

Before finishing, check:

- The project runs from a clean checkout.
- Required environment variables are documented.
- Agent outputs are schema-validated.
- Runtime Claude configuration is explicit and tested when used.
- The README shows a real command that produces an output artifact.
- Tests or a clearly stated validation command were run.
