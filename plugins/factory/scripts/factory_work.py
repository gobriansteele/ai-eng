"""Small persistence primitives for an agent-owned factory invocation."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import subprocess
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Literal, TypedDict, cast

from factory_config import (
    Config,
    ConfigError,
    Harness,
    load_config,
    mapping,
    string,
    timestamp,
)

PACKAGE = Path(__file__).resolve().parents[1]
ACTIONS = ("tickets", "posts", "pushes", "pull_requests")


class WorkError(ValueError):
    pass


class Owner(TypedDict):
    pid: int
    started_at: str
    executable: str


class Scope(TypedDict):
    action: str
    target: str
    revision: str


class Approval(TypedDict):
    id: str
    scope: Scope
    evidence: str


class Pending(TypedDict):
    id: str
    scope: Scope
    status: str
    returned_id: str | None
    returned_url: str | None
    evidence: str


class Item(TypedDict):
    id: str
    synthetic: bool
    source_id: str
    subitem_key: str
    source_links: list[str]
    jira_keys: list[str]
    classification: str
    stage: str
    status: str
    next_action: str
    required_role: str | None
    artifact_paths: dict[str, str]
    code: dict[str, str]
    fix_rounds: int
    approvals: list[Approval]
    pending_actions: list[Pending]


class Invocation(TypedDict):
    id: str
    owner: Owner
    harness: str
    started_at: str
    finished_at: str | None
    outcome: str | None
    max_steps: int
    steps: int
    plugin_version: str
    source_fingerprint: str
    config_hash: str
    effective_config: Config


class Decision(TypedDict):
    id: str
    reason: str
    item: Item


class Event(TypedDict):
    revision: int
    at: str
    run_id: str
    kind: str
    decision: Decision | None
    item: Item


class Snapshot(TypedDict):
    schema_version: int
    config_path: str
    factory_id: str
    revision: int
    active_run: str | None
    item: Item
    synthetic_cursors: dict[str, str]
    invocations: list[Invocation]
    events: list[Event]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def obj(value: object, where: str) -> dict[str, object]:
    if not isinstance(value, dict) or any(not isinstance(k, str) for k in value):
        raise WorkError(f"{where}: expected string-keyed object")
    return cast(dict[str, object], value)


def sequence(value: object, where: str) -> list[object]:
    if not isinstance(value, list):
        raise WorkError(f"{where}: expected array")
    return cast(list[object], value)


def integer(value: object, where: str, low: int, high: int) -> int:
    if type(value) is not int or not low <= value <= high:
        raise WorkError(f"{where}: expected integer {low}..{high}")
    return value


def nullable(value: object, where: str) -> str | None:
    return None if value is None else string(value, where)


def strings(value: object, where: str) -> list[str]:
    result = [string(v, where) for v in sequence(value, where)]
    if len(result) != len(set(result)):
        raise WorkError(f"{where}: duplicate values")
    return result


def string_map(value: object, where: str) -> dict[str, str]:
    return {k: string(v, where) for k, v in obj(value, where).items()}


def read_json(path: Path) -> object:
    try:
        return cast(
            object, json.loads(path.read_text(), object_pairs_hook=unique_pairs)
        )
    except (OSError, ValueError) as exc:
        raise WorkError(f"Cannot read {path}; repair without resetting: {exc}") from exc


def unique_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise WorkError(f"Duplicate JSON key {key}")
        result[key] = value
    return result


def scope(value: object) -> Scope:
    data = mapping(value, {"action", "target", "revision"}, "scope")
    action = string(data["action"], "scope.action")
    if action not in ACTIONS:
        raise WorkError("Unsupported external action")
    return {
        "action": action,
        "target": string(data["target"], "scope.target"),
        "revision": string(data["revision"], "scope.revision"),
    }


def approval(value: object) -> Approval:
    data = mapping(value, {"id", "scope", "evidence"}, "approval")
    return {
        "id": string(data["id"], "approval.id"),
        "scope": scope(data["scope"]),
        "evidence": string(data["evidence"], "approval.evidence"),
    }


def pending(value: object) -> Pending:
    data = mapping(
        value,
        {"id", "scope", "status", "returned_id", "returned_url", "evidence"},
        "pending action",
    )
    status = string(data["status"], "pending.status")
    if status not in ("proposed", "uncertain", "confirmed"):
        raise WorkError("Invalid pending action status")
    result: Pending = {
        "id": string(data["id"], "pending.id"),
        "scope": scope(data["scope"]),
        "status": status,
        "returned_id": nullable(data["returned_id"], "returned_id"),
        "returned_url": nullable(data["returned_url"], "returned_url"),
        "evidence": string(data["evidence"], "pending.evidence"),
    }
    if status == "confirmed" and (
        result["returned_id"] is None or result["returned_url"] is None
    ):
        raise WorkError("Confirmed actions require observed returned ID and URL")
    return result


def stable_id(source_id: str, subitem_key: str) -> str:
    return "item-" + digest([source_id, subitem_key])[:24]


def item(value: object) -> Item:
    data = mapping(value, set(Item.__annotations__), "item")
    if data["synthetic"] is not True:
        raise WorkError("Phase 3 accepts explicitly synthetic items only")
    source_id = string(data["source_id"], "source_id")
    subitem_key = string(data["subitem_key"], "subitem_key")
    identity = stable_id(source_id, subitem_key)
    if data["id"] != identity:
        raise WorkError("Item ID does not match its stable source identity")
    approvals = [approval(v) for v in sequence(data["approvals"], "approvals")]
    actions = [pending(v) for v in sequence(data["pending_actions"], "pending_actions")]
    for entries in (approvals, actions):
        if len({v["id"] for v in entries}) != len(entries):
            raise WorkError("Duplicate approval/action identity")
    status = string(data["status"], "status")
    if status not in ("ready", "blocked", "waiting_for_human", "done"):
        raise WorkError("Invalid item status")
    artifact_paths = string_map(data["artifact_paths"], "artifact_paths")
    if any(not Path(v).is_absolute() for v in artifact_paths.values()):
        raise WorkError("Artifact paths must be durable absolute paths")
    code = string_map(data["code"], "code")
    if not set(code) <= {
        "branch",
        "worktree",
        "pr_url",
        "reviewed_commit",
        "worker_reference",
    }:
        raise WorkError("Unknown code reference")
    if "worktree" in code and not Path(code["worktree"]).is_absolute():
        raise WorkError("Worktree must be an absolute path")
    return {
        "id": identity,
        "synthetic": True,
        "source_id": source_id,
        "subitem_key": subitem_key,
        "source_links": strings(data["source_links"], "source_links"),
        "jira_keys": strings(data["jira_keys"], "jira_keys"),
        "classification": string(data["classification"], "classification"),
        "stage": string(data["stage"], "stage"),
        "status": status,
        "next_action": string(data["next_action"], "next_action"),
        "required_role": nullable(data["required_role"], "required_role"),
        "artifact_paths": artifact_paths,
        "code": code,
        "fix_rounds": integer(data["fix_rounds"], "fix_rounds", 0, 2),
        "approvals": approvals,
        "pending_actions": actions,
    }


def decision(value: object) -> Decision:
    data = mapping(value, {"id", "reason", "item"}, "decision")
    return {
        "id": string(data["id"], "decision.id"),
        "reason": string(data["reason"], "decision.reason"),
        "item": item(data["item"]),
    }


def owner(value: object) -> Owner:
    data = mapping(value, {"pid", "started_at", "executable"}, "owner")
    return {
        "pid": integer(data["pid"], "owner.pid", 2, 2**31 - 1),
        "started_at": string(data["started_at"], "owner.started_at"),
        "executable": string(data["executable"], "owner.executable"),
    }


def saved_config(value: object) -> Config:
    data = mapping(value, set(Config.__annotations__), "saved effective config")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise WorkError("Unsupported saved config schema")
    slack = mapping(data["slack"], {"workspace_id", "channels"}, "saved slack")
    repositories = mapping(
        data["repositories"], {"roots", "paths"}, "saved repositories"
    )
    jira = mapping(data["jira"], {"project_key"}, "saved jira")
    intake = mapping(data["intake"], {"start_at"}, "saved intake")
    limits = mapping(
        data["limits"], {"active_work_items", "fix_rounds"}, "saved limits"
    )
    if limits != {"active_work_items": 1, "fix_rounds": 2} or any(
        type(v) is not int for v in limits.values()
    ):
        raise WorkError("Unsupported saved limits")
    channels = []
    for entry in sequence(slack["channels"], "saved channels"):
        channel = mapping(entry, {"id", "name"}, "saved channel")
        channels.append(
            {
                "id": string(channel["id"], "saved channel ID"),
                "name": string(channel["name"], "saved channel name"),
            }
        )
    if len({c["id"] for c in channels}) != len(channels):
        raise WorkError("Duplicate saved channel IDs")
    runtime = string(data["runtime_path"], "saved runtime")
    roots = strings(repositories["roots"], "saved repository roots")
    paths = strings(repositories["paths"], "saved repository paths")
    if any(not Path(v).is_absolute() for v in [runtime, *roots, *paths]):
        raise WorkError("Saved effective paths must be absolute")
    start = (
        None
        if intake["start_at"] is None
        else timestamp(intake["start_at"], "saved intake.start_at")
    )
    actions = string_map(data["actions"], "saved actions")
    if actions != {
        **{k: "approval_required" for k in ACTIONS},
        "merge": "disabled",
        "deployment": "disabled",
        "cleanup": "preview_only",
    }:
        raise WorkError("Unsupported saved action policy")
    return {
        "schema_version": 1,
        "factory_id": string(data["factory_id"], "saved factory_id"),
        "runtime_path": runtime,
        "slack": {
            "workspace_id": nullable(slack["workspace_id"], "saved workspace"),
            "channels": [{"id": c["id"], "name": c["name"]} for c in channels],
        },
        "jira": {"project_key": string(jira["project_key"], "saved project_key")},
        "repositories": {"roots": roots, "paths": paths},
        "intake": {"start_at": start},
        "limits": {"active_work_items": 1, "fix_rounds": 2},
        "actions": actions,
    }


def invocation(value: object) -> Invocation:
    data = mapping(value, set(Invocation.__annotations__), "invocation")
    effective = saved_config(data["effective_config"])
    config_hash = string(data["config_hash"], "config_hash")
    if digest(effective) != config_hash:
        raise WorkError("Saved effective configuration hash mismatch")
    harness = string(data["harness"], "harness")
    if harness not in ("codex", "claude-code"):
        raise WorkError("Invalid saved harness")
    limit = integer(data["max_steps"], "max_steps", 1, 10)
    steps = integer(data["steps"], "steps", 0, limit)
    started = timestamp(data["started_at"], "started_at")
    finished = nullable(data["finished_at"], "finished_at")
    outcome = nullable(data["outcome"], "outcome")
    if finished:
        timestamp(finished, "finished_at")
    if (finished is None) != (outcome is None):
        raise WorkError("Invocation completion mismatch")
    return {
        "id": string(data["id"], "run.id"),
        "owner": owner(data["owner"]),
        "harness": harness,
        "started_at": started,
        "finished_at": finished,
        "outcome": outcome,
        "max_steps": limit,
        "steps": steps,
        "plugin_version": string(data["plugin_version"], "plugin_version"),
        "source_fingerprint": string(data["source_fingerprint"], "source_fingerprint"),
        "config_hash": config_hash,
        "effective_config": effective,
    }


def event(value: object) -> Event:
    data = mapping(value, set(Event.__annotations__), "event")
    kind = string(data["kind"], "event.kind")
    if kind not in ("begin", "decision", "finish"):
        raise WorkError("Invalid event kind")
    operation = None if data["decision"] is None else decision(data["decision"])
    if (kind == "decision") != (operation is not None):
        raise WorkError("Event decision mismatch")
    return {
        "revision": integer(data["revision"], "event.revision", 1, 2**53),
        "at": timestamp(data["at"], "event.at"),
        "run_id": string(data["run_id"], "event.run_id"),
        "kind": kind,
        "decision": operation,
        "item": item(data["item"]),
    }


def snapshot(value: object) -> Snapshot:
    data = mapping(value, set(Snapshot.__annotations__), "snapshot")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise WorkError("Unsupported work schema")
    runs = [invocation(v) for v in sequence(data["invocations"], "invocations")]
    events = [event(v) for v in sequence(data["events"], "events")]
    revision = integer(data["revision"], "revision", 1, 2**53)
    active = nullable(data["active_run"], "active_run")
    current = item(data["item"])
    if len({r["id"] for r in runs}) != len(runs):
        raise WorkError("Duplicate run identity")
    if [r["id"] for r in runs if r["finished_at"] is None] != (
        [] if active is None else [active]
    ):
        raise WorkError("Active invocation mismatch")
    if len(events) != revision or [e["revision"] for e in events] != list(
        range(1, revision + 1)
    ):
        raise WorkError("History revision gap")
    if not events or events[-1]["item"] != current:
        raise WorkError("Current item differs from committed history")
    decisions: set[str] = set()
    for e in events:
        if (
            e["run_id"] not in {r["id"] for r in runs}
            or e["item"]["id"] != current["id"]
        ):
            raise WorkError("History identity mismatch")
        d = e["decision"]
        if d is not None:
            if d["id"] in decisions or d["item"] != e["item"]:
                raise WorkError("Decision identity/history mismatch")
            decisions.add(d["id"])
    for r in runs:
        if r["steps"] != sum(
            e["kind"] == "decision" and e["run_id"] == r["id"] for e in events
        ):
            raise WorkError("Invocation step count differs from history")
    return {
        "schema_version": 1,
        "config_path": string(data["config_path"], "config_path"),
        "factory_id": string(data["factory_id"], "factory_id"),
        "revision": revision,
        "active_run": active,
        "item": current,
        "synthetic_cursors": string_map(data["synthetic_cursors"], "synthetic_cursors"),
        "invocations": runs,
        "events": events,
    }


def atomic_snapshot(path: Path, state: Snapshot) -> None:
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


def process(pid: int) -> tuple[Owner, int, str] | None:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return None
    except PermissionError as exc:
        raise WorkError("Owner liveness unknown; refuse takeover") from exc
    environment = {**os.environ, "LC_ALL": "C", "TZ": "UTC"}
    try:
        result = subprocess.run(
            [
                "ps",
                "-ww",
                "-p",
                str(pid),
                "-o",
                "ppid=",
                "-o",
                "lstart=",
                "-o",
                "comm=",
            ],
            check=True,
            capture_output=True,
            text=True,
            env=environment,
        )
        fields = result.stdout.strip().split(None, 6)
        if len(fields) != 7:
            raise ValueError("Incomplete process identity")
        arguments = subprocess.run(
            ["ps", "-ww", "-p", str(pid), "-o", "args="],
            check=True,
            capture_output=True,
            text=True,
            env=environment,
        )
        return (
            {"pid": pid, "started_at": " ".join(fields[1:6]), "executable": fields[6]},
            int(fields[0]),
            arguments.stdout.strip(),
        )
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        # A failed ps is not proof of death: sandbox restrictions look identical.
        raise WorkError(
            "Owner identity unknown; allow process inspection or stop"
        ) from exc


def cli_command(identity: Owner, command: str, harness: Harness) -> bool:
    expected = "codex" if harness == "codex" else "claude"
    executable = identity["executable"]
    if Path(executable).name != expected:
        return False
    if harness == "claude-code":
        return True
    if command.startswith(executable + " "):
        arguments = command[len(executable) :].split()
    elif command == executable:
        arguments = []
    else:
        parts = command.split()
        if not parts or Path(parts[0]).name != expected:
            return False
        arguments = parts[1:]
    takes_value = {
        "-c",
        "--config",
        "-m",
        "--model",
        "-p",
        "--profile",
        "-s",
        "--sandbox",
        "-a",
        "--ask-for-approval",
        "-C",
        "--cd",
        "--add-dir",
        "--enable",
        "--disable",
        "--local-provider",
        "-i",
        "--image",
    }
    flags = {"--search", "--oss", "--no-alt-screen", "--full-auto", "--approve-for-me"}
    index = 0
    while index < len(arguments):
        argument = arguments[index]
        if not argument.startswith("-"):
            return argument != "app-server"
        option = argument.split("=", 1)[0]
        if option in takes_value:
            if "=" in argument:
                index += 1
            elif index + 1 < len(arguments) and not any(
                c in arguments[index + 1] for c in "\"'"
            ):
                index += 2
            else:
                return False
        elif option in flags:
            index += 1
        else:
            return False
    return True


def owners(harness: Harness) -> list[Owner]:
    candidates: list[Owner] = []
    pid = os.getppid()
    seen: set[int] = set()
    while pid > 1 and pid not in seen:
        seen.add(pid)
        info = process(pid)
        if info is None:
            raise WorkError("Process ancestry changed; retry discovery")
        identity, pid, command = info
        expected = "codex" if harness == "codex" else "claude"
        if Path(identity["executable"]).name == expected:
            return [identity] if cli_command(identity, command, harness) else []
    return candidates


def verify_owner(pid: int, harness: Harness) -> Owner:
    candidates = [candidate for candidate in owners(harness) if candidate["pid"] == pid]
    if len(candidates) != 1:
        raise WorkError(
            "No verified long-lived harness CLI ancestor; desktop must dispatch a bounded CLI invocation"
        )
    return candidates[0]


def owner_alive(identity: Owner) -> bool:
    info = process(identity["pid"])
    return info is not None and info[0] == identity


def plugin_identity(package: Path = PACKAGE) -> tuple[str, str]:
    versions: list[str] = []
    for manifest in (".codex-plugin/plugin.json", ".claude-plugin/plugin.json"):
        versions.append(
            string(obj(read_json(package / manifest), manifest)["version"], "version")
        )
    if len(set(versions)) != 1:
        raise WorkError("Loaded plugin manifest versions disagree")
    source = hashlib.sha256()
    for path in sorted(package.rglob("*")):
        relative = path.relative_to(package)
        if (
            any(
                part in ("__pycache__", ".venv", ".mypy_cache", ".ruff_cache")
                for part in relative.parts
            )
            or path.suffix == ".pyc"
        ):
            continue
        if path.name == ".DS_Store" or path.name.startswith("._"):
            continue
        if path.is_file():
            source.update(str(relative).encode() + b"\0" + path.read_bytes() + b"\0")
    return versions[0], source.hexdigest()


class Store:
    def __init__(self, config: Path, local: Path | None = None) -> None:
        self.config_path = config.resolve()
        self.config: Config = load_config(config, local)
        self.runtime = Path(self.config["runtime_path"])
        self.path = self.runtime / "state" / "work.json"
        association = config.resolve().with_name(f".{config.name}.factory-setup.json")
        if association.exists():
            data = mapping(
                read_json(association),
                {"runtime_path", "intake_start_at"},
                "setup association",
            )
            if (
                data["runtime_path"] != str(self.runtime)
                or data["intake_start_at"] != self.config["intake"]["start_at"]
            ):
                raise WorkError(
                    "Setup association changed; repair or explicitly relocate in setup, never reset work"
                )

    def read(self) -> Snapshot | None:
        if not self.path.exists():
            return None
        try:
            state = snapshot(read_json(self.path))
            if (
                state["config_path"] != str(self.config_path)
                or state["factory_id"] != self.config["factory_id"]
            ):
                raise WorkError("Runtime belongs to a different config/factory")
            return state
        except (ValueError, KeyError, TypeError) as exc:
            raise WorkError(
                f"Saved work needs repair without resetting {self.path}: {exc}"
            ) from exc

    @contextmanager
    def mutation(self) -> Iterator[None]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with (self.path.parent / ".work.mutex").open("a+") as mutex:
            try:
                fcntl.flock(mutex, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise WorkError("Concurrent state mutation; retry later") from exc
            try:
                yield
            finally:
                fcntl.flock(mutex, fcntl.LOCK_UN)

    def append(
        self, state: Snapshot, run_id: str, kind: str, operation: Decision | None = None
    ) -> None:
        state["revision"] += 1
        # Copy through validated parsing so later mutations cannot edit history.
        saved_item = item(read_copy(state["item"]))
        state["events"].append(
            {
                "revision": state["revision"],
                "at": now(),
                "run_id": run_id,
                "kind": kind,
                "decision": operation,
                "item": saved_item,
            }
        )

    def begin(
        self,
        harness: Harness,
        pid: int,
        request_id: str,
        fixture: Path | None,
        max_steps: int = 3,
    ) -> Snapshot:
        identity = verify_owner(pid, harness)
        integer(max_steps, "max_steps", 1, 10)
        string(request_id, "request_id")
        version, fingerprint = plugin_identity()
        effective = saved_config(read_copy(self.config))
        with self.mutation():
            state = self.read()
            if state is not None:
                for previous in state["invocations"]:
                    if previous["id"] == request_id:
                        if (
                            previous["owner"] != identity
                            or previous["harness"] != harness
                            or previous["config_hash"] != digest(effective)
                            or previous["max_steps"] != max_steps
                            or previous["source_fingerprint"] != fingerprint
                        ):
                            raise WorkError(
                                "Invocation ID reused with different inputs"
                            )
                        return state
                if state["active_run"] is not None:
                    active = next(
                        r
                        for r in state["invocations"]
                        if r["id"] == state["active_run"]
                    )
                    if owner_alive(active["owner"]):
                        raise WorkError("Another invocation still owns this workspace")
                    active["finished_at"], active["outcome"] = (
                        now(),
                        "interrupted_owner_dead",
                    )
                    self.append(state, active["id"], "finish")
                if fixture is not None:
                    incoming, _ = load_fixture(fixture)
                    if incoming["id"] != state["item"]["id"]:
                        raise WorkError(
                            "One active item supported; refuse a different fixture"
                        )
            else:
                if fixture is None:
                    raise WorkError(
                        "No saved item; Phase 3 requires an explicit synthetic fixture (live intake is not implemented)"
                    )
                incoming, cursors = load_fixture(fixture)
                state = {
                    "schema_version": 1,
                    "config_path": str(self.config_path),
                    "factory_id": self.config["factory_id"],
                    "revision": 0,
                    "active_run": None,
                    "item": incoming,
                    "synthetic_cursors": cursors,
                    "invocations": [],
                    "events": [],
                }
            run: Invocation = {
                "id": request_id,
                "owner": identity,
                "harness": harness,
                "started_at": now(),
                "finished_at": None,
                "outcome": None,
                "max_steps": max_steps,
                "steps": 0,
                "plugin_version": version,
                "source_fingerprint": fingerprint,
                "config_hash": digest(effective),
                "effective_config": effective,
            }
            state["invocations"].append(run)
            state["active_run"] = request_id
            self.append(state, request_id, "begin")
            atomic_snapshot(self.path, state)
            return state

    def owned(
        self,
        state: Snapshot,
        token: str,
        harness: Harness,
        pid: int,
        allow_finished: bool = False,
    ) -> Invocation:
        identity = verify_owner(pid, harness)
        matches = [r for r in state["invocations"] if r["id"] == token]
        if len(matches) != 1:
            raise WorkError("Unknown invocation token")
        run = matches[0]
        if run["owner"] != identity or run["harness"] != harness:
            raise WorkError("Invocation belongs to a different owner/harness")
        if not allow_finished and (
            state["active_run"] != token or run["finished_at"] is not None
        ):
            raise WorkError("Invocation is no longer active")
        if (
            run["config_hash"] != digest(self.config)
            or run["source_fingerprint"] != plugin_identity()[1]
        ):
            raise WorkError(
                "Config or plugin changed during invocation; stop and resume in a fresh invocation"
            )
        return run

    def save(
        self,
        token: str,
        harness: Harness,
        pid: int,
        expected_revision: int,
        operation: Decision,
    ) -> Snapshot:
        operation = decision(operation)
        with self.mutation():
            state = self.read()
            if state is None:
                raise WorkError("No saved work; repair without resetting")
            run = self.owned(state, token, harness, pid)
            for e in state["events"]:
                if e["decision"] is not None and e["decision"]["id"] == operation["id"]:
                    if e["decision"] != operation:
                        raise WorkError("Decision ID reused with different content")
                    return state
            if state["revision"] != expected_revision:
                raise WorkError("Revision changed; reread before deciding")
            if run["steps"] >= run["max_steps"]:
                raise WorkError(
                    "Invocation step limit reached; finish and resume later"
                )
            previous, updated = state["item"], operation["item"]
            if (
                previous["id"],
                previous["synthetic"],
                previous["source_id"],
                previous["subitem_key"],
            ) != (
                updated["id"],
                updated["synthetic"],
                updated["source_id"],
                updated["subitem_key"],
            ):
                raise WorkError("Cannot replace saved source identity")
            if updated["fix_rounds"] < previous["fix_rounds"]:
                raise WorkError("Fix-round count cannot decrease")
            if not set(previous["source_links"]) <= set(
                updated["source_links"]
            ) or not set(previous["jira_keys"]) <= set(updated["jira_keys"]):
                raise WorkError("Cannot drop saved source/Jira links")
            for key in ("approvals", "pending_actions"):
                if any(entry not in updated[key] for entry in previous[key]):
                    raise WorkError(
                        "Preserve scoped approvals and pending actions; reconcile explicitly in a future role"
                    )
            state["item"] = updated
            run["steps"] += 1
            self.append(state, token, "decision", operation)
            atomic_snapshot(self.path, state)
            return state

    def finish(self, token: str, harness: Harness, pid: int, outcome: str) -> Snapshot:
        if outcome not in (
            "single_step",
            "step_limit",
            "blocked",
            "waiting_for_human",
            "no_available_work",
            "stopped",
        ):
            raise WorkError("Unsupported finish outcome")
        with self.mutation():
            state = self.read()
            if state is None:
                raise WorkError("No saved work")
            run = self.owned(state, token, harness, pid, allow_finished=True)
            if run["finished_at"] is not None:
                if run["outcome"] != outcome:
                    raise WorkError("Finish retry outcome differs")
                return state
            if state["active_run"] != token:
                raise WorkError("Invocation is no longer active")
            run["finished_at"], run["outcome"] = now(), outcome
            state["active_run"] = None
            self.append(state, token, "finish")
            atomic_snapshot(self.path, state)
            return state


def read_copy(value: object) -> object:
    return cast(object, json.loads(json.dumps(value)))


def load_fixture(path: Path) -> tuple[Item, dict[str, str]]:
    data = mapping(
        read_json(path),
        {"synthetic", "description", "item", "synthetic_cursors"},
        "fixture",
    )
    if data["synthetic"] is not True:
        raise WorkError("Fixture must explicitly declare synthetic=true")
    string(data["description"], "fixture.description")
    raw_item = obj(data["item"], "fixture.item").copy()
    raw_item["id"] = stable_id(
        string(raw_item["source_id"], "source_id"),
        string(raw_item["subitem_key"], "subitem_key"),
    )
    return item(raw_item), string_map(data["synthetic_cursors"], "synthetic_cursors")


@dataclass
class Arguments:
    command: Literal["owners", "inspect", "begin", "save", "finish"]
    config: Path
    local: Path | None
    harness: Harness
    owner_pid: int | None
    run_id: str | None
    fixture: Path | None
    max_steps: int
    expected_revision: int | None
    decision: Path | None
    outcome: str | None


def parse_arguments() -> Arguments:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("owners", "inspect", "begin", "save", "finish")
    )
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--local", type=Path)
    parser.add_argument("--harness", required=True, choices=("codex", "claude-code"))
    parser.add_argument("--owner-pid", type=int)
    parser.add_argument("--run-id")
    parser.add_argument("--fixture", type=Path)
    bounds = parser.add_mutually_exclusive_group()
    bounds.add_argument("--single-step", action="store_true")
    bounds.add_argument("--max-steps", type=int, default=3)
    parser.add_argument("--expected-revision", type=int)
    parser.add_argument("--decision", type=Path)
    parser.add_argument("--outcome")
    raw: dict[str, object] = vars(parser.parse_args())
    return Arguments(
        command=cast(
            Literal["owners", "inspect", "begin", "save", "finish"], raw["command"]
        ),
        config=cast(Path, raw["config"]),
        local=cast(Path | None, raw["local"]),
        harness=cast(Harness, raw["harness"]),
        owner_pid=cast(int | None, raw["owner_pid"]),
        run_id=cast(str | None, raw["run_id"]),
        fixture=cast(Path | None, raw["fixture"]),
        max_steps=1 if raw["single_step"] is True else cast(int, raw["max_steps"]),
        expected_revision=cast(int | None, raw["expected_revision"]),
        decision=cast(Path | None, raw["decision"]),
        outcome=cast(str | None, raw["outcome"]),
    )


def main() -> int:
    try:
        args = parse_arguments()
        harness = args.harness
        store = Store(args.config, args.local)
        result: object
        if args.command == "owners":
            result = {"owners": owners(harness)}
        elif args.command == "inspect":
            result = {"state_path": str(store.path), "snapshot": store.read()}
        else:
            if args.owner_pid is None or args.run_id is None:
                raise WorkError(
                    "Mutations require --owner-pid and stable --run-id (generate once; reuse on retry)"
                )
            if args.command == "begin":
                result = store.begin(
                    harness,
                    args.owner_pid,
                    args.run_id,
                    args.fixture,
                    args.max_steps,
                )
            elif args.command == "save":
                if args.decision is None or args.expected_revision is None:
                    raise WorkError("save requires --decision and --expected-revision")
                result = store.save(
                    args.run_id,
                    harness,
                    args.owner_pid,
                    args.expected_revision,
                    decision(read_json(args.decision)),
                )
            else:
                if args.outcome is None:
                    raise WorkError("finish requires --outcome")
                result = store.finish(
                    args.run_id, harness, args.owner_pid, args.outcome
                )
        print(json.dumps(result, indent=2))
        return 0
    except (WorkError, ConfigError, OSError, KeyError) as exc:
        print(
            json.dumps(
                {
                    "error": str(exc),
                    "action": "Stop; preserve files and request repair when state is corrupt. Never reset or invent ownership.",
                }
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
