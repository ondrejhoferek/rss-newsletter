# Structured Contract Rules

- Define schemas before implementing the agent prompt.
- Use stable IDs to join outputs across phases.
- Validate all agent outputs with Pydantic.
- Never parse machine-consumed agent outputs with regular expressions as the normal path.
- Include confidence or warnings when source input is incomplete.
- Store final machine-readable artifacts as JSON for auditability.
- Keep human-readable Markdown rendering separate from structured data generation.
