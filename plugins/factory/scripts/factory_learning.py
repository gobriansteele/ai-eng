"""Record evidence-backed improvement candidates without changing engineering state."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, TypedDict, cast

from factory_config import ConfigError, atomic_write, load_config, mapping, string

Kind = Literal["observation", "adjudication", "evaluation"]
Status = Literal[
    "open", "accepted", "rejected", "already_fixed", "verified", "regressed"
]


class Evidence(TypedDict):
    path: str
    sha256: str


class Event(TypedDict):
    id: str
    kind: Kind
    details: dict[str, str]
    evidence: list[Evidence]
    recorded_at: str


class Candidate(TypedDict):
    schema_version: int
    key: str
    events: list[Event]


FIELDS: dict[Kind, set[str]] = {
    "observation": {"summary", "trigger", "expected_behavior", "source_version"},
    "adjudication": {"disposition", "reason", "acceptance_scenario"},
    "evaluation": {"outcome", "change", "reason"},
}


def read_json(path: Path) -> object:
    try:
        return cast(object, json.loads(path.read_text()))
    except (OSError, ValueError) as exc:
        raise ConfigError(f"Cannot read {path}: {exc}") from exc


def candidate_key(value: object) -> str:
    key = string(value, "key")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,95}", key):
        raise ConfigError("key must be a short lowercase issue identifier")
    return key


def kind_of(value: object) -> Kind:
    if not isinstance(value, str) or value not in FIELDS:
        raise ConfigError("kind must be observation, adjudication or evaluation")
    return value


def details_for(kind: Kind, value: object) -> dict[str, str]:
    raw = mapping(value, FIELDS[kind], "details")
    details = {key: string(entry, key) for key, entry in raw.items()}
    if kind == "adjudication" and details["disposition"] not in (
        "accepted",
        "rejected",
        "already_fixed",
    ):
        raise ConfigError("Invalid adjudication disposition")
    if kind == "evaluation" and details["outcome"] not in (
        "passed",
        "failed",
        "inconclusive",
    ):
        raise ConfigError("Invalid evaluation outcome")
    return details


def capture_evidence(value: object) -> list[Evidence]:
    if not isinstance(value, list) or not value:
        raise ConfigError("evidence must contain readable absolute file paths")
    evidence: list[Evidence] = []
    for entry in value:
        path = Path(string(entry, "evidence path")).expanduser()
        if not path.is_absolute():
            raise ConfigError("Evidence paths must be absolute")
        try:
            content = path.read_bytes()
        except OSError as exc:
            raise ConfigError(f"Cannot read evidence {path}: {exc}") from exc
        if not content:
            raise ConfigError(f"Evidence is empty: {path}")
        evidence.append(
            {"path": str(path.resolve()), "sha256": hashlib.sha256(content).hexdigest()}
        )
    if len({entry["path"] for entry in evidence}) != len(evidence):
        raise ConfigError("Duplicate evidence path")
    return evidence


def parse_event(value: object) -> Event:
    raw = mapping(
        value, {"id", "kind", "details", "evidence", "recorded_at"}, "saved event"
    )
    kind = kind_of(raw["kind"])
    evidence = raw["evidence"]
    if not isinstance(evidence, list) or not evidence:
        raise ConfigError("Saved event has no evidence")
    checked: list[Evidence] = []
    for entry in evidence:
        source = mapping(entry, {"path", "sha256"}, "saved evidence")
        path = string(source["path"], "path")
        digest = string(source["sha256"], "sha256")
        if not Path(path).is_absolute() or not re.fullmatch(r"[a-f0-9]{64}", digest):
            raise ConfigError("Invalid saved evidence identity")
        checked.append({"path": path, "sha256": digest})
    recorded_at = string(raw["recorded_at"], "recorded_at")
    try:
        observed = datetime.fromisoformat(recorded_at)
        if observed.tzinfo is None:
            raise ValueError("Timezone missing")
    except ValueError as exc:
        raise ConfigError("Invalid saved observation time") from exc
    return {
        "id": string(raw["id"], "id"),
        "kind": kind,
        "details": details_for(kind, raw["details"]),
        "evidence": checked,
        "recorded_at": recorded_at,
    }


def read_candidate(path: Path, key: str) -> Candidate:
    raw = mapping(read_json(path), {"schema_version", "key", "events"}, "candidate")
    if (
        type(raw["schema_version"]) is not int
        or raw["schema_version"] != 1
        or raw["key"] != key
    ):
        raise ConfigError("Candidate identity/schema mismatch")
    events = raw["events"]
    if not isinstance(events, list) or not events:
        raise ConfigError("Candidate must contain events")
    parsed = [parse_event(event) for event in events]
    if len({event["id"] for event in parsed}) != len(parsed):
        raise ConfigError("Duplicate saved event identity")
    result: Candidate = {"schema_version": 1, "key": key, "events": parsed}
    state_of(result)
    return result


def state_of(candidate: Candidate) -> Status:
    status: Status = "open"
    observations = 0
    for event in candidate["events"]:
        kind, details = event["kind"], event["details"]
        if kind == "observation":
            observations += 1
        elif not observations:
            raise ConfigError("An observation must precede adjudication/evaluation")
        elif kind == "adjudication":
            status = cast(Status, details["disposition"])
        else:
            if status not in ("accepted", "verified", "regressed"):
                raise ConfigError("Evaluation requires an accepted candidate")
            if details["outcome"] == "passed":
                status = "verified"
            elif details["outcome"] == "failed":
                status = "regressed"
            else:
                status = "accepted"
    return status


def unreviewed_observations(candidate: Candidate) -> int:
    count = 0
    for event in reversed(candidate["events"]):
        if event["kind"] != "observation":
            break
        count += 1
    return count


def record(root: Path, value: object) -> dict[str, object]:
    raw = mapping(value, {"id", "key", "kind", "details", "evidence"}, "event")
    key, kind = candidate_key(raw["key"]), kind_of(raw["kind"])
    event: Event = {
        "id": string(raw["id"], "id"),
        "kind": kind,
        "details": details_for(kind, raw["details"]),
        "evidence": capture_evidence(raw["evidence"]),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    root.mkdir(parents=True, exist_ok=True)
    with (root / ".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        path = root / f"{key}.json"
        candidate: Candidate = (
            read_candidate(path, key)
            if path.exists()
            else {"schema_version": 1, "key": key, "events": []}
        )
        for previous in candidate["events"]:
            if previous["id"] == event["id"]:
                if (
                    previous["kind"] != event["kind"]
                    or previous["details"] != event["details"]
                    or previous["evidence"] != event["evidence"]
                ):
                    raise ConfigError("Event ID reused with changed content/evidence")
                return {
                    "changed": False,
                    "path": str(path),
                    "status": state_of(candidate),
                    "unreviewed_observations": unreviewed_observations(candidate),
                    "candidate": candidate,
                }
        candidate["events"].append(event)
        status = state_of(candidate)
        atomic_write(path, json.dumps(candidate, indent=2, sort_keys=True) + "\n")
        return {
            "changed": True,
            "path": str(path),
            "status": status,
            "unreviewed_observations": unreviewed_observations(candidate),
            "candidate": candidate,
        }


def inspect(
    root: Path, key: str | None = None, summary: bool = False
) -> list[dict[str, object]]:
    paths = (
        [root / f"{candidate_key(key)}.json"] if key else sorted(root.glob("*.json"))
    )
    result: list[dict[str, object]] = []
    for path in paths:
        candidate = read_candidate(path, candidate_key(path.stem))
        entry: dict[str, object] = {
            "path": str(path),
            "status": state_of(candidate),
            "unreviewed_observations": unreviewed_observations(candidate),
        }
        if summary:
            entry.update(
                key=candidate["key"],
                event_count=len(candidate["events"]),
                latest_summary=next(
                    event["details"]["summary"]
                    for event in reversed(candidate["events"])
                    if event["kind"] == "observation"
                ),
            )
        else:
            entry["candidate"] = candidate
        result.append(entry)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("record", "inspect"))
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--local", type=Path)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--key")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    try:
        runtime = Path(load_config(args.config, args.local)["runtime_path"])
        root = runtime / "retros" / "candidates"
        if args.command == "record":
            if args.input is None or args.key is not None or args.summary:
                raise ConfigError(
                    "record requires --input; --key/--summary are inspect-only"
                )
            result: object = record(root, read_json(args.input))
        else:
            if args.input is not None:
                raise ConfigError("inspect does not accept --input")
            result = inspect(root, args.key, args.summary)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (ConfigError, OSError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
