# Quality Gates

Run the narrowest useful verification command after changes.

Preferred order:

```bash
uv run pytest tests/test_specific_file.py
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```

For reproducibility-sensitive checks, prefer locked validation when practical:

```bash
uv run --locked pytest
uv lock --check
```

Before considering work complete, verify:

- The changed code is simple, focused, and easy to review.
- Unused code, unused imports, stale comments, and commented-out code are removed.
- No speculative features or abstractions were added.
- Error handling is explicit at I/O, configuration, and agent-output boundaries.
- Type safety is maintained with Python type hints and Pydantic validation.
- Agent outputs are schema-validated before downstream use.
- Tests are added or updated for changed behavior.
- Network-dependent tests are opt-in or isolated behind fixtures.
- There are no hardcoded secrets, tokens, paths, or environment-specific values.
- README commands and documentation match the implemented project.
- Runtime Claude configuration is explicit and tested when the application uses it.

When a command is unavailable because the project is not initialized yet, create the missing project configuration instead of skipping validation silently.
