# Prompt to start Claude Code implementation

Use this prompt in Claude Code from the repository root after placing this starter pack in an empty project directory:

```text
Read @GOAL.md carefully and implement the project described there.

Follow the repository instructions and Claude Code configuration already present in this directory. Keep product requirements in product documentation and keep reusable technical guidance in Claude configuration.

Important implementation priorities:
1. Build a small but working MVP first.
2. Use deterministic Python for RSS fetch, parse, normalization, and basic dedupe.
3. Use Claude Agent SDK Python for relevance scoring, summarization, and newsletter editing.
4. Use validated structured JSON contracts between phases.
5. Create the runtime Claude configuration directory required by the goal and wire the SDK runner to load it with an explicit runtime cwd and project setting sources.
6. Add tests, README, sample config, and a runnable CLI command.

Start in plan mode: inspect the files, propose the implementation plan, then proceed after the plan is accepted.
```
