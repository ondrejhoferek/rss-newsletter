# Python Engineering Rules

## Project structure

- Use a `src/` layout for importable packages.
- Use `pyproject.toml` as the single source for project metadata and tool configuration.
- Keep modules small and named by responsibility.
- Keep network I/O separate from pure transformation logic.
- Keep orchestration separate from rendering and persistence.
- Put sample data under `tests/fixtures/` when needed.

## uv and dependency management

- Use `uv` as the default Python project manager.
- Prefer `uv run ...` for all project commands.
- Use `uv sync` for explicit local environment setup.
- Do not use `pip`, `poetry`, `pipenv`, or manual virtualenv commands unless the existing project requires them.
- Manage dependencies through `pyproject.toml` and `uv.lock`.
- Commit `uv.lock` for applications.
- Add runtime dependencies with `uv add <package>`.
- Add development dependencies with dependency groups, for example `uv add --group dev pytest ruff mypy`.
- Prefer `[dependency-groups]` for dev/test/lint dependencies.
- Use `.python-version` when the project benefits from pinning a local Python version.

## Code quality

- Choose the simplest implementation that satisfies the requirement.
- Prefer plain functions and composition before classes or inheritance.
- Keep functions small, focused, and at one level of abstraction.
- Use meaningful, domain-oriented names.
- Avoid speculative features, speculative abstractions, and premature optimization.
- Remove dead code, unused imports, stale comments, commented-out code, and open-ended TODOs.
- Comments should explain why, not restate what the code does.
- Do not duplicate logic; extract a small function when duplication becomes real.

## Types, validation, and errors

- Use Python 3.10+ type syntax consistently.
- Use Pydantic models for external data, configuration, and agent contracts.
- Validate inputs at system boundaries.
- Fail fast with explicit, actionable errors.
- Never silently ignore exceptions from I/O, configuration loading, or agent output validation.
- Use timezone-aware datetimes for stored timestamps.

## Testing

- Do not let tests depend on live network by default.
- Prefer fixtures and small sample inputs for deterministic tests.
- Test normal paths and failure paths.
- Add regression tests for parsing, normalization, deduplication, rendering, and structured contract validation.
