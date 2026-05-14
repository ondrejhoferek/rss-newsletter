---
name: project-quality-review
description: Review a Python agentic project before considering the implementation complete.
---

# Project Quality Review Skill

Use this skill before final delivery.

## Checklist

1. Run the relevant tests.
2. Check that the CLI command in README works or is honestly documented.
3. Check that deterministic code is not implemented as unnecessary agent calls.
4. Check that agent outputs are schema-validated.
5. Check that runtime Claude configuration is explicit and tested if the SDK app loads it.
6. Check that no secrets are committed.
7. Check that sample config files are safe to share.
8. Check that generated output directories have `.gitkeep` or are gitignored as appropriate.
9. Summarize remaining risks and follow-up work.
