from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "plugins/factory/scripts"
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location(
    "factory_learning", SCRIPTS / "factory_learning.py"
)
assert spec and spec.loader
learning = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = learning
spec.loader.exec_module(learning)


class LearningTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.root = self.base / "runtime/retros/candidates"
        self.evidence = self.base / "outcome.txt"
        self.evidence.write_text("User: continue. Agent: implementation resumed.\n")
        self.observation = {
            "id": "run-one-continuation",
            "key": "routine-continuation-question",
            "kind": "observation",
            "details": {
                "summary": "Run waited for an unnecessary continuation reply",
                "trigger": "Implementation was authorized and access was available",
                "expected_behavior": "Continue to the authorized endpoint",
                "source_version": "synthetic-0.18.0",
            },
            "evidence": [str(self.evidence)],
        }

    def event(self, identity, kind, details):
        value = deepcopy(self.observation)
        value.update(id=identity, kind=kind, details=details)
        return value

    def adjudicate(self, disposition="accepted"):
        return learning.record(
            self.root,
            self.event(
                "adjudication-one",
                "adjudication",
                {
                    "disposition": disposition,
                    "reason": "The source shows authority and available access",
                    "acceptance_scenario": "Resume an authorized run without another question",
                },
            ),
        )

    def evaluate(
        self,
        outcome="passed",
        identity="evaluation-one",
        change="synthetic-revision-two",
    ):
        return learning.record(
            self.root,
            self.event(
                identity,
                "evaluation",
                {
                    "outcome": outcome,
                    "change": change,
                    "reason": "Fresh synthetic worker output is retained",
                },
            ),
        )

    def test_retry_and_concurrent_runs_accumulate_one_candidate(self) -> None:
        first = learning.record(self.root, self.observation)
        self.assertTrue(first["changed"])
        original = Path(first["path"]).read_bytes()
        self.assertFalse(learning.record(self.root, self.observation)["changed"])
        self.assertEqual(Path(first["path"]).read_bytes(), original)

        def observe(index):
            event = deepcopy(self.observation)
            event["id"] = f"run-{index}"
            return learning.record(self.root, event)

        with ThreadPoolExecutor(max_workers=4) as executor:
            list(executor.map(observe, range(8)))
        inspected = learning.inspect(self.root)
        self.assertEqual(len(inspected), 1)
        self.assertEqual(len(inspected[0]["candidate"]["events"]), 9)
        self.assertEqual(inspected[0]["status"], "open")

    def test_reused_identity_with_changed_content_or_evidence_fails(self) -> None:
        learning.record(self.root, self.observation)
        path = self.root / "routine-continuation-question.json"
        before = path.read_bytes()
        changed = deepcopy(self.observation)
        changed["details"]["summary"] = "Different issue"
        with self.assertRaisesRegex(learning.ConfigError, "reused"):
            learning.record(self.root, changed)
        self.evidence.write_text("Changed source bytes")
        with self.assertRaisesRegex(learning.ConfigError, "reused"):
            learning.record(self.root, self.observation)
        self.assertEqual(path.read_bytes(), before)

    def test_summary_inventory_omits_history_and_keeps_deduplication_context(
        self,
    ) -> None:
        learning.record(self.root, self.observation)
        self.adjudicate()
        summary = learning.inspect(self.root, summary=True)[0]
        self.assertNotIn("candidate", summary)
        self.assertEqual(summary["key"], self.observation["key"])
        self.assertEqual(summary["event_count"], 2)
        self.assertEqual(summary["status"], "accepted")
        self.assertEqual(summary["unreviewed_observations"], 0)
        self.assertEqual(
            summary["latest_summary"], self.observation["details"]["summary"]
        )
        full = learning.inspect(self.root, self.observation["key"])[0]
        self.assertEqual(len(full["candidate"]["events"]), 2)

    def test_rejection_survives_resume_and_new_observation(self) -> None:
        learning.record(self.root, self.observation)
        self.adjudicate("rejected")
        repeated = deepcopy(self.observation)
        repeated["id"] = "run-two"
        learning.record(self.root, repeated)
        current = learning.inspect(self.root, self.observation["key"])[0]
        self.assertEqual(current["status"], "rejected")
        self.assertEqual(len(current["candidate"]["events"]), 3)
        with self.assertRaisesRegex(learning.ConfigError, "accepted"):
            self.evaluate()

    def test_historical_evidence_does_not_claim_regression_after_verified_fix(
        self,
    ) -> None:
        learning.record(self.root, self.observation)
        self.adjudicate()
        self.assertEqual(self.evaluate()["status"], "verified")
        historical = deepcopy(self.observation)
        historical["id"] = "historical-run"
        recorded = learning.record(self.root, historical)
        self.assertEqual(recorded["status"], "verified")
        self.assertEqual(recorded["unreviewed_observations"], 1)
        self.assertEqual(
            self.evaluate("failed", "evaluation-two")["status"], "regressed"
        )
        self.assertEqual(
            self.evaluate("inconclusive", "evaluation-three")["status"], "accepted"
        )
        self.assertEqual(len(learning.inspect(self.root)[0]["candidate"]["events"]), 6)

    def test_malformed_kind_is_a_validation_error(self) -> None:
        for value in ([], {}, 1, None):
            malformed = deepcopy(self.observation)
            malformed["kind"] = value
            with self.assertRaisesRegex(learning.ConfigError, "kind must be"):
                learning.record(self.root, malformed)
        self.assertFalse(self.root.exists())

    def test_inconclusive_new_change_does_not_reuse_prior_verified_status(self) -> None:
        learning.record(self.root, self.observation)
        self.adjudicate()
        self.assertEqual(self.evaluate()["status"], "verified")
        result = self.evaluate(
            "inconclusive", "evaluation-next", "synthetic-revision-three"
        )
        self.assertEqual(result["status"], "accepted")
        self.assertEqual(
            result["candidate"]["events"][-2]["details"]["outcome"], "passed"
        )

    def test_cli_uses_pinned_local_runtime_and_does_not_touch_work_state(self) -> None:
        config = self.base / "config.yaml"
        config.write_text((SCRIPTS.parents[2] / "config/example.yaml").read_text())
        local = self.base / "local.yaml"
        local.write_text("runtime_path: alternate-runtime\n")
        event = self.base / "event.json"
        event.write_text(json.dumps(self.observation))
        command = [
            sys.executable,
            str(SCRIPTS / "factory_learning.py"),
            "record",
            "--config",
            str(config),
            "--local",
            str(local),
            "--input",
            str(event),
        ]
        completed = subprocess.run(command, text=True, capture_output=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(
            Path(result["path"]).parents[2], self.base / "alternate-runtime"
        )
        self.assertFalse((self.base / "runtime").exists())
        self.assertFalse((self.base / "alternate-runtime/state").exists())

    def test_missing_evidence_and_out_of_order_updates_preserve_state(self) -> None:
        bad = deepcopy(self.observation)
        bad["evidence"] = [str(self.base / "missing.txt")]
        with self.assertRaisesRegex(learning.ConfigError, "Cannot read evidence"):
            learning.record(self.root, bad)
        self.assertFalse(self.root.exists())
        with self.assertRaisesRegex(learning.ConfigError, "observation must precede"):
            self.adjudicate()
        self.assertEqual(list(self.root.glob("*.json")), [])
        learning.record(self.root, self.observation)
        with self.assertRaisesRegex(learning.ConfigError, "accepted"):
            self.evaluate()
        self.assertEqual(len(learning.inspect(self.root)[0]["candidate"]["events"]), 1)

    def test_corrupt_saved_records_are_not_overwritten(self) -> None:
        learning.record(self.root, self.observation)
        path = self.root / "routine-continuation-question.json"
        data = json.loads(path.read_text())
        data["events"].append(data["events"][0])
        path.write_text(json.dumps(data))
        before = path.read_bytes()
        with self.assertRaisesRegex(learning.ConfigError, "Duplicate saved event"):
            learning.record(self.root, self.observation)
        self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
