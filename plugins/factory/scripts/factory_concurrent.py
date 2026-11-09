"""Item-owned concurrent invocations with replayable, atomic local transactions."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import TypedDict, cast

import factory_work as fw
import yaml
from factory_collection import (
    Collection,
    empty,
    identity,
    observation,
    overlap_start,
    start_ts,
)
from factory_collection import apply as apply_collection
from factory_config import (
    Harness,
    discover,
    mapping,
    read_yaml,
    string,
    timestamp,
)
from factory_source import Receipt, Routing, receipt_id, routing, source, source_digest


class Run(fw.Invocation):
    item_id: str | None


class Resource(TypedDict):
    item_id: str
    worktree: str
    git_dir: str
    common_dir: str
    branch: str | None


class Event(TypedDict):
    revision: int
    at: str
    run_id: str
    kind: str
    operation: dict[str, object]


class State(TypedDict):
    schema_version: int
    config_path: str
    factory_id: str
    legacy: dict[str, object] | None
    revision: int
    items: dict[str, fw.Item]
    item_versions: dict[str, int]
    sources: dict[str, Receipt]
    collection: Collection
    invocations: list[Run]
    claims: dict[str, str]
    resources: dict[str, Resource]
    events: list[Event]


class Route(TypedDict):
    id: str
    reason: str
    receipt_id: str
    routing: Routing
    items: list[fw.Item]
    inventory_version: str


def seed(config_path: str, factory_id: str, legacy: dict[str, object] | None) -> State:
    old = None if legacy is None else fw.snapshot(legacy)
    if old is not None and (old["config_path"], old["factory_id"]) != (
        config_path,
        factory_id,
    ):
        raise fw.WorkError("Legacy state belongs to another factory")
    items = {} if old is None else deepcopy(old["items"])
    return {
        "schema_version": 4,
        "config_path": config_path,
        "factory_id": factory_id,
        "legacy": deepcopy(legacy),
        "revision": 0 if old is None else old["revision"],
        "items": items,
        "item_versions": {key: 1 for key in items},
        "sources": {} if old is None else deepcopy(old["sources"]),
        "collection": empty()
        if old is None
        else deepcopy(old.get("collection", empty())),
        "invocations": [],
        "claims": {},
        "resources": {},
        "events": [],
    }


def run_record(value: object) -> Run:
    data = mapping(value, set(fw.Invocation.__annotations__) | {"item_id"}, "run")
    previous = fw.invocation({k: v for k, v in data.items() if k != "item_id"})
    return {**previous, "item_id": fw.nullable(data["item_id"], "item_id")}


def resource(value: object) -> Resource:
    data = mapping(value, set(Resource.__annotations__), "resource")
    result: Resource = {
        "item_id": string(data["item_id"], "resource.item_id"),
        "worktree": string(data["worktree"], "resource.worktree"),
        "git_dir": string(data["git_dir"], "resource.git_dir"),
        "common_dir": string(data["common_dir"], "resource.common_dir"),
        "branch": fw.nullable(data["branch"], "resource.branch"),
    }
    if any(
        not Path(path).is_absolute()
        for path in (result["worktree"], result["git_dir"], result["common_dir"])
    ):
        raise fw.WorkError("Resource paths must be absolute")
    if result["branch"] is not None and not result["branch"].startswith("refs/heads/"):
        raise fw.WorkError("Resource branch must be a full local branch ref")
    return result


def branch_ref(value: str | None) -> str | None:
    if value is None or value.startswith("refs/heads/"):
        return value
    return "refs/heads/" + value


def current_run(state: State, token: str, finished: bool = False) -> Run:
    matches = [r for r in state["invocations"] if r["id"] == token]
    if len(matches) != 1:
        raise fw.WorkError("Unknown concurrent invocation")
    run = matches[0]
    if not finished and run["finished_at"] is not None:
        raise fw.WorkError("Invocation is finished")
    return run


def active_items(state: State) -> dict[str, str]:
    return {
        r["item_id"]: r["id"]
        for r in state["invocations"]
        if r["finished_at"] is None and r["item_id"] is not None
    }


def inventory_version(state: State) -> str:
    return fw.digest({"items": state["items"], "sources": state["sources"]})


def receipt_source(state: State, value: object) -> None:
    incoming = source(value)
    key = receipt_id(incoming)
    if key in state["sources"]:
        if state["sources"][key]["source"] != incoming:
            raise fw.WorkError("Conflicting immutable source version")
    else:
        state["sources"][key] = {
            "source": incoming,
            "digest": source_digest(incoming),
            "routing": None,
            "item_ids": {},
        }


def bound_item(state: State, run: Run) -> str:
    selected = run["item_id"]
    if selected is None or active_items(state).get(selected) != run["id"]:
        raise fw.WorkError("Run must exclusively claim an item first")
    return selected


def version_check(state: State, item_id: str, value: object) -> None:
    expected = fw.integer(value, "expected item version", 1, 2**53)
    if state["item_versions"].get(item_id) != expected:
        raise fw.WorkError("Item version changed; reread before deciding")


def resource_conflict(state: State, updated: Resource) -> None:
    for existing in state["resources"].values():
        if existing["worktree"] == updated["worktree"] and (
            existing["git_dir"],
            existing["common_dir"],
        ) != (updated["git_dir"], updated["common_dir"]):
            raise fw.WorkError(
                "Saved worktree identity changed; restore or repair before reuse"
            )
        if existing["item_id"] == updated["item_id"]:
            continue
        if (
            existing["worktree"] == updated["worktree"]
            or existing["git_dir"] == updated["git_dir"]
            or updated["branch"] is not None
            and (existing["common_dir"], existing["branch"])
            == (updated["common_dir"], updated["branch"])
        ):
            raise fw.WorkError("Worktree or branch is reserved by another item")
    for other in state["items"].values():
        path = other["code"].get("worktree")
        if other["id"] != updated["item_id"] and path == updated["worktree"]:
            raise fw.WorkError("Worktree remains referenced by another item")


def apply_event(state: State, event: Event) -> None:
    kind, token, op = event["kind"], event["run_id"], event["operation"]
    string(op.get("id"), "operation ID")
    if kind == "begin":
        data = mapping(op, {"id", "run", "source", "fixture"}, "begin")
        run = run_record(data["run"])
        if (
            run["id"] != token
            or run["item_id"] is not None
            or run["finished_at"] is not None
        ):
            raise fw.WorkError("Invalid initial concurrent run")
        if run["steps"] != 0 or any(r["id"] == token for r in state["invocations"]):
            raise fw.WorkError("Duplicate run or initial steps")
        state["invocations"].append(run)
        if data["source"] is not None:
            receipt_source(state, data["source"])
        if data["fixture"] is not None:
            initial = fw.item(data["fixture"])
            if not initial["synthetic"] or initial["id"] in state["items"]:
                raise fw.WorkError("Fixture must be a new synthetic item")
            state["items"][initial["id"]] = initial
            state["item_versions"][initial["id"]] = 1
        return
    run = current_run(state, token)
    if kind == "claim":
        data = mapping(op, {"id", "item_id", "expected_version"}, "claim")
        selected = string(data["item_id"], "item_id")
        version_check(state, selected, data["expected_version"])
        if run["item_id"] is not None or selected in active_items(state):
            raise fw.WorkError("Item already claimed or run already bound")
        run["item_id"] = selected
    elif kind == "intake_claim":
        data = mapping(op, {"id", "key"}, "intake claim")
        key = string(data["key"], "claim key")
        if key in state["claims"] and state["claims"][key] != token:
            raise fw.WorkError("Intake resource is busy")
        if not key.startswith(("channel:", "receipt:")):
            raise fw.WorkError("Unknown intake claim domain")
        state["claims"][key] = token
    elif kind == "release_intake":
        data = mapping(op, {"id", "key"}, "release intake")
        key = string(data["key"], "claim key")
        if state["claims"].get(key) != token:
            raise fw.WorkError("Intake claim belongs to another run")
        del state["claims"][key]
    elif kind == "collect":
        data = mapping(op, {"id", "observation"}, "collect")
        observed = observation(data["observation"])
        key = "channel:" + identity(observed["workspace_id"], observed["channel_id"])
        if state["claims"].get(key) != token:
            raise fw.WorkError("Claim the channel before reading/collecting")
        state["collection"] = apply_collection(
            state["collection"], state["sources"], observed
        )
    elif kind == "route":
        apply_route(state, run, op)
    elif kind in ("save", "reconcile"):
        data = mapping(op, {"id", "expected_version", "decision"}, kind)
        selected = bound_item(state, run)
        version_check(state, selected, data["expected_version"])
        if kind == "save":
            decision = fw.decision(data["decision"])
            if decision["id"] != op["id"]:
                raise fw.WorkError("Decision operation identity mismatch")
            updated = decision["item"]
            if updated["id"] != selected:
                raise fw.WorkError("Cannot save another run's item")
            fw.preserve(state["items"][selected], updated)
            for key in ("worktree", "branch"):
                if updated["code"].get(key) != state["items"][selected]["code"].get(
                    key
                ):
                    matches = [
                        r
                        for r in state["resources"].values()
                        if r["item_id"] == selected
                    ]
                    if not any(
                        r["worktree"] == updated["code"].get("worktree")
                        and r["branch"] == branch_ref(updated["code"].get("branch"))
                        for r in matches
                    ):
                        raise fw.WorkError(
                            "Reserve the worktree and branch before saving code references"
                        )
            state["items"][selected] = updated
        else:
            reconciliation = fw.reconciliation(data["decision"])
            if reconciliation["id"] != op["id"]:
                raise fw.WorkError("Reconciliation operation identity mismatch")
            fw.apply_reconciliation(state["items"], selected, reconciliation)
        state["item_versions"][selected] += 1
        run["steps"] += 1
    elif kind == "reserve":
        data = mapping(op, {"id", "resources"}, "reserve")
        selected = bound_item(state, run)
        requested = [resource(r) for r in fw.sequence(data["resources"], "resources")]
        if not requested or len({r["worktree"] for r in requested}) != len(requested):
            raise fw.WorkError("Reserve distinct nonempty resources")
        for reserved in requested:
            if reserved["item_id"] != selected:
                raise fw.WorkError("Cannot reserve another item's resource")
            resource_conflict(state, reserved)
            key = identity(
                reserved["item_id"], reserved["worktree"], reserved["branch"] or ""
            )
            state["resources"][key] = reserved
    elif kind == "finish":
        data = mapping(op, {"id", "outcome"}, "finish")
        outcome = string(data["outcome"], "outcome")
        if outcome not in (
            "single_step",
            "step_limit",
            "blocked",
            "waiting_for_human",
            "no_available_work",
            "stopped",
            "completed",
        ):
            raise fw.WorkError("Unsupported finish outcome")
        if outcome == "completed":
            selected = bound_item(state, run)
            completed = state["items"][selected]
            if (
                completed["stage"] != "follow_pr"
                or completed["status"] != "done"
                or completed["required_role"] is not None
                or not completed["code"].get("pr_url")
                or any(
                    action["scope"]["action"] in ("pushes", "pull_requests")
                    and action["status"] != "confirmed"
                    for action in completed["pending_actions"]
                )
            ):
                raise fw.WorkError(
                    "Completion requires a done PR item with resolved publication actions"
                )
        run["finished_at"], run["outcome"] = event["at"], outcome
        state["claims"] = {
            key: owner for key, owner in state["claims"].items() if owner != token
        }
    elif kind == "recover":
        data = mapping(op, {"id", "target_run"}, "recover")
        target = current_run(state, string(data["target_run"], "target_run"))
        if target["id"] == token:
            raise fw.WorkError("Cannot recover own running invocation")
        target["finished_at"], target["outcome"] = event["at"], "interrupted_owner_dead"
        state["claims"] = {
            key: owner
            for key, owner in state["claims"].items()
            if owner != target["id"]
        }
    else:
        raise fw.WorkError("Unknown concurrent event kind")
    if run["max_steps"] is not None and run["steps"] > run["max_steps"]:
        raise fw.WorkError("Invocation step limit reached; finish and resume")


def apply_route(state: State, run: Run, value: object) -> None:
    data = mapping(value, set(Route.__annotations__), "concurrent route")
    string(data["reason"], "route reason")
    key = string(data["receipt_id"], "receipt_id")
    if state["claims"].get("receipt:" + key) != run["id"]:
        raise fw.WorkError("Claim the source receipt before routing")
    if string(data["inventory_version"], "inventory version") != inventory_version(
        state
    ):
        raise fw.WorkError(
            "Routing inventory changed; reread and reconsider associations"
        )
    saved = state["sources"].get(key)
    if saved is None or saved["routing"] is not None:
        raise fw.WorkError("Receipt missing or already routed")
    result = routing(data["routing"], saved["source"])
    updates = [fw.item(v) for v in fw.sequence(data["items"], "new items")]
    created = {v["id"]: v for v in updates}
    if len(created) != len(updates):
        raise fw.WorkError("Duplicate new item")
    associations: dict[str, str] = {}
    new_ids: set[str] = set()
    for finding in result["findings"]:
        if finding["disposition"] == "no_action":
            if finding["existing_item_id"] is not None:
                raise fw.WorkError("No-action finding cannot attach an item")
            continue
        target = finding["existing_item_id"]
        if target is None:
            target = fw.stable_id(saved["source"]["source_id"], finding["key"])
            if target in state["items"] or target not in created:
                raise fw.WorkError(
                    "New finding needs a new explicit item; associate existing work explicitly"
                )
            updated = created[target]
            if (updated["source_id"], updated["subitem_key"], updated["synthetic"]) != (
                saved["source"]["source_id"],
                finding["key"],
                saved["source"]["synthetic"],
            ):
                raise fw.WorkError("New item source identity mismatch")
            if (
                updated["fix_rounds"]
                or updated["approvals"]
                or updated["pending_actions"]
                or updated["code"]
                or updated["artifact_paths"]
                or "execution" in updated
            ):
                raise fw.WorkError(
                    "Fresh routed items cannot inherit execution evidence, resources or permission"
                )
            if saved["source"]["link"] not in updated["source_links"]:
                raise fw.WorkError("New item must retain its source link")
            new_ids.add(target)
        elif target not in state["items"]:
            raise fw.WorkError("Associated item is missing")
        associations[finding["key"]] = target
    if set(created) != new_ids:
        raise fw.WorkError(
            "Routing may create new items only; existing items receive receipt associations"
        )
    state["items"].update(created)
    state["item_versions"].update({key: 1 for key in created})
    for target in set(associations.values()) - new_ids:
        state["item_versions"][target] += 1
    saved["routing"], saved["item_ids"] = result, associations
    run["steps"] += 1


def snapshot(value: object) -> State:
    data = mapping(value, set(State.__annotations__), "concurrent snapshot")
    if type(data["schema_version"]) is not int or data["schema_version"] != 4:
        raise fw.WorkError("Unsupported concurrent work schema")
    fw.integer(data["revision"], "revision", 0, 2**53)
    for version in fw.obj(data["item_versions"], "item_versions").values():
        fw.integer(version, "item version", 1, 2**53)
    for item in fw.obj(data["items"], "items").values():
        fw.item(item)
    legacy = None if data["legacy"] is None else fw.obj(data["legacy"], "legacy")
    result = seed(
        string(data["config_path"], "config path"),
        string(data["factory_id"], "factory id"),
        legacy,
    )
    seen: set[str] = set()
    for value in fw.sequence(data["events"], "events"):
        raw = mapping(value, set(Event.__annotations__), "event")
        revision = fw.integer(raw["revision"], "revision", 1, 2**53)
        if revision != result["revision"] + 1:
            raise fw.WorkError("Concurrent history revision gap")
        op = fw.obj(raw["operation"], "operation")
        operation_id = string(op.get("id"), "operation ID")
        if operation_id in seen:
            raise fw.WorkError("Duplicate concurrent operation ID")
        seen.add(operation_id)
        event: Event = {
            "revision": revision,
            "at": timestamp(raw["at"], "event at"),
            "run_id": string(raw["run_id"], "run ID"),
            "kind": string(raw["kind"], "event kind"),
            "operation": op,
        }
        apply_event(result, event)
        result["revision"] = revision
        result["events"].append(deepcopy(event))
    if dict(result) != data:
        raise fw.WorkError("Concurrent snapshot differs from committed history")
    return result


def atomic_snapshot(path: Path, state: State) -> None:
    snapshot(state)
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=".work.")
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(json.dumps(state, indent=2) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Store:
    def __init__(self, config: Path, local: Path | None = None) -> None:
        self.base = fw.Store(config, local)
        self.config_path = self.base.config_path
        self.config = self.base.config
        self.local = local
        self.path = self.base.path
        self.runtime = self.base.runtime

    def read(self) -> State | None:
        if not self.path.exists():
            return None
        state = snapshot(fw.read_json(self.path))
        if (state["config_path"], state["factory_id"]) != (
            str(self.config_path),
            self.config["factory_id"],
        ):
            raise fw.WorkError("Runtime belongs to another factory")
        return state

    def owned(
        self,
        state: State,
        token: str,
        harness: Harness,
        pid: int,
        finished: bool = False,
    ) -> Run:
        owner = fw.verify_owner(pid, harness)
        run = current_run(state, token, finished)
        if run["owner"] != owner or run["harness"] != harness:
            raise fw.WorkError("Invocation belongs to a different owner/harness")
        if (
            run["config_hash"] != fw.digest(self.config)
            or run["source_fingerprint"] != fw.plugin_identity()[1]
        ):
            raise fw.WorkError(
                "Config or plugin changed; stop and resume in a fresh invocation"
            )
        return run

    def append(
        self, state: State, token: str, kind: str, op: dict[str, object]
    ) -> State:
        event: Event = {
            "revision": state["revision"] + 1,
            "at": fw.now(),
            "run_id": token,
            "kind": kind,
            "operation": deepcopy(op),
        }
        apply_event(state, event)
        state["revision"] = event["revision"]
        state["events"].append(event)
        atomic_snapshot(self.path, state)
        return state

    def begin(
        self,
        harness: Harness,
        pid: int,
        token: str,
        incoming: Path | None = None,
        fixture: Path | None = None,
        max_steps: int | None = None,
        synthetic_source: bool = False,
    ) -> State:
        if self.config["schema_version"] != 2:
            raise fw.WorkError("Use explicit upgrade before concurrent execution")
        owner = fw.verify_owner(pid, harness)
        string(token, "run ID")
        if max_steps is not None:
            fw.integer(max_steps, "max_steps", 1, 2**53)
        if incoming is not None and fixture is not None:
            raise fw.WorkError("Choose one input")
        incoming_source = None if incoming is None else source(fw.read_json(incoming))
        if incoming_source is not None:
            if synthetic_source and not incoming_source["synthetic"]:
                raise fw.WorkError("--source is synthetic only")
            if not synthetic_source and "direct" not in incoming_source:
                raise fw.WorkError("--request requires direct intake provenance")
        initial = None if fixture is None else fw.load_fixture(fixture)[0]
        with self.base.mutation():
            state = self.read() or seed(
                str(self.config_path), self.config["factory_id"], None
            )
            if state["legacy"] is not None and any(
                r["id"] == token for r in fw.snapshot(state["legacy"])["invocations"]
            ):
                raise fw.WorkError("Run ID belongs to legacy history; use a new UUID")
            previous = next(
                (
                    e
                    for e in state["events"]
                    if e["kind"] == "begin" and e["run_id"] == token
                ),
                None,
            )
            version, fingerprint = fw.plugin_identity()
            if previous is not None:
                run = self.owned(state, token, harness, pid, True)
                if (
                    run["max_steps"] != max_steps
                    or previous["operation"]["source"] != incoming_source
                    or previous["operation"]["fixture"] != initial
                ):
                    raise fw.WorkError("Run ID reused with different inputs")
                return state
            run = {
                "id": token,
                "owner": owner,
                "harness": harness,
                "started_at": fw.now(),
                "finished_at": None,
                "outcome": None,
                "max_steps": max_steps,
                "steps": 0,
                "plugin_version": version,
                "source_fingerprint": fingerprint,
                "config_hash": fw.digest(self.config),
                "effective_config": deepcopy(self.config),
                "item_id": None,
            }
            return self.append(
                state,
                token,
                "begin",
                {
                    "id": "begin:" + token,
                    "run": run,
                    "source": incoming_source,
                    "fixture": initial,
                },
            )

    def mutate(
        self, token: str, harness: Harness, pid: int, kind: str, value: object
    ) -> State:
        op = fw.obj(value, "operation")
        operation_id = string(op.get("id"), "operation ID")
        with self.base.mutation():
            state = self.read()
            if state is None:
                raise fw.WorkError("Begin an invocation first")
            run = self.owned(state, token, harness, pid, kind == "finish")
            if state["legacy"] is not None:
                for historical in fw.snapshot(state["legacy"])["events"]:
                    old_operation = fw.operation_identity(historical)
                    if old_operation is not None and old_operation[0] == operation_id:
                        raise fw.WorkError(
                            "Operation ID belongs to legacy history; inspect its original outcome"
                        )
            for previous in state["events"]:
                if previous["operation"]["id"] == operation_id:
                    if previous["kind"] != kind or previous["operation"] != op:
                        raise fw.WorkError(
                            "Operation ID reused with different content or domain"
                        )
                    if previous["run_id"] != token:
                        original = current_run(state, previous["run_id"], True)
                        allowed = False
                        if kind in ("save", "reconcile", "reserve"):
                            allowed = (
                                run["item_id"] is not None
                                and original["item_id"] == run["item_id"]
                            )
                        elif kind == "collect":
                            observed = observation(op.get("observation"))
                            key = "channel:" + identity(
                                observed["workspace_id"], observed["channel_id"]
                            )
                            allowed = state["claims"].get(key) == token
                        elif kind == "route":
                            key = "receipt:" + string(
                                op.get("receipt_id"), "receipt ID"
                            )
                            allowed = state["claims"].get(key) == token
                        if original["finished_at"] is None or not allowed:
                            raise fw.WorkError(
                                "Retry belongs to another invocation/item"
                            )
                    return state
            if kind == "recover":
                target = current_run(state, string(op.get("target_run"), "target run"))
                if fw.owner_alive(target["owner"]):
                    raise fw.WorkError("Prior owner is alive; cannot recover")
            if kind == "collect":
                observed = observation(op.get("observation"))
                if observed["workspace_id"] != self.config["slack"][
                    "workspace_id"
                ] or observed["channel_id"] not in {
                    c["id"] for c in self.config["slack"]["channels"]
                }:
                    raise fw.WorkError(
                        "Collection must use configured workspace/channel"
                    )
                start = self.base.channel_starts().get(
                    f"{observed['workspace_id']}:{observed['channel_id']}"
                )
                if start is None or start != observed["start_at"]:
                    raise fw.WorkError(
                        "Collection requires preserved setup channel start"
                    )
            if kind == "intake_claim":
                key = string(op.get("key"), "claim key")
                channels = {
                    "channel:"
                    + identity(str(self.config["slack"]["workspace_id"]), c["id"])
                    for c in self.config["slack"]["channels"]
                }
                if (
                    key.startswith("channel:")
                    and key not in channels
                    or key.startswith("receipt:")
                    and key[8:] not in state["sources"]
                ):
                    raise fw.WorkError(
                        "Intake claim must identify a configured channel or saved receipt"
                    )
            if kind == "save":
                updated = fw.decision(op.get("decision"))["item"]
                selected = bound_item(state, run)
                self.base.check_execution_evidence(state["items"][selected], updated)
            if kind == "reconcile":
                action = fw.reconciliation(op.get("decision"))["action"]
                if not Path(action["evidence"]).read_text().strip():
                    raise fw.WorkError("Reconciliation requires readable evidence")
            if kind == "reserve":
                selected = bound_item(state, run)
                observed_resources = [
                    resource(v) for v in fw.sequence(op.get("resources"), "resources")
                ]
                for reserved in observed_resources:
                    actual = self.observe_resource(Path(reserved["worktree"]), selected)
                    if reserved != actual:
                        raise fw.WorkError(
                            "Git resource identity changed; reobserve before reservation"
                        )
                    for other in state["items"].values():
                        path = other["code"].get("worktree")
                        if (
                            other["id"] != selected
                            and path is not None
                            and Path(path).resolve() == Path(reserved["worktree"])
                        ):
                            raise fw.WorkError("Worktree belongs to another saved item")
                        if (
                            other["id"] != selected
                            and reserved["branch"] is not None
                            and branch_ref(other["code"].get("branch"))
                            == reserved["branch"]
                        ):
                            if path is None:
                                raise fw.WorkError(
                                    "Cannot establish legacy branch ownership without its worktree"
                                )
                            prior = self.observe_resource(Path(path), other["id"])
                            if prior["common_dir"] == reserved["common_dir"]:
                                raise fw.WorkError(
                                    "Branch belongs to another saved item"
                                )
            return self.append(state, token, kind, op)

    def observe_resource(self, path: Path, item_id: str) -> Resource:
        path = path.resolve(strict=True)

        def git(*args: str) -> str:
            result = subprocess.run(
                ["git", "-C", str(path), *args],
                text=True,
                capture_output=True,
                check=True,
            )
            return result.stdout.strip()

        top = Path(git("rev-parse", "--show-toplevel")).resolve()
        if top != path:
            raise fw.WorkError("Resource must name the worktree root")
        common = Path(
            git("rev-parse", "--path-format=absolute", "--git-common-dir")
        ).resolve()
        git_dir = Path(git("rev-parse", "--absolute-git-dir")).resolve()
        if git_dir == common:
            raise fw.WorkError(
                "Use a dedicated linked worktree, not the source checkout"
            )
        authorized: set[Path] = set()
        for root in discover(self.config)["repositories"]:
            result = subprocess.run(
                [
                    "git",
                    "-C",
                    root,
                    "rev-parse",
                    "--path-format=absolute",
                    "--git-common-dir",
                ],
                text=True,
                capture_output=True,
            )
            if result.returncode == 0:
                authorized.add(Path(result.stdout.strip()).resolve())
        if common not in authorized:
            raise fw.WorkError("Worktree repository is outside configured scope")
        branch_result = subprocess.run(
            ["git", "-C", str(path), "symbolic-ref", "-q", "HEAD"],
            text=True,
            capture_output=True,
        )
        if branch_result.returncode not in (0, 1):
            raise fw.WorkError("Cannot establish worktree branch")
        return {
            "item_id": item_id,
            "worktree": str(path),
            "git_dir": str(git_dir),
            "common_dir": str(common),
            "branch": branch_result.stdout.strip()
            if branch_result.returncode == 0
            else None,
        }

    def watch_plan(self) -> dict[str, object]:
        state = self.read()
        saved = empty() if state is None else state["collection"]
        starts = self.base.channel_starts()
        workspace = self.config["slack"]["workspace_id"]
        channels: list[dict[str, object]] = []
        for channel in self.config["slack"]["channels"]:
            key = identity(str(workspace), channel["id"])
            start = starts.get(f"{workspace}:{channel['id']}")
            lower = (
                None if start is None else saved["cursors"].get(key, start_ts(start))
            )
            channels.append(
                {
                    "channel_id": channel["id"],
                    "claim_key": "channel:" + key,
                    "claimed_by": None
                    if state is None
                    else state["claims"].get("channel:" + key),
                    "start_at": start,
                    "lower": lower,
                    "scan_lower": None
                    if lower is None or start is None
                    else overlap_start(lower, start_ts(start)),
                    "tracked_roots": [
                        cast(list[str], json.loads(k))[2]
                        for k in saved["tracked"]
                        if cast(list[str], json.loads(k))[:2]
                        == [workspace, channel["id"]]
                    ],
                    "blocked": None
                    if start is not None and workspace is not None
                    else "Setup has not verified/started this channel",
                }
            )
        return {
            "workspace_id": workspace,
            "channels": channels,
            "revision": None if state is None else state["revision"],
        }


def backup_file(path: Path, content: bytes) -> None:
    if path.exists():
        if path.read_bytes() != content:
            raise fw.WorkError("Upgrade backup conflict; preserve files and repair")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
    sync_directory(path.parent)


def sync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def upgrade(store: Store, harness: Harness, pid: int) -> dict[str, object]:
    fw.verify_owner(pid, harness)
    with store.base.mutation():
        config_bytes = store.config_path.read_bytes()
        raw = (
            None
            if not store.path.exists()
            else fw.obj(fw.read_json(store.path), "snapshot")
        )
        if raw is not None and raw.get("schema_version") == 4:
            state = snapshot(raw)
            if (
                state["config_path"] != str(store.config_path)
                or state["factory_id"] != store.config["factory_id"]
            ):
                raise fw.WorkError("Runtime belongs to another factory")
        else:
            previous = None if raw is None else fw.snapshot(raw)
            if previous is not None:
                if (
                    previous["config_path"] != str(store.config_path)
                    or previous["factory_id"] != store.config["factory_id"]
                ):
                    raise fw.WorkError("Runtime belongs to another factory")
                for run in previous["invocations"]:
                    if run["finished_at"] is None and fw.owner_alive(run["owner"]):
                        raise fw.WorkError("Stop the legacy owner before upgrade")
            state = seed(str(store.config_path), store.config["factory_id"], raw)
        if state["invocations"] and store.config["schema_version"] != 2:
            raise fw.WorkError(
                "Concurrent work exists with legacy config; repair without rollback"
            )
        backup_key = fw.digest(
            {"config": config_bytes.decode(), "legacy": state["legacy"]}
        )
        backup = store.path.parent / "upgrades" / backup_key
        if (
            store.config["schema_version"] == 1
            or raw is None
            or raw.get("schema_version") != 4
        ):
            backup_file(backup / "config.yaml", config_bytes)
            if state["legacy"] is not None:
                if raw is not None and raw.get("schema_version") != 4:
                    backup_file(backup / "work.json", store.path.read_bytes())
                elif fw.read_json(backup / "work.json") != state["legacy"]:
                    raise fw.WorkError(
                        "Original upgrade backup missing or inconsistent"
                    )
            sync_directory(backup.parent)
            sync_directory(store.path.parent)
            atomic_snapshot(store.path, state)
            updated = read_yaml(store.config_path)
            updated["schema_version"] = 2
            updated["limits"] = {"fix_rounds": 2}
            descriptor, temporary = tempfile.mkstemp(
                dir=store.config_path.parent, prefix=".factory-upgrade."
            )
            try:
                with os.fdopen(descriptor, "w") as stream:
                    stream.write(yaml.safe_dump(updated, sort_keys=False))
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(temporary, store.config_path)
                sync_directory(store.config_path.parent)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
        return {
            "state_path": str(store.path),
            "schema_version": 4,
            "config_schema_version": 2,
            "backup_path": str(backup) if backup.exists() else None,
            "action": "Recheck setup capabilities in each host; resume by item ID. Older plugins cannot resume this factory.",
        }


def cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=(
            "inspect",
            "owners",
            "watch-plan",
            "upgrade",
            "begin",
            "claim",
            "intake-claim",
            "release-intake",
            "collect",
            "route",
            "save",
            "reconcile",
            "reserve",
            "recover",
            "finish",
        ),
    )
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--local", type=Path)
    parser.add_argument("--harness", choices=("codex", "claude-code"), required=True)
    parser.add_argument("--owner-pid", type=int)
    parser.add_argument("--run-id")
    parser.add_argument("--decision", type=Path)
    parser.add_argument("--fixture", type=Path)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--request", type=Path)
    parser.add_argument("--item-id")
    parser.add_argument("--expected-item-version", type=int)
    parser.add_argument("--expected-revision", type=int)
    parser.add_argument("--operation-id")
    parser.add_argument("--key")
    parser.add_argument("--target-run")
    parser.add_argument("--outcome")
    bounds = parser.add_mutually_exclusive_group()
    bounds.add_argument("--single-step", action="store_true")
    bounds.add_argument("--max-steps", type=int)
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args(argv)
    try:
        harness = cast(Harness, args.harness)
        store = Store(args.config, args.local)
        result: object
        if args.command == "owners":
            result = {"owners": fw.owners(harness)}
        elif args.command == "inspect":
            state = store.read()
            result = {
                "state_path": str(store.path),
                "snapshot": state,
                "active_items": {} if state is None else active_items(state),
                "inventory_version": None
                if state is None
                else inventory_version(state),
            }
        elif args.command == "watch-plan":
            result = store.watch_plan()
        else:
            if store.config["schema_version"] != 2 and args.command != "upgrade":
                raise fw.WorkError(
                    "Complete explicit upgrade before concurrent mutations"
                )
            if args.owner_pid is None:
                raise fw.WorkError("Mutations require --owner-pid")
            if args.command == "upgrade":
                result = upgrade(store, harness, args.owner_pid)
            else:
                if args.run_id is None:
                    raise fw.WorkError("Mutations require --run-id")
                if args.command == "begin":
                    if (
                        sum(
                            p is not None
                            for p in (args.fixture, args.request, args.source)
                        )
                        > 1
                    ):
                        raise fw.WorkError("Choose one input")
                    result = store.begin(
                        harness,
                        args.owner_pid,
                        args.run_id,
                        args.request or args.source,
                        args.fixture,
                        1 if args.single_step else args.max_steps,
                        args.source is not None,
                    )
                else:
                    op: dict[str, object]
                    kind = args.command.replace("-", "_")
                    if kind in ("save", "reconcile"):
                        if args.decision is None or args.expected_item_version is None:
                            raise fw.WorkError(
                                "Require --decision and --expected-item-version; global revisions are not item versions"
                            )
                        decision = fw.obj(fw.read_json(args.decision), "decision")
                        op = {
                            "id": string(decision.get("id"), "decision ID"),
                            "expected_version": args.expected_item_version,
                            "decision": decision,
                        }
                    elif kind in ("route", "reserve"):
                        if args.decision is None:
                            raise fw.WorkError("Require --decision")
                        op = fw.obj(fw.read_json(args.decision), "operation")
                    elif kind == "collect":
                        if args.decision is None:
                            raise fw.WorkError("Require --decision")
                        observed = observation(fw.read_json(args.decision))
                        op = {"id": observed["id"], "observation": observed}
                    else:
                        op = {
                            "id": args.operation_id
                            or ("finish:" + args.run_id if kind == "finish" else "")
                        }
                        if kind == "claim":
                            op.update(
                                item_id=args.item_id,
                                expected_version=args.expected_item_version,
                            )
                        elif kind in ("intake_claim", "release_intake"):
                            op["key"] = args.key
                        elif kind == "recover":
                            op["target_run"] = args.target_run
                        elif kind == "finish":
                            op["outcome"] = args.outcome
                    result = store.mutate(
                        args.run_id, harness, args.owner_pid, kind, op
                    )
                if args.summary:
                    state = store.read()
                    if state is not None:
                        result = {
                            "state_path": str(store.path),
                            "revision": state["revision"],
                            "active_items": active_items(state),
                            "invocation": current_run(state, args.run_id, True),
                            "item_versions": state["item_versions"],
                            "inventory_version": inventory_version(state),
                        }
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(
            json.dumps(
                {
                    "error": str(exc),
                    "action": "Preserve state. Retry busy transactions; reobserve conflicts. Never reset ownership or history.",
                }
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(cli())
