#!/usr/bin/env python3
"""Tests for the SkillShelf safety scanner.

Uses unittest (no pytest dependency). Run with:
    python test_safety_scanner.py
"""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add scripts dir to path so we can import the scanner
SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

import safety_scanner as ss

FIXTURES_DIR = SCRIPTS_DIR.parent / "fixtures" / "safety-scanner"
SKILLS_DIR = SCRIPTS_DIR.parent / "skills"


def _scan(fixture_name: str) -> ss.ScanContext:
    """Run rule-based checks only on a fixture directory."""
    skill_dir = FIXTURES_DIR / fixture_name
    ctx = ss.ScanContext(skill_dir=skill_dir, skill_name=fixture_name)
    ss.run_rule_based_checks(ctx)
    return ctx


def _rules(ctx: ss.ScanContext) -> list[str]:
    """Extract just the rule IDs from findings."""
    return [f.rule for f in ctx.findings]


def _blocks(ctx: ss.ScanContext) -> list[str]:
    """Extract rule IDs of BLOCK findings."""
    return [f.rule for f in ctx.findings if f.severity == "BLOCK"]


def _warns(ctx: ss.ScanContext) -> list[str]:
    """Extract rule IDs of WARN findings."""
    return [f.rule for f in ctx.findings if f.severity == "WARN"]


# -----------------------------------------------------------------------
# Safe skill baseline
# -----------------------------------------------------------------------

class TestSafeSkill(unittest.TestCase):
    def test_no_findings(self):
        ctx = _scan("safe-skill")
        self.assertEqual(_blocks(ctx), [])
        self.assertEqual(_warns(ctx), [])


# -----------------------------------------------------------------------
# File-level checks
# -----------------------------------------------------------------------

class TestFileLevel(unittest.TestCase):
    def test_forbidden_extension(self):
        ctx = _scan("forbidden-files")
        self.assertIn("FILE_FORBIDDEN_EXTENSION", _blocks(ctx))

    def test_hidden_file(self):
        """Dotfiles should produce WARN."""
        # Create a temp fixture with a hidden file
        import tempfile, shutil
        tmp = Path(tempfile.mkdtemp())
        skill_dir = tmp / "hidden-test"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: test\n---\n# Test\n")
        (skill_dir / ".hidden").write_text("secret")
        try:
            ctx = ss.ScanContext(skill_dir=skill_dir, skill_name="hidden-test")
            ss.run_rule_based_checks(ctx)
            self.assertIn("FILE_HIDDEN_FILE", _warns(ctx))
        finally:
            shutil.rmtree(tmp)


# -----------------------------------------------------------------------
# Python scanner
# -----------------------------------------------------------------------

class TestPythonScanner(unittest.TestCase):
    def test_dangerous_imports_are_warn(self):
        ctx = _scan("dangerous-imports")
        blocks = _blocks(ctx)
        warns = _warns(ctx)
        # subprocess, socket, http.client should be WARN not BLOCK
        self.assertNotIn("PY_DANGEROUS_IMPORT", blocks)
        self.assertIn("PY_DANGEROUS_IMPORT", warns)

    def test_eval_exec_is_block(self):
        ctx = _scan("eval-exec")
        blocks = _blocks(ctx)
        self.assertIn("PY_EVAL_EXEC", blocks)

    def test_os_system_is_block(self):
        ctx = _scan("eval-exec")
        blocks = _blocks(ctx)
        self.assertIn("PY_OS_EXEC_CALL", blocks)

    def test_encoded_payload_is_block(self):
        ctx = _scan("eval-exec")
        blocks = _blocks(ctx)
        self.assertIn("PY_ENCODED_PAYLOAD", blocks)

    def test_env_access_is_warn(self):
        ctx = _scan("env-access")
        blocks = _blocks(ctx)
        warns = _warns(ctx)
        self.assertNotIn("PY_ENV_ACCESS", blocks)
        self.assertIn("PY_ENV_ACCESS", warns)

    def test_os_import_is_warn(self):
        ctx = _scan("env-access")
        self.assertIn("PY_DANGEROUS_IMPORT_OS", _warns(ctx))


# -----------------------------------------------------------------------
# JavaScript scanner
# -----------------------------------------------------------------------

class TestJavaScriptScanner(unittest.TestCase):
    def test_child_process_is_block(self):
        ctx = _scan("js-dangerous")
        self.assertIn("JS_CHILD_PROCESS", _blocks(ctx))

    def test_eval_is_block(self):
        ctx = _scan("js-dangerous")
        self.assertIn("JS_EVAL", _blocks(ctx))

    def test_process_env_is_warn(self):
        ctx = _scan("js-dangerous")
        self.assertIn("JS_PROCESS_ENV", _warns(ctx))

    def test_network_access_is_warn(self):
        """fetch, XMLHttpRequest, etc. should be WARN."""
        # The js-dangerous fixture doesn't have fetch, but test the pattern
        import tempfile, shutil
        tmp = Path(tempfile.mkdtemp())
        skill_dir = tmp / "js-net-test"
        (skill_dir / "scripts").mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("---\nname: test\n---\n# Test\n")
        (skill_dir / "scripts" / "net.js").write_text("fetch('http://example.com')\n")
        try:
            ctx = ss.ScanContext(skill_dir=skill_dir, skill_name="js-net-test")
            ss.run_rule_based_checks(ctx)
            self.assertIn("JS_NETWORK_ACCESS", _warns(ctx))
            self.assertNotIn("JS_NETWORK_ACCESS", _blocks(ctx))
        finally:
            shutil.rmtree(tmp)


# -----------------------------------------------------------------------
# Shell scanner
# -----------------------------------------------------------------------

class TestShellScanner(unittest.TestCase):
    def test_reverse_shell_is_block(self):
        ctx = _scan("shell-dangerous")
        self.assertIn("SH_REVERSE_SHELL", _blocks(ctx))

    def test_pipe_to_shell_is_block(self):
        ctx = _scan("shell-dangerous")
        self.assertIn("SH_PIPE_TO_SHELL", _blocks(ctx))

    def test_privilege_escalation_is_block(self):
        ctx = _scan("shell-dangerous")
        self.assertIn("SH_PRIVILEGE_ESCALATION", _blocks(ctx))

    def test_network_tool_is_warn(self):
        ctx = _scan("shell-dangerous")
        self.assertIn("SH_NETWORK_TOOL", _warns(ctx))


# -----------------------------------------------------------------------
# Reference file scanner
# -----------------------------------------------------------------------

class TestReferenceScanner(unittest.TestCase):
    def test_html_comment_instructions(self):
        ctx = _scan("hidden-content")
        self.assertIn("REF_HTML_COMMENT_INSTRUCTIONS", _warns(ctx))

    def test_encoded_payload(self):
        ctx = _scan("hidden-content")
        self.assertIn("REF_ENCODED_PAYLOAD", _warns(ctx))

    def test_suspicious_url(self):
        ctx = _scan("hidden-content")
        self.assertIn("REF_SUSPICIOUS_URL", _warns(ctx))

    def test_zero_width_chars(self):
        ctx = _scan("zero-width")
        self.assertIn("REF_ZERO_WIDTH_CHARS", _blocks(ctx))

    def test_prompt_injection_keywords(self):
        ctx = _scan("prompt-injection")
        self.assertIn("REF_PROMPT_INJECTION_KEYWORDS", _warns(ctx))


# -----------------------------------------------------------------------
# LLM integration (mocked)
# -----------------------------------------------------------------------

class TestLLMIntegration(unittest.TestCase):
    def test_skips_without_api_key(self):
        ctx = ss.ScanContext(
            skill_dir=FIXTURES_DIR / "safe-skill",
            skill_name="safe-skill",
        )
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": ""}):
            ss.run_llm_checks(ctx)
        rules = _rules(ctx)
        self.assertIn("LLM_SKIPPED", rules)

    def test_parses_clean_response(self):
        ctx = ss.ScanContext(
            skill_dir=FIXTURES_DIR / "safe-skill",
            skill_name="safe-skill",
        )
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="[]")]
        mock_client.messages.create.return_value = mock_response

        mock_anthropic = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}), \
             patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            ss.run_llm_checks(ctx)

        # No findings added (empty array = clean)
        self.assertEqual(len(ctx.findings), 0)

    def test_parses_findings_response(self):
        ctx = ss.ScanContext(
            skill_dir=FIXTURES_DIR / "safe-skill",
            skill_name="safe-skill",
        )
        llm_response = json.dumps([{
            "severity": "WARN",
            "file": "SKILL.md",
            "line": 10,
            "rule": "DECEPTIVE_FRAMING",
            "message": "Suspicious pattern in instructions"
        }])

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=llm_response)]
        mock_client.messages.create.return_value = mock_response

        mock_anthropic = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}), \
             patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            ss.run_llm_checks(ctx)

        self.assertEqual(len(ctx.findings), 1)
        self.assertEqual(ctx.findings[0].severity, "WARN")
        self.assertEqual(ctx.findings[0].rule, "DECEPTIVE_FRAMING")
        self.assertIn("[LLM]", ctx.findings[0].message)

    def test_handles_api_error(self):
        ctx = ss.ScanContext(
            skill_dir=FIXTURES_DIR / "safe-skill",
            skill_name="safe-skill",
        )
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("API timeout")

        mock_anthropic = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}), \
             patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            ss.run_llm_checks(ctx)

        self.assertIn("LLM_API_ERROR", _rules(ctx))

    def test_handles_markdown_wrapped_json(self):
        ctx = ss.ScanContext(
            skill_dir=FIXTURES_DIR / "safe-skill",
            skill_name="safe-skill",
        )
        llm_response = '```json\n[{"severity": "WARN", "file": "SKILL.md", "line": null, "rule": "TEST", "message": "test"}]\n```'

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=llm_response)]
        mock_client.messages.create.return_value = mock_response

        mock_anthropic = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}), \
             patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            ss.run_llm_checks(ctx)

        self.assertEqual(len(ctx.findings), 1)


# -----------------------------------------------------------------------
# Integration: existing skills must pass
# -----------------------------------------------------------------------

class TestExistingSkills(unittest.TestCase):
    """Run rule-based checks against all real skills in the catalog."""

    def test_all_existing_skills_zero_blocks(self):
        """Every existing skill must produce zero BLOCK findings."""
        if not SKILLS_DIR.exists():
            self.skipTest("skills/ directory not found")

        for skill_dir in sorted(SKILLS_DIR.iterdir()):
            if not skill_dir.is_dir():
                continue
            if not (skill_dir / "SKILL.md").exists():
                continue
            with self.subTest(skill=skill_dir.name):
                ctx = ss.ScanContext(
                    skill_dir=skill_dir,
                    skill_name=skill_dir.name,
                )
                ss.run_rule_based_checks(ctx)
                block_findings = [
                    f for f in ctx.findings if f.severity == "BLOCK"
                ]
                self.assertEqual(
                    block_findings, [],
                    f"{skill_dir.name} has BLOCK findings: "
                    + ", ".join(f"{f.rule}: {f.message}" for f in block_findings)
                )

    def test_os_import_skills_produce_warn_only(self):
        """Skills with 'import os' should produce WARN, not BLOCK."""
        os_skills = [
            "product-attribute-dictionary",
            # summarize_catalog.py and summarize_metafields.py both import os
        ]
        for name in os_skills:
            skill_dir = SKILLS_DIR / name
            if not skill_dir.exists():
                continue
            with self.subTest(skill=name):
                ctx = ss.ScanContext(
                    skill_dir=skill_dir, skill_name=name,
                )
                ss.run_rule_based_checks(ctx)
                self.assertEqual(_blocks(ctx), [])
                self.assertIn("PY_DANGEROUS_IMPORT_OS", _warns(ctx))


# -----------------------------------------------------------------------
# Output formatting
# -----------------------------------------------------------------------

class TestOutputFormatting(unittest.TestCase):
    def test_format_findings_no_issues(self):
        ctx = ss.ScanContext(
            skill_dir=Path("skills/test"), skill_name="test"
        )
        output = ss.format_findings([ctx])
        self.assertIn("0 FAILED", output)
        self.assertIn("1 PASSED", output)

    def test_format_findings_with_block(self):
        ctx = ss.ScanContext(
            skill_dir=Path("skills/test"), skill_name="test"
        )
        ctx.add("BLOCK", "scripts/bad.py", 5, "PY_EVAL_EXEC", "Uses eval()")
        output = ss.format_findings([ctx])
        self.assertIn("1 FAILED", output)
        self.assertIn("PY_EVAL_EXEC", output)
        self.assertIn("BLOCK", output)


# -----------------------------------------------------------------------
# Scan context helpers
# -----------------------------------------------------------------------

class TestScanContext(unittest.TestCase):
    def test_has_blocks(self):
        ctx = ss.ScanContext(skill_dir=Path("."), skill_name="test")
        self.assertFalse(ctx.has_blocks())
        ctx.add("WARN", "f", None, "R", "m")
        self.assertFalse(ctx.has_blocks())
        ctx.add("BLOCK", "f", None, "R", "m")
        self.assertTrue(ctx.has_blocks())


if __name__ == "__main__":
    unittest.main()
