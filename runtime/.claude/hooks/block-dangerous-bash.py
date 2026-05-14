#!/usr/bin/env python3
"""Hook to block dangerous bash commands in the runtime agent context.

This is a safety measure — the runtime agents should not have Bash access,
but this hook provides defense in depth.
"""

import json
import sys

BLOCKED_PATTERNS = [
    "rm -rf",
    "sudo",
    "chmod 777",
    "mkfs",
    "dd if=",
    "shutdown",
    "reboot",
    "git push",
    "git reset --hard",
    "curl | sh",
    "wget | sh",
]


def main() -> None:
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        return

    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "")

    for pattern in BLOCKED_PATTERNS:
        if pattern in command.lower():
            result = {"decision": "block", "reason": f"Blocked dangerous pattern: {pattern}"}
            print(json.dumps(result))
            return

    print(json.dumps({}))


if __name__ == "__main__":
    main()
