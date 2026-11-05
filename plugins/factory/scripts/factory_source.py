"""Typed saved-source and router artifact contracts; no routing judgments."""

from __future__ import annotations

import hashlib
import json
import re
from typing import NotRequired, TypedDict, cast

from factory_config import ConfigError, mapping, string, timestamp


class Message(TypedDict):
    id: str
    author: str
    text: str


class Evidence(TypedDict):
    id: str
    kind: str
    text: str


class LiveEvidence(Evidence):
    observed_at: str
    sources: list[str]
    limitations: str


class Intake(TypedDict):
    workspace_id: str
    channel_id: str
    thread_ts: str
    trigger_message_ids: list[str]
    mode: str
    lower: str
    scan_lower: str
    upper: str
    coverage: str


class Source(TypedDict):
    synthetic: bool
    source_id: str
    version: str
    link: str
    available_thread: list[Message]
    availability: str
    evidence: list[Evidence]
    intake: NotRequired[Intake]


class Finding(TypedDict):
    key: str
    classification: str
    disposition: str
    evidence: list[str]
    reason: str
    duplicate_check: str
    investigation_brief: str | None
    proposed_ticket: str | None
    existing_item_id: str | None


class Routing(TypedDict):
    source_id: str
    source_version: str
    source_digest: str
    covered_message_ids: list[str]
    findings: list[Finding]
    observations: NotRequired[list[LiveEvidence]]


class Receipt(TypedDict):
    source: Source
    digest: str
    routing: Routing | None
    item_ids: dict[str, str]


def array(value: object, where: str) -> list[object]:
    if not isinstance(value, list):
        raise ConfigError(f"{where}: expected array")
    return cast(list[object], value)


def text_list(value: object, where: str) -> list[str]:
    result = [string(v, where) for v in array(value, where)]
    if len(result) != len(set(result)):
        raise ConfigError(f"{where}: duplicate identity")
    return result


def optional(value: object, where: str) -> str | None:
    return None if value is None else string(value, where)


def message_text(value: object) -> str:
    if not isinstance(value, str):
        raise ConfigError("Message text must be a string")
    return value


def source(value: object) -> Source:
    raw_source = cast(dict[str, object], value) if isinstance(value, dict) else {}
    fields = set(Source.__annotations__) - {"intake"}
    data = mapping(
        value, fields | ({"intake"} if "intake" in raw_source else set()), "source"
    )
    if type(data["synthetic"]) is not bool:
        raise ConfigError("source.synthetic must be boolean")
    if data["synthetic"] is False and "intake" not in data:
        raise ConfigError("Live sources require intake provenance")
    messages: list[Message] = []
    for value in array(data["available_thread"], "available_thread"):
        raw = mapping(value, set(Message.__annotations__), "message")
        messages.append(
            {
                "id": string(raw["id"], "message.id"),
                "author": string(raw["author"], "author"),
                "text": message_text(raw["text"]),
            }
        )
    if not messages:
        raise ConfigError("Saved source must include its full available thread")
    evidence: list[Evidence] = []
    for value in array(data["evidence"], "evidence"):
        raw = mapping(value, set(Evidence.__annotations__), "evidence")
        evidence.append(
            {
                "id": string(raw["id"], "evidence.id"),
                "kind": string(raw["kind"], "kind"),
                "text": string(raw["text"], "text"),
            }
        )
    ids = [v["id"] for v in messages] + [v["id"] for v in evidence]
    if len(ids) != len(set(ids)):
        raise ConfigError("Duplicate source evidence identity")
    result: Source = {
        "synthetic": data["synthetic"],
        "source_id": string(data["source_id"], "source_id"),
        "version": string(data["version"], "version"),
        "link": string(data["link"], "link"),
        "available_thread": messages,
        "availability": string(data["availability"], "availability"),
        "evidence": evidence,
    }

    if "intake" in data:
        raw_intake = mapping(data["intake"], set(Intake.__annotations__), "intake")
        result["intake"] = {
            "workspace_id": string(raw_intake["workspace_id"], "workspace_id"),
            "channel_id": string(raw_intake["channel_id"], "channel_id"),
            "thread_ts": string(raw_intake["thread_ts"], "thread_ts"),
            "trigger_message_ids": text_list(
                raw_intake["trigger_message_ids"], "triggers"
            ),
            "mode": string(raw_intake["mode"], "mode"),
            "lower": string(raw_intake["lower"], "lower"),
            "scan_lower": string(raw_intake["scan_lower"], "scan_lower"),
            "upper": string(raw_intake["upper"], "upper"),
            "coverage": string(raw_intake["coverage"], "coverage"),
        }
        if not set(result["intake"]["trigger_message_ids"]) <= {
            m["id"] for m in messages
        }:
            raise ConfigError("Intake triggers must be saved messages")
        intake = result["intake"]
        if (
            intake["mode"] not in ("live", "import")
            or not intake["trigger_message_ids"]
        ):
            raise ConfigError(
                "Collected sources require a valid mode and eligible triggers"
            )
        for key in ("thread_ts", "lower", "scan_lower", "upper"):
            if re.fullmatch(r"[0-9]+\.[0-9]{6}", intake[key]) is None:
                raise ConfigError("Invalid collected source timestamp")
        prefix = [intake["workspace_id"], intake["channel_id"]]
        root_id = "slack:" + json.dumps(
            prefix + [intake["thread_ts"]], separators=(",", ":")
        )
        if result["source_id"] != root_id or root_id not in {m["id"] for m in messages}:
            raise ConfigError(
                "Collected source must retain its stable thread/root identity"
            )
    return result


def source_digest(value: Source) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def receipt_id(value: Source) -> str:
    return json.dumps([value["source_id"], value["version"]], separators=(",", ":"))


def routing(value: object, saved: Source) -> Routing:
    raw_routing = cast(dict[str, object], value) if isinstance(value, dict) else {}
    fields = set(Routing.__annotations__) - {"observations"}
    data = mapping(
        value,
        fields | ({"observations"} if "observations" in raw_routing else set()),
        "routing",
    )
    if (data["source_id"], data["source_version"], data["source_digest"]) != (
        saved["source_id"],
        saved["version"],
        source_digest(saved),
    ):
        raise ConfigError("Routing does not identify the saved source version/content")
    covered = text_list(data["covered_message_ids"], "covered messages")
    if set(covered) != {v["id"] for v in saved["available_thread"]}:
        raise ConfigError("Routing must cover every available thread message")
    ids = {v["id"] for v in saved["available_thread"]} | {
        v["id"] for v in saved["evidence"]
    }
    observations: list[LiveEvidence] = []
    for value in array(data.get("observations", []), "observations"):
        raw = mapping(value, set(LiveEvidence.__annotations__), "observation")
        observations.append(
            {
                "id": string(raw["id"], "id"),
                "kind": string(raw["kind"], "kind"),
                "text": string(raw["text"], "text"),
                "observed_at": timestamp(raw["observed_at"], "observed_at"),
                "sources": text_list(raw["sources"], "observation.sources"),
                "limitations": string(raw["limitations"], "limitations"),
            }
        )
    if observations and saved["synthetic"]:
        raise ConfigError("Synthetic routes cannot add live observations")
    if len({v["id"] for v in observations}) != len(observations) or ids & {
        v["id"] for v in observations
    }:
        raise ConfigError("Duplicate observation identity")
    ids |= {v["id"] for v in observations}
    findings: list[Finding] = []
    for value in array(data["findings"], "findings"):
        raw = mapping(value, set(Finding.__annotations__), "finding")
        refs = text_list(raw["evidence"], "finding.evidence")
        if not refs or not set(refs) <= ids:
            raise ConfigError("Each finding requires references to saved evidence")
        classification = string(raw["classification"], "classification")
        disposition = string(raw["disposition"], "disposition")
        check = string(raw["duplicate_check"], "duplicate_check")
        if (
            classification
            not in ("bug", "regression", "feature", "conversation", "unknown")
            or disposition
            not in (
                "investigate",
                "already_underway",
                "verify_existing_work",
                "needs_clarification",
                "no_action",
            )
            or check not in ("complete", "incomplete", "not_applicable")
        ):
            raise ConfigError("Unsupported routing vocabulary")
        findings.append(
            {
                "key": string(raw["key"], "finding.key"),
                "classification": classification,
                "disposition": disposition,
                "evidence": refs,
                "reason": string(raw["reason"], "reason"),
                "duplicate_check": check,
                "investigation_brief": optional(
                    raw["investigation_brief"], "investigation_brief"
                ),
                "proposed_ticket": optional(raw["proposed_ticket"], "proposed_ticket"),
                "existing_item_id": optional(
                    raw["existing_item_id"], "existing_item_id"
                ),
            }
        )
    if not findings or len({v["key"] for v in findings}) != len(findings):
        raise ConfigError("Routing needs findings with unique stable keys")
    result: Routing = {
        "source_id": saved["source_id"],
        "source_version": saved["version"],
        "source_digest": source_digest(saved),
        "covered_message_ids": covered,
        "findings": findings,
    }

    if "observations" in data:
        result["observations"] = observations
    return result


def receipt(value: object) -> Receipt:
    data = mapping(value, set(Receipt.__annotations__), "receipt")
    saved = source(data["source"])
    if data["digest"] != source_digest(saved):
        raise ConfigError("Saved source content digest mismatch")
    links = data["item_ids"]
    if not isinstance(links, dict) or any(not isinstance(k, str) for k in links):
        raise ConfigError("receipt.item_ids must be a string-keyed object")
    ids = {k: string(v, "item ID") for k, v in cast(dict[str, object], links).items()}
    result = None if data["routing"] is None else routing(data["routing"], saved)
    if result is None and ids:
        raise ConfigError("Unrouted source cannot have item associations")
    if result is not None and set(ids) != {
        f["key"] for f in result["findings"] if f["disposition"] != "no_action"
    }:
        raise ConfigError("Routing/item association mismatch")
    return {
        "source": saved,
        "digest": source_digest(saved),
        "routing": result,
        "item_ids": ids,
    }
