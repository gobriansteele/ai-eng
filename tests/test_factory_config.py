from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

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
        self.config = self.root / "config.yaml"
        self.repo = self.root / "repos" / "project"
        (self.repo / ".git").mkdir(parents=True)
        self.data = yaml.safe_load((ROOT / "config/example.yaml").read_text())
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


if __name__ == "__main__":
    unittest.main()
