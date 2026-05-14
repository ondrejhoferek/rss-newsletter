---
name: project-quality-review
description: Review a Python agentic project before considering the implementation complete.
---

# Project Quality Review Skill

Use this skill before final delivery.

## Checklist

1. Run the narrowest useful tests, then the broader suite when practical.
2. Run linting and formatting checks.
3. Run type checking when configured.
4. Check that the CLI command in README works or is honestly documented.
5. Check that deterministic code is not implemented as unnecessary agent calls.
6. Check that agent outputs are schema-validated before downstream use.
7. Check that runtime Claude configuration is explicit and tested if the SDK app loads it.
8. Check that `uv`, `pyproject.toml`, and `uv.lock` are used consistently for Python project management.
9. Check that no secrets are committed and `.env.example` contains only placeholders.
10. Check that sample config files are safe to share.
11. Check that generated output directories have `.gitkeep` or are gitignored as appropriate.
12. Remove unused imports, dead code, stale comments, and commented-out code.
13. Verify that error handling is explicit at I/O, configuration, and agent-output boundaries.
14. Verify that documentation describes the actual implementation, not aspirational features.
15. Summarize remaining risks and follow-up work.
