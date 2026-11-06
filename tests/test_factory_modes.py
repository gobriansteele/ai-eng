from __future__ import annotations

import json
import sys
import unittest
from copy import deepcopy
from unittest.mock import patch

import test_factory_route as route_tests
import test_factory_work as work_tests

fw = work_tests.fw


class ModeTests(unittest.TestCase):
    setUp = work_tests.WorkTests.setUp
    operation = work_tests.WorkTests.operation
    source_begin = route_tests.RouteTests.source_begin
    route_operation = route_tests.RouteTests.route_operation

    def begin(self, token="mode-run", limit=None):
        return self.store.begin("codex", 12345, token, self.fixture, limit)

    def set_mode(self, state, mode, name="set-mode"):
        evidence = self.root / (name + ".md")
        evidence.write_text(
            f"Synthetic direct instruction: run this item in {mode} mode.\n"
        )
        operation = self.operation(state, name)
        operation["item"]["execution"] = {"mode": mode, "evidence": str(evidence)}
        return self.store.save("mode-run", "codex", 12345, state["revision"], operation)

    def test_default_has_no_cap_and_old_numeric_history_stays_bounded(self):
        old = self.begin("old", 1)
        operation = self.operation(old)
        saved = self.store.save("old", "codex", 12345, old["revision"], operation)
        with self.assertRaisesRegex(fw.WorkError, "step limit"):
            self.store.save(
                "old",
                "codex",
                12345,
                saved["revision"],
                self.operation(saved, "too-many"),
            )
        self.store.finish("old", "codex", 12345, "step_limit")
        state = self.store.begin("claude-code", 12345, "uncapped", None)
        self.assertIsNone(state["invocations"][-1]["max_steps"])
        for index in range(12):
            state = self.store.save(
                "uncapped",
                "claude-code",
                12345,
                state["revision"],
                self.operation(state, f"transition-{index}"),
            )
        self.assertEqual(state["invocations"][0]["max_steps"], 1)
        self.assertEqual(state["invocations"][-1]["steps"], 12)
        self.assertEqual(self.store.read(), state)
        with self.assertRaisesRegex(fw.WorkError, "different inputs"):
            self.store.begin("claude-code", 12345, "uncapped", None, 3)

    def test_cli_limits_are_optional_and_explicit_limits_are_preserved(self):
        prefix = [
            "factory_work.py",
            "begin",
            "--config",
            str(self.config),
            "--harness",
            "codex",
        ]
        for options, expected in (
            ([], None),
            (["--single-step"], 1),
            (["--max-steps", "20"], 20),
        ):
            with (
                self.subTest(options=options),
                patch.object(sys, "argv", prefix + options),
            ):
                self.assertEqual(fw.parse_arguments().max_steps, expected)
        for limit in (0, -1, True):
            with self.subTest(limit=limit), self.assertRaises(fw.WorkError):
                self.begin(limit=limit)
        self.assertIsNone(self.store.read())

    def test_mode_persists_across_hosts_without_changing_other_fields(self):
        state = self.set_mode(self.begin(), "bedtime")
        item = deepcopy(work_tests.current(state))
        self.store.finish("mode-run", "codex", 12345, "stopped")
        resumed = self.store.begin("claude-code", 12345, "resume", None)
        self.assertEqual(work_tests.current(resumed), item)
        self.assertEqual(work_tests.current(resumed)["execution"]["mode"], "bedtime")
        self.assertIsNone(resumed["invocations"][-1]["max_steps"])

    def test_mode_changes_require_new_readable_evidence(self):
        state = self.set_mode(self.begin(), "restricted")
        before = self.store.path.read_bytes()
        for change in ("remove", "reuse-report", "missing-report", "invalid-mode"):
            operation = self.operation(state, change)
            policy = operation["item"]["execution"]
            if change == "remove":
                operation["item"].pop("execution")
            elif change == "reuse-report":
                policy["mode"] = "bedtime"
            elif change == "missing-report":
                policy.update(mode="bedtime", evidence=str(self.root / "missing.md"))
            else:
                policy["mode"] = "whatever"
            with (
                self.subTest(change=change),
                self.assertRaises((fw.WorkError, OSError)),
            ):
                self.store.save(
                    "mode-run", "codex", 12345, state["revision"], operation
                )
            self.assertEqual(self.store.path.read_bytes(), before)
        changed = self.set_mode(state, "bedtime", "explicit-delegation")
        self.assertEqual(work_tests.current(changed)["execution"]["mode"], "bedtime")
        self.assertEqual(changed["events"][: len(state["events"])], state["events"])

    def test_productive_fixes_continue_and_restricted_downgrade_keeps_count(self):
        state = self.set_mode(self.begin(), "default")
        for count in (2, 3, 4):
            operation = self.operation(state, f"fix-{count}")
            operation["item"]["fix_rounds"] = count
            state = self.store.save(
                "mode-run", "codex", 12345, state["revision"], operation
            )
        self.assertEqual(work_tests.current(self.store.read())["fix_rounds"], 4)
        state = self.set_mode(state, "restricted", "restrict-now")
        operation = self.operation(state, "fix-5")
        operation["item"]["fix_rounds"] = 5
        with self.assertRaisesRegex(fw.WorkError, "at most two"):
            self.store.save("mode-run", "codex", 12345, state["revision"], operation)
        self.assertEqual(work_tests.current(self.store.read())["fix_rounds"], 4)

    def test_routing_cannot_delegate_to_pending_items_or_change_existing_mode(self):
        state = self.source_begin()
        operation = self.route_operation(state, count=2)
        evidence = self.root / "execution.md"
        evidence.write_text(
            "Synthetic scoped bedtime delegation for selected item only"
        )
        for updated in operation["items"]:
            updated["execution"] = {"mode": "bedtime", "evidence": str(evidence)}
        with self.assertRaisesRegex(fw.WorkError, "selected item"):
            self.store.route("source-run", "codex", 12345, state["revision"], operation)
        operation["items"][1].pop("execution")
        routed = self.store.route(
            "source-run", "codex", 12345, state["revision"], operation
        )
        self.assertNotIn("execution", routed["items"][operation["items"][1]["id"]])
        self.store.finish("source-run", "codex", 12345, "stopped")
        related = self.source_begin("related-thread", "related")
        operation = self.route_operation(related, existing=routed["active_item_id"])
        evidence2 = self.root / "different.md"
        evidence2.write_text("Different report")
        operation["items"][0]["execution"] = {
            "mode": "default",
            "evidence": str(evidence2),
        }
        with self.assertRaisesRegex(fw.WorkError, "Routing cannot change"):
            self.store.route("related", "codex", 12345, related["revision"], operation)

    def test_completion_requires_done_item_and_reconciled_publication(self):
        state = self.begin()
        with self.assertRaisesRegex(fw.WorkError, "Completion requires"):
            self.store.finish("mode-run", "codex", 12345, "completed")
        operation = self.operation(state, "verified-pr")
        operation["item"].update(stage="follow_pr", status="done", required_role=None)
        operation["item"]["code"]["pr_url"] = "https://example.invalid/pull/1"
        state = self.store.save(
            "mode-run", "codex", 12345, state["revision"], operation
        )
        with self.assertRaisesRegex(fw.WorkError, "Completion requires"):
            self.store.finish("mode-run", "codex", 12345, "completed")
        evidence = self.root / "publication.md"
        evidence.write_text("Synthetic publication observations for reconciliation")
        action = deepcopy(work_tests.current(state)["pending_actions"][0])
        action.update(status="uncertain", evidence=str(evidence))
        for status in ("uncertain", "confirmed"):
            action["status"] = status
            if status == "confirmed":
                action.update(
                    returned_id="1", returned_url="https://example.invalid/pull/1"
                )
            state = self.store.reconcile(
                "mode-run",
                "codex",
                12345,
                state["revision"],
                {
                    "id": status,
                    "reason": "Synthetic observation",
                    "item_id": state["active_item_id"],
                    "action": action,
                },
            )
        finished = self.store.finish("mode-run", "codex", 12345, "completed")
        self.assertIsNone(finished["active_run"])
        self.assertEqual(finished["invocations"][-1]["outcome"], "completed")
        self.assertEqual(
            self.store.finish("mode-run", "codex", 12345, "completed"), finished
        )
        self.assertEqual(
            json.loads(self.store.path.read_text())["items"], state["items"]
        )
