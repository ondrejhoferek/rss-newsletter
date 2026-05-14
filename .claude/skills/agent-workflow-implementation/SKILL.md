---
name: agent-workflow-implementation
description: Implement a small orchestrator-subagent workflow in a Python Claude Agent SDK application.
---

# Agent Workflow Implementation Skill

Use this workflow for small production-style agentic applications.

## Steps

1. Identify deterministic steps and implement them as ordinary Python functions.
2. Identify judgment-heavy steps and implement them as agent calls.
3. Define Pydantic models for every machine-consumed input and output.
4. Implement a Python orchestrator that calls each step explicitly.
5. Persist intermediate artifacts only when useful for debugging or auditability.
6. Add bounded retries for recoverable agent-output failures.
7. Add tests for deterministic steps and schema validation.
8. Add a small CLI command that exercises the full pipeline.

## Design rules

- Do not create agents for simple parsing, file I/O, or exact deduplication.
- Do not pass unnecessary context to agents.
- Prefer small batches over one huge prompt.
- Fail clearly when validation fails.
- Keep rendering separate from orchestration.
