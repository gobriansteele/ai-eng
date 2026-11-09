"""Capture a command and declared input-file evidence in a new external directory."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict


class FileObservation(TypedDict):
    path: str
    sha256: str | None
    error: str | None


class GitObservation(TypedDict):
    root: str | None
    head: str | None
    status: str | None


class Snapshot(TypedDict):
    git: GitObservation
    files: list[FileObservation]


def git_value(cwd: Path, *arguments: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *arguments], cwd=cwd, capture_output=True, text=True, check=False
        )
    except OSError:
        return None
    return result.stdout.rstrip("\n") if result.returncode == 0 else None


def snapshot(cwd: Path, paths: list[Path]) -> Snapshot:
    files: list[FileObservation] = []
    for path in paths:
        try:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            error = None
        except OSError as exc:
            digest, error = None, str(exc)
        files.append({"path": str(path), "sha256": digest, "error": error})
    return {
        "git": {
            "root": git_value(cwd, "rev-parse", "--show-toplevel"),
            "head": git_value(cwd, "rev-parse", "HEAD"),
            "status": git_value(
                cwd, "status", "--porcelain=v1", "--untracked-files=all"
            ),
        },
        "files": files,
    }


def record(cwd: Path, output: Path, inputs: list[Path], command: list[str]) -> int:
    cwd, output = cwd.resolve(strict=True), output.resolve()
    if not cwd.is_dir() or not command or not inputs:
        raise ValueError(
            "Require a working directory, command and declared input files"
        )
    if any(".." in path.parts for path in inputs):
        raise ValueError("Declared input paths must not contain parent traversal")
    paths = [cwd / path for path in inputs]
    if len(set(paths)) != len(paths):
        raise ValueError("Declared input files must be distinct")
    before = snapshot(cwd, paths)
    if any(entry["error"] is not None for entry in before["files"]):
        raise ValueError(
            "Every declared input must be readable before command execution"
        )
    git_root = before["git"]["root"]
    source = Path(git_root).resolve() if git_root else cwd
    if output == source or source in output.parents:
        raise ValueError("Evidence directory must be outside the source checkout")
    output.mkdir(parents=True, exist_ok=False)
    started_at = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    exit_code: int | None = None
    launch_error: str | None = None
    with (
        (output / "stdout.txt").open("wb") as stdout,
        (output / "stderr.txt").open("wb") as stderr,
    ):
        try:
            result = subprocess.run(
                command, cwd=cwd, stdout=stdout, stderr=stderr, check=False
            )
            exit_code = result.returncode
        except OSError as exc:
            launch_error = str(exc)
    elapsed = time.monotonic() - started
    ended_at = datetime.now(timezone.utc).isoformat()
    after = snapshot(cwd, paths)
    metadata = {
        "schema_version": 1,
        "command": command,
        "cwd": str(cwd),
        "started_at": started_at,
        "ended_at": ended_at,
        "elapsed_seconds": elapsed,
        "exit_code": exit_code,
        "launch_error": launch_error,
        "stdout_path": str(output / "stdout.txt"),
        "stderr_path": str(output / "stderr.txt"),
        "before": before,
        "after": after,
    }
    (output / "command.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n"
    )
    return exit_code if exit_code is not None and exit_code >= 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cwd", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--input", required=True, action="append", type=Path)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    try:
        return record(args.cwd, args.output, args.input, command)
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
