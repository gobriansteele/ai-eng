"""Validate factory configuration and preserve setup state across harnesses."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Literal, TypedDict, cast

import yaml

Harness = Literal["codex", "claude-code"]
Command = Literal["resolve-config", "validate", "discover", "setup", "status"]


class Channel(TypedDict):
    id: str
    name: str


class Slack(TypedDict):
    workspace_id: str | None
    channels: list[Channel]


class Repositories(TypedDict):
    roots: list[str]
    paths: list[str]


class Intake(TypedDict):
    start_at: str | None


class Jira(TypedDict):
    project_key: str


class Config(TypedDict):
    schema_version: int
    factory_id: str
    runtime_path: str
    slack: Slack
    jira: Jira
    repositories: Repositories
    intake: Intake
    limits: dict[str, int]
    actions: dict[str, str]


class Observation(TypedDict):
    status: Literal["observed", "unavailable", "not_checked"]
    evidence: str


class Evidence(TypedDict):
    harness: Harness
    capabilities: dict[str, Observation]


class Report(Evidence):
    checked_at: str
    config_hash: str
    effective_config: Config


class Discovery(TypedDict):
    repositories: list[str]
    unavailable: dict[str, str]


class Validation(TypedDict):
    valid: bool
    effective_config: Config


class Resolution(TypedDict):
    config_path: str
    local_path: str | None
    runtime_path: str
    factory_id: str
    source: Literal["explicit", "registry", "conventional"]


class Registry(TypedDict):
    schema_version: int
    default_config: str
    default_local: str | None


class SetupStatus(Resolution):
    effective_config: Config
    harness: Harness
    setup_status: Literal["partial", "ready"]
    blocked: list[str]
    capability_report: Report | None
    implemented: list[str]
    workflow: str


@dataclass
class Arguments:
    command: Command
    config: Path | None = None
    local: Path | None = None
    harness: Harness | None = None
    evidence: Path | None = None
    confirm_runtime_change: bool = False
    registry: Path | None = None
    set_default: bool = False


class ConfigError(ValueError):
    pass


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader: UniqueLoader, node: yaml.MappingNode) -> dict[str, object]:
    result: dict[str, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if not isinstance(key, str) or key in result:
            raise ConfigError("YAML keys must be unique strings")
        result[key] = loader.construct_object(value_node)
    return result


UniqueLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping
)
CAPABILITIES = (
    "slack_connection",
    "slack_channels",
    "slack_pagination",
    "slack_thread_replies",
    "slack_write",
    "jira_read",
    "jira_write",
    "github_read",
    "github_write",
    "local_execution",
)
HARNESSES = ("codex", "claude-code")


def mapping(value: object, keys: set[str], where: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != keys:
        raise ConfigError(f"{where}: expected exactly {sorted(keys)}")
    return cast(dict[str, object], value)


def string(value: object, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{where}: expected a nonempty string")
    return value


def read_yaml(path: Path) -> dict[str, object]:
    try:
        value: object = yaml.load(path.read_text(), Loader=UniqueLoader)
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ConfigError(f"Cannot read YAML {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ConfigError(f"{path}: expected a mapping")
    return cast(dict[str, object], value)


def paths(value: object, base: Path, where: str) -> list[str]:
    if not isinstance(value, list):
        raise ConfigError(f"{where}: expected a list")
    result = [str(resolve_path(item, base, where)) for item in value]
    if len(set(result)) != len(result):
        raise ConfigError(f"{where}: duplicate canonical paths")
    return result


def resolve_path(value: object, base: Path, where: str) -> Path:
    raw = Path(string(value, where)).expanduser()
    return (base / raw).resolve() if not raw.is_absolute() else raw.resolve()


def timestamp(value: object, where: str) -> str:
    try:
        parsed = datetime.fromisoformat(string(value, where).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError("timezone missing")
    except ValueError as exc:
        raise ConfigError(
            f"{where}: expected a quoted ISO timestamp with timezone"
        ) from exc
    return cast(str, value)


def load_config(config: Path, local: Path | None = None) -> Config:
    config = config.resolve()
    data = read_yaml(config)
    mapping(
        data,
        {
            "schema_version",
            "factory_id",
            "runtime_path",
            "slack",
            "jira",
            "repositories",
            "intake",
            "limits",
            "actions",
        },
        "config",
    )
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise ConfigError("Unsupported schema_version; expected 1")
    if not re.fullmatch(
        r"[a-z0-9][a-z0-9-]{0,63}", string(data["factory_id"], "factory_id")
    ):
        raise ConfigError("factory_id must be a short lowercase identifier")
    repos = mapping(data["repositories"], {"roots", "paths"}, "repositories")
    data["runtime_path"] = str(
        resolve_path(data["runtime_path"], config.parent, "runtime_path")
    )
    repos["roots"] = paths(repos["roots"], config.parent, "repositories.roots")
    repos["paths"] = paths(repos["paths"], config.parent, "repositories.paths")
    if local:
        override = read_yaml(local)
        if not set(override) <= {"runtime_path", "repositories"}:
            raise ConfigError("Local override permits filesystem paths only")
        if "runtime_path" in override:
            data["runtime_path"] = str(
                resolve_path(
                    override["runtime_path"], local.resolve().parent, "runtime_path"
                )
            )
        if "repositories" in override:
            replacement = override["repositories"]
            if not isinstance(replacement, dict) or not set(replacement) <= {
                "roots",
                "paths",
            }:
                raise ConfigError(
                    "Local repositories override permits roots and paths only"
                )
            for key, value in replacement.items():
                repos[key] = paths(value, local.resolve().parent, f"repositories.{key}")
    roots = [Path(p) for p in cast(list[str], repos["roots"])]
    for path in cast(list[str], repos["paths"]):
        if not any(Path(path).is_relative_to(root) for root in roots):
            raise ConfigError(f"Repository escapes configured roots: {path}")
    slack = mapping(data["slack"], {"workspace_id", "channels"}, "slack")
    if slack["workspace_id"] is not None:
        string(slack["workspace_id"], "slack.workspace_id")
    if not isinstance(slack["channels"], list):
        raise ConfigError("slack.channels: expected a list")
    ids: set[str] = set()
    for channel in slack["channels"]:
        channel = mapping(channel, {"id", "name"}, "channel")
        channel_id = string(channel["id"], "channel.id")
        string(channel["name"], "channel.name")
        if channel_id in ids:
            raise ConfigError("Duplicate channel ID")
        ids.add(channel_id)
    jira = mapping(data["jira"], {"project_key"}, "jira")
    string(jira["project_key"], "jira.project_key")
    intake = mapping(data["intake"], {"start_at"}, "intake")
    if intake["start_at"] is not None:
        timestamp(intake["start_at"], "intake.start_at")
    limits = mapping(data["limits"], {"active_work_items", "fix_rounds"}, "limits")
    if any(type(v) is not int for v in limits.values()) or limits != {
        "active_work_items": 1,
        "fix_rounds": 2,
    }:
        raise ConfigError(
            "This trial supports one active item and two total fix rounds"
        )
    expected_actions = {
        "tickets": "approval_required",
        "posts": "approval_required",
        "pushes": "approval_required",
        "pull_requests": "approval_required",
        "merge": "disabled",
        "deployment": "disabled",
        "cleanup": "preview_only",
    }
    if data["actions"] != expected_actions:
        raise ConfigError(
            "actions must retain trial approval, disabled merge/deployment, and preview cleanup settings"
        )
    result = cast(Config, data)
    runtime = Path(result["runtime_path"])
    package = Path(__file__).resolve().parents[1]
    forbidden = [package]
    if package.parent.name == "plugins":
        forbidden.append(package.parent.parent)
    forbidden.extend(Path(path) for path in result["repositories"]["paths"])
    forbidden.extend(Path(path) for path in discover(result)["repositories"])
    for root in forbidden:
        if runtime.is_relative_to(root):
            raise ConfigError(
                f"Runtime must be durable and outside plugin/source and target repositories: {root}"
            )
    return result


def registry_path(path: Path | None = None) -> Path:
    if path is not None:
        return Path(os.path.abspath(path.expanduser()))
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else Path.home() / ".config"
    if not base.is_absolute():
        raise ConfigError("XDG_CONFIG_HOME must be an absolute path")
    return Path(os.path.abspath(base / "ai-eng" / "registry.json"))


def absolute_registry_path(value: object, where: str) -> str:
    path = Path(string(value, where))
    if not path.is_absolute():
        raise ConfigError(f"{where}: expected an absolute path")
    return str(path.resolve())


def read_registry(path: Path) -> Registry | None:
    try:
        text = path.read_text()
    except FileNotFoundError as exc:
        if path.is_symlink() or path.parent.exists() and not path.parent.is_dir():
            raise ConfigError(f"Registry needs repair at {path}: {exc}") from exc
        return None
    except (OSError, UnicodeError) as exc:
        raise ConfigError(f"Registry needs repair at {path}: {exc}") from exc
    try:
        raw = mapping(
            json.loads(text, object_pairs_hook=unique_json_mapping),
            {"schema_version", "default_config", "default_local"},
            "registry",
        )
        if type(raw["schema_version"]) is not int or raw["schema_version"] != 1:
            raise ConfigError("Unsupported registry schema_version; expected 1")
        return {
            "schema_version": 1,
            "default_config": absolute_registry_path(
                raw["default_config"], "registry.default_config"
            ),
            "default_local": (
                absolute_registry_path(raw["default_local"], "registry.default_local")
                if raw["default_local"] is not None
                else None
            ),
        }
    except (ValueError, OSError, RuntimeError) as exc:
        raise ConfigError(
            f"Registry needs repair at {path}: {exc}; use factory-setup with explicit --config and --set-default"
        ) from exc


def unique_json_mapping(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ConfigError(f"Duplicate registry key: {key}")
        result[key] = value
    return result


def registry_config(registry: Registry) -> tuple[Path, Path | None]:
    return Path(registry["default_config"]), (
        Path(registry["default_local"]) if registry["default_local"] else None
    )


def resolve_config(
    config: Path | None = None,
    local: Path | None = None,
    registry: Path | None = None,
) -> Resolution:
    source: Literal["explicit", "registry", "conventional"] = "explicit"
    if config is None:
        saved = read_registry(registry_path(registry))
        if saved is not None:
            config, remembered_local = registry_config(saved)
            if local is None:
                local = remembered_local
            source = "registry"
        else:
            config = Path.home() / "factories" / "default" / "config.yaml"
            source = "conventional"
    try:
        config = config.expanduser().resolve()
        local = local.expanduser().resolve() if local is not None else None
        data = load_config(config, local)
    except (ConfigError, OSError, RuntimeError) as exc:
        raise ConfigError(
            f"Cannot resolve {source} factory configuration: {exc}; run factory-setup to create or repair it"
        ) from exc
    return {
        "config_path": str(config),
        "local_path": str(local) if local is not None else None,
        "runtime_path": data["runtime_path"],
        "factory_id": data["factory_id"],
        "source": source,
    }


@contextmanager
def registry_lock(path: Path) -> Iterator[None]:
    try:
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        descriptor = os.open(
            path.with_name(f".{path.name}.lock"), os.O_CREAT | os.O_RDWR, 0o600
        )
        with os.fdopen(descriptor, "w") as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            yield
    except OSError as exc:
        raise ConfigError(f"Cannot update registry at {path}: {exc}") from exc


def register_default(path: Path, resolution: Resolution) -> None:
    config = Path(resolution["config_path"])
    local = Path(resolution["local_path"]) if resolution["local_path"] else None
    load_config(config, local)
    registry: Registry = {
        "schema_version": 1,
        "default_config": str(config),
        "default_local": str(local) if local is not None else None,
    }
    atomic_write(path, json.dumps(registry, indent=2) + "\n")


def inspect_directory(path: Path) -> str | None:
    if not path.is_dir() or not os.access(path, os.R_OK | os.X_OK):
        return "directory is missing or unreadable"
    try:
        next(path.iterdir(), None)
    except OSError as exc:
        return str(exc)
    return None


def discover(data: Config) -> Discovery:
    found: set[str] = set()
    unavailable: dict[str, str] = {}
    for root_text in data["repositories"]["roots"]:
        root = Path(root_text)
        problem = inspect_directory(root)
        if problem:
            unavailable[root_text] = problem
            continue

        def onerror(error: OSError) -> None:
            unavailable[str(error.filename)] = str(error)

        for current, directories, files in os.walk(
            root, followlinks=False, onerror=onerror
        ):
            here = Path(current)
            git_marker = ".git" in directories or ".git" in files
            directories[:] = sorted(
                d for d in directories if d != ".git" and not (here / d).is_symlink()
            )
            if git_marker and not (here / ".git").is_symlink():
                found.add(str(here))
                directories.clear()
    for text in data["repositories"]["paths"]:
        path = Path(text)
        problem = inspect_directory(path)
        if problem:
            unavailable[text] = problem
        elif (path / ".git").is_symlink() or not (path / ".git").exists():
            unavailable[text] = "not a Git checkout"
        else:
            found.add(text)
    return {"repositories": sorted(found), "unavailable": unavailable}


def validate_capabilities(value: object, data: Config) -> dict[str, Observation]:
    expected = set(CAPABILITIES) | {
        f"slack_channel:{c['id']}" for c in data["slack"]["channels"]
    }
    caps = mapping(value, expected, "capabilities")
    for key, entry in caps.items():
        observation = mapping(entry, {"status", "evidence"}, key)
        if observation["status"] not in ("observed", "unavailable", "not_checked"):
            raise ConfigError(f"{key}: invalid evidence status")
        string(observation["evidence"], f"{key}.evidence")
    return cast(dict[str, Observation], caps)


def evidence_report(path: Path, data: Config, harness: Harness) -> Evidence:
    try:
        value: object = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        raise ConfigError(f"Cannot read evidence: {exc}") from exc
    raw = mapping(value, {"harness", "capabilities"}, "evidence")
    if raw["harness"] != harness:
        raise ConfigError("Evidence belongs to another harness")
    return {
        "harness": harness,
        "capabilities": validate_capabilities(raw["capabilities"], data),
    }


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def readiness(data: Config, report: Report | None) -> list[str]:
    blocked: list[str] = []
    slack_enabled = bool(data["slack"]["channels"])
    if slack_enabled and not data["slack"]["workspace_id"]:
        blocked.append("Slack workspace ID missing")
    if slack_enabled and not data["intake"]["start_at"]:
        blocked.append("Intake start not established")
    repos = discover(data)
    if not repos["repositories"]:
        blocked.append("No accessible repositories discovered")
    blocked.extend(
        f"Repository unavailable: {key}: {value}"
        for key, value in repos["unavailable"].items()
    )
    if report is None:
        blocked.append("Current harness has no capability evidence")
    else:
        blocked.extend(
            f"Capability {key}: {value['status']}"
            for key, value in report["capabilities"].items()
            if value["status"] != "observed"
            and (slack_enabled or not key.startswith("slack_"))
        )
    return blocked


def run(args: Arguments) -> Resolution | Validation | Discovery | SetupStatus:
    if args.set_default and args.command != "setup":
        raise ConfigError("--set-default is supported only by setup")
    resolution = resolve_config(args.config, args.local, args.registry)
    if args.command == "resolve-config":
        return resolution
    if args.command != "setup":
        return run_resolved(args, resolution)
    path = registry_path(args.registry)
    selected_paths = {resolution["config_path"], resolution["local_path"]}
    if (
        str(path.resolve()) in selected_paths
        or str(path.with_name(f".{path.name}.lock").resolve()) in selected_paths
    ):
        raise ConfigError(
            "Registry and registry lock must be separate from config and local files"
        )
    with registry_lock(path):
        resolution = resolve_config(args.config, args.local, args.registry)
        saved = None
        if not args.set_default:
            saved = read_registry(path)
            if saved is not None:
                try:
                    load_config(*registry_config(saved))
                except ConfigError as exc:
                    raise ConfigError(
                        f"Registered default needs repair: {exc}; use factory-setup with explicit --config and --set-default"
                    ) from exc
        result = run_resolved(args, resolution)
        if saved is None or args.set_default:
            register_default(path, resolution)
        return result


def run_resolved(
    args: Arguments, resolution: Resolution
) -> Validation | Discovery | SetupStatus:
    config = Path(resolution["config_path"])
    local = Path(resolution["local_path"]) if resolution["local_path"] else None
    data = load_config(config, local)
    if args.command == "discover":
        return discover(data)
    if args.command == "validate":
        return {"valid": True, "effective_config": data}
    if args.harness is None:
        raise ConfigError("setup and status require --harness")
    runtime = Path(data["runtime_path"])
    association_path = config.with_name(f".{config.name}.factory-setup.json")
    previous_runtime = None
    if association_path.exists():
        try:
            association = mapping(
                json.loads(association_path.read_text()),
                {"runtime_path", "intake_start_at"},
                "setup association",
            )
            previous_runtime = string(association["runtime_path"], "saved runtime_path")
            previous_start = association["intake_start_at"]
            if previous_start is not None:
                timestamp(previous_start, "saved intake start")
            if previous_start != data["intake"]["start_at"]:
                raise ConfigError(
                    "intake.start_at is system-managed; restore its established value without resetting runtime"
                )
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise ConfigError(
                f"Setup association needs repair; never reset: {exc}"
            ) from exc
    if not association_path.exists() and data["intake"]["start_at"] is not None:
        raise ConfigError(
            "Initial intake.start_at must be null; historical intake is not implemented"
        )
    runtime_changed = previous_runtime is not None and previous_runtime != str(runtime)
    if args.command == "setup" and runtime_changed and not args.confirm_runtime_change:
        raise ConfigError(
            f"Runtime path changed from {previous_runtime} to {runtime}; obtain explicit user choice then use --confirm-runtime-change. Existing records are not moved."
        )
    encoded = json.dumps(data, sort_keys=True)
    config_hash = hashlib.sha256(encoded.encode()).hexdigest()
    report_path = (
        runtime / "setup" / data["factory_id"] / f"{args.harness}-{config_hash}.json"
    )
    report: Report | None = None
    if args.command == "setup":
        if args.evidence is None:
            raise ConfigError("setup requires --evidence")
        evidence = evidence_report(args.evidence, data, args.harness)
        observed = evidence["capabilities"]
        channel_keys = ["slack_connection", "slack_channels"] + [
            f"slack_channel:{c['id']}" for c in data["slack"]["channels"]
        ]
        if (
            data["intake"]["start_at"] is None
            and data["slack"]["workspace_id"]
            and data["slack"]["channels"]
            and all(observed[key]["status"] == "observed" for key in channel_keys)
        ):
            data["intake"]["start_at"] = datetime.now(timezone.utc).isoformat()
            original = read_yaml(config)
            mapping(original["intake"], {"start_at"}, "intake")["start_at"] = data[
                "intake"
            ]["start_at"]

        starts_path = runtime / "setup" / data["factory_id"] / "channel-starts.json"
        try:
            raw_starts: object = (
                json.loads(starts_path.read_text()) if starts_path.exists() else {}
            )
            if not isinstance(raw_starts, dict) or any(
                not isinstance(k, str) or not isinstance(v, str)
                for k, v in raw_starts.items()
            ):
                raise ValueError("expected channel-to-timestamp mapping")
            starts = cast(dict[str, str], raw_starts)
            for value in starts.values():
                timestamp(value, "saved channel start")
        except (OSError, ValueError) as exc:
            raise ConfigError(
                f"Channel start metadata needs repair; never reset: {exc}"
            ) from exc
        now = datetime.now(timezone.utc).isoformat()
        if (
            data["slack"]["workspace_id"]
            and observed["slack_connection"]["status"] == "observed"
        ):
            for channel in data["slack"]["channels"]:
                if observed[f"slack_channel:{channel['id']}"]["status"] == "observed":
                    key = f"{data['slack']['workspace_id']}:{channel['id']}"
                    starts.setdefault(key, now)
        if starts or starts_path.exists():
            atomic_write(starts_path, json.dumps(starts, indent=2) + "\n")
        if (
            data["intake"]["start_at"]
            != mapping(read_yaml(config)["intake"], {"start_at"}, "intake")["start_at"]
        ):
            atomic_write(config, yaml.safe_dump(original, sort_keys=False))
        encoded = json.dumps(data, sort_keys=True)
        report = {
            "harness": args.harness,
            "capabilities": observed,
            "checked_at": now,
            "config_hash": hashlib.sha256(encoded.encode()).hexdigest(),
            "effective_config": data,
        }
        report_path = (
            runtime
            / "setup"
            / data["factory_id"]
            / f"{args.harness}-{report['config_hash']}.json"
        )
        report["effective_config"] = data
        atomic_write(report_path, json.dumps(report, indent=2) + "\n")
        atomic_write(
            association_path,
            json.dumps(
                {
                    "runtime_path": str(runtime),
                    "intake_start_at": data["intake"]["start_at"],
                },
                indent=2,
            )
            + "\n",
        )
    elif report_path.exists():
        try:
            saved = mapping(
                json.loads(report_path.read_text()),
                {
                    "harness",
                    "capabilities",
                    "checked_at",
                    "config_hash",
                    "effective_config",
                },
                "saved report",
            )
            timestamp(saved["checked_at"], "saved checked_at")
            if (
                saved["harness"] != args.harness
                or saved["config_hash"] != config_hash
                or saved["effective_config"] != data
            ):
                raise ConfigError(
                    "Saved report identity or configuration mismatch; repair without resetting runtime"
                )
            validate_capabilities(saved["capabilities"], data)
            report = cast(Report, saved)
        except (ValueError, OSError) as exc:
            raise ConfigError(
                f"Saved setup report is unreadable; repair without resetting runtime: {exc}"
            ) from exc
    blocked = readiness(data, report)
    if runtime_changed and args.command == "status":
        blocked.append(
            f"Runtime relocation requires explicit choice; previous records remain at {previous_runtime}"
        )
    return {
        **resolution,
        "effective_config": data,
        "runtime_path": str(runtime),
        "harness": args.harness,
        "setup_status": "partial" if blocked else "ready",
        "blocked": blocked,
        "capability_report": report,
        "implemented": [
            "status",
            "setup",
            "configuration validation",
            "bounded repository discovery",
            "saved-work orchestration",
            "saved-source routing",
            "direct harness request intake",
            "bounded Slack collection and historical thread import",
            "scoped investigation with durable local evidence",
            "product planning with durable questions and answer resume",
            "technical design with justified skips and durable architectural choices",
            "explicitly authorized local implementation with dedicated worktrees and durable evidence",
            "independent review, adjudication and two shared fix rounds",
            "scoped draft PR publication, uncertain-action reconciliation and fresh CI/review follow-up",
            "deduplicated local Slack/Jira report drafts and scoped post reconciliation preserving engineering state",
            "evidence-based local retrospectives and ownership-aware maintenance previews/additive archive copies",
            "native scheduling runbook without schedule activation",
        ],
        "workflow": "direct chat and bounded Slack intake, routing, investigation, product planning, technical design, authorized local implementation, independent review and authorized draft PR follow-up with two shared fix rounds; remote coverage and permission limits reported; local report drafts preserve engineering state; exact authorized message delivery untested; native scheduling documented but not activated/tested; maintenance defaults preview-only",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("resolve-config", "validate", "discover", "setup", "status")
    )
    parser.add_argument("--config", type=Path)
    parser.add_argument("--registry", type=Path)
    parser.add_argument("--set-default", action="store_true")
    parser.add_argument("--local", type=Path)
    parser.add_argument("--harness", choices=HARNESSES)
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--confirm-runtime-change", action="store_true")
    parsed = parser.parse_args()
    args = Arguments(
        command=parsed.command,
        config=parsed.config,
        local=parsed.local,
        harness=parsed.harness,
        evidence=parsed.evidence,
        confirm_runtime_change=parsed.confirm_runtime_change,
        registry=parsed.registry,
        set_default=parsed.set_default,
    )
    if args.command in ("setup", "status") and not args.harness:
        parser.error("setup and status require --harness")
    if args.command == "setup" and not args.evidence:
        parser.error("setup requires --evidence")
    try:
        print(json.dumps(run(args), indent=2))
    except (ConfigError, OSError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
