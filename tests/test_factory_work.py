from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "plugins/factory/scripts"))
fw = importlib.import_module("factory_work")


def current(state):
    return state["items"][state["active_item_id"]]


class WorkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.config = self.root / "config.yaml"
        data = yaml.safe_load((ROOT / "config/example.yaml").read_text())
        data["schema_version"] = 1
        data["limits"]["active_work_items"] = 1
        data["repositories"] = {"roots": [], "paths": []}
        self.config.write_text(yaml.safe_dump(data))
        self.store = fw.Store(self.config)
        self.fixture = ROOT / "plugins/factory/fixtures/synthetic-resume.json"
        self.identity = {
            "pid": 12345,
            "started_at": "synthetic-owner-start",
            "executable": "/synthetic/codex",
        }
        self.owner_patch = patch.object(fw, "verify_owner", return_value=self.identity)
        self.owner_patch.start()
        self.addCleanup(self.owner_patch.stop)
        self.fingerprint = patch.object(
            fw, "plugin_identity", return_value=("0.2.3", "synthetic-fingerprint")
        )
        self.fingerprint.start()
        self.addCleanup(self.fingerprint.stop)

    def begin(self, token="run-one", harness="codex", fixture=True, limit=3):
        return self.store.begin(
            harness, 12345, token, self.fixture if fixture else None, limit
        )

    def operation(self, state, name="choose-route"):
        updated = deepcopy(current(state))
        updated.update(
            stage="route",
            status="blocked",
            required_role="factory-route",
            next_action="Implement factory-route before continuing",
        )
        return {
            "id": name,
            "reason": "Synthetic role availability decision",
            "item": updated,
        }

    def save(self, state, name="choose-route", token="run-one", harness="codex"):
        return self.store.save(
            token, harness, 12345, state["revision"], self.operation(state, name)
        )

    def test_duplicate_fixture_and_two_direction_handoff_preserve_state(self):
        for first, second in (("codex", "claude-code"), ("claude-code", "codex")):
            with self.subTest(first=first):
                if self.store.path.exists():
                    self.store.path.unlink()
                cursors = self.store.runtime / "state/cursors.json"
                cursors.parent.mkdir(parents=True, exist_ok=True)
                cursors.write_text('{"synthetic:C_ONE":"unaltered"}')
                starts = self.store.runtime / "setup/example/channel-starts.json"
                starts.parent.mkdir(parents=True, exist_ok=True)
                starts.write_text('{"synthetic:C_ONE":"synthetic-start"}')
                initial = self.begin(harness=first)
                saved = self.save(initial, harness=first)
                self.store.finish("run-one", first, 12345, "blocked")
                resumed = self.begin("run-two", second)
                self.assertEqual(current(resumed), current(saved))
                self.assertEqual(
                    resumed["synthetic_cursors"], initial["synthetic_cursors"]
                )
                self.assertEqual(current(resumed)["fix_rounds"], 1)
                self.assertEqual(
                    current(resumed)["approvals"], current(initial)["approvals"]
                )
                self.assertEqual(
                    current(resumed)["pending_actions"],
                    current(initial)["pending_actions"],
                )
                self.assertEqual(cursors.read_text(), '{"synthetic:C_ONE":"unaltered"}')
                self.assertEqual(
                    starts.read_text(), '{"synthetic:C_ONE":"synthetic-start"}'
                )
                self.assertEqual(
                    sum(e["kind"] == "decision" for e in resumed["events"]), 1
                )
                self.store.finish("run-two", second, 12345, "blocked")

    def test_one_invocation_blocks_live_and_unknown_owner_and_checks_identity(self):
        initial = self.begin()
        for effect in (True, fw.WorkError("unknown")):
            with patch.object(
                fw,
                "owner_alive",
                side_effect=effect if isinstance(effect, Exception) else None,
                return_value=effect,
            ):
                with self.assertRaises(fw.WorkError):
                    self.begin("run-two")
        self.assertEqual(self.store.read(), initial)
        with patch.object(
            fw, "verify_owner", return_value={**self.identity, "pid": 54321}
        ):
            with self.assertRaisesRegex(fw.WorkError, "different owner"):
                self.save(initial)

    def test_verified_dead_owner_takeover_keeps_saved_transition(self):
        saved = self.save(self.begin())
        with patch.object(fw, "owner_alive", return_value=False):
            resumed = self.begin("run-two", "claude-code", fixture=False)
        self.assertEqual(current(resumed), current(saved))
        self.assertEqual(resumed["invocations"][0]["outcome"], "interrupted_owner_dead")
        self.assertEqual(resumed["active_run"], "run-two")
        self.assertEqual(sum(e["kind"] == "decision" for e in resumed["events"]), 1)

    def test_atomic_failure_before_replace_leaves_complete_prior_snapshot(self):
        initial = self.begin()
        original = self.store.path.read_bytes()
        with patch.object(
            fw.os, "replace", side_effect=OSError("injected before replacement")
        ):
            with self.assertRaises(OSError):
                self.save(initial)
        self.assertEqual(self.store.path.read_bytes(), original)
        self.assertEqual(self.store.read(), initial)
        self.assertEqual(
            list(self.store.path.parent.glob(".work.*")),
            [self.store.path.parent / ".work.mutex"],
        )

    def test_after_replace_lost_reply_retries_once_without_replaying_step(self):
        initial = self.begin(limit=1)
        real_fsync = os.fsync
        calls = 0

        def fail_directory_sync(fd):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("injected after replace")
            real_fsync(fd)

        with patch.object(fw.os, "fsync", side_effect=fail_directory_sync):
            with self.assertRaises(OSError):
                self.save(initial)
        committed = self.store.read()
        retried = self.save(initial)
        self.assertEqual(retried, committed)
        self.assertEqual(retried["invocations"][0]["steps"], 1)
        self.assertEqual(sum(e["kind"] == "decision" for e in retried["events"]), 1)
        self.assertEqual(self.begin(limit=1), committed)
        finished = self.store.finish("run-one", "codex", 12345, "blocked")
        self.assertEqual(
            self.store.finish("run-one", "codex", 12345, "blocked"), finished
        )
        self.assertEqual(self.begin(limit=1), finished)

    def test_corruption_requests_repair_without_reset(self):
        self.begin()
        for corrupt in (
            "broken",
            '{"schema_version":1,"schema_version":1}',
            '{"schema_version":99}',
        ):
            self.store.path.write_text(corrupt)
            with self.assertRaisesRegex(fw.WorkError, "repair"):
                self.begin("run-two")
            self.assertEqual(self.store.path.read_text(), corrupt)

    def test_semantic_history_corruption_and_missing_fields_refused(self):
        initial = self.begin()
        for mutate in (
            lambda s: current(s).update(fix_rounds=0),
            lambda s: s.update(revision=19),
            lambda s: s["invocations"][0].update(steps=1),
            lambda s: current(s).pop("approvals"),
        ):
            bad = deepcopy(initial)
            mutate(bad)
            self.store.path.write_text(json.dumps(bad))
            with self.assertRaisesRegex(fw.WorkError, "repair"):
                self.store.read()

    def test_bounds_revision_fix_round_and_scoped_records_preserved(self):
        initial = self.begin(limit=1)
        for key, value in (
            ("fix_rounds", 0),
            ("fix_rounds", 3),
            ("approvals", []),
            ("pending_actions", []),
            ("source_links", []),
        ):
            operation = self.operation(initial)
            operation["item"][key] = value
            with self.assertRaises((fw.WorkError, fw.ConfigError)):
                self.store.save(
                    "run-one", "codex", 12345, initial["revision"], operation
                )
        with self.assertRaisesRegex(fw.WorkError, "Revision"):
            self.store.save("run-one", "codex", 12345, 0, self.operation(initial))
        saved = self.save(initial)
        with self.assertRaisesRegex(fw.WorkError, "step limit"):
            self.save(saved, "second-decision")
        conflicting = self.operation(saved)
        conflicting["reason"] = "Different input"
        with self.assertRaisesRegex(fw.WorkError, "different content"):
            self.store.save("run-one", "codex", 12345, saved["revision"], conflicting)
        self.assertEqual(self.store.read(), saved)

    def test_fixture_identity_not_file_name_and_no_reinitialization(self):
        initial = self.begin()
        saved = self.save(initial)
        self.store.finish("run-one", "codex", 12345, "blocked")
        incoming = json.loads(self.fixture.read_text())
        incoming["item"]["fix_rounds"] = 0
        changed = self.root / "same-input-new-path.json"
        changed.write_text(json.dumps(incoming))
        resumed = self.store.begin("claude-code", 12345, "run-two", changed)
        self.assertEqual(current(resumed), current(saved))
        self.store.finish("run-two", "claude-code", 12345, "blocked")
        incoming["item"]["source_id"] = "synthetic:other"
        changed.write_text(json.dumps(incoming))
        with self.assertRaisesRegex(fw.WorkError, "One active item"):
            self.store.begin("codex", 12345, "run-three", changed)

    def test_config_change_and_cross_config_runtime_reuse_refused(self):
        initial = self.begin()
        config = yaml.safe_load(self.config.read_text())
        config["jira"]["project_key"] = "OTHER"
        self.config.write_text(yaml.safe_dump(config))
        changed_store = fw.Store(self.config)
        with self.assertRaisesRegex(fw.WorkError, "changed during"):
            changed_store.save(
                "run-one", "codex", 12345, initial["revision"], self.operation(initial)
            )
        other = self.root / "other.yaml"
        other.write_text(self.config.read_text())
        with self.assertRaisesRegex(fw.WorkError, "different config"):
            fw.Store(other).read()

    def test_pid_identity_death_and_unknown_are_distinct(self):
        with patch.object(fw, "process", return_value=None):
            self.assertFalse(fw.owner_alive(self.identity))
        with patch.object(
            fw,
            "process",
            return_value=({**self.identity, "started_at": "reused"}, 1, "codex"),
        ):
            self.assertFalse(fw.owner_alive(self.identity))
        with patch.object(fw.os, "kill", side_effect=PermissionError):
            with self.assertRaisesRegex(fw.WorkError, "unknown"):
                fw.process(12345)
        with (
            patch.object(fw.os, "kill"),
            patch.object(fw.subprocess, "run", side_effect=OSError("sandbox")),
        ):
            with self.assertRaisesRegex(fw.WorkError, "unknown"):
                fw.process(12345)

    def test_desktop_appserver_and_nonancestor_rejected(self):
        self.owner_patch.stop()
        with (
            patch.object(fw.os, "getppid", return_value=12345),
            patch.object(
                fw, "process", return_value=(self.identity, 1, "codex app-server")
            ),
        ):
            self.assertEqual(fw.owners("codex"), [])
            with self.assertRaisesRegex(fw.WorkError, "desktop"):
                fw.verify_owner(12345, "codex")
        with (
            patch.object(fw.os, "getppid", return_value=12345),
            patch.object(
                fw, "process", return_value=(self.identity, 1, "codex exec -")
            ),
        ):
            self.assertEqual(fw.verify_owner(12345, "codex"), self.identity)
            with self.assertRaises(fw.WorkError):
                fw.verify_owner(54321, "codex")

    def test_only_nearest_matching_cli_can_own_invocation(self):
        self.owner_patch.stop()
        outer = {**self.identity, "pid": 54321}
        with (
            patch.object(fw.os, "getppid", return_value=12345),
            patch.object(
                fw, "process", side_effect=[(self.identity, 54321, "codex exec -")]
            ),
        ):
            self.assertEqual(fw.owners("codex"), [self.identity])
        with (
            patch.object(fw.os, "getppid", return_value=12345),
            patch.object(
                fw, "process", return_value=(self.identity, 54321, "codex exec -")
            ),
        ):
            with self.assertRaises(fw.WorkError):
                fw.verify_owner(outer["pid"], "codex")

    def test_appserver_word_in_cli_prompt_is_not_a_service(self):
        for command in (
            "/synthetic/codex exec discuss app-server now",
            "/synthetic/codex --config features.foo=true exec discuss app-server",
        ):
            self.assertTrue(fw.cli_command(self.identity, command, "codex"))
        self.assertFalse(
            fw.cli_command(
                self.identity,
                "/synthetic/codex --config features.foo=true app-server",
                "codex",
            )
        )
        self.assertFalse(
            fw.cli_command(
                self.identity, "/synthetic/codex --unknown app-server", "codex"
            )
        )
        self.assertTrue(
            fw.cli_command(
                {**self.identity, "executable": "/synthetic/claude"},
                "/synthetic/claude -p discuss app-server",
                "claude-code",
            )
        )

    def test_real_process_lock_excludes_another_mutator(self):
        self.begin()
        mutex = self.store.path.parent / ".work.mutex"
        code = "import fcntl,sys; f=open(sys.argv[1], 'a+'); fcntl.flock(f, fcntl.LOCK_EX); print('locked', flush=True); sys.stdin.read()"
        with subprocess.Popen(
            [sys.executable, "-c", code, str(mutex)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        ) as child:
            try:
                self.assertEqual(child.stdout.readline().strip(), "locked")
                with self.assertRaisesRegex(fw.WorkError, "Concurrent"):
                    with self.store.mutation():
                        self.fail("mutex incorrectly admitted two processes")
            finally:
                child.communicate("release", timeout=5)
        with self.store.mutation():
            self.assertIsNotNone(self.store.read())

    def test_real_process_death_is_required_for_takeover(self):
        with subprocess.Popen(
            [sys.executable, "-c", "import sys; sys.stdin.read()"],
            stdin=subprocess.PIPE,
        ) as child:
            try:
                info = fw.process(child.pid)
                self.assertIsNotNone(info)
                identity = info[0]
                self.assertTrue(fw.owner_alive(identity))
            finally:
                child.terminate()
                child.wait(timeout=5)
        self.assertFalse(fw.owner_alive(identity))

    def test_process_identity_is_stable_across_ambient_locale_and_timezone(self):
        first = fw.process(os.getpid())
        with patch.dict(
            os.environ, {"LC_ALL": "invalid-locale-for-test", "TZ": "Pacific/Auckland"}
        ):
            second = fw.process(os.getpid())
        self.assertEqual(first, second)

    def test_fix_round_increment_is_preserved_across_invocations(self):
        initial = self.begin()
        operation = self.operation(initial)
        operation["item"]["fix_rounds"] = 2
        saved = self.store.save(
            "run-one", "codex", 12345, initial["revision"], operation
        )
        self.store.finish("run-one", "codex", 12345, "blocked")
        resumed = self.begin("run-two", "claude-code", fixture=False)
        self.assertEqual(current(resumed)["fix_rounds"], 2)
        self.assertEqual(current(saved), current(resumed))

    def test_legacy_schema_one_rejects_duplicate_decision_ids(self):
        state = self.save(self.begin(), "first")
        state = self.save(state, "second")
        legacy = {
            k: deepcopy(state[k])
            for k in (
                "config_path",
                "factory_id",
                "revision",
                "active_run",
                "synthetic_cursors",
                "invocations",
                "events",
            )
        }
        legacy.update(schema_version=1, item=deepcopy(current(state)))
        for event in legacy["events"]:
            event.pop("change")
        self.assertEqual(fw.snapshot(legacy)["schema_version"], 1)
        legacy["events"][-1]["decision"]["id"] = "first"
        with self.assertRaisesRegex(fw.WorkError, "identity/history"):
            fw.snapshot(legacy)

    def reconciliation(self, state, status="uncertain", name="attempt-pr"):
        action = deepcopy(current(state)["pending_actions"][0])
        report = self.root / (name + ".md")
        report.write_text("Synthetic observed evidence; no actual external action.")
        action.update(status=status, evidence=str(report))
        if status == "confirmed":
            action.update(
                returned_id="17", returned_url="https://example.invalid/pr/17"
            )
        return {
            "id": name,
            "reason": "Synthetic reconciliation",
            "item_id": current(state)["id"],
            "action": action,
        }

    def reconcile(
        self,
        state,
        status="uncertain",
        name="attempt-pr",
        token="run-one",
        harness="codex",
    ):
        return self.store.reconcile(
            token,
            harness,
            12345,
            state["revision"],
            self.reconciliation(state, status, name),
        )

    def post_fixture(self, target, action="posts"):
        raw = json.loads(self.fixture.read_text())
        post_scope = {
            "action": action,
            "target": target,
            "revision": "payload-sha256=synthetic-content status-sha256=synthetic-observation",
        }
        raw["item"]["approvals"][0]["scope"] = post_scope
        raw["item"]["pending_actions"][0]["scope"] = post_scope
        raw["item"].update(
            stage="investigate",
            status="blocked",
            required_role="factory-investigate",
            next_action="Supply the missing supported environment",
        )
        self.fixture = self.root / "post-fixture.json"
        self.fixture.write_text(json.dumps(raw))
        return self.begin()

    def test_post_reconciliation_preserves_engineering_state_and_cross_host_history(
        self,
    ):
        initial = self.post_fixture(
            "slack:T_SYNTHETIC/C_ORIGIN/1700000000.000000:thread_reply"
        )
        before = deepcopy(current(initial))
        uncertain = self.reconcile(initial)
        self.store.finish("run-one", "codex", 12345, "stopped")
        resumed = self.begin("run-two", "claude-code", fixture=False)
        confirmed = self.reconcile(
            resumed, "confirmed", "confirm-post", "run-two", "claude-code"
        )
        after = deepcopy(current(confirmed))
        after["pending_actions"] = before["pending_actions"]
        self.assertEqual(after, before)
        self.assertEqual(
            confirmed["events"][: len(initial["events"])], initial["events"]
        )
        self.assertEqual(uncertain["invocations"][0]["steps"], 1)
        self.assertEqual(confirmed["invocations"][-1]["steps"], 1)
        self.assertEqual(self.store.read(), confirmed)

    def test_jira_post_scope_cannot_change_operation_destination_or_payload(self):
        initial = self.post_fixture("jira:https://example.invalid/jira/SYN-12:comment")
        for target, revision in (
            (
                "jira:https://example.invalid/jira/SYN-12:transition",
                current(initial)["pending_actions"][0]["scope"]["revision"],
            ),
            (
                "jira:https://example.invalid/jira/SYN-13:comment",
                current(initial)["pending_actions"][0]["scope"]["revision"],
            ),
            (
                current(initial)["pending_actions"][0]["scope"]["target"],
                "payload-sha256=changed status-sha256=synthetic-observation",
            ),
        ):
            op = self.reconciliation(initial)
            op["action"]["scope"].update(target=target, revision=revision)
            with self.assertRaisesRegex(fw.WorkError, "scope"):
                self.store.reconcile("run-one", "codex", 12345, initial["revision"], op)
        uncertain = self.reconcile(initial)
        confirmed = self.reconcile(uncertain, "confirmed", "confirm-jira-comment")
        self.assertEqual(
            current(confirmed)["pending_actions"][0]["scope"]["action"], "posts"
        )
        self.assertEqual(self.store.read(), confirmed)

    def test_ticket_reconciliation_survives_cross_host_resume_without_replay(self):
        initial = self.post_fixture(
            "jira:https://example.invalid/jira/SYN-12:transition:31", "tickets"
        )
        before = deepcopy(current(initial))
        uncertain = self.reconcile(initial)
        self.assertEqual(
            self.store.reconcile(
                "run-one", "codex", 12345, 0, self.reconciliation(initial)
            ),
            uncertain,
        )
        self.store.finish("run-one", "codex", 12345, "stopped")
        resumed = self.begin("run-two", "claude-code", fixture=False)
        confirmed = self.reconcile(
            resumed, "confirmed", "confirm-ticket", "run-two", "claude-code"
        )
        after = deepcopy(current(confirmed))
        after["pending_actions"] = before["pending_actions"]
        self.assertEqual(after, before)
        self.assertEqual(
            current(confirmed)["pending_actions"][0]["scope"],
            before["pending_actions"][0]["scope"],
        )
        with self.assertRaisesRegex(fw.WorkError, "transition"):
            self.reconcile(
                confirmed, "proposed", "replay-ticket", "run-two", "claude-code"
            )
        self.assertEqual(self.store.read(), confirmed)

    def test_ticket_reconciliation_requires_unchanged_scope_and_matching_approval(self):
        initial = self.post_fixture(
            "jira:https://example.invalid/jira/SYN-12:fields", "tickets"
        )
        for changes in (
            {"action": "posts"},
            {"target": "jira:https://other.invalid/jira/SYN-12:fields"},
            {"target": "jira:https://example.invalid/jira/SYN-13:fields"},
            {"target": "jira:https://example.invalid/jira/SYN-12:transition:31"},
            {"revision": "different-payload"},
        ):
            with self.subTest(changes=changes):
                op = self.reconciliation(initial)
                op["action"]["scope"].update(changes)
                with self.assertRaisesRegex(fw.WorkError, "scope"):
                    self.store.reconcile(
                        "run-one", "codex", 12345, initial["revision"], op
                    )
                self.assertEqual(self.store.read(), initial)
        items = deepcopy(initial["items"])
        items[current(initial)["id"]]["approvals"] = []
        with self.assertRaisesRegex(fw.WorkError, "matching saved approval"):
            fw.apply_reconciliation(
                items, initial["active_item_id"], self.reconciliation(initial)
            )
        self.assertEqual(self.store.read(), initial)
        uncertain = self.reconcile(initial)
        confirmed = self.reconcile(uncertain, "confirmed", "confirm-fields")
        self.assertEqual(
            current(confirmed)["pending_actions"][0]["scope"]["action"], "tickets"
        )

    def test_confirmed_ticket_fields_do_not_confirm_a_separate_transition(self):
        initial = self.post_fixture(
            "jira:https://example.invalid/jira/SYN-12:fields", "tickets"
        )
        updated = deepcopy(current(initial))
        report = self.root / "transition-request.md"
        report.write_text("Synthetic scoped transition request and authorization")
        transition = deepcopy(updated["pending_actions"][0])
        transition.update(id="ticket-transition", evidence=str(report))
        transition["scope"]["target"] = (
            "jira:https://example.invalid/jira/SYN-12:transition:31"
        )
        updated["approvals"].append(
            {
                "id": "transition-approval",
                "scope": transition["scope"],
                "evidence": str(report),
            }
        )
        updated["pending_actions"].append(transition)
        saved = self.store.save(
            "run-one",
            "codex",
            12345,
            initial["revision"],
            {"id": "add-transition", "reason": "Separate operation", "item": updated},
        )
        uncertain = self.reconcile(saved)
        confirmed = self.reconcile(uncertain, "confirmed", "confirm-fields")
        actions = current(confirmed)["pending_actions"]
        self.assertEqual(actions[0]["status"], "confirmed")
        self.assertEqual(actions[1], transition)
        self.assertEqual(self.store.read(), confirmed)

    def test_reconciliation_retry_handoff_and_immutable_history(self):
        initial = self.begin()
        prefix = deepcopy(initial["events"])
        uncertain = self.reconcile(initial)
        self.assertEqual(uncertain["events"][: len(prefix)], prefix)
        op = self.reconciliation(initial)
        self.assertEqual(
            self.store.reconcile("run-one", "codex", 12345, 0, op), uncertain
        )
        self.assertEqual(uncertain["invocations"][0]["steps"], 1)
        self.store.finish("run-one", "codex", 12345, "stopped")
        resumed = self.begin("run-two", "claude-code", fixture=False)
        confirmed = self.reconcile(
            resumed, "confirmed", "confirm-pr", "run-two", "claude-code"
        )
        self.assertEqual(current(confirmed)["fix_rounds"], 1)
        self.assertEqual(current(confirmed)["pending_actions"][0]["returned_id"], "17")
        self.assertEqual(current(confirmed)["approvals"], current(initial)["approvals"])
        self.assertEqual(confirmed["events"][: len(prefix)], prefix)
        self.assertEqual(self.store.read(), confirmed)
        for report in self.root.glob("*.md"):
            report.unlink()
        self.assertEqual(self.store.read(), confirmed)
        with self.assertRaisesRegex(fw.WorkError, "transition"):
            self.reconcile(
                confirmed, "proposed", "retry-confirmed", "run-two", "claude-code"
            )

    def test_reconciliation_scope_missing_approval_evidence_and_ordinary_save(self):
        initial = self.begin()
        for change in (
            {
                "status": "confirmed",
                "returned_id": "1",
                "returned_url": "https://example.invalid/1",
            },
            {"id": "unknown"},
            {"evidence": "relative.md"},
            {"evidence": str(self.root / "missing.md")},
            {
                "scope": {
                    "action": "pull_requests",
                    "target": "other",
                    "revision": "other",
                }
            },
        ):
            op = self.reconciliation(initial)
            op["action"].update(change)
            with self.assertRaises(fw.WorkError):
                self.store.reconcile("run-one", "codex", 12345, initial["revision"], op)
        operation = self.operation(initial)
        operation["item"]["pending_actions"][0]["status"] = "uncertain"
        with self.assertRaisesRegex(fw.WorkError, "Preserve scoped"):
            self.store.save("run-one", "codex", 12345, initial["revision"], operation)
        items = deepcopy(initial["items"])
        items[current(initial)["id"]]["approvals"] = []
        with self.assertRaisesRegex(fw.WorkError, "approval scope"):
            fw.apply_reconciliation(
                items, initial["active_item_id"], self.reconciliation(initial)
            )
        self.assertEqual(self.store.read(), initial)

    def test_reconciliation_absence_reset_bounds_cas_and_lost_reply(self):
        initial = self.begin(limit=2)
        with self.assertRaisesRegex(fw.WorkError, "Revision"):
            self.store.reconcile(
                "run-one", "codex", 12345, 0, self.reconciliation(initial)
            )
        with patch.object(
            fw, "verify_owner", return_value={**self.identity, "pid": 54321}
        ):
            with self.assertRaisesRegex(fw.WorkError, "different owner"):
                self.reconcile(initial)
        uncertain = self.reconcile(initial)
        reset_op = self.reconciliation(uncertain, "proposed", "authoritative-absence")
        real_sync = os.fsync
        calls = 0

        def lost_reply(fd):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("lost reply after replace")
            real_sync(fd)

        with patch.object(fw.os, "fsync", side_effect=lost_reply):
            with self.assertRaises(OSError):
                self.store.reconcile(
                    "run-one", "codex", 12345, uncertain["revision"], reset_op
                )
        reset = self.store.read()
        self.assertEqual(
            self.store.reconcile("run-one", "codex", 12345, 0, reset_op), reset
        )
        self.assertEqual(current(reset)["pending_actions"][0]["status"], "proposed")
        self.assertEqual(reset["invocations"][0]["steps"], 2)
        with self.assertRaisesRegex(fw.WorkError, "step limit"):
            self.reconcile(reset, name="attempt-again")

    def test_reconciliation_replay_rejects_tampered_scope_and_operation_collision(self):
        initial = self.begin()
        saved = self.reconcile(initial)
        for mutate in (
            lambda s: s["events"][-1]["change"]["action"]["scope"].update(
                revision="other"
            ),
            lambda s: s["events"][-1]["change"]["action"].update(
                evidence="relative.md"
            ),
            lambda s: s["events"][-1]["change"]["action"].update(
                status="confirmed",
                returned_id="9",
                returned_url="https://example.invalid/9",
            ),
        ):
            bad = deepcopy(saved)
            mutate(bad)
            with self.assertRaises((fw.WorkError, fw.ConfigError)):
                fw.snapshot(bad)
        with self.assertRaisesRegex(fw.WorkError, "domain"):
            self.save(saved, "attempt-pr")
        saved = self.save(saved, "save-domain")
        with self.assertRaisesRegex(fw.WorkError, "domain"):
            self.reconcile(saved, "confirmed", "save-domain")
        self.assertEqual(self.store.read(), saved)

    def test_fingerprint_includes_local_content_changes(self):
        self.fingerprint.stop()
        package = self.root / "package"
        for manifest in (".codex-plugin", ".claude-plugin"):
            (package / manifest).mkdir(parents=True)
            (package / manifest / "plugin.json").write_text('{"version":"0.2.3"}')
        source = package / "skill.md"
        source.write_text("one")
        first = fw.plugin_identity(package)
        source.write_text("two")
        second = fw.plugin_identity(package)
        self.assertEqual(first[0], second[0])
        self.assertNotEqual(first[1], second[1])
        (package / "__pycache__").mkdir()
        (package / "__pycache__/noise.pyc").write_bytes(b"cache")
        self.assertEqual(fw.plugin_identity(package), second)


if __name__ == "__main__":
    unittest.main()
