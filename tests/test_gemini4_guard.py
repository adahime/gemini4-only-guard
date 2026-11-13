#!/usr/bin/env python3
"""Unit tests for scripts/gemini4_guard.py."""

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "gemini4_guard.py"


def run_hook(payload: dict) -> dict:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(proc.stdout.strip())


class Gemini4GuardTests(unittest.TestCase):
    def test_swarm_add_omitted_model_denied(self) -> None:
        res = run_hook({"toolCall": {"name": "swarm", "args": {"action": "add", "name": "w1", "brief": "x"}}})
        self.assertEqual(res["decision"], "deny")

    def test_swarm_non_gemini4_models_denied(self) -> None:
        for model in (
            "gemini-3.8-flash-medium",
            "Gemini 3.8 Flash (High)",
            "claude-sonnet-5-5-medium",
            "gpt-oss-120b-medium",
            "gemini-flash-worker-agy",
            "gemini-pro-orchestrator-g1-pro",
        ):
            for action in ("add", "model"):
                res = run_hook({"toolCall": {"name": "swarm", "args": {"action": action, "name": "w1", "model": model}}})
                self.assertEqual(res["decision"], "deny", msg=f"Expected deny for {action} {model}")

    def test_swarm_gemini4_models_allowed(self) -> None:
        for model in (
            "gemini-4-argon-high",
            "gemini-4-argon-medium",
            "gemini-4-hydrogen-xhigh",
            "Gemini 4 Hydrogen (High)",
        ):
            res = run_hook({"toolCall": {"name": "swarm", "args": {"action": "add", "name": "w1", "model": model}}})
            self.assertEqual(res["decision"], "allow", msg=f"Expected allow for {model}")

    def test_swarm_management_actions_allowed(self) -> None:
        for action in ("status", "models", "kill", "title"):
            res = run_hook({"toolCall": {"name": "swarm", "args": {"action": action}}})
            self.assertEqual(res["decision"], "allow")

    def test_subagent_flash_denied_inherit_pro_allowed(self) -> None:
        for tier in ("flash", "flash_lite"):
            res = run_hook({"toolCall": {"name": "invoke_subagent", "args": {"TypeName": "browser", "Model": tier}}})
            self.assertEqual(res["decision"], "deny")
        for tier in ("inherit", "pro"):
            res = run_hook({"toolCall": {"name": "invoke_subagent", "args": {"TypeName": "research", "Model": tier}}})
            self.assertEqual(res["decision"], "allow")
        res_default = run_hook({"toolCall": {"name": "invoke_subagent", "args": {"TypeName": "research"}}})
        self.assertEqual(res_default["decision"], "allow")


if __name__ == "__main__":
    unittest.main(verbosity=2)
