from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import test_factory_work as work_tests
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "plugins/factory/scripts"))
fw = importlib.import_module("factory_work")
fc = importlib.import_module("factory_concurrent")


class ConcurrentTests(unittest.TestCase):
    def setUp(self):
        work_tests.WorkTests.setUp(self)
        data = yaml.safe_load(self.config.read_text())
        data["schema_version"] = 2
        data["limits"] = {"fix_rounds": 2}
        self.config.write_text(yaml.safe_dump(data))
        self.store = fc.Store(self.config)

    def start(self, token, seed=True):
        path = None
        if seed:
            raw = json.loads(
                (ROOT / "plugins/factory/fixtures/synthetic-item.json").read_text()
            )
            raw["item"]["source_id"] = "synthetic:" + token
            path = self.root / (token + ".json")
            path.write_text(json.dumps(raw))
        state = self.store.begin("codex", 12345, token, fixture=path)
        if seed:
            selected = fw.load_fixture(path)[0]["id"]
            state = self.change(
                token, "claim", {"item_id": selected, "expected_version": 1}
            )
        return state

    def change(self, token, kind, payload, name=None):
        return self.store.mutate(
            token, "codex", 12345, kind, {"id": name or token + ":" + kind, **payload}
        )

    def decision(self, state, token, name, expected=None):
        selected = fc.current_run(state, token)["item_id"]
        item = deepcopy(state["items"][selected])
        item.update(stage="investigate", next_action="Investigate synthetic evidence")
        return {
            "id": name,
            "expected_version": expected or state["item_versions"][selected],
            "decision": {
                "id": name,
                "reason": "Synthetic concurrent save",
                "item": item,
            },
        }

    def test_independent_runs_interleave_without_global_revision_conflicts(self):
        self.start("a")
        original = self.start("b")
        op_a = self.decision(original, "a", "save-a")
        op_b = self.decision(original, "b", "save-b")
        after_a = self.store.mutate("a", "codex", 12345, "save", op_a)
        after_b = self.store.mutate("b", "codex", 12345, "save", op_b)
        self.assertEqual(len(fc.active_items(after_b)), 2)
        for token in ("a", "b"):
            selected = fc.current_run(after_b, token)["item_id"]
            self.assertEqual(after_b["item_versions"][selected], 2)
        self.assertEqual(self.store.read(), after_b)
        self.assertGreater(after_b["revision"], after_a["revision"])
        with self.assertRaisesRegex(fw.WorkError, "version"):
            self.store.mutate("a", "codex", 12345, "save", {**op_a, "id": "stale-a"})

    def test_claim_and_cross_item_mutation_rejected(self):
        state = self.start("a")
        selected = fc.current_run(state, "a")["item_id"]
        self.start("b", False)
        before = self.store.path.read_bytes()
        with self.assertRaisesRegex(fw.WorkError, "claimed"):
            self.change("b", "claim", {"item_id": selected, "expected_version": 1})
        with self.assertRaisesRegex(fw.WorkError, "claim"):
            self.store.mutate(
                "b", "codex", 12345, "save", self.decision(state, "a", "steal")
            )
        self.assertEqual(self.store.path.read_bytes(), before)
        with patch.object(
            fw, "verify_owner", return_value={**self.identity, "pid": 67890}
        ):
            with self.assertRaisesRegex(fw.WorkError, "different owner"):
                self.change("a", "finish", {"outcome": "stopped"})

    def test_finish_releases_only_own_item_and_resume_reuses_history(self):
        self.start("a")
        state = self.start("b")
        selected = fc.current_run(state, "a")["item_id"]
        self.change("a", "finish", {"outcome": "waiting_for_human"})
        state = self.start("c", False)
        state = self.change("c", "claim", {"item_id": selected, "expected_version": 1})
        self.assertEqual(fc.active_items(state)[selected], "c")
        self.assertIsNone(fc.current_run(state, "b")["finished_at"])
        self.assertEqual(
            fc.current_run(state, "a", True)["outcome"], "waiting_for_human"
        )

    def test_recovery_requires_dead_owner_and_leaves_other_runs_active(self):
        self.start("a")
        before = self.start("b")
        for effect in (True, fw.WorkError("unknown process state")):
            with patch.object(
                fw,
                "owner_alive",
                side_effect=effect if isinstance(effect, Exception) else None,
                return_value=effect,
            ):
                with self.assertRaises(fw.WorkError):
                    self.change("b", "recover", {"target_run": "a"})
        self.assertEqual(self.store.read(), before)
        with patch.object(fw, "owner_alive", return_value=False):
            state = self.change("b", "recover", {"target_run": "a"})
        self.assertEqual(
            fc.current_run(state, "a", True)["outcome"], "interrupted_owner_dead"
        )
        self.assertIsNone(fc.current_run(state, "b")["finished_at"])

    def test_busy_intake_claim_does_not_block_independent_item(self):
        self.start("a")
        state = self.start("b")
        capture = json.loads(
            (ROOT / "plugins/factory/fixtures/sources/open-ticket.json").read_text()
        )
        path = self.root / "source.json"
        path.write_text(json.dumps(capture))
        state = self.store.begin(
            "codex", 12345, "intake", incoming=path, synthetic_source=True
        )
        key = "receipt:" + next(iter(state["sources"]))
        self.change("a", "intake_claim", {"key": key})
        with self.assertRaisesRegex(fw.WorkError, "busy"):
            self.change("b", "intake_claim", {"key": key})
        state = self.store.read()
        self.store.mutate(
            "b", "codex", 12345, "save", self.decision(state, "b", "save-b")
        )
        self.change("a", "finish", {"outcome": "stopped"})
        state = self.change("b", "intake_claim", {"key": key}, "b:retry-intake")
        self.assertEqual(state["claims"][key], "b")

    def capture(self, token, name="open-ticket"):
        path = ROOT / "plugins/factory/fixtures/sources" / (name + ".json")
        state = self.store.begin(
            "codex", 12345, token, incoming=path, synthetic_source=True
        )
        key = next(
            key
            for key, receipt in state["sources"].items()
            if receipt["routing"] is None
        )
        state = self.change(token, "intake_claim", {"key": "receipt:" + key})
        return state, key

    def route(self, state, key, existing=None, no_action=False):
        saved = state["sources"][key]
        finding = {
            "key": "bug",
            "classification": "conversation" if no_action else "bug",
            "disposition": "no_action" if no_action else "investigate",
            "evidence": [saved["source"]["available_thread"][-1]["id"]],
            "reason": "Synthetic routing result",
            "duplicate_check": "incomplete",
            "investigation_brief": None,
            "proposed_ticket": None,
            "existing_item_id": existing,
        }
        items = []
        if existing is None and not no_action:
            item = deepcopy(
                fw.load_fixture(ROOT / "plugins/factory/fixtures/synthetic-item.json")[
                    0
                ]
            )
            item.update(
                id=fw.stable_id(saved["source"]["source_id"], "bug"),
                source_id=saved["source"]["source_id"],
                subitem_key="bug",
                source_links=[saved["source"]["link"]],
            )
            items.append(item)
        return {
            "id": "route:" + key,
            "reason": "Synthetic routing",
            "receipt_id": key,
            "routing": {
                "source_id": saved["source"]["source_id"],
                "source_version": saved["source"]["version"],
                "source_digest": saved["digest"],
                "covered_message_ids": [
                    m["id"] for m in saved["source"]["available_thread"]
                ],
                "findings": [finding],
            },
            "items": items,
            "inventory_version": fc.inventory_version(state),
        }

    def test_routing_associates_new_evidence_without_overwriting_owned_item(self):
        initial = self.start("a")
        selected = fc.current_run(initial, "a")["item_id"]
        pending = self.decision(initial, "a", "before-new-context")
        state, key = self.capture("route")
        operation = self.route(state, key, existing=selected)
        state = self.store.mutate("route", "codex", 12345, "route", operation)
        self.assertEqual(state["items"][selected], initial["items"][selected])
        self.assertEqual(state["sources"][key]["item_ids"], {"bug": selected})
        self.assertEqual(state["item_versions"][selected], 2)
        with self.assertRaisesRegex(fw.WorkError, "version"):
            self.store.mutate("a", "codex", 12345, "save", pending)
        refreshed = self.decision(state, "a", "after-new-context")
        self.store.mutate("a", "codex", 12345, "save", refreshed)

    def test_routing_rejects_stale_inventory_and_foreign_item_replacements(self):
        state, key = self.capture("route")
        operation = self.route(state, key)
        state = self.start("a")
        before = self.store.path.read_bytes()
        with self.assertRaisesRegex(fw.WorkError, "inventory"):
            self.store.mutate("route", "codex", 12345, "route", operation)
        self.assertEqual(self.store.path.read_bytes(), before)
        operation = self.route(state, key)
        state = self.store.mutate("route", "codex", 12345, "route", operation)
        self.assertEqual(len(state["items"]), 2)
        self.assertIsNone(fc.current_run(state, "route")["item_id"])

    def test_no_action_routing_creates_no_item_and_step_cap_preserves_state(self):
        state, key = self.capture("route", "conversation")
        state = self.store.mutate(
            "route", "codex", 12345, "route", self.route(state, key, no_action=True)
        )
        self.assertEqual(state["items"], {})
        self.change("route", "finish", {"outcome": "no_available_work"})
        self.store.begin(
            "codex",
            12345,
            "bounded",
            fixture=ROOT / "plugins/factory/fixtures/synthetic-item.json",
            max_steps=1,
        )
        state = self.store.read()
        selected = next(iter(state["items"]))
        state = self.change(
            "bounded", "claim", {"item_id": selected, "expected_version": 1}
        )
        state = self.store.mutate(
            "bounded", "codex", 12345, "save", self.decision(state, "bounded", "one")
        )
        before = self.store.path.read_bytes()
        with self.assertRaisesRegex(fw.WorkError, "limit"):
            self.store.mutate(
                "bounded",
                "codex",
                12345,
                "save",
                self.decision(state, "bounded", "two"),
            )
        self.assertEqual(self.store.path.read_bytes(), before)

    def test_channel_cursors_commit_independently_and_incomplete_read_is_atomic(self):
        data = yaml.safe_load(self.config.read_text())
        data["slack"] = {
            "workspace_id": "T_SYNTHETIC",
            "channels": [
                {"id": "C_SYNTHETIC_ONE", "name": "one"},
                {"id": "C_SYNTHETIC_TWO", "name": "two"},
            ],
        }
        self.config.write_text(yaml.safe_dump(data))
        self.store = fc.Store(self.config)
        starts = self.store.runtime / "setup/example/channel-starts.json"
        starts.parent.mkdir(parents=True)
        starts.write_text(
            json.dumps(
                {
                    "T_SYNTHETIC:C_SYNTHETIC_ONE": "2023-11-14T22:13:20+00:00",
                    "T_SYNTHETIC:C_SYNTHETIC_TWO": "2023-11-14T22:13:45+00:00",
                }
            )
        )
        self.start("a", False)
        self.start("b", False)
        first = json.loads(
            (ROOT / "plugins/factory/fixtures/watch/first.json").read_text()
        )
        second = json.loads(
            (ROOT / "plugins/factory/fixtures/watch/second-channel.json").read_text()
        )
        for token, observation in (("a", first), ("b", second)):
            self.change(
                token,
                "intake_claim",
                {
                    "key": "channel:"
                    + fc.identity(
                        observation["workspace_id"], observation["channel_id"]
                    )
                },
            )
        self.change("a", "collect", {"observation": first}, first["id"])
        state = self.change("b", "collect", {"observation": second}, second["id"])
        self.assertEqual(len(state["collection"]["cursors"]), 2)
        before = self.store.path.read_bytes()
        bad = deepcopy(second)
        bad.update(id="incomplete", complete=False, lower=second["upper"])
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            self.change("b", "collect", {"observation": bad}, bad["id"])
        self.assertEqual(self.store.path.read_bytes(), before)

    def test_atomic_replace_failures_and_exact_retry(self):
        initial = self.start("a")
        op = self.decision(initial, "a", "save-a")
        before = self.store.path.read_bytes()
        with patch.object(fc.os, "replace", side_effect=OSError("before replace")):
            with self.assertRaises(OSError):
                self.store.mutate("a", "codex", 12345, "save", op)
        self.assertEqual(self.store.path.read_bytes(), before)
        real_fsync = os.fsync
        calls = 0

        def fsync(fd):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("after replace")
            real_fsync(fd)

        with patch.object(fc.os, "fsync", side_effect=fsync):
            with self.assertRaises(OSError):
                self.store.mutate("a", "codex", 12345, "save", op)
        saved = self.store.read()
        self.assertEqual(self.store.mutate("a", "codex", 12345, "save", op), saved)
        self.assertEqual(fc.current_run(saved, "a")["steps"], 1)
        self.change("a", "finish", {"outcome": "stopped"})
        self.start("b", False)
        selected = fc.current_run(saved, "a")["item_id"]
        self.change("b", "claim", {"item_id": selected, "expected_version": 2})
        retried = self.store.mutate("b", "codex", 12345, "save", op)
        self.assertEqual(fc.current_run(retried, "b")["steps"], 0)

    def test_history_tampering_and_operation_collision_refuse(self):
        state = self.start("a")
        corrupted = deepcopy(state)
        next(iter(corrupted["items"].values()))["next_action"] = "invented"
        with self.assertRaisesRegex(fw.WorkError, "history"):
            fc.snapshot(corrupted)
        with self.assertRaisesRegex(fw.WorkError, "reused"):
            self.change("a", "finish", {"outcome": "stopped"}, "a:claim")

    def git(self, *args):
        return subprocess.run(
            ["git", *map(str, args)], check=True, text=True, capture_output=True
        ).stdout.strip()

    def repository(self):
        repo = self.root / "repos" / "example"
        repo.mkdir(parents=True)
        self.git("init", repo)
        self.git(
            "-C",
            repo,
            "-c",
            "user.name=Synthetic",
            "-c",
            "user.email=synthetic@example.invalid",
            "commit",
            "--allow-empty",
            "-m",
            "initial",
        )
        data = yaml.safe_load(self.config.read_text())
        data["repositories"] = {"roots": [str(repo.parent)], "paths": []}
        self.config.write_text(yaml.safe_dump(data))
        self.store = fc.Store(self.config)
        return repo

    def test_same_repository_distinct_worktrees_and_persistent_reservations(self):
        repo = self.repository()
        self.start("a")
        state = self.start("b")
        a = fc.current_run(state, "a")["item_id"]
        b = fc.current_run(state, "b")["item_id"]
        first, second = self.root / "first", self.root / "second"
        self.git("-C", repo, "worktree", "add", "-b", "first", first)
        self.git("-C", repo, "worktree", "add", "-b", "second", second)
        ra = self.store.observe_resource(first, a)
        rb = self.store.observe_resource(second, b)
        self.change("a", "reserve", {"resources": [ra]})
        state = self.change("b", "reserve", {"resources": [rb]})
        self.assertEqual(ra["common_dir"], rb["common_dir"])
        self.assertEqual(len(state["resources"]), 2)
        self.change("a", "finish", {"outcome": "waiting_for_human"})
        with self.assertRaisesRegex(fw.WorkError, "reserved"):
            self.change(
                "b", "reserve", {"resources": [{**ra, "item_id": b}]}, "b:steal"
            )
        alias = self.root / "alias"
        alias.symlink_to(first, target_is_directory=True)
        self.assertEqual(self.store.observe_resource(alias, a), ra)
        self.start("resume", False)
        state = self.change("resume", "claim", {"item_id": a, "expected_version": 1})
        self.change("resume", "reserve", {"resources": [ra]})
        self.assertEqual(len(state["resources"]), 2)
        with self.assertRaisesRegex(fw.WorkError, "source checkout"):
            self.store.observe_resource(repo, a)

    def test_detached_worktree_checkpoint_then_full_branch_reference(self):
        repo = self.repository()
        state = self.start("a")
        selected = fc.current_run(state, "a")["item_id"]
        worktree = self.root / "detached"
        self.git("-C", repo, "worktree", "add", "--detach", worktree)
        reserved = self.store.observe_resource(worktree, selected)
        self.assertIsNone(reserved["branch"])
        state = self.change("a", "reserve", {"resources": [reserved]})
        decision = self.decision(state, "a", "detached-checkpoint")
        decision["decision"]["item"]["code"] = {"worktree": str(worktree)}
        self.store.mutate("a", "codex", 12345, "save", decision)
        self.git("-C", worktree, "checkout", "-b", "attached")
        reserved = self.store.observe_resource(worktree, selected)
        state = self.change(
            "a", "reserve", {"resources": [reserved]}, "reserve-attached"
        )
        decision = self.decision(state, "a", "branch-checkpoint")
        decision["decision"]["item"]["code"]["branch"] = "refs/heads/attached"
        state = self.store.mutate("a", "codex", 12345, "save", decision)
        self.assertEqual(
            state["items"][selected]["code"]["branch"], "refs/heads/attached"
        )
        self.git("-C", worktree, "checkout", "-b", "next")
        state = self.change(
            "a",
            "reserve",
            {"resources": [self.store.observe_resource(worktree, selected)]},
            "reserve-next",
        )
        decision = self.decision(state, "a", "next-branch-checkpoint")
        decision["decision"]["item"]["code"]["branch"] = "next"
        self.store.mutate("a", "codex", 12345, "save", decision)
        state = self.start("b")
        other = fc.current_run(state, "b")["item_id"]
        contender = self.root / "contender"
        self.git("-C", repo, "worktree", "add", contender, "attached")
        with self.assertRaisesRegex(fw.WorkError, "reserved"):
            self.change(
                "b",
                "reserve",
                {"resources": [self.store.observe_resource(contender, other)]},
            )

    def test_upgrade_preserves_originals_and_rejects_alive_unknown_owner(self):
        data = yaml.safe_load(self.config.read_text())
        data["schema_version"] = 1
        data["limits"]["active_work_items"] = 1
        self.config.write_text(yaml.safe_dump(data))
        legacy = fw.Store(self.config)
        old = legacy.begin("codex", 12345, "old", self.fixture)
        self.store = fc.Store(self.config)
        config_bytes = self.config.read_bytes()
        state_bytes = self.store.path.read_bytes()
        for effect in (True, fw.WorkError("unknown")):
            with patch.object(
                fw,
                "owner_alive",
                side_effect=effect if isinstance(effect, Exception) else None,
                return_value=effect,
            ):
                with self.assertRaises(fw.WorkError):
                    fc.upgrade(self.store, "codex", 12345)
            self.assertEqual(self.config.read_bytes(), config_bytes)
            self.assertEqual(self.store.path.read_bytes(), state_bytes)
        legacy.finish("old", "codex", 12345, "stopped")
        state_bytes = self.store.path.read_bytes()
        old = legacy.read()
        result = fc.upgrade(self.store, "codex", 12345)
        backup = Path(result["backup_path"])
        self.assertEqual((backup / "config.yaml").read_bytes(), config_bytes)
        self.assertEqual((backup / "work.json").read_bytes(), state_bytes)
        self.assertEqual(yaml.safe_load(self.config.read_text())["schema_version"], 2)
        self.store = fc.Store(self.config)
        state = self.store.read()
        self.assertEqual(state["legacy"], json.loads(state_bytes))
        self.assertEqual(state["items"], old["items"])
        self.assertNotIn("active_item_id", state)
        self.assertEqual(fc.upgrade(self.store, "codex", 12345)["schema_version"], 4)
        with self.assertRaises(fw.WorkError):
            fw.snapshot(json.loads(self.store.path.read_text()))

    def test_upgrade_can_resume_after_state_replace_before_config_replace(self):
        data = yaml.safe_load(self.config.read_text())
        data["schema_version"] = 1
        data["limits"]["active_work_items"] = 1
        self.config.write_text(yaml.safe_dump(data))
        self.store = fc.Store(self.config)
        real_replace = os.replace

        def replace(src, dst):
            if Path(dst) == self.config:
                raise OSError("lost config replacement")
            return real_replace(src, dst)

        with patch.object(fc.os, "replace", side_effect=replace):
            with self.assertRaises(OSError):
                fc.upgrade(self.store, "codex", 12345)
        self.assertEqual(json.loads(self.store.path.read_text())["schema_version"], 4)
        self.assertEqual(yaml.safe_load(self.config.read_text())["schema_version"], 1)
        result = fc.upgrade(self.store, "codex", 12345)
        self.assertEqual(result["config_schema_version"], 2)

    def test_upgrade_retry_preserves_noncanonical_original_bytes(self):
        data = yaml.safe_load(self.config.read_text())
        data["schema_version"] = 1
        data["limits"]["active_work_items"] = 1
        self.config.write_text(yaml.safe_dump(data))
        legacy = fw.Store(self.config)
        legacy.begin("codex", 12345, "legacy", self.fixture)
        legacy.finish("legacy", "codex", 12345, "stopped")
        original = json.dumps(
            json.loads(legacy.path.read_text()), separators=(",", ":")
        ).encode()
        legacy.path.write_bytes(original)
        self.store = fc.Store(self.config)
        real_replace = os.replace

        def replace(src, dst):
            if Path(dst) == self.config:
                raise OSError("before config replacement")
            return real_replace(src, dst)

        with patch.object(fc.os, "replace", side_effect=replace):
            with self.assertRaises(OSError):
                fc.upgrade(self.store, "codex", 12345)
        result = fc.upgrade(self.store, "codex", 12345)
        self.assertEqual(
            (Path(result["backup_path"]) / "work.json").read_bytes(), original
        )

    def test_upgrade_cannot_restart_a_legacy_uuid_or_reuse_legacy_decision_id(self):
        data = yaml.safe_load(self.config.read_text())
        data["schema_version"] = 1
        data["limits"]["active_work_items"] = 1
        self.config.write_text(yaml.safe_dump(data))
        legacy = fw.Store(self.config)
        initial = legacy.begin("codex", 12345, "legacy-run", self.fixture)
        operation = work_tests.WorkTests.operation(self, initial, "legacy-decision")
        legacy.save("legacy-run", "codex", 12345, initial["revision"], operation)
        legacy.finish("legacy-run", "codex", 12345, "stopped")
        self.store = fc.Store(self.config)
        fc.upgrade(self.store, "codex", 12345)
        self.store = fc.Store(self.config)
        with self.assertRaisesRegex(fw.WorkError, "legacy"):
            self.store.begin("codex", 12345, "legacy-run")
        state = self.start("resume", False)
        selected = next(iter(state["items"]))
        state = self.change(
            "resume", "claim", {"item_id": selected, "expected_version": 1}
        )
        with self.assertRaisesRegex(fw.WorkError, "legacy"):
            self.store.mutate(
                "resume",
                "codex",
                12345,
                "save",
                self.decision(state, "resume", "legacy-decision"),
            )

    def test_upgrade_schema_one_and_three_preserves_history_and_collection(self):
        for schema in (1, 3):
            with self.subTest(schema=schema):
                home = self.root / str(schema)
                home.mkdir()
                config = home / "config.yaml"
                data = yaml.safe_load(self.config.read_text())
                data["schema_version"] = 1
                data["limits"]["active_work_items"] = 1
                if schema == 3:
                    data["slack"] = {
                        "workspace_id": "T_SYNTHETIC",
                        "channels": [{"id": "C_SYNTHETIC_ONE", "name": "one"}],
                    }
                config.write_text(yaml.safe_dump(data))
                legacy = fw.Store(config)
                state = legacy.begin("codex", 12345, "legacy", self.fixture)
                if schema == 3:
                    starts = legacy.runtime / "setup/example/channel-starts.json"
                    starts.parent.mkdir(parents=True)
                    starts.write_text(
                        json.dumps(
                            {"T_SYNTHETIC:C_SYNTHETIC_ONE": "2023-11-14T22:13:20+00:00"}
                        )
                    )
                    observation = json.loads(
                        (ROOT / "plugins/factory/fixtures/watch/first.json").read_text()
                    )
                    state = legacy.collect(
                        "legacy", "codex", 12345, state["revision"], observation
                    )
                state = legacy.finish("legacy", "codex", 12345, "stopped")
                if schema == 1:
                    state = {
                        key: value
                        for key, value in state.items()
                        if key not in ("items", "active_item_id", "sources")
                    }
                    state.update(
                        schema_version=1, item=fw.load_fixture(self.fixture)[0]
                    )
                    state["events"] = [
                        {key: value for key, value in event.items() if key != "change"}
                        for event in state["events"]
                    ]
                    legacy.path.write_text(json.dumps(state))
                original = legacy.path.read_bytes()
                projected = fw.snapshot(json.loads(original))
                fc.upgrade(fc.Store(config), "codex", 12345)
                saved = fc.Store(config).read()
                self.assertEqual(saved["legacy"], json.loads(original))
                self.assertEqual(saved["items"], projected["items"])
                self.assertEqual(saved["sources"], projected["sources"])
                self.assertEqual(
                    saved["collection"], projected.get("collection", fc.empty())
                )

    def test_post_reconciliation_is_scoped_and_survives_cross_host_resume(self):
        self.check_reconciliation_resume("posts", "slack:T/C/123:thread_reply")

    def test_ticket_reconciliation_is_scoped_and_survives_cross_host_resume(self):
        self.check_reconciliation_resume(
            "tickets", "jira:https://example.invalid/SYN-12:transition:31"
        )

    def check_reconciliation_resume(self, action_type, target):
        state = self.start("a")
        operation = self.decision(state, "a", "proposal")
        report = self.root / "authorization.md"
        report.write_text("Synthetic authorization and outgoing payload evidence only")
        scope = {
            "action": action_type,
            "target": target,
            "revision": "synthetic-payload-sha",
        }
        action = {
            "id": "outgoing",
            "scope": scope,
            "status": "proposed",
            "returned_id": None,
            "returned_url": None,
            "evidence": str(report),
        }
        operation["decision"]["item"]["approvals"] = [
            {"id": "permission", "scope": scope, "evidence": str(report)}
        ]
        operation["decision"]["item"]["pending_actions"] = [action]
        state = self.store.mutate("a", "codex", 12345, "save", operation)
        selected = fc.current_run(state, "a")["item_id"]
        uncertain = {**action, "status": "uncertain"}
        reconciliation = {
            "id": "attempt",
            "reason": "Synthetic attempt",
            "item_id": selected,
            "action": uncertain,
        }
        state = self.store.mutate(
            "a",
            "codex",
            12345,
            "reconcile",
            {"id": "attempt", "expected_version": 2, "decision": reconciliation},
        )
        self.start("b")
        with self.assertRaisesRegex(fw.WorkError, "selected active"):
            self.store.mutate(
                "b",
                "codex",
                12345,
                "reconcile",
                {
                    "id": "steal-action",
                    "expected_version": 1,
                    "decision": {**reconciliation, "id": "steal-action"},
                },
            )
        self.change("a", "finish", {"outcome": "stopped"})
        self.store.begin("claude-code", 12345, "resume")
        self.store.mutate(
            "resume",
            "claude-code",
            12345,
            "claim",
            {"id": "resume:claim", "item_id": selected, "expected_version": 3},
        )
        confirmed = {
            **action,
            "status": "confirmed",
            "returned_id": "observed-id",
            "returned_url": "https://example.invalid/observed",
        }
        state = self.store.mutate(
            "resume",
            "claude-code",
            12345,
            "reconcile",
            {
                "id": "confirm",
                "expected_version": 3,
                "decision": {
                    "id": "confirm",
                    "reason": "Synthetic exact postcondition",
                    "item_id": selected,
                    "action": confirmed,
                },
            },
        )
        self.assertEqual(
            state["items"][selected]["pending_actions"][0]["status"], "confirmed"
        )
        self.assertEqual(state["item_versions"][selected], 4)

    def test_actual_processes_compete_for_one_item(self):
        state = self.start("seed")
        selected = fc.current_run(state, "seed")["item_id"]
        self.change("seed", "finish", {"outcome": "stopped"})
        script = self.root / "race.py"
        script.write_text(
            "import sys, time\n"
            f"sys.path.insert(0, {str(ROOT / 'plugins/factory/scripts')!r})\n"
            "import factory_work as fw, factory_concurrent as fc\n"
            "from pathlib import Path\n"
            "fw.verify_owner=lambda pid,harness: {'pid':pid,'started_at':'synthetic','executable':'/synthetic/codex'}\n"
            "fw.plugin_identity=lambda: ('test','race')\n"
            "store=fc.Store(Path(sys.argv[1])); token=sys.argv[2]\n"
            "for n in range(100):\n"
            " try:\n"
            "  store.begin('codex', int(sys.argv[3]), token); break\n"
            " except fw.WorkError as e:\n"
            "  if 'Concurrent state mutation' not in str(e): raise\n"
            "  time.sleep(.01)\n"
            "for n in range(100):\n"
            " try:\n"
            "  store.mutate(token,'codex',int(sys.argv[3]),'claim',{'id':token+':claim','item_id':sys.argv[4],'expected_version':1}); sys.exit(0)\n"
            " except fw.WorkError as e:\n"
            "  if 'Concurrent state mutation' not in str(e): print(e); sys.exit(2)\n"
            "  time.sleep(.01)\n"
            "sys.exit(3)\n"
        )
        processes = [
            subprocess.Popen(
                [
                    sys.executable,
                    str(script),
                    str(self.config),
                    token,
                    str(pid),
                    selected,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            for token, pid in (("race-a", 91001), ("race-b", 91002))
        ]
        outputs = [p.communicate(timeout=20) for p in processes]
        self.assertEqual(sorted(p.returncode for p in processes), [0, 2], outputs)
        self.assertEqual(len(fc.active_items(self.store.read())), 1)

    def test_actual_processes_save_different_items_without_lost_updates(self):
        self.start("seed-a")
        state = self.start("seed-b")
        targets = [
            fc.current_run(state, token)["item_id"] for token in ("seed-a", "seed-b")
        ]
        for token in ("seed-a", "seed-b"):
            self.change(token, "finish", {"outcome": "stopped"})
        script = self.root / "independent.py"
        script.write_text(
            "import sys,time\nfrom pathlib import Path\n"
            f"sys.path.insert(0, {str(ROOT / 'plugins/factory/scripts')!r})\n"
            "import factory_work as fw, factory_concurrent as fc\n"
            "fw.verify_owner=lambda pid,h: {'pid':pid,'started_at':'synthetic','executable':'/synthetic/codex'}\n"
            "fw.plugin_identity=lambda: ('test','independent')\n"
            "store=fc.Store(Path(sys.argv[1])); token=sys.argv[2]; pid=int(sys.argv[3]); item_id=sys.argv[4]\n"
            "def retry(fn):\n"
            " for n in range(200):\n"
            "  try: return fn()\n"
            "  except fw.WorkError as e:\n"
            "   if 'Concurrent state mutation' not in str(e): raise\n"
            "   time.sleep(.005)\n"
            " raise RuntimeError('mutex retry exhausted')\n"
            "retry(lambda:store.begin('codex',pid,token))\n"
            "retry(lambda:store.mutate(token,'codex',pid,'claim',{'id':token+':claim','item_id':item_id,'expected_version':1}))\n"
            "marker=Path(sys.argv[1]).parent/(token+'.ready');marker.write_text('ready')\n"
            "deadline=time.monotonic()+5\n"
            "while len(list(marker.parent.glob('process-*.ready')))<2:\n"
            " if time.monotonic()>deadline: raise RuntimeError('barrier timeout')\n"
            " time.sleep(.005)\n"
            "item=store.read()['items'][item_id];item['next_action']=token+' checkpoint'\n"
            "decision={'id':token+':save','reason':'Synthetic process checkpoint','item':item}\n"
            "retry(lambda:store.mutate(token,'codex',pid,'save',{'id':decision['id'],'expected_version':1,'decision':decision}))\n"
            "retry(lambda:store.mutate(token,'codex',pid,'finish',{'id':token+':finish','outcome':'stopped'}))\n"
        )
        processes = [
            subprocess.Popen(
                [
                    sys.executable,
                    str(script),
                    str(self.config),
                    token,
                    str(pid),
                    item_id,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            for token, pid, item_id in zip(
                ("process-a", "process-b"), (91101, 91102), targets
            )
        ]
        outputs = [p.communicate(timeout=20) for p in processes]
        self.assertEqual([p.returncode for p in processes], [0, 0], outputs)
        state = self.store.read()
        for token, item_id in zip(("process-a", "process-b"), targets):
            self.assertEqual(
                state["items"][item_id]["next_action"], token + " checkpoint"
            )
            self.assertEqual(state["item_versions"][item_id], 2)
        self.assertEqual(fc.active_items(state), {})


if __name__ == "__main__":
    unittest.main()
