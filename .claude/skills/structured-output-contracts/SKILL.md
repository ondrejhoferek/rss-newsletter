---
name: structured-output-contracts
description: Design Pydantic and JSON Schema contracts for agent-to-application data exchange.
---

# Structured Output Contracts Skill

Use this skill before implementing an agent step whose output is consumed by application logic.

## Contract design checklist

- Define a Pydantic model before writing the prompt.
- Include stable IDs for joining data across steps.
- Add constrained fields where possible, such as score ranges and enums.
- Separate user-facing text from machine-control fields.
- Include warnings for incomplete or low-confidence source data.
- Avoid optional fields when downstream code requires the value.
- Write tests for valid and invalid examples.

## Prompting checklist

- Tell the agent that the output is consumed by code.
- Tell the agent not to invent facts beyond the provided input.
- Provide compact examples only when they clarify edge cases.
- Validate the result through the SDK structured output mechanism or through Pydantic immediately after receiving it.
