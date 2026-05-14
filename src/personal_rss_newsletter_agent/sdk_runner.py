"""Claude Agent SDK runner.

Wraps the SDK query() function with structured output validation,
bounded retries, and explicit runtime directory configuration.
"""

import json
import logging
from pathlib import Path
from typing import Any, TypeVar

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

RUNTIME_DIR = Path(__file__).resolve().parent.parent.parent / "runtime"
MAX_RETRIES = 2


UNSUPPORTED_KEYWORDS = frozenset({
    "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum",
    "minLength", "maxLength", "pattern", "minItems", "maxItems",
    "uniqueItems", "title", "description", "default", "examples",
})


def _prepare_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Prepare a Pydantic JSON schema for the Anthropic structured output API.

    - Adds additionalProperties: false to all object types
    - Strips unsupported validation keywords (minimum, maximum, title, etc.)
    """
    if schema.get("type") == "object":
        schema["additionalProperties"] = False
    for kw in UNSUPPORTED_KEYWORDS:
        schema.pop(kw, None)
    properties: dict[str, Any] = schema.get("properties", {})
    for prop in properties.values():
        if isinstance(prop, dict):
            _prepare_schema(prop)
    defs: dict[str, Any] = schema.get("$defs", {})
    for defn in defs.values():
        if isinstance(defn, dict):
            _prepare_schema(defn)
    items: Any = schema.get("items")
    if isinstance(items, dict):
        _prepare_schema(items)
    return schema


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
    schema = _prepare_schema(output_schema.model_json_schema())

    options = ClaudeAgentOptions(
        cwd=str(runtime_dir),
        setting_sources=["user", "project"],
        allowed_tools=[],
        output_format={"type": "json_schema", "schema": schema},
        permission_mode="bypassPermissions",
    )

    last_error: Exception | None = None
    schema_name = output_schema.__name__

    for attempt in range(max_retries + 1):
        retry_note = ""
        if attempt > 0:
            logger.warning(
                "%s: retry %d/%d (last error: %s)", schema_name, attempt, max_retries, last_error
            )
            retry_note = (
                f"\n\n(Previous attempt failed validation: {last_error}. "
                "Please ensure your response matches the schema exactly.)"
            )

        logger.info(
            "%s: starting agent call (attempt %d, prompt_len=%d)",
            schema_name, attempt + 1, len(prompt),
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

        logger.debug(
            "%s: ResultMessage dump:\n%s", schema_name, _dump_result_message(result_message)
        )

        _log_result_summary(schema_name, result_message)

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
            validated = output_schema.model_validate(result_message.structured_output)
            logger.info("%s: validated successfully", schema_name)
            return validated
        except ValidationError as e:
            last_error = e
            continue

    raise RuntimeError(f"Agent failed after {max_retries + 1} attempts. Last error: {last_error}")


def _usage_val(usage: dict[str, Any], key: str, default: str = "?") -> str:
    v = usage.get(key, default)
    return str(v) if v is not None else default


def _log_result_summary(schema_name: str, result_message: ResultMessage) -> None:
    """Log a concise summary of a ResultMessage: model, tokens, cache, cost, duration."""
    raw_usage = result_message.usage
    raw_model_usage = result_message.model_usage

    model = "?"
    if isinstance(raw_model_usage, dict) and raw_model_usage:
        model = str(next(iter(raw_model_usage)))

    usage: dict[str, Any] = raw_usage if isinstance(raw_usage, dict) else {}
    input_tokens = _usage_val(usage, "input_tokens")
    output_tokens = _usage_val(usage, "output_tokens")
    cache_read = _usage_val(usage, "cache_read_input_tokens", "0")
    cache_created = _usage_val(usage, "cache_creation_input_tokens", "0")

    cost = result_message.total_cost_usd
    cost_str = f"${cost:.6f}" if isinstance(cost, float) else "?"
    duration_str = f"{result_message.duration_ms}ms"

    logger.info(
        "%s: model=%s turns=%s duration=%s cost=%s "
        "tokens input=%s output=%s cache_read=%s cache_created=%s",
        schema_name,
        model,
        result_message.num_turns,
        duration_str,
        cost_str,
        input_tokens,
        output_tokens,
        cache_read,
        cache_created,
    )


def _dump_result_message(result_message: ResultMessage) -> str:
    """Serialize ResultMessage to a JSON string for debug logging."""
    try:
        import dataclasses
        if dataclasses.is_dataclass(result_message):
            raw = dataclasses.asdict(result_message)
        else:
            raw = vars(result_message)
        return json.dumps(raw, default=str, indent=2)
    except Exception:
        return repr(result_message)
