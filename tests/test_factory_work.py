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
