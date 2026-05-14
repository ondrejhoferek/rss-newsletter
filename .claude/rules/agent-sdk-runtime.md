# Claude Agent SDK Runtime Rules

Use these rules for Python applications that execute Claude agents through the Claude Agent SDK.

- Set an explicit runtime directory for SDK calls.
- Load project settings intentionally when application behavior depends on filesystem-based Claude configuration.
- Do not depend on user-level Claude settings for application correctness.
- Keep application runtime Claude configuration under source control.
- Keep runtime instructions separate from product documentation.
- Use narrow `allowed_tools` lists.
- Use subagents only for focused tasks with clear role descriptions.
- Prefer programmatic agents when behavior must be fully defined in code.
- Use filesystem-based agents, skills, hooks, and rules only when the application intentionally loads them through its runtime `cwd`.
- Add a test that verifies the SDK runner resolves the intended runtime directory.
