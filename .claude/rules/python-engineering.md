# Python Engineering Rules

- Use a `src/` layout for packages.
- Use `pyproject.toml` as the single source for project metadata and tool configuration.
- Prefer `uv run ...` for commands.
- Keep modules small and named by responsibility.
- Keep network I/O separate from pure transformation logic.
- Use Pydantic models for external data, configuration, and agent contracts.
- Use timezone-aware datetimes for stored timestamps.
- Do not let tests depend on live network by default.
- Put sample data under `tests/fixtures/` when needed.
