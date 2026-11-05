from __future__ import annotations

import importlib
import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import test_factory_work as work_tests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "plugins/factory/scripts"))
fw = importlib.import_module("factory_work")
fs = importlib.import_module("factory_source")


class RouteTests(unittest.TestCase):
    setUp = work_tests.WorkTests.setUp
    begin = work_tests.WorkTests.begin

    def source_begin(self, name="open-ticket", token="source-run"):
        path = ROOT / "plugins/factory/fixtures/sources" / (name + ".json")
        return self.store.begin("codex", 12345, token, None, 3, path)

    def route_operation(self, state, count=1, disposition="investigate", existing=None):
        key = next(k for k, v in state["sources"].items() if v["routing"] is None)
        saved = state["sources"][key]
        findings, updates = [], []
        for index in range(count):
            finding_key = "test-item-" + str(index)
            findings.append(
                {
                    "key": finding_key,
                    "classification": "bug",
                    "disposition": disposition,
                    "evidence": [saved["source"]["available_thread"][-1]["id"]],
                    "reason": "Manufactured persistence test artifact; not a router evaluation",
                    "duplicate_check": "incomplete",
                    "investigation_brief": None,
                    "proposed_ticket": None,
                    "existing_item_id": existing,
                }
            )
            if disposition != "no_action":
                updated = (
                    deepcopy(state["items"][existing])
                    if existing
                    else deepcopy(fw.load_fixture(self.fixture)[0])
                )
                if not existing:
                    updated.update(
                        id=fw.stable_id(saved["source"]["source_id"], finding_key),
                        source_id=saved["source"]["source_id"],
                        subitem_key=finding_key,
                    )
                if not existing:
                    updated.update(fix_rounds=0, approvals=[], pending_actions=[])
                updated["source_links"] = list(
                    dict.fromkeys(updated["source_links"] + [saved["source"]["link"]])
                )
                updated.update(
                    stage="investigate",
                    status="blocked",
                    required_role="factory-investigate",
                    next_action="Investigator unavailable",
                )
                updates.append(updated)
        selected = state["active_item_id"] or (updates[0]["id"] if updates else None)
        return {
            "id": "route-" + saved["source"]["source_id"] + saved["source"]["version"],
            "reason": "Persistence test explicit orchestrator update",
            "receipt_id": key,
            "routing": {
                "source_id": saved["source"]["source_id"],
                "source_version": saved["source"]["version"],
                "source_digest": saved["digest"],
                "covered_message_ids": [
                    m["id"] for m in saved["source"]["available_thread"]
                ],
                "findings": findings,
            },
            "items": updates,
            "active_item_id": selected,
        }

    def route_save(self, state, operation, token="source-run"):
        return self.store.route(token, "codex", 12345, state["revision"], operation)

    def test_no_action_receipt_has_no_work_and_exact_replay_is_empty(self):
        initial = self.source_begin("conversation")
        operation = self.route_operation(initial, disposition="no_action")
        saved = self.route_save(initial, operation)
        self.assertEqual(saved["items"], {})
        self.assertIsNone(saved["active_item_id"])
        self.store.finish("source-run", "codex", 12345, "no_available_work")
        replay = self.source_begin("conversation", "replay")
        self.assertEqual(replay["sources"], saved["sources"])
        self.assertEqual(len(replay["sources"]), 1)
        self.assertEqual(sum(e["kind"] == "route" for e in replay["events"]), 1)

    def test_three_pending_items_one_selected_and_new_source_despite_block(self):
        initial = self.source_begin("three-items")
        saved = self.route_save(initial, self.route_operation(initial, count=3))
        self.assertEqual(len(saved["items"]), 3)
        self.assertIn(saved["active_item_id"], saved["items"])
        self.store.finish("source-run", "codex", 12345, "blocked")
        second = self.source_begin("feature", "second")
        saved_second = self.route_save(second, self.route_operation(second), "second")
        self.assertEqual(len(saved_second["items"]), 4)
        self.assertEqual(saved_second["active_item_id"], saved["active_item_id"])
        self.assertEqual(
            {v["id"] for v in saved_second["items"].values()},
            set(saved_second["items"]),
        )

    def test_related_source_preserves_execution_records_and_attaches(self):
        initial = self.source_begin()
        op = self.route_operation(initial)
        op["items"][0]["artifact_paths"] = {
            "investigation": str(self.root / "evidence.md")
        }
        op["items"][0]["code"] = {
            "branch": "synthetic/existing",
            "worktree": str(self.root / "worktree"),
        }
        saved = self.route_save(initial, op)
        executed = deepcopy(work_tests.current(saved))
        prior = fw.load_fixture(self.fixture)[0]
        executed.update(
            fix_rounds=prior["fix_rounds"],
            approvals=prior["approvals"],
            pending_actions=prior["pending_actions"],
        )
        saved = self.store.save(
            "source-run",
            "codex",
            12345,
            saved["revision"],
            {
                "id": "prior-synthetic-execution",
                "reason": "Manufactured prior execution/authorization state for preservation testing only",
                "item": executed,
            },
        )
        target = saved["active_item_id"]
        self.store.finish("source-run", "codex", 12345, "blocked")
        related = self.source_begin("related-thread", "related")
        operation = self.route_operation(related, existing=target)
        for key, bad in (
            ("fix_rounds", 2),
            ("artifact_paths", {}),
            ("code", {}),
            ("approvals", []),
            ("pending_actions", []),
        ):
            broken = deepcopy(operation)
            broken["items"][0][key] = bad
            with self.assertRaises(fw.WorkError):
                self.route_save(related, broken, "related")
        attached = self.route_save(related, operation, "related")
        self.assertEqual(len(attached["items"]), 1)
        self.assertEqual(len(attached["sources"]), 2)
        self.assertEqual(work_tests.current(attached)["fix_rounds"], 1)
        self.assertEqual(
            work_tests.current(attached)["code"], work_tests.current(saved)["code"]
        )
        self.assertEqual(
            work_tests.current(attached)["pending_actions"],
            work_tests.current(saved)["pending_actions"],
        )

    def test_source_versions_retained_conflicts_refused_and_retry_exact(self):
        initial = self.source_begin()
        self.assertEqual(self.source_begin(), initial)
        saved = self.route_save(initial, self.route_operation(initial))
        self.store.finish("source-run", "codex", 12345, "blocked")
        changed = json.loads(
            (ROOT / "plugins/factory/fixtures/sources/open-ticket.json").read_text()
        )
        changed["available_thread"][0]["text"] = "different capture under same version"
        path = self.root / "conflict.json"
        path.write_text(json.dumps(changed))
        before = self.store.path.read_bytes()
        with self.assertRaisesRegex(fw.WorkError, "immutable source version"):
            self.store.begin("codex", 12345, "conflict", None, 3, path)
        self.assertEqual(self.store.path.read_bytes(), before)
        later = self.source_begin("open-ticket-followup", "later")
        op = self.route_operation(later, existing=saved["active_item_id"])
        routed = self.route_save(later, op, "later")
        self.assertEqual(len(routed["sources"]), 2)
        self.assertEqual(len(routed["items"]), 1)

    def test_route_cas_lost_reply_idempotency_and_invalid_refs(self):
        initial = self.source_begin()
        operation = self.route_operation(initial)
        bad = deepcopy(operation)
        bad["routing"]["covered_message_ids"] = ["m1"]
        with self.assertRaises(fw.ConfigError):
            self.route_save(initial, bad)
        bad = deepcopy(operation)
        bad["routing"]["findings"][0]["evidence"] = ["invented"]
        with self.assertRaises(fw.ConfigError):
            self.route_save(initial, bad)
        with self.assertRaisesRegex(fw.WorkError, "Revision"):
            self.store.route("source-run", "codex", 12345, 0, operation)
        real = fw.os.fsync
        count = 0

        def fail_after_replace(fd):
            nonlocal count
            count += 1
            if count == 2:
                raise OSError("lost route reply")
            real(fd)

        with patch.object(fw.os, "fsync", side_effect=fail_after_replace):
            with self.assertRaises(OSError):
                self.route_save(initial, operation)
        committed = self.store.read()
        self.assertEqual(self.route_save(initial, operation), committed)
        self.assertEqual(committed["invocations"][0]["steps"], 1)
        self.assertEqual(len(committed["items"]), 1)
        conflicting = deepcopy(operation)
        conflicting["reason"] = "changed"
        with self.assertRaisesRegex(fw.WorkError, "different content"):
            self.route_save(committed, conflicting)

    def legacy_state(self, active=False):
        state = self.begin()
        if not active:
            state = self.store.finish("run-one", "codex", 12345, "blocked")
        legacy = self.legacy_from_snapshot(state)
        self.store.path.write_text(json.dumps(legacy))
        return legacy

    def test_legacy_inspect_no_write_and_owner_begin_migration_preserves_history(self):
        legacy = self.legacy_state()
        original = self.store.path.read_bytes()
        read = self.store.read()
        self.assertEqual(read["schema_version"], 1)
        self.assertEqual(self.store.path.read_bytes(), original)
        resumed = self.begin("migrate", "claude-code", fixture=False)
        self.assertEqual(resumed["schema_version"], 2)
        self.assertEqual(work_tests.current(resumed), legacy["item"])
        self.assertEqual(resumed["events"][: len(legacy["events"])], legacy["events"])
        self.assertEqual(
            resumed["invocations"][: len(legacy["invocations"])], legacy["invocations"]
        )
        self.assertEqual(resumed["synthetic_cursors"], legacy["synthetic_cursors"])
        self.assertEqual(resumed["sources"], {})
        self.assertEqual(sum(e["kind"] == "migrate" for e in resumed["events"]), 1)

    def test_legacy_live_unknown_and_corrupt_refuse_without_migration(self):
        legacy = self.legacy_state(active=True)
        before = self.store.path.read_bytes()
        for alive in (True, fw.WorkError("unknown")):
            with patch.object(
                fw,
                "owner_alive",
                return_value=alive,
                side_effect=alive if isinstance(alive, Exception) else None,
            ):
                with self.assertRaises(fw.WorkError):
                    self.begin("migration", "claude-code", fixture=False)
            self.assertEqual(self.store.path.read_bytes(), before)
        legacy["item"]["fix_rounds"] = 0
        self.store.path.write_text(json.dumps(legacy))
        corrupt = self.store.path.read_bytes()
        with self.assertRaisesRegex(fw.WorkError, "repair"):
            self.begin("migration", fixture=False)
        self.assertEqual(self.store.path.read_bytes(), corrupt)

    def test_corrupt_inventory_receipt_and_route_history_refused(self):
        initial = self.source_begin()
        state = self.route_save(initial, self.route_operation(initial))
        for mutate in (
            lambda s: s["items"].clear(),
            lambda s: next(iter(s["sources"].values()))["source"]["available_thread"][
                0
            ].update(text="tampered"),
            lambda s: s.update(active_item_id=None),
            lambda s: s["events"][-1]["change"]["routing"]["findings"][0].update(
                reason="changed history"
            ),
        ):
            broken = deepcopy(state)
            mutate(broken)
            self.store.path.write_text(json.dumps(broken))
            with self.assertRaisesRegex(fw.WorkError, "repair"):
                self.store.read()

    def test_migration_atomic_failure_keeps_legacy_then_exact_retry_commits_once(self):
        legacy = self.legacy_state()
        original = self.store.path.read_bytes()
        with patch.object(
            fw.os, "replace", side_effect=OSError("before migration replace")
        ):
            with self.assertRaises(OSError):
                self.begin("migrate", "claude-code", fixture=False)
        self.assertEqual(self.store.path.read_bytes(), original)
        real_fsync = fw.os.fsync
        calls = 0

        def fail_directory_sync(fd):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("after migration replace")
            real_fsync(fd)

        with patch.object(fw.os, "fsync", side_effect=fail_directory_sync):
            with self.assertRaises(OSError):
                self.begin("migrate", "claude-code", fixture=False)
        committed = self.store.read()
        self.assertEqual(self.begin("migrate", "claude-code", fixture=False), committed)
        self.assertEqual(work_tests.current(committed), legacy["item"])
        self.assertEqual(committed["events"][: len(legacy["events"])], legacy["events"])
        self.assertEqual(sum(e["kind"] == "migrate" for e in committed["events"]), 1)

    def test_raw_source_fixtures_validate_and_followup_preserves_prior_messages(self):
        folder = ROOT / "plugins/factory/fixtures/sources"
        fixtures = {
            path.stem: fs.source(fw.read_json(path)) for path in folder.glob("*.json")
        }
        self.assertEqual(len(fixtures), 9)
        first, later = fixtures["open-ticket"], fixtures["open-ticket-followup"]
        self.assertEqual(first["source_id"], later["source_id"])
        self.assertEqual(first["link"], later["link"])
        self.assertNotEqual(first["version"], later["version"])
        self.assertEqual(first["available_thread"], later["available_thread"][:-1])

    def test_missing_duplicate_lifecycle_events_refuse_and_preserve_bytes(self):
        self.begin()
        finished = self.store.finish("run-one", "codex", 12345, "blocked")
        legacy = self.legacy_from_snapshot(finished)
        for original in (finished, legacy):
            for kind in ("begin", "finish"):
                for duplicate in (False, True):
                    with self.subTest(
                        schema=original["schema_version"],
                        kind=kind,
                        duplicate=duplicate,
                    ):
                        broken = deepcopy(original)
                        event = next(e for e in broken["events"] if e["kind"] == kind)
                        if duplicate:
                            broken["events"].append(deepcopy(event))
                        else:
                            broken["events"].remove(event)
                        for revision, saved_event in enumerate(broken["events"], 1):
                            saved_event["revision"] = revision
                        broken["revision"] = len(broken["events"])
                        self.store.path.write_text(json.dumps(broken))
                        before = self.store.path.read_bytes()
                        with self.assertRaisesRegex(fw.WorkError, "repair.*lifecycle"):
                            self.store.read()
                        with self.assertRaisesRegex(fw.WorkError, "repair.*lifecycle"):
                            self.begin("run-one", fixture=False)
                        self.assertEqual(self.store.path.read_bytes(), before)

    def legacy_from_snapshot(self, state):
        legacy = {
            k: deepcopy(v)
            for k, v in state.items()
            if k not in ("items", "active_item_id", "sources")
        }
        legacy["schema_version"] = 1
        legacy["item"] = deepcopy(work_tests.current(state))
        for e in legacy["events"]:
            e.pop("change")
        return legacy

    def test_verified_dead_active_legacy_migration_finishes_old_before_new_begin(self):
        legacy = self.legacy_state(active=True)
        with patch.object(fw, "owner_alive", return_value=False):
            resumed = self.begin("migrate", "claude-code", fixture=False)
        self.assertEqual(resumed["schema_version"], 2)
        self.assertEqual(work_tests.current(resumed), legacy["item"])
        self.assertEqual(resumed["events"][: len(legacy["events"])], legacy["events"])
        self.assertEqual(resumed["invocations"][0]["outcome"], "interrupted_owner_dead")
        self.assertEqual(
            [
                (e["run_id"], e["kind"])
                for e in resumed["events"][len(legacy["events"]) :]
            ],
            [("run-one", "finish"), ("migrate", "migrate"), ("migrate", "begin")],
        )
        self.assertEqual(resumed["active_run"], "migrate")
        self.assertEqual(self.store.read(), resumed)

    def test_fresh_routed_items_cannot_inherit_fix_round_or_action_ledgers(self):
        initial = self.source_begin()
        operation = self.route_operation(initial)
        prior = fw.load_fixture(self.fixture)[0]
        before = self.store.path.read_bytes()
        for key in ("fix_rounds", "approvals", "pending_actions"):
            with self.subTest(key=key):
                broken = deepcopy(operation)
                broken["items"][0][key] = deepcopy(prior[key])
                with self.assertRaisesRegex(fw.WorkError, "Fresh routed items"):
                    self.route_save(initial, broken)
                self.assertEqual(self.store.path.read_bytes(), before)
        saved = self.route_save(initial, operation)
        current = work_tests.current(saved)
        self.assertEqual(current["fix_rounds"], 0)
        self.assertEqual(current["approvals"], [])
        self.assertEqual(current["pending_actions"], [])
