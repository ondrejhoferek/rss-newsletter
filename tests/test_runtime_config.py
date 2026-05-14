"""Tests for runtime Claude configuration."""

from pathlib import Path

from personal_rss_newsletter_agent.sdk_runner import RUNTIME_DIR, get_runtime_dir


class TestRuntimeDirectory:
    def test_runtime_dir_exists(self) -> None:
        assert RUNTIME_DIR.is_dir(), f"Runtime directory not found: {RUNTIME_DIR}"

    def test_get_runtime_dir_returns_path(self) -> None:
        path = get_runtime_dir()
        assert isinstance(path, Path)
        assert path.is_dir()

    def test_claude_md_exists(self) -> None:
        claude_md = RUNTIME_DIR / "CLAUDE.md"
        assert claude_md.is_file()

    def test_settings_json_exists(self) -> None:
        settings = RUNTIME_DIR / ".claude" / "settings.json"
        assert settings.is_file()

    def test_rules_directory(self) -> None:
        rules_dir = RUNTIME_DIR / ".claude" / "rules"
        assert rules_dir.is_dir()
        rule_files = list(rules_dir.glob("*.md"))
        assert len(rule_files) >= 3

    def test_agents_directory(self) -> None:
        agents_dir = RUNTIME_DIR / ".claude" / "agents"
        assert agents_dir.is_dir()
        agent_files = list(agents_dir.glob("*.md"))
        assert len(agent_files) >= 3

    def test_skills_directory(self) -> None:
        skills_dir = RUNTIME_DIR / ".claude" / "skills"
        assert skills_dir.is_dir()
        skill_files = list(skills_dir.glob("*/SKILL.md"))
        assert len(skill_files) >= 2

    def test_hooks_directory(self) -> None:
        hooks_dir = RUNTIME_DIR / ".claude" / "hooks"
        assert hooks_dir.is_dir()
        hook_files = list(hooks_dir.glob("*.py"))
        assert len(hook_files) >= 1

    def test_expected_agent_files(self) -> None:
        agents_dir = RUNTIME_DIR / ".claude" / "agents"
        expected = ["relevance-scorer.md", "article-summarizer.md", "newsletter-editor.md"]
        for name in expected:
            assert (agents_dir / name).is_file(), f"Missing agent: {name}"

    def test_expected_rule_files(self) -> None:
        rules_dir = RUNTIME_DIR / ".claude" / "rules"
        expected = ["agent-runtime.md", "structured-output.md", "newsletter-quality.md"]
        for name in expected:
            assert (rules_dir / name).is_file(), f"Missing rule: {name}"
