from __future__ import annotations

import importlib
import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import test_factory_route as route_tests
import test_factory_work as work_tests
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "plugins/factory/scripts"))
fw = importlib.import_module("factory_work")
fc = importlib.import_module("factory_collection")
fs = importlib.import_module("factory_source")
FIXTURES = ROOT / "plugins/factory/fixtures/watch"


class WatchTests(unittest.TestCase):
    route_operation = route_tests.RouteTests.route_operation

    def setUp(self):
        work_tests.WorkTests.setUp(self)
        data = yaml.safe_load(self.config.read_text())
        data["slack"] = {
            "workspace_id": "T_SYNTHETIC",
            "channels": [
                {"id": "C_SYNTHETIC_ONE", "name": "synthetic-one"},
                {"id": "C_SYNTHETIC_TWO", "name": "synthetic-two"},
            ],
        }
        self.config.write_text(yaml.safe_dump(data))
        self.store = fw.Store(self.config)
        self.starts_path = self.store.runtime / "setup/example/channel-starts.json"
        self.starts_path.parent.mkdir(parents=True)
        self.starts = {
            "T_SYNTHETIC:C_SYNTHETIC_ONE": "2023-11-14T22:13:20+00:00",
            "T_SYNTHETIC:C_SYNTHETIC_TWO": "2023-11-14T22:13:45+00:00",
        }
        self.starts_path.write_text(json.dumps(self.starts))
        self.state = self.store.begin("codex", 12345, "watch-run", None)

    def capture(self, name):
        return fw.read_json(FIXTURES / (name + ".json"))

    def collect(self, name, state=None, value=None):
        return self.store.collect(
            "watch-run",
            "codex",
            12345,
            (state or self.store.read())["revision"],
            value or self.capture(name),
        )

    def test_empty_production_begin_and_independent_channel_cursors(self):
        self.assertEqual(self.state["schema_version"], 2)
        saved = self.collect("first")
        self.assertEqual(saved["schema_version"], 3)
        self.assertEqual(len(saved["sources"]), 2)
        second = self.collect("second-channel")
        self.assertEqual(
            second["collection"]["cursors"],
            {
                '["T_SYNTHETIC","C_SYNTHETIC_ONE"]': "1700000040.000000",
                '["T_SYNTHETIC","C_SYNTHETIC_TWO"]': "1700000040.000000",
            },
        )
        self.assertEqual(len(second["sources"]), 3)
        self.assertEqual(second["items"], {})
        self.assertEqual(second["invocations"][0]["steps"], 0)
        self.assertEqual(self.store.read(), second)

    def test_multipage_overlap_root_context_and_repeated_reads(self):
        saved = self.collect("first")
        old = next(
            v["source"]
            for v in saved["sources"].values()
            if v["source"]["intake"]["thread_ts"] == "1699999000.000000"
        )
        self.assertEqual(len(old["available_thread"]), 2)
        self.assertEqual(
            old["intake"]["trigger_message_ids"],
            [fc.message_id("T_SYNTHETIC", "C_SYNTHETIC_ONE", "1700000030.000000")],
        )
        self.assertEqual(self.collect("first", self.state), saved)
        repeated = self.collect("repeat")
        self.assertEqual(repeated["sources"], saved["sources"])
        self.assertEqual(len(repeated["collection"]["seen"]), 4)
        changed = self.capture("first")
        changed["complete"] = False
        with self.assertRaisesRegex(fw.WorkError, "different content"):
            self.collect("", value=changed)

    def test_partial_and_broken_pagination_preserve_bytes_then_retry(self):
        before = self.store.path.read_bytes()
        for mutate in (
            lambda o: o.update(complete=False),
            lambda o: o["history"].pop(),
            lambda o: o["history"][1].update(cursor="wrong"),
            lambda o: o["threads"][0].update(complete=False),
            lambda o: o["threads"].pop(),
            lambda o: o["discovery"].pop(),
        ):
            op = self.capture("first")
            mutate(op)
            with self.assertRaises(fw.ConfigError):
                self.collect("", value=op)
            self.assertEqual(self.store.path.read_bytes(), before)
        saved = self.collect("first")
        self.assertEqual(len(saved["sources"]), 2)

    def test_tracked_old_root_and_late_overlap_reply_create_one_later_capture(self):
        self.collect("first")
        repeated = self.collect("repeat")
        followup = self.collect("followup")
        self.assertEqual(len(followup["sources"]), 3)
        later = next(
            v["source"]
            for k, v in followup["sources"].items()
            if k not in repeated["sources"]
        )
        self.assertEqual(len(later["available_thread"]), 4)
        self.assertEqual(
            later["intake"]["trigger_message_ids"],
            [
                fc.message_id("T_SYNTHETIC", "C_SYNTHETIC_ONE", ts)
                for ts in ("1700000045.000000", "1700000060.000000")
            ],
        )
        self.assertIn("unverified", later["intake"]["coverage"])
        self.assertIn("1700000000.000000", later["intake"]["coverage"])
        bad = self.capture("followup")
        bad.update(
            id="missing-tracked", lower="1700000070.000000", upper="1700000080.000000"
        )
        bad["threads"].pop(0)
        with self.assertRaisesRegex(fw.ConfigError, "tracked"):
            self.collect("", value=bad)

    def test_explicit_historical_import_preserves_live_cursor_and_replays(self):
        self.collect("first")
        self.collect("repeat")
        before = self.collect("followup")
        imported = self.collect("manual-import")
        self.assertEqual(
            imported["collection"]["cursors"], before["collection"]["cursors"]
        )
        self.assertEqual(len(imported["sources"]), len(before["sources"]) + 1)
        op = self.capture("manual-import")
        op["id"] = "manual-again"
        again = self.collect("", value=op)
        self.assertEqual(again["sources"], imported["sources"])
        self.assertEqual(
            again["collection"]["cursors"], before["collection"]["cursors"]
        )

    def test_no_accidental_history_or_outside_setup_overlap(self):
        for field, value in (
            ("scan_lower", "1699999999.000000"),
            ("lower", "1699999999.000000"),
            ("upper", "1699999999.000000"),
            ("start_at", "2023-11-14T22:13:00+00:00"),
        ):
            op = self.capture("first")
            op[field] = value
            with self.assertRaises((fw.WorkError, fw.ConfigError)):
                self.collect("", value=op)
        op = self.capture("first")
        op["history"] = [{"cursor": None, "next_cursor": None, "messages": []}]
        op["discovery"] = []
        op["threads"] = []
        saved = self.collect("", value=op)
        self.assertEqual(saved["sources"], {})
        self.assertEqual(saved["collection"]["seen"], [])

    def test_missing_added_removed_channels_and_corrupt_starts(self):
        self.starts_path.write_text(
            json.dumps(
                {
                    "T_SYNTHETIC:C_SYNTHETIC_ONE": self.starts[
                        "T_SYNTHETIC:C_SYNTHETIC_ONE"
                    ]
                }
            )
        )
        plan = self.store.watch_plan()
        self.assertIsNotNone(plan["channels"][1]["blocked"])
        with self.assertRaisesRegex(fw.WorkError, "channel start"):
            self.collect("second-channel")
        self.collect("first")
        self.starts_path.write_text("broken")
        before = self.store.path.read_bytes()
        with self.assertRaisesRegex(fw.WorkError, "repair"):
            self.store.watch_plan()
        self.assertEqual(self.store.path.read_bytes(), before)

    def test_collection_crash_boundary_preserves_sources_and_cursor_together(self):
        before = self.store.path.read_bytes()
        with patch.object(fw.os, "replace", side_effect=OSError("before replace")):
            with self.assertRaises(OSError):
                self.collect("first")
        self.assertEqual(self.store.path.read_bytes(), before)
        real = fw.os.fsync
        calls = 0

        def fail_after(fd):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("after replace")
            real(fd)

        with patch.object(fw.os, "fsync", side_effect=fail_after):
            with self.assertRaises(OSError):
                self.collect("first")
        committed = self.store.read()
        self.assertEqual(self.collect("first", self.state), committed)
        self.assertEqual(len(committed["sources"]), 2)
        self.assertEqual(len(committed["collection"]["cursors"]), 1)
        self.assertEqual(sum(e["kind"] == "collect" for e in committed["events"]), 1)

    def test_corrupt_collection_sources_and_events_request_repair(self):
        saved = self.collect("first")
        for mutate in (
            lambda s: s["collection"]["cursors"].clear(),
            lambda s: s["collection"]["seen"].clear(),
            lambda s: s["collection"]["tracked"].clear(),
            lambda s: s["events"][-1]["change"].update(upper="1700000090.000000"),
        ):
            bad = deepcopy(saved)
            mutate(bad)
            self.store.path.write_text(json.dumps(bad))
            with self.assertRaisesRegex(fw.WorkError, "repair"):
                self.store.read()

    def test_owner_revision_and_live_previous_owner_protection(self):
        with patch.object(
            fw, "verify_owner", return_value={**self.identity, "pid": 54321}
        ):
            with self.assertRaisesRegex(fw.WorkError, "different owner"):
                self.collect("first")
        with self.assertRaisesRegex(fw.WorkError, "Revision"):
            self.store.collect("watch-run", "codex", 12345, 0, self.capture("first"))
        with patch.object(fw, "owner_alive", return_value=True):
            with self.assertRaisesRegex(fw.WorkError, "still owns"):
                self.store.begin("claude-code", 12345, "other", None)

    def test_live_source_routes_with_auditable_observations_and_fresh_items(self):
        op = self.capture("first")
        op["synthetic"] = False
        saved = self.collect("", value=op)
        operation = self.route_operation(saved)
        operation["items"][0]["synthetic"] = False
        operation["routing"]["observations"] = [
            {
                "id": "live-check",
                "kind": "capability_limit",
                "text": "Manufactured test evidence: no Jira connector; no duplicate conclusion.",
                "observed_at": "2026-11-05T12:00:00+00:00",
                "sources": [],
                "limitations": "Unavailable connector; duplicate and ownership checks incomplete.",
            }
        ]
        routed = self.store.route(
            "watch-run", "codex", 12345, saved["revision"], operation
        )
        self.assertFalse(work_tests.current(routed)["synthetic"])
        self.assertEqual(self.store.read(), routed)
        self.assertEqual(len(routed["sources"]), 2)
        synthetic = self.capture("second-channel")
        second = self.collect("", value=synthetic)
        selected = deepcopy(second)
        selected["sources"] = {
            k: v for k, v in second["sources"].items() if v["source"]["synthetic"]
        }
        operation = self.route_operation(selected)
        operation["routing"]["observations"] = operation.get(
            "observations",
            [
                {
                    "id": "wrong",
                    "kind": "live",
                    "text": "do not read live",
                    "observed_at": "2026-11-05T12:00:00+00:00",
                    "sources": [],
                    "limitations": "test",
                }
            ],
        )
        with self.assertRaisesRegex(fw.ConfigError, "Synthetic"):
            self.store.route("watch-run", "codex", 12345, second["revision"], operation)

    def test_terminal_page_cannot_restart_a_pagination_chain(self):
        op = self.capture("first")
        op["history"].append({"cursor": None, "next_cursor": None, "messages": []})
        before = self.store.path.read_bytes()
        with self.assertRaisesRegex(fw.ConfigError, "terminal"):
            self.collect("", value=op)
        self.assertEqual(self.store.path.read_bytes(), before)

    def test_first_import_promotes_prior_context_and_repeat_is_idempotent(self):
        saved = self.collect("first")
        op = self.capture("first")
        op.update(
            id="promote-context",
            mode="import",
            lower="1700000040.000000",
            upper="1700000050.000000",
            history=[],
            discovery=[],
        )
        op["threads"] = [op["threads"][1]]
        imported = self.collect("", value=op)
        self.assertEqual(len(imported["sources"]), len(saved["sources"]) + 1)
        added = next(
            v["source"]
            for k, v in imported["sources"].items()
            if k not in saved["sources"]
        )
        self.assertIn(
            fc.message_id("T_SYNTHETIC", "C_SYNTHETIC_ONE", "1699999000.000000"),
            added["intake"]["trigger_message_ids"],
        )
        self.assertEqual(
            imported["collection"]["cursors"], saved["collection"]["cursors"]
        )
        op["id"] = "promote-repeat"
        repeated = self.collect("", value=op)
        self.assertEqual(repeated["sources"], imported["sources"])

    def test_empty_collection_fixes_channel_mode_before_any_receipts(self):
        op = self.capture("first")
        op.update(
            history=[{"cursor": None, "next_cursor": None, "messages": []}],
            discovery=[],
            threads=[],
        )
        saved = self.collect("", value=op)
        self.assertEqual(saved["sources"], {})
        before = self.store.path.read_bytes()
        op.update(
            id="live-after-synthetic",
            synthetic=False,
            lower="1700000040.000000",
            upper="1700000050.000000",
        )
        with self.assertRaisesRegex(fw.ConfigError, "mix synthetic and live"):
            self.collect("", value=op)
        self.assertEqual(self.store.path.read_bytes(), before)

    def test_new_capture_uses_only_current_observed_thread_and_keeps_history(self):
        self.collect("first")
        previous = self.collect("repeat")
        op = self.capture("followup")
        op["threads"][1]["pages"][0]["messages"].pop(1)
        saved = self.collect("", value=op)
        later = next(
            v["source"]
            for k, v in saved["sources"].items()
            if k not in previous["sources"]
        )
        omitted = fc.message_id("T_SYNTHETIC", "C_SYNTHETIC_ONE", "1700000030.000000")
        self.assertNotIn(omitted, [m["id"] for m in later["available_thread"]])
        self.assertIn(omitted, saved["collection"]["seen"])
        self.assertEqual(
            {k: saved["sources"][k] for k in previous["sources"]}, previous["sources"]
        )

    def test_history_only_reports_older_untracked_coverage_limit(self):
        op = self.capture("first")
        op.update(
            discovery=[],
            discovery_note="Reply discovery unavailable; older untracked replies not covered",
        )
        op["threads"].pop()
        saved = self.collect("", value=op)
        self.assertEqual(len(saved["sources"]), 1)
        source = next(iter(saved["sources"].values()))["source"]
        self.assertIn("not covered", source["intake"]["coverage"])

    def test_removed_channel_retains_cursor_and_readded_channel_keeps_start(self):
        saved = self.collect("first")
        self.store.finish("watch-run", "codex", 12345, "blocked")
        config = yaml.safe_load(self.config.read_text())
        channels = config["slack"]["channels"]
        config["slack"]["channels"] = [channels[1]]
        self.config.write_text(yaml.safe_dump(config))
        removed = fw.Store(self.config)
        self.assertEqual(len(removed.watch_plan()["channels"]), 1)
        self.assertEqual(removed.read()["collection"], saved["collection"])
        config["slack"]["channels"] = channels
        self.config.write_text(yaml.safe_dump(config))
        readded = fw.Store(self.config)
        plan = readded.watch_plan()["channels"][0]
        self.assertEqual(plan["lower"], "1700000040.000000")
        self.assertEqual(plan["start_at"], self.starts["T_SYNTHETIC:C_SYNTHETIC_ONE"])

    def test_observed_permalink_is_preserved_and_missing_link_uses_durable_id(self):
        op = self.capture("first")
        op["threads"][0]["link"] = None
        observed = op["threads"][1]["link"]
        saved = self.collect("", value=op)
        sources = [v["source"] for v in saved["sources"].values()]
        fallback = next(
            v for v in sources if v["intake"]["thread_ts"] == "1700000010.000000"
        )
        self.assertEqual(fallback["link"], fallback["source_id"])
        self.assertIn(observed, [v["link"] for v in sources])

    def test_search_recovers_unseen_untracked_reply_below_prior_cursor(self):
        self.collect("first")
        self.collect("repeat")
        op = self.capture("followup")
        root = {
            "ts": "1699997000.000000",
            "thread_ts": "1699997000.000000",
            "author": "synthetic-user",
            "text": "Historical root is context only.",
        }
        late = {
            "ts": "1700000046.000000",
            "thread_ts": "1699997000.000000",
            "author": "synthetic-user",
            "text": "Late-indexed new reply to previously untracked root.",
        }
        op["threads"].append(
            {
                "root": root["ts"],
                "link": None,
                "pages": [
                    {"cursor": None, "next_cursor": None, "messages": [root, late]}
                ],
                "complete": True,
                "availability": "Synthetic complete available thread",
            }
        )
        op["discovery"][0]["messages"].append(late)
        saved = self.collect("", value=op)
        source = next(
            v["source"]
            for v in saved["sources"].values()
            if v["source"]["intake"]["thread_ts"] == root["ts"]
        )
        self.assertEqual(
            source["intake"]["trigger_message_ids"],
            [fc.message_id("T_SYNTHETIC", "C_SYNTHETIC_ONE", late["ts"])],
        )

    def test_live_source_file_cannot_bypass_collection_and_mode_gate(self):
        op = self.capture("first")
        op["synthetic"] = False
        saved = self.collect("", value=op)
        path = self.root / "live-source.json"
        path.write_text(json.dumps(next(iter(saved["sources"].values()))["source"]))
        before = self.store.path.read_bytes()
        with self.assertRaisesRegex(fw.WorkError, "owner-gated collection"):
            self.store.begin("codex", 12345, "source-bypass", None, 3, path)
        self.assertEqual(self.store.path.read_bytes(), before)

    def test_tracked_reply_attach_preserves_work_and_old_receipts_cross_host(self):
        saved = self.collect("first")
        first_op = self.route_operation(saved)
        saved = self.store.route(
            "watch-run", "codex", 12345, saved["revision"], first_op
        )
        target = saved["active_item_id"]
        self.collect("repeat")
        later = self.collect("followup")
        key = next(k for k in later["sources"] if k not in saved["sources"])
        # Select the new capture explicitly; another original receipt is still pending.
        old_pending = next(
            k for k, v in later["sources"].items() if v["routing"] is None and k != key
        )
        pending_op = self.route_operation(later, disposition="no_action")
        self.assertEqual(pending_op["receipt_id"], old_pending)
        later = self.store.route(
            "watch-run", "codex", 12345, later["revision"], pending_op
        )
        attach = self.route_operation(later, existing=target)
        later = self.store.route("watch-run", "codex", 12345, later["revision"], attach)
        self.assertEqual(len(later["items"]), 1)
        self.store.finish("watch-run", "codex", 12345, "blocked")
        resumed = self.store.begin("claude-code", 12345, "handoff", None)
        self.assertEqual(resumed["collection"], later["collection"])
        self.assertEqual(resumed["sources"], later["sources"])
        self.assertEqual(resumed["items"], later["items"])
