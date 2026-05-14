"""Claude Agent SDK runner.

Wraps the SDK query() function with structured output validation,
bounded retries, and explicit runtime directory configuration.
"""

from pathlib import Path
from typing import TypeVar

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query
from pydantic import BaseModel, ValidationError

from personal_rss_newsletter_agent.config import get_model

T = TypeVar("T", bound=BaseModel)

RUNTIME_DIR = Path(__file__).resolve().parent.parent.parent / "runtime"
MAX_RETRIES = 2


def get_runtime_dir() -> Path:
    """Return the absolute path to the runtime configuration directory."""
    if not RUNTIME_DIR.is_dir():
        raise RuntimeError(f"Runtime directory not found: {RUNTIME_DIR}")
    return RUNTIME_DIR


async def run_agent(
    prompt: str,
    output_schema: type[T],
    max_retries: int = MAX_RETRIES,
) -> T:
    """Run a Claude agent with structured output and Pydantic validation.

    Args:
        prompt: The complete prompt including article data and instructions.
        output_schema: Pydantic model class for response validation.
        max_retries: Maximum retry attempts on validation failure.

    Returns:
        Validated Pydantic model instance.

    Raises:
        RuntimeError: If all retries are exhausted or the agent returns an error.
    """
    runtime_dir = get_runtime_dir()
    schema = output_schema.model_json_schema()

    options = ClaudeAgentOptions(
        cwd=str(runtime_dir),
        setting_sources=["user", "project"],
        allowed_tools=[],
        output_format={"type": "json_schema", "schema": schema},
        permission_mode="bypassPermissions",
        model=get_model(),
        max_turns=1,
    )

    last_error: Exception | None = None

    for attempt in range(max_retries + 1):
        retry_note = ""
        if attempt > 0:
            retry_note = (
                f"\n\n(Previous attempt failed validation: {last_error}. "
                "Please ensure your response matches the schema exactly.)"
            )

        result_message: ResultMessage | None = None
        try:
            async for message in query(prompt=prompt + retry_note, options=options):
                if isinstance(message, ResultMessage):
                    result_message = message
        except Exception as e:
            if result_message is None:
                last_error = RuntimeError(
                    f"SDK error (no result collected): {e}. "
                    "Check Claude authentication: run 'claude --version' or set ANTHROPIC_API_KEY."
                )
                continue
            # ResultMessage was collected before the exception — proceed with it

        if result_message is None:
            last_error = RuntimeError("No ResultMessage received from agent")
            continue

        if result_message.is_error:
            status = getattr(result_message, "api_error_status", None)
            errors = getattr(result_message, "errors", None)
            detail = (
                "; ".join(errors) if errors
                else f"HTTP {status}" if status
                else result_message.result or "Unknown API error"
            )
            last_error = RuntimeError(f"Agent returned error: {detail}")
            continue

        if result_message.structured_output is None:
            last_error = RuntimeError("Agent did not return structured output")
            continue

        try:
            return output_schema.model_validate(result_message.structured_output)
        except ValidationError as e:
            last_error = e
            continue

    raise RuntimeError(f"Agent failed after {max_retries + 1} attempts. Last error: {last_error}")
