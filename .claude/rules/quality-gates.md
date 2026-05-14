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

When a command is unavailable because the project is not initialized yet, create the missing project configuration instead of skipping validation silently.
