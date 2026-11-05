"""Validate observed Slack pages and derive atomic collection changes; no network calls."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from decimal import Decimal
from typing import TypedDict, cast

from factory_config import ConfigError, mapping, string, timestamp
from factory_source import (
    Message,
    Receipt,
    Source,
    array,
    message_text,
    optional,
    receipt_id,
    source,
    source_digest,
)

COVERAGE = "Fully paginated channel history in (scan_lower, upper], plus tracked/newly observed thread rechecks through upper. Replies to older untracked roots are unverified and may be missed; import those threads explicitly. Edits and deletions are not reconciled."


class SlackMessage(TypedDict):
    ts: str
    thread_ts: str
    author: str
    text: str


class Page(TypedDict):
    cursor: str | None
    next_cursor: str | None
    messages: list[SlackMessage]


class Thread(TypedDict):
    root: str
    link: str | None
    pages: list[Page]
    complete: bool
    availability: str


class Collection(TypedDict):
    cursors: dict[str, str]
    seen: list[str]
    tracked: dict[str, str]
    modes: dict[str, bool]


class Observation(TypedDict):
    id: str
    synthetic: bool
    mode: str
    workspace_id: str
    channel_id: str
    start_at: str
    lower: str
    scan_lower: str
    discovery: list[Page]
    discovery_note: str
    upper: str
    complete: bool
    history: list[Page]
    threads: list[Thread]


def slack_ts(value: object) -> str:
    result = string(value, "Slack timestamp")
    if re.fullmatch(r"[0-9]+\.[0-9]{6}", result) is None:
        raise ConfigError("Slack timestamps must retain six fractional digits")
    return result


def start_ts(value: str) -> str:
    parsed = datetime.fromisoformat(
        timestamp(value, "channel start").replace("Z", "+00:00")
    )
    seconds = int(parsed.timestamp())
    return f"{seconds}.{parsed.microsecond:06d}"


def overlap_start(cursor: str, start: str) -> str:
    value = max(Decimal(start), Decimal(cursor) - Decimal(86400))
    return f"{value:.6f}"


def identity(*values: str) -> str:
    return json.dumps(values, separators=(",", ":"))


def message_id(workspace: str, channel: str, ts: str) -> str:
    return "slack:" + identity(workspace, channel, ts)


def empty() -> Collection:
    return {"cursors": {}, "seen": [], "tracked": {}, "modes": {}}


def collection(value: object) -> Collection:
    data = mapping(value, set(Collection.__annotations__), "collection")
    maps: list[dict[str, str]] = []
    for name in ("cursors", "tracked"):
        raw = data[name]
        if not isinstance(raw, dict) or any(not isinstance(k, str) for k in raw):
            raise ConfigError("Collection map requires string keys")
        maps.append(
            {k: string(v, name) for k, v in cast(dict[str, object], raw).items()}
        )
    seen = [string(v, "seen identity") for v in array(data["seen"], "seen")]
    if len(seen) != len(set(seen)):
        raise ConfigError("Duplicate collected identity")
    for value in maps[0].values():
        slack_ts(value)
    raw_modes = data["modes"]
    if not isinstance(raw_modes, dict) or any(
        not isinstance(k, str) or type(v) is not bool for k, v in raw_modes.items()
    ):
        raise ConfigError(
            "Collection modes require channel keys and boolean synthetic markers"
        )
    modes = {k: cast(bool, v) for k, v in cast(dict[str, object], raw_modes).items()}
    return {"cursors": maps[0], "seen": seen, "tracked": maps[1], "modes": modes}


def pages(value: object) -> list[Page]:
    result: list[Page] = []
    for value in array(value, "pages"):
        raw = mapping(value, set(Page.__annotations__), "page")
        messages: list[SlackMessage] = []
        for value in array(raw["messages"], "page.messages"):
            msg = mapping(value, set(SlackMessage.__annotations__), "Slack message")
            messages.append(
                {
                    "ts": slack_ts(msg["ts"]),
                    "thread_ts": slack_ts(msg["thread_ts"]),
                    "author": string(msg["author"], "author"),
                    "text": message_text(msg["text"]),
                }
            )
        result.append(
            {
                "cursor": optional(raw["cursor"], "cursor"),
                "next_cursor": optional(raw["next_cursor"], "next_cursor"),
                "messages": messages,
            }
        )
    return result


def observation(value: object) -> Observation:
    data = mapping(value, set(Observation.__annotations__), "collection observation")
    if type(data["synthetic"]) is not bool or type(data["complete"]) is not bool:
        raise ConfigError("synthetic and complete must be boolean")
    mode = string(data["mode"], "mode")
    if mode not in ("live", "import"):
        raise ConfigError("Collection mode must be live or explicit import")
    threads: list[Thread] = []
    for value in array(data["threads"], "threads"):
        raw = mapping(value, set(Thread.__annotations__), "thread")
        if type(raw["complete"]) is not bool:
            raise ConfigError("thread.complete must be boolean")
        threads.append(
            {
                "root": slack_ts(raw["root"]),
                "link": optional(raw["link"], "thread.link"),
                "pages": pages(raw["pages"]),
                "complete": raw["complete"],
                "availability": string(raw["availability"], "availability"),
            }
        )
    if len({v["root"] for v in threads}) != len(threads):
        raise ConfigError("Duplicate thread fetch")
    return {
        "id": string(data["id"], "collection.id"),
        "synthetic": data["synthetic"],
        "mode": mode,
        "workspace_id": string(data["workspace_id"], "workspace_id"),
        "channel_id": string(data["channel_id"], "channel_id"),
        "start_at": timestamp(data["start_at"], "start_at"),
        "lower": slack_ts(data["lower"]),
        "scan_lower": slack_ts(data["scan_lower"]),
        "discovery": pages(data["discovery"]),
        "discovery_note": string(data["discovery_note"], "discovery_note"),
        "upper": slack_ts(data["upper"]),
        "complete": data["complete"],
        "history": pages(data["history"]),
        "threads": threads,
    }


def flatten(values: list[Page], upper: str) -> list[SlackMessage]:
    if not values:
        raise ConfigError(
            "Incomplete fetch: require an observed terminal page, including empty results"
        )
    expected: str | None = None
    used: set[str] = set()
    messages: dict[str, SlackMessage] = {}
    for index, page in enumerate(values):
        if index > 0 and expected is None:
            raise ConfigError("Pagination continues after a terminal page")
        if page["cursor"] != expected:
            raise ConfigError("Incomplete pagination chain")
        if expected is not None:
            if expected in used:
                raise ConfigError("Pagination cursor loop")
            used.add(expected)
        for msg in page["messages"]:
            if Decimal(msg["ts"]) > Decimal(upper):
                continue
            if msg["ts"] in messages and messages[msg["ts"]] != msg:
                raise ConfigError(
                    "Conflicting overlapping message; refetch before committing"
                )
            messages[msg["ts"]] = msg
        expected = page["next_cursor"]
    if expected is not None:
        raise ConfigError("Incomplete pagination: terminal cursor is missing")
    return sorted(messages.values(), key=lambda m: Decimal(m["ts"]))


def apply(
    previous: Collection, receipts: dict[str, Receipt], op: Observation
) -> Collection:
    if not op["complete"]:
        raise ConfigError("Incomplete collection; cursor and source receipts unchanged")
    workspace, channel = op["workspace_id"], op["channel_id"]
    key = identity(workspace, channel)
    expected = previous["cursors"].get(key, start_ts(op["start_at"]))
    if op["lower"] != expected or Decimal(op["upper"]) < Decimal(expected):
        raise ConfigError("Collection boundary differs from saved cursor/start")
    if (
        not Decimal(start_ts(op["start_at"]))
        <= Decimal(op["scan_lower"])
        <= Decimal(expected)
    ):
        raise ConfigError("Overlap must stay between setup start and saved cursor")
    result = collection(previous)
    if key in result["modes"] and result["modes"][key] != op["synthetic"]:
        raise ConfigError("Cannot mix synthetic and live collection for a channel")
    result["modes"][key] = op["synthetic"]
    seen = set(result["seen"])
    history = flatten(op["history"], op["upper"]) if op["mode"] == "live" else []
    discovered = flatten(op["discovery"], op["upper"]) if op["discovery"] else []
    if op["mode"] == "import" and (
        op["history"] or op["discovery"] or len(op["threads"]) != 1
    ):
        raise ConfigError("Explicit import requires one thread and no channel history")
    required = {
        m["thread_ts"]
        for m in history + discovered
        if Decimal(op["scan_lower"]) < Decimal(m["ts"]) <= Decimal(op["upper"])
    }
    for thread_key in previous["tracked"]:
        parts: object = json.loads(thread_key)
        if isinstance(parts, list) and parts[:2] == [workspace, channel]:
            required.add(string(parts[2], "tracked root"))
    supplied = {t["root"] for t in op["threads"]}
    if op["mode"] == "live" and not required <= supplied:
        raise ConfigError(
            "Incomplete collection: missing newly observed or tracked thread recheck"
        )
    for thread in op["threads"]:
        if not thread["complete"]:
            raise ConfigError("Incomplete thread fetch; cursor unchanged")
        messages = flatten(thread["pages"], op["upper"])
        if not any(m["ts"] == thread["root"] for m in messages) or any(
            m["thread_ts"] != thread["root"] for m in messages
        ):
            raise ConfigError(
                "Thread must retain its root and contain only that thread"
            )
        fetched = {m["ts"]: m for m in messages}
        for msg in history + discovered:
            if msg["thread_ts"] == thread["root"] and fetched.get(msg["ts"]) != msg:
                raise ConfigError(
                    "Thread fetch omits or conflicts with channel evidence"
                )
        thread_key = identity(workspace, channel, thread["root"])
        eligibility_start = (
            start_ts(op["start_at"])
            if thread_key in previous["tracked"]
            else op["scan_lower"]
        )
        imported_ids = {
            m["id"]
            for receipt in receipts.values()
            if receipt["source"]["source_id"] == "slack:" + thread_key
            and receipt["source"].get("intake", {}).get("mode") == "import"
            for m in receipt["source"]["available_thread"]
        }
        excluded_ids = imported_ids if op["mode"] == "import" else seen
        trigger = [
            message_id(workspace, channel, m["ts"])
            for m in messages
            if message_id(workspace, channel, m["ts"]) not in excluded_ids
            and (
                op["mode"] == "import"
                or Decimal(eligibility_start) < Decimal(m["ts"]) <= Decimal(op["upper"])
            )
        ]
        if not trigger:
            continue
        thread_key = identity(workspace, channel, thread["root"])
        merged: dict[str, Message] = {
            message_id(workspace, channel, m["ts"]): {
                "id": message_id(workspace, channel, m["ts"]),
                "author": m["author"],
                "text": m["text"],
            }
            for m in messages
        }
        if thread_key in previous["tracked"]:
            prior = receipts[previous["tracked"][thread_key]]["source"]
            if prior["synthetic"] != op["synthetic"]:
                raise ConfigError("Cannot mix synthetic and live collection identities")
        saved: Source = {
            "synthetic": op["synthetic"],
            "source_id": "slack:" + thread_key,
            "version": "pending",
            "link": thread["link"] or "slack:" + thread_key,
            "available_thread": sorted(
                merged.values(),
                key=lambda m: Decimal(cast(list[str], json.loads(m["id"][6:]))[2]),
            ),
            "availability": thread["availability"],
            "evidence": [],
            "intake": {
                "workspace_id": workspace,
                "channel_id": channel,
                "thread_ts": thread["root"],
                "trigger_message_ids": trigger,
                "mode": op["mode"],
                "lower": op["lower"],
                "scan_lower": op["scan_lower"],
                "upper": op["upper"],
                "coverage": COVERAGE
                + " Discovery: "
                + op["discovery_note"]
                + " Scan interval: ("
                + op["scan_lower"]
                + ", "
                + op["upper"]
                + "]."
                if op["mode"] == "live"
                else "Explicit historical thread import only; live channel cursor unchanged.",
            },
        }
        saved["version"] = (
            "capture-"
            + hashlib.sha256(json.dumps(saved, sort_keys=True).encode()).hexdigest()[
                :24
            ]
        )
        saved = source(saved)
        rid = receipt_id(saved)
        if rid in receipts and receipts[rid]["source"] != saved:
            raise ConfigError("Conflicting immutable collection receipt")
        if rid not in receipts:
            receipts[rid] = {
                "source": saved,
                "digest": source_digest(saved),
                "routing": None,
                "item_ids": {},
            }
        result["tracked"][thread_key] = rid
        seen.update(merged)
    if op["mode"] == "live":
        result["cursors"][key] = op["upper"]
    result["seen"] = sorted(seen)
    return result
