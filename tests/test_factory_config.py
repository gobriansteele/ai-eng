from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "factory_config", ROOT / "plugins/factory/scripts/factory_config.py"
)
assert spec and spec.loader
fc = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = fc
spec.loader.exec_module(fc)


class ConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.registry = self.root / "settings" / "ai-eng" / "registry.json"
        environment = patch.dict(
            os.environ, {"XDG_CONFIG_HOME": str(self.root / "settings")}
        )
        environment.start()
        self.addCleanup(environment.stop)
        self.config = self.root / "config.yaml"
        self.repo = self.root / "repos" / "project"
        (self.repo / ".git").mkdir(parents=True)
        self.data = yaml.safe_load((ROOT / "config/example.yaml").read_text())
        self.data["schema_version"] = 1
        self.data["limits"]["active_work_items"] = 1
        self.data.update(
            runtime_path="runtime",
            repositories={"roots": ["repos"], "paths": ["repos/project"]},
        )
        self.data["slack"] = {
            "workspace_id": "T_SYNTHETIC",
            "channels": [{"id": "C_ONE", "name": "one"}],
        }
        self.save()
        self.evidence = self.root / "evidence.json"

    def save(self) -> None:
        self.config.write_text(yaml.safe_dump(self.data))

    def args(self, command="setup", harness="codex"):
        caps = {
            key: {
                "status": "observed",
                "evidence": "Synthetic test observation; no external write executed",
            }
            for key in fc.CAPABILITIES
        }
        caps.update(
            {
                f"slack_channel:{c['id']}": {
                    "status": "observed",
                    "evidence": "Synthetic channel read",
                }
                for c in self.data["slack"]["channels"]
            }
        )
        self.evidence.write_text(json.dumps({"harness": harness, "capabilities": caps}))
        return fc.Arguments(
            command=command,
            config=self.config,
            local=None,
            harness=harness,
            evidence=self.evidence,
            confirm_runtime_change=False,
        )

    def test_chat_only_setup_does_not_require_slack(self) -> None:
        self.data["slack"] = {"workspace_id": None, "channels": []}
        self.save()
        args = self.args()
        evidence = json.loads(self.evidence.read_text())
        for key, value in evidence["capabilities"].items():
            if key.startswith("slack_"):
                value.update(status="unavailable", evidence="Slack not connected")
        self.evidence.write_text(json.dumps(evidence))
        result = fc.run(args)
        self.assertEqual(result["setup_status"], "ready")
        self.assertIsNone(result["effective_config"]["intake"]["start_at"])
        self.assertEqual(
            result["capability_report"]["capabilities"]["slack_connection"]["status"],
            "unavailable",
        )
        self.assertEqual(fc.run(self.args("status"))["setup_status"], "ready")

    def test_unknown_version_duplicate_and_missing_runtime_rejected(self) -> None:
        for key, value in (("schema_version", 2), ("fix_round", 9)):
            data = deepcopy(self.data)
            data[key] = value
            self.config.write_text(yaml.safe_dump(data))
            with self.assertRaises(fc.ConfigError):
                fc.load_config(self.config)
        data.pop("fix_round")
        data.pop("runtime_path")
        self.config.write_text(yaml.safe_dump(data))
        with self.assertRaises(fc.ConfigError):
            fc.load_config(self.config)
        self.save()
        self.config.write_text(self.config.read_text() + "factory_id: duplicate\n")
        with self.assertRaises(fc.ConfigError):
            fc.load_config(self.config)
        self.assertFalse((self.root / "runtime").exists())

    def test_relative_paths_and_local_override_are_file_relative(self) -> None:
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()
        local = elsewhere / "local.yaml"
        local.write_text(
            "runtime_path: ../custom-runtime\nrepositories:\n  paths: [../repos/project]\n"
        )
        cwd = Path.cwd()
        try:
            os.chdir("/private/tmp")
            result = fc.load_config(self.config, local)
        finally:
            os.chdir(cwd)
        self.assertEqual(result["runtime_path"], str(self.root / "custom-runtime"))
        self.assertEqual(result["repositories"]["paths"], [str(self.repo)])
        local.write_text("limits: {fix_rounds: 8}\n")
        with self.assertRaises(fc.ConfigError):
            fc.load_config(self.config, local)

    def test_factory_home_setup_and_status_from_another_directory(self) -> None:
        self.data["runtime_path"] = "./runtime"
        self.save()
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()
        args = self.args()
        args.config = Path("../config.yaml")
        cwd = Path.cwd()
        try:
            os.chdir(elsewhere)
            setup = fc.run(args)
            args.command = "status"
            status = fc.run(args)
        finally:
            os.chdir(cwd)
        self.assertEqual(setup["setup_status"], "ready")
        self.assertEqual(status["runtime_path"], str(self.root / "runtime"))
        self.assertEqual(status["capability_report"], setup["capability_report"])
        self.assertTrue((self.root / ".config.yaml.factory-setup.json").is_file())
        self.assertTrue((self.root / "runtime/setup/example").is_dir())
        self.assertFalse((elsewhere / "runtime").exists())
        self.assertEqual(
            yaml.safe_load(self.config.read_text())["runtime_path"], "./runtime"
        )

    def test_separate_config_and_local_runtime_setup(self) -> None:
        overrides = self.root / "overrides"
        overrides.mkdir()
        local = overrides / "paths.yaml"
        local.write_text("runtime_path: ../separate-runtime\n")
        args = self.args()
        args.local = local
        setup = fc.run(args)
        args.command = "status"
        status = fc.run(args)
        self.assertEqual(status["setup_status"], "ready")
        self.assertEqual(setup["runtime_path"], str(self.root / "separate-runtime"))
        self.assertEqual(status["capability_report"], setup["capability_report"])
        self.assertTrue((self.root / "separate-runtime/setup/example").is_dir())
        self.assertFalse((self.root / "runtime").exists())
        self.assertEqual(
            yaml.safe_load(self.config.read_text())["runtime_path"], "runtime"
        )

    def test_escape_rejected_and_discovery_skips_symlinks(self) -> None:
        outside = self.root / "outside"
        (outside / ".git").mkdir(parents=True)
        (self.root / "repos" / "escape").symlink_to(outside, target_is_directory=True)
        self.data["repositories"]["paths"] = ["repos/escape"]
        self.save()
        with self.assertRaises(fc.ConfigError):
            fc.load_config(self.config)
        self.data["repositories"]["paths"] = []
        self.save()
        self.assertEqual(
            fc.discover(fc.load_config(self.config))["repositories"], [str(self.repo)]
        )

    def test_missing_repositories_partial_without_discarding_choice(self) -> None:
        self.data["repositories"]["roots"] = ["missing"]
        self.data["repositories"]["paths"] = []
        self.save()
        result = fc.run(self.args())
        self.assertEqual(result["setup_status"], "partial")
        self.assertEqual(
            result["effective_config"]["repositories"]["roots"],
            [str(self.root / "missing")],
        )

    def test_rerun_handoff_channel_changes_preserve_all_runtime(self) -> None:
        first = fc.run(self.args())
        self.assertEqual(first["setup_status"], "ready")
        runtime = self.root / "runtime"
        arbitrary = runtime / "state" / "cursors.json"
        arbitrary.parent.mkdir()
        arbitrary.write_text('{"C_ONE":"unchanged"}')
        work = runtime / "work.json"
        work.write_text(
            '{"fix_rounds":2,"pending_actions":["preserve"],"approvals":["scoped"]}'
        )
        starts_path = runtime / "setup/example/channel-starts.json"
        initial = json.loads(starts_path.read_text())
        self.data = yaml.safe_load(self.config.read_text())
        self.data["slack"]["channels"] = [{"id": "C_TWO", "name": "two"}]
        self.save()
        second = fc.run(self.args(harness="claude-code"))
        starts = json.loads(starts_path.read_text())
        self.assertEqual(starts["T_SYNTHETIC:C_ONE"], initial["T_SYNTHETIC:C_ONE"])
        self.assertGreater(starts["T_SYNTHETIC:C_TWO"], starts["T_SYNTHETIC:C_ONE"])
        self.assertEqual(
            second["effective_config"]["intake"], first["effective_config"]["intake"]
        )
        self.assertEqual(arbitrary.read_text(), '{"C_ONE":"unchanged"}')
        self.assertEqual(
            work.read_text(),
            '{"fix_rounds":2,"pending_actions":["preserve"],"approvals":["scoped"]}',
        )
        self.assertEqual(len(list(starts_path.parent.glob("*-*.json"))), 3)
        status = fc.run(self.args("status", "codex"))
        self.assertIsNone(status["capability_report"])

    def test_unavailable_channel_never_ready_or_started(self) -> None:
        args = self.args()
        evidence = json.loads(self.evidence.read_text())
        evidence["capabilities"]["slack_channel:C_ONE"]["status"] = "unavailable"
        self.evidence.write_text(json.dumps(evidence))
        result = fc.run(args)
        self.assertEqual(result["setup_status"], "partial")
        self.assertIsNone(result["effective_config"]["intake"]["start_at"])
        self.assertFalse(
            (self.root / "runtime/setup/example/channel-starts.json").exists()
        )

    def test_runtime_change_requires_explicit_choice_and_preserves_old(self) -> None:
        fc.run(self.args())
        marker = self.root / "runtime" / "keep.txt"
        marker.write_text("old runtime record")
        self.data = yaml.safe_load(self.config.read_text())
        self.data["runtime_path"] = "other-runtime"
        self.save()
        args = self.args()
        with self.assertRaisesRegex(fc.ConfigError, "Runtime path changed"):
            fc.run(args)
        self.assertFalse((self.root / "other-runtime").exists())
        args.confirm_runtime_change = True
        fc.run(args)
        self.assertEqual(marker.read_text(), "old runtime record")
        self.assertTrue((self.root / "other-runtime/setup").exists())

    def test_intake_start_is_managed_and_cannot_be_rewound(self) -> None:
        fc.run(self.args())
        self.data = yaml.safe_load(self.config.read_text())
        established = self.data["intake"]["start_at"]
        self.data["intake"]["start_at"] = None
        self.save()
        with self.assertRaisesRegex(fc.ConfigError, "system-managed"):
            fc.run(self.args())
        self.data["intake"]["start_at"] = established
        self.save()
        self.assertEqual(fc.run(self.args())["setup_status"], "ready")

    def test_runtime_inside_target_repository_is_rejected(self) -> None:
        self.data["runtime_path"] = "repos/project/runtime"
        self.save()
        with self.assertRaisesRegex(fc.ConfigError, "durable"):
            fc.load_config(self.config)
        self.assertFalse((self.repo / "runtime").exists())

    def test_saved_timestamp_cannot_be_null(self) -> None:
        fc.run(self.args())
        report_path = next((self.root / "runtime/setup/example").glob("codex-*.json"))
        report = json.loads(report_path.read_text())
        report["checked_at"] = None
        report_path.write_text(json.dumps(report))
        with self.assertRaisesRegex(fc.ConfigError, "quoted ISO"):
            fc.run(self.args("status"))

    def test_corrupt_starts_not_reset(self) -> None:
        fc.run(self.args())
        path = self.root / "runtime/setup/example/channel-starts.json"
        path.write_text("corrupt")
        with self.assertRaisesRegex(fc.ConfigError, "repair"):
            fc.run(self.args())
        self.assertEqual(path.read_text(), "corrupt")

    def test_first_setup_registers_absolute_identity_restrictively(self) -> None:
        result = fc.run(self.args())
        self.assertEqual(
            json.loads(self.registry.read_text()),
            {
                "schema_version": 1,
                "default_config": str(self.config),
                "default_local": None,
            },
        )
        self.assertEqual(self.registry.stat().st_mode & 0o777, 0o600)
        self.assertEqual(result["config_path"], str(self.config))
        self.assertEqual(result["source"], "explicit")
        self.assertEqual(result["factory_id"], "example")

    def test_no_config_status_and_setup_across_harnesses(self) -> None:
        setup = fc.run(self.args())
        args = self.args("status")
        args.config = None
        status = fc.run(args)
        self.assertEqual(status["source"], "registry")
        self.assertEqual(status["capability_report"], setup["capability_report"])
        args.harness = "claude-code"
        self.assertIsNone(fc.run(args)["capability_report"])
        other = self.args(harness="claude-code")
        other.config = None
        fc.run(other)
        self.assertEqual(fc.run(args)["setup_status"], "ready")
        args.harness = "codex"
        self.assertEqual(fc.run(args)["setup_status"], "ready")

    def second_config(self) -> Path:
        path = self.root / "second" / "config.yaml"
        path.parent.mkdir(exist_ok=True)
        data = deepcopy(self.data)
        data["factory_id"] = "second"
        data["repositories"] = {"roots": ["../repos"], "paths": ["../repos/project"]}
        path.write_text(yaml.safe_dump(data))
        return path

    def test_second_setup_preserves_default_until_explicit_switch(self) -> None:
        fc.run(self.args())
        before = self.registry.read_bytes()
        args = self.args()
        args.config = self.second_config()
        second = fc.run(args)
        self.assertEqual(second["factory_id"], "second")
        self.assertEqual(self.registry.read_bytes(), before)
        self.assertEqual(fc.resolve_config()["config_path"], str(self.config))
        args.set_default = True
        fc.run(args)
        self.assertEqual(fc.resolve_config()["config_path"], str(args.config))
        self.assertEqual(fc.resolve_config()["factory_id"], "second")

    def test_remembered_local_and_unrelated_explicit_override(self) -> None:
        local = self.root / "local.yaml"
        local.write_text("runtime_path: local-runtime\n")
        args = self.args()
        args.local = local
        fc.run(args)
        resolved = fc.resolve_config()
        self.assertEqual(resolved["local_path"], str(local))
        self.assertEqual(resolved["runtime_path"], str(self.root / "local-runtime"))
        status = self.args("status")
        status.config = None
        self.assertEqual(fc.run(status)["setup_status"], "ready")
        explicit = fc.resolve_config(self.second_config())
        self.assertIsNone(explicit["local_path"])
        self.assertEqual(explicit["runtime_path"], str(self.root / "second/runtime"))
        explicit = fc.resolve_config(self.config)
        self.assertIsNone(explicit["local_path"])
        override = self.root / "another-local.yaml"
        override.write_text("runtime_path: another-runtime\n")
        self.assertEqual(
            fc.resolve_config(local=override)["runtime_path"],
            str(self.root / "another-runtime"),
        )

    def test_same_config_local_change_does_not_silently_replace_default(self) -> None:
        fc.run(self.args())
        before = self.registry.read_bytes()
        local = self.root / "local.yaml"
        local.write_text("runtime_path: another-runtime\n")
        args = self.args()
        args.local = local
        with self.assertRaisesRegex(fc.ConfigError, "Runtime path changed"):
            fc.run(args)
        self.assertEqual(self.registry.read_bytes(), before)
        args.confirm_runtime_change = True
        fc.run(args)
        self.assertEqual(self.registry.read_bytes(), before)
        args.set_default = True
        fc.run(args)
        self.assertEqual(fc.resolve_config()["local_path"], str(local))

    def test_explicit_read_commands_bypass_unrelated_corrupt_registry(self) -> None:
        self.registry.parent.mkdir(parents=True)
        self.registry.write_text("broken")
        before = self.registry.read_bytes()
        for command in ("resolve-config", "validate", "discover", "status"):
            with self.subTest(command=command):
                result = fc.run(self.args(command))
                self.assertIsInstance(result, dict)
        self.assertEqual(self.registry.read_bytes(), before)
        self.assertFalse((self.root / "runtime").exists())

    def test_conventional_fallback_only_when_registry_absent(self) -> None:
        home = self.root / "home"
        conventional = home / "factories/default/config.yaml"
        conventional.parent.mkdir(parents=True)
        data = deepcopy(self.data)
        data["repositories"] = {
            "roots": [str(self.repo.parent)],
            "paths": [str(self.repo)],
        }
        conventional.write_text(yaml.safe_dump(data))
        with patch.object(fc.Path, "home", return_value=home):
            resolved = fc.resolve_config()
            self.assertEqual(resolved["config_path"], str(conventional))
            self.assertEqual(resolved["source"], "conventional")
            self.assertFalse(self.registry.parent.exists())
            self.registry.parent.mkdir(parents=True)
            self.registry.write_text("broken")
            with self.assertRaisesRegex(fc.ConfigError, "Registry needs repair"):
                fc.resolve_config()
            self.registry.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "default_config": str(self.root / "missing.yaml"),
                        "default_local": None,
                    }
                )
            )
            with self.assertRaisesRegex(fc.ConfigError, "factory-setup"):
                fc.resolve_config()

    def test_missing_default_directs_setup_without_writes(self) -> None:
        with patch.object(fc.Path, "home", return_value=self.root / "home"):
            with self.assertRaisesRegex(fc.ConfigError, "factory-setup"):
                fc.resolve_config()
        self.assertFalse(self.registry.parent.exists())
        self.assertFalse((self.root / "home").exists())

    def test_registry_invalid_schema_duplicate_keys_and_stale_local_stop(self) -> None:
        self.registry.parent.mkdir(parents=True)
        cases = [
            "{",
            '{"schema_version":1,"schema_version":1,"default_config":"/tmp/config","default_local":null}',
            json.dumps(
                {
                    "schema_version": True,
                    "default_config": str(self.config),
                    "default_local": None,
                }
            ),
            json.dumps(
                {
                    "schema_version": 1,
                    "default_config": "relative",
                    "default_local": None,
                }
            ),
            json.dumps(
                {
                    "schema_version": 1,
                    "default_config": str(self.config),
                    "default_local": str(self.root / "missing.yaml"),
                }
            ),
        ]
        for text in cases:
            with self.subTest(text=text):
                self.registry.write_text(text)
                with self.assertRaises(fc.ConfigError):
                    fc.resolve_config()
                self.assertEqual(self.registry.read_text(), text)
        self.assertFalse((self.root / "runtime").exists())

    def test_unreadable_registry_stops_without_fallback(self) -> None:
        original = fc.Path.read_text

        def read(path, *args, **kwargs):
            if path == self.registry:
                raise PermissionError("synthetic unreadable registry")
            return original(path, *args, **kwargs)

        with patch.object(fc.Path, "read_text", read):
            with self.assertRaisesRegex(fc.ConfigError, "Registry needs repair"):
                fc.resolve_config()

    def test_broken_or_stale_registry_setup_requires_deliberate_repair(self) -> None:
        self.registry.parent.mkdir(parents=True)
        for text in (
            "broken",
            json.dumps(
                {
                    "schema_version": 1,
                    "default_config": str(self.root / "missing.yaml"),
                    "default_local": None,
                }
            ),
        ):
            self.registry.write_text(text)
            args = self.args()
            with self.assertRaisesRegex(fc.ConfigError, "--set-default"):
                fc.run(args)
            self.assertEqual(self.registry.read_text(), text)
            self.assertFalse((self.root / "runtime").exists())
        args.set_default = True
        fc.run(args)
        self.assertEqual(fc.resolve_config()["config_path"], str(self.config))

    def test_resolution_and_status_are_read_only_and_keep_existing_runtime(
        self,
    ) -> None:
        fc.run(self.args())
        marker = self.root / "runtime/work.json"
        marker.write_text('{"durable":"unchanged"}')
        before = {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        fc.run(fc.Arguments(command="resolve-config"))
        for harness in fc.HARNESSES:
            fc.run(fc.Arguments(command="status", harness=harness))
        after = {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(after, before)

    def test_failed_setup_never_registers_or_replaces_default(self) -> None:
        args = self.args()
        self.evidence.write_text("broken")
        with self.assertRaises(fc.ConfigError):
            fc.run(args)
        self.assertFalse(self.registry.exists())
        self.assertFalse((self.root / "runtime").exists())
        fc.run(self.args())
        before = self.registry.read_bytes()
        args = self.args()
        args.config = self.second_config()
        args.set_default = True
        self.evidence.write_text("broken")
        with self.assertRaises(fc.ConfigError):
            fc.run(args)
        self.assertEqual(self.registry.read_bytes(), before)

    def test_explicit_registry_is_isolated_and_set_default_only_for_setup(self) -> None:
        registry = self.root / "isolated" / "registry.json"
        args = self.args()
        args.registry = registry
        fc.run(args)
        self.assertFalse(self.registry.exists())
        self.assertEqual(
            fc.resolve_config(registry=registry)["config_path"], str(self.config)
        )
        args.command = "validate"
        args.set_default = True
        with self.assertRaisesRegex(fc.ConfigError, "only by setup"):
            fc.run(args)

    def test_dangling_registry_symlink_never_falls_back_or_overwrites(self) -> None:
        self.registry.parent.mkdir(parents=True)
        missing = self.root / "missing-registry.json"
        self.registry.symlink_to(missing)
        with self.assertRaisesRegex(fc.ConfigError, "Registry needs repair"):
            fc.resolve_config()
        with self.assertRaisesRegex(fc.ConfigError, "Registry needs repair"):
            fc.run(self.args())
        self.assertTrue(self.registry.is_symlink())
        self.assertFalse(missing.exists())
        args = self.args()
        args.set_default = True
        fc.run(args)
        self.assertFalse(self.registry.is_symlink())
        self.assertFalse(missing.exists())
        self.assertEqual(fc.resolve_config()["config_path"], str(self.config))

    def test_registry_cannot_overwrite_config_local_or_lock(self) -> None:
        args = self.args()
        args.set_default = True
        for path in (self.config, self.config.with_name(".config.yaml.lock")):
            with self.subTest(path=path):
                if path != self.config:
                    args.config = path
                    path.write_bytes(self.config.read_bytes())
                    args.registry = self.config
                else:
                    args.config = self.config
                    args.registry = self.config
                before = args.config.read_bytes()
                with self.assertRaisesRegex(fc.ConfigError, "must be separate"):
                    fc.run(args)
                self.assertEqual(args.config.read_bytes(), before)
        args.config = self.config
        local = self.root / "local.yaml"
        local.write_text("runtime_path: local-runtime\n")
        args.local = local
        args.registry = local
        before = local.read_bytes()
        with self.assertRaisesRegex(fc.ConfigError, "must be separate"):
            fc.run(args)
        self.assertEqual(local.read_bytes(), before)

    def test_failed_registry_replace_preserves_existing_default(self) -> None:
        fc.run(self.args())
        before = self.registry.read_bytes()
        args = self.args()
        args.config = self.second_config()
        args.set_default = True
        original_replace = fc.os.replace

        def replace(source, destination):
            if destination == self.registry:
                raise PermissionError("synthetic atomic replacement failure")
            return original_replace(source, destination)

        with patch.object(fc.os, "replace", replace):
            with self.assertRaisesRegex(fc.ConfigError, "Cannot update registry"):
                fc.run(args)
        self.assertEqual(self.registry.read_bytes(), before)
        self.assertEqual(len(list(self.registry.parent.glob(".registry.json.*"))), 1)

    def test_registry_with_invalid_encoding_stops_clearly(self) -> None:
        self.registry.parent.mkdir(parents=True)
        self.registry.write_bytes(b"\xff")
        with self.assertRaisesRegex(fc.ConfigError, "Registry needs repair"):
            fc.resolve_config()

    def test_invalid_selected_config_never_uses_another_factory(self) -> None:
        fc.run(self.args())
        other = self.second_config()
        other.write_text("schema_version: 1\n")
        with self.assertRaisesRegex(fc.ConfigError, "Cannot resolve explicit"):
            fc.resolve_config(other)
        other.write_bytes(b"\xff")
        with self.assertRaisesRegex(fc.ConfigError, "Cannot resolve explicit"):
            fc.resolve_config(other)
        self.assertEqual(fc.resolve_config()["config_path"], str(self.config))
        self.config.write_text("broken: mapping\n")
        with self.assertRaisesRegex(fc.ConfigError, "Cannot resolve registry"):
            fc.resolve_config()

    def test_concurrent_first_setups_keep_one_complete_default(self) -> None:
        first = self.args()
        second = self.args()
        second.config = self.second_config()
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(fc.run, (first, second)))
        registered = fc.resolve_config()
        self.assertIn(
            registered["config_path"], {result["config_path"] for result in results}
        )
        self.assertEqual(json.loads(self.registry.read_text())["schema_version"], 1)
        self.assertEqual(len(list(self.registry.parent.glob(".registry.json.*"))), 1)


if __name__ == "__main__":
    unittest.main()
