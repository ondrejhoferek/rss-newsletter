#!/usr/bin/env python3
"""Claude Code PreToolUse hook: block accidental reads of common secret files."""

from __future__ import annotations

import json
import os
import sys
from typing import Any

SENSITIVE_MARKERS = (
    ".env",
    "id_rsa",
    "id_ed25519",
    "credentials",
    "secrets",
    "token",
    "cookie",
)

SAFE_EXCEPTIONS = (
    ".env.example",
    "example.env",
    "README",
)


def deny(path: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"Reading sensitive-looking file is blocked: {path}",
                }
            }
        )
    )


def main() -> int:
    try:
        payload: dict[str, Any] = json.load(sys.stdin)
    except Exception:
        return 0

    tool_input = payload.get("tool_input", {})
    raw_path = str(tool_input.get("file_path") or tool_input.get("path") or "")
    if not raw_path:
        return 0

    base = os.path.basename(raw_path)
    lowered = raw_path.lower()

    if any(exc.lower() in lowered for exc in SAFE_EXCEPTIONS):
        return 0

    if any(marker in base.lower() or marker in lowered for marker in SENSITIVE_MARKERS):
        deny(raw_path)
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
