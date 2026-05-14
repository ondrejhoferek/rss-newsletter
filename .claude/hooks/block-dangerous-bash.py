#!/usr/bin/env python3
"""Claude Code PreToolUse hook: block dangerous Bash commands."""

from __future__ import annotations

import json
import re
import sys
from typing import Any


def deny(reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )


def main() -> int:
    try:
        payload: dict[str, Any] = json.load(sys.stdin)
    except Exception:
        return 0

    command = str(payload.get("tool_input", {}).get("command", ""))
    normalized = " ".join(command.strip().split())
    lowered = normalized.lower()

    blocked_patterns = [
        (r"\brm\s+-rf\b", "Blocked destructive recursive removal."),
        (r"\bsudo\b", "Blocked sudo command."),
        (r"\bchmod\s+777\b", "Blocked chmod 777."),
        (r"\bchown\s+-r\b", "Blocked recursive chown."),
        (r"\bmkfs\b", "Blocked filesystem formatting command."),
        (r"\bdd\s+if=", "Blocked raw disk write command."),
        (r"\bshutdown\b|\breboot\b", "Blocked system shutdown/reboot."),
        (r"\bgit\s+reset\s+--hard\b", "Blocked hard git reset."),
        (r"\bgit\s+clean\s+-f", "Blocked forced git clean."),
        (r"\bgit\s+push\s+--force\b", "Blocked force push."),
        (r"\bdocker\s+system\s+prune\b", "Blocked Docker system prune."),
        (r"curl\b.*\|\s*(sh|bash)\b", "Blocked executing remote curl output."),
        (r"wget\b.*\|\s*(sh|bash)\b", "Blocked executing remote wget output."),
    ]

    for pattern, reason in blocked_patterns:
        if re.search(pattern, lowered):
            deny(reason)
            return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
