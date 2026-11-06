from __future__ import annotations

import json
import unittest
from copy import deepcopy

import test_factory_route as route_tests
import test_factory_work as work_tests
import yaml

fw = work_tests.fw
fs = route_tests.fs
ROOT = work_tests.ROOT


def direct_source(synthetic=False):
    return {
        "synthetic": synthetic,
        "source_id": "direct:request-one",
        "version": "capture-one",
        "link": "direct:request-one",
        "available_thread": [
            {
                "id": "direct:request-one",
                "author": "user",
                "text": "Users lose their filters when they return to results. Investigate this.",
            }
        ],
        "availability": "Current request only; chat identifier unavailable",
        "evidence": [],
        "direct": {
            "harness": "codex",
            "conversation_id": None,
            "request_id": "request-one",
            "received_at": "2026-01-01T12:00:00+00:00",
            "trigger_message_ids": ["direct:request-one"],
        },
    }


class DirectTests(unittest.TestCase):
    setUp = work_tests.WorkTests.setUp
    route_operation = route_tests.RouteTests.route_operation

    def begin_request(self, value=None, token="direct-run", harness="codex"):
        path = self.root / "request.json"
        path.write_text(json.dumps(direct_source() if value is None else value))
        return self.store.begin(harness, 12345, token, None, request_path=path)

    def route_request(self, state, token="direct-run", existing=None):
        operation = self.route_operation(state, existing=existing)
        saved = state["sources"][operation["receipt_id"]]["source"]
        if existing is None:
            operation["items"][0]["synthetic"] = saved["synthetic"]
        return self.store.route(token, "codex", 12345, state["revision"], operation)

    def test_live_request_without_slack_routes_and_resumes_across_hosts(self):
        initial = self.begin_request()
        self.assertEqual(initial["invocations"][-1]["steps"], 0)
        self.assertEqual(self.store.watch_plan()["blocked"], [])
        self.assertEqual(self.store.watch_plan()["channels"], [])
        self.assertEqual(self.begin_request(), initial)
        saved = self.route_request(initial)
        selected = saved["active_item_id"]
        self.assertFalse(saved["items"][selected]["synthetic"])
        self.assertEqual(saved["items"][selected]["approvals"], [])
        self.store.finish("direct-run", "codex", 12345, "step_limit")
        replay = self.begin_request(token="resume", harness="claude-code")
        self.assertEqual(replay["sources"], saved["sources"])
        self.assertEqual(replay["items"], saved["items"])
        self.assertEqual(sum(e["kind"] == "route" for e in replay["events"]), 1)

    def test_followup_attaches_without_resetting_prior_evidence(self):
        saved = self.route_request(self.begin_request())
        selected = saved["active_item_id"]
        updated = deepcopy(saved["items"][selected])
        updated["artifact_paths"] = {"investigation": str(self.root / "report.md")}
        updated["fix_rounds"] = 1
        saved = self.store.save(
            "direct-run",
            "codex",
            12345,
            saved["revision"],
            {
                "id": "prior-work",
                "reason": "Controlled prior evidence",
                "item": updated,
            },
        )
        self.store.finish("direct-run", "codex", 12345, "step_limit")
        followup = direct_source()
        followup["version"] = "capture-two"
        followup["available_thread"].append(
            {
                "id": "answer-one",
                "author": "user",
                "text": "Only the status filter is lost.",
            }
        )
        followup["direct"]["trigger_message_ids"] = ["answer-one"]
        resumed = self.begin_request(followup, "followup")
        result = self.route_request(resumed, "followup", selected)
        self.assertEqual(len(result["sources"]), 2)
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(
            result["items"][selected]["artifact_paths"], updated["artifact_paths"]
        )
        self.assertEqual(result["items"][selected]["fix_rounds"], 1)

    def test_conflicting_capture_is_refused_without_mutation(self):
        self.begin_request()
        self.store.finish("direct-run", "codex", 12345, "step_limit")
        before = self.store.path.read_bytes()
        changed = direct_source()
        changed["available_thread"][0]["text"] = "Replacement request"
        with self.assertRaisesRegex(fw.WorkError, "immutable source version"):
            self.begin_request(changed, "conflict")
        self.assertEqual(self.store.path.read_bytes(), before)

    def test_direct_and_slack_collection_share_a_run_and_keep_both_sources(self):
        observation = fw.read_json(ROOT / "plugins/factory/fixtures/watch/first.json")
        data = yaml.safe_load(self.config.read_text())
        data["slack"] = {
            "workspace_id": observation["workspace_id"],
            "channels": [{"id": observation["channel_id"], "name": "synthetic"}],
        }
        self.config.write_text(yaml.safe_dump(data))
        self.store = fw.Store(self.config)
        starts = self.store.runtime / "setup/example/channel-starts.json"
        starts.parent.mkdir(parents=True)
        starts.write_text(
            json.dumps(
                {
                    f"{observation['workspace_id']}:{observation['channel_id']}": observation[
                        "start_at"
                    ]
                }
            )
        )
        initial = self.begin_request(direct_source(synthetic=True))
        collected = self.store.collect(
            "direct-run", "codex", 12345, initial["revision"], observation
        )
        self.assertEqual(len(collected["sources"]), 3)
        direct_receipt = fs.receipt_id(direct_source(synthetic=True))
        self.assertEqual(
            collected["sources"][direct_receipt], initial["sources"][direct_receipt]
        )
        direct_routed = self.route_request(collected)
        operation = self.route_operation(
            direct_routed, existing=direct_routed["active_item_id"]
        )
        both_routed = self.store.route(
            "direct-run", "codex", 12345, direct_routed["revision"], operation
        )
        operation = self.route_operation(both_routed, disposition="no_action")
        both_routed = self.store.route(
            "direct-run", "codex", 12345, both_routed["revision"], operation
        )
        self.assertEqual(len(both_routed["items"]), 1)
        self.assertTrue(
            all(r["routing"] is not None for r in both_routed["sources"].values())
        )
        self.assertEqual(both_routed["collection"], collected["collection"])

    def test_failed_collection_does_not_discard_direct_request(self):
        initial = self.begin_request()
        with self.assertRaisesRegex(fw.WorkError, "configured workspace/channel"):
            self.store.collect(
                "direct-run",
                "codex",
                12345,
                initial["revision"],
                fw.read_json(ROOT / "plugins/factory/fixtures/watch/first.json"),
            )
        self.assertEqual(self.store.read(), initial)
        self.assertEqual(len(self.route_request(initial)["items"]), 1)

    def test_invalid_provenance_and_entry_paths_are_rejected(self):
        valid = direct_source()
        for key, value in (
            ("harness", "invented"),
            ("received_at", "yesterday"),
            ("request_id", "another"),
            ("trigger_message_ids", []),
            ("trigger_message_ids", ["missing-message"]),
        ):
            with self.subTest(key=key, value=value):
                bad = deepcopy(valid)
                bad["direct"][key] = value
                with self.assertRaises(fw.ConfigError):
                    fs.source(bad)
        bad = deepcopy(valid)
        bad["intake"] = {}
        with self.assertRaisesRegex(fw.ConfigError, "one intake surface"):
            fs.source(bad)
        path = self.root / "request.json"
        path.write_text(json.dumps(valid))
        with self.assertRaisesRegex(fw.WorkError, "synthetic input"):
            self.store.begin("codex", 12345, "wrong-source", None, source_path=path)
        with self.assertRaisesRegex(fw.WorkError, "multiple inputs"):
            self.store.begin("codex", 12345, "both", self.fixture, request_path=path)
        path.write_text(
            (ROOT / "plugins/factory/fixtures/sources/open-ticket.json").read_text()
        )
        with self.assertRaisesRegex(fw.WorkError, "direct harness"):
            self.store.begin("codex", 12345, "wrong-request", None, request_path=path)
        self.assertFalse(self.store.path.exists())
