"""Boundaries that keep skill evaluations private and catch unauthorized edits."""
import importlib.util
import pathlib
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("eval_runner", pathlib.Path(__file__).parents[1] / "evals/run.py")
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class EvaluationBoundaryTests(unittest.TestCase):
    def test_case_git_root_cannot_resolve_to_a_parent_repository(self):
        runner.RUNS.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=runner.RUNS) as tmp:
            work = pathlib.Path(tmp) / "repo"
            runner.prepare({"id": "git-root-unit"}, work)
            top = subprocess.check_output(["git", "-C", str(work), "rev-parse", "--show-toplevel"], text=True).strip()
            self.assertEqual(pathlib.Path(top).resolve(), work.resolve())
            self.assertFalse(any(p.startswith(".git/") for p in runner.snapshot(work)))

    def test_privacy_read_fails_even_when_no_file_was_changed(self):
        import json
        exp = {"codex_no_read_paths": ["brain/"]}
        for command in ("rtk read AGENTS.md brain/index.md", "cat '/copy/brain/accounts/a.md'", "cd brain && cat index.md"):
            with self.subTest(command=command):
                events = json.dumps({"type": "item.completed", "item": {"type": "command_execution", "command": command}})
                self.assertTrue(runner.check_codex_reads(exp, events))
        events = json.dumps({"type": "item.completed", "item": {"type": "command_execution", "command": "cat skills/follow-through/SKILL.md"}})
        self.assertEqual(runner.check_codex_reads(exp, events), [])
        for command in ("/bin/zsh -lc \"rg --files -g '!brain/**'\"", "rg --files --glob=!**/brain/**"):
            events = json.dumps({"item": {"command": command}})
            self.assertEqual(runner.check_codex_reads(exp, events), [])
        events = json.dumps({"item": {"command": "rg data brain/ --glob=!brain/private/**"}})
        self.assertTrue(runner.check_codex_reads(exp, events))

    def test_nested_private_records_and_feedback_do_not_reach_case(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            note = root / "brain/decisions/follow-through/call.md"
            note.parent.mkdir(parents=True)
            note.write_text("private call")
            (root / "brain/corrections.md").write_text("private feedback")
            runner.clear_private(root)
            self.assertFalse(note.exists())
            self.assertFalse((root / "brain/corrections.md").exists())

    def test_change_records_and_readbacks_do_not_reach_case(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            private = ("brain/changes/2026-10-01-real.md", "brain/readbacks/2026-11-01-real.md",
                       "brain/readbacks/2026/customer.md", "brain/changes/old/README.md")
            for rel in ("brain/changes/README.md", "brain/readbacks/README.md") + private:
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / rel).write_text("x")
            runner.clear_private(root)
            for rel in private:
                self.assertFalse((root / rel).exists(), rel)
            self.assertTrue((root / "brain/changes/README.md").exists())
            self.assertTrue((root / "brain/readbacks/README.md").exists())

    def test_outside_links_become_copies_and_inside_links_stay(self):
        with tempfile.TemporaryDirectory() as tmp:
            outside = pathlib.Path(tmp) / "outside"
            outside.mkdir()
            (outside / "contacts.csv").write_text("real")
            work = pathlib.Path(tmp) / "work"
            (work / "brain/crm-export").mkdir(parents=True)
            (work / "brain/crm-export/contacts.csv").symlink_to(outside / "contacts.csv")
            (work / "brain/linked").symlink_to(outside, target_is_directory=True)
            (work / "brain/inside.md").write_text("in")
            (work / "brain/alias.md").symlink_to(work / "brain/inside.md")
            runner.localize_links(work)
            runner.clear_private(work)
            self.assertFalse((work / "brain/crm-export/contacts.csv").is_symlink())
            self.assertFalse((work / "brain/linked").is_symlink())
            self.assertEqual((work / "brain/linked/contacts.csv").read_text(), "real")
            self.assertEqual((outside / "contacts.csv").read_text(), "real")
            self.assertTrue((work / "brain/alias.md").is_symlink())

    def test_claude_may_run_only_the_named_scripts(self):
        cmd = runner.command("claude", "Run.", None, pathlib.Path("final.txt"))
        tools = cmd[cmd.index("--allowedTools") + 1].split(",")
        self.assertIn("Bash(python3 scripts/readback_count.py:*)", tools)
        self.assertEqual([t for t in tools if t.startswith("Bash(") and "readback" not in t
                          and "content_checks" not in t and "panel_run.py --canned" not in t], [])

    def test_no_brain_case_actually_removes_base_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = pathlib.Path(tmp) / "repo"
            runner.prepare({"id": "no-brain-unit", "no_brain": True}, work)
            self.assertFalse((work / "brain").exists())
            self.assertTrue((work / "AGENTS.md").exists())

    def test_verdict_and_outcome_require_both_permissions_and_preserve_body(self):
        name = "brain/decisions/follow-through/call.md"
        old = b"---\nstatus: proposed\napproved_by:\nverdict_reason:\nverdict_date:\n---\n## Recap\nKeep this.\n## outcome_log\n"
        new = old.replace(b"status: proposed", b"status: approved") + b"- 2026-10-25: Sam reported a reply.\n"
        for permissions, allowed in [({"verdict_files": [name], "append_only": [name]}, True),
                                     ({"verdict_files": [name]}, False), ({"append_only": [name]}, False)]:
            with self.subTest(permissions=permissions):
                failures = runner.check({"expect": permissions}, {name: old}, {name: new}, "")
                self.assertEqual(not failures, allowed)
        bad = new.replace(b"Keep this.", b"Changed the approved draft.")
        self.assertTrue(runner.check({"expect": {"verdict_files": [name], "append_only": [name]}},
                                     {name: old}, {name: bad}, ""))

    def test_dry_run_prepares_without_invoking_a_model(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(runner, "RUNS", pathlib.Path(tmp)):
            with patch.object(runner.subprocess, "run") as invoke:
                _, failures, saved = runner.run({"id": "dry-unit", "request": "Run start-here.",
                                                 "today": "2026-10-25", "expect": {}},
                                                None, True, "codex", True)
                self.assertEqual(failures, [])
                invoke.assert_not_called()
                self.assertTrue((saved / "command.json").exists())

    def test_codex_uses_final_message_and_does_not_start_claude(self):
        def invoke(cmd, **kwargs):
            self.assertEqual(cmd[:2], ["codex", "exec"])
            self.assertIn("workspace-write", cmd)
            self.assertNotIn("TYPESAFE_API_KEY", kwargs["env"])
            self.assertNotIn("features.hooks=false", cmd)
            pathlib.Path(cmd[cmd.index("-o") + 1]).write_text("Ready draft")
            return subprocess.CompletedProcess(cmd, 0, "event stream without final answer", "")

        with tempfile.TemporaryDirectory() as tmp, patch.object(runner, "RUNS", pathlib.Path(tmp)):
            with patch.object(runner.subprocess, "run", side_effect=invoke):
                _, failures, _ = runner.run({"id": "codex-unit", "request": "Draft.", "today": "2026-10-25",
                                             "expect": {"output_has": ["Ready draft"]}}, None, False, "codex")
                self.assertEqual(failures, [])

    def test_default_engine_still_selects_claude(self):
        def invoke(cmd, **kwargs):
            self.assertEqual(cmd[:2], ["claude", "-p"])
            self.assertIn("claude-sonnet-5-5", cmd)
            return subprocess.CompletedProcess(cmd, 0, "OK", "")

        with tempfile.TemporaryDirectory() as tmp, patch.object(runner, "RUNS", pathlib.Path(tmp)):
            with patch.object(runner.subprocess, "run", side_effect=invoke):
                _, failures, _ = runner.run({"id": "claude-unit", "request": "Draft.", "today": "2026-10-25",
                                             "expect": {"output_has": ["OK"]}}, None, False)
                self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
