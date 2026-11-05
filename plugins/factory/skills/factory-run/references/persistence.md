# Saved work and invocation contract

Use `uv run --isolated --frozen --no-dev --project <loaded-plugin> python
<loaded-plugin>/scripts/factory_work.py <command> --config <path> --harness
codex|claude-code [--local <yaml>]`. Dependencies/cache behavior matches the
[configuration contract](../../factory-setup/references/configuration.md).
No global registry, environment borrowing, or config schema change is involved.

`owners` is read-only and prints verified harness CLI ancestor identities. The
actual long-lived process must be the nearest `codex` or `claude` executable in
this helper's ancestry; `codex app-server` is excluded. `ps` establishes executable, start time
and ancestry with locale/timezone normalized to C/UTC, and `kill(pid, 0)`
establishes liveness. Sandbox denial is unknown,
not death. Use a reported candidate's exact PID. Each mutator verifies the same
owner again; a token alone cannot transfer ownership to another live harness.
`inspect` is read-only, returns `state_path` and `snapshot` (null when absent), and
validates existing records. Both commands require explicit config/harness.

Generate a UUID once with local Python's `uuid.uuid4()` and reuse it on retries.
For a new synthetic test only:

```text
begin --owner-pid <observed-cli-pid> --run-id <uuid> --fixture <loaded-plugin>/fixtures/synthetic-item.json --single-step
```

To test preservation instead, select `fixtures/synthetic-resume.json`; its one
fix round, illustrative approval scope and proposed action are explicitly
synthetic. They grant no real permissions and claim no external execution.
`synthetic_cursors` are illustrative handoff metadata, not watcher cursors. Real
cursor files and setup channel starts remain untouched. On an existing item omit
`--fixture`; providing the same fixture deduplicates by source ID/subitem key and
never resets persisted values. A different fixture is refused while this single
item is present. Phase 3 snapshot schema version 1 deliberately supports only one
synthetic item; later multi-item intake needs a reviewed compatible migration,
not resetting this state.

Normal `begin` defaults to `--max-steps 3`, with valid range 1..10;
`--single-step` is equivalent to 1. No YAML limit is added. The run UUID is the
durable token. `begin` with the same UUID and same invocation inputs is
idempotent, including after replacement succeeded but the reply was lost.
A finished UUID never silently starts a new invocation: use a fresh UUID.

`save --owner-pid <pid> --run-id <uuid> --expected-revision <read-revision>
--decision <absolute-json-path>` takes exactly:

```json
{"id":"stable-decision-id","reason":"Evidence for this agent decision","item":{}}
```

Replace `{}` with the complete item copied from the latest snapshot and changed
only as justified. Item fields: stable `id`, `synthetic`, `source_id`,
`subitem_key`, `source_links`, `jira_keys`, `classification`, `stage`, `status`,
`next_action`, nullable `required_role`, `artifact_paths`, `code`, `fix_rounds`,
`approvals`, `pending_actions`. Status is `ready`, `blocked`, `waiting_for_human`
or `done`; the helper does not choose stages or roles. Artifact/worktree paths
are absolute. `code` can contain branch, worktree, pr_url, reviewed_commit and
worker_reference when observed. Durable paths/links are the handoff; a host worker
ID alone is insufficient. Approval scope is exactly action/target/revision with
an ID and evidence; a pending action additionally carries status
proposed/uncertain/confirmed, nullable returned_id/returned_url and evidence.
Confirmed actions require observed returned ID and URL. Phase 3 preserves prior
approvals/actions verbatim; a future implementing role must add a reviewed
reconciliation operation before changing them. The helper validates structure;
it cannot prove human permission, remote state, or artifact existence.

The helper enforces one active invocation, revision CAS, step bounds, stable
identity, nondecreasing fix rounds (0..2), preserved source/Jira links and prior
scoped approval/action entries. Duplicate decision ID with identical content
returns saved state without consuming another step, even with an old revision.
Reusing an ID with different content fails. Use a stable ID for the logical
transition across interruptions; read history before choosing a new decision.

`finish --owner-pid <pid> --run-id <uuid> --outcome <reason>` releases ownership.
Reasons: single_step, step_limit, blocked, waiting_for_human, no_available_work,
stopped. Retrying the same finish is idempotent. A crash before finish leaves the
token active; a later `begin` may mark it interrupted only after verifying the
owner is dead or its PID now has a different observed identity. An alive owner
blocks even when it seems idle; unknown ownership blocks until inspection/repair.
No elapsed-time takeover. Stop the original CLI before switching harnesses.

The only authority is `<runtime>/state/work.json`, containing current item,
ordered decision history and all invocation records together. This is a small
Phase 3 refinement of the plan's suggested record/event/run tree: no mirrors or
multi-file transaction engine. The helper validates the full snapshot before
any mutation, writes a temporary file, fsyncs it, atomically replaces the
snapshot, then fsyncs its directory. A crash exposes the prior or next complete
snapshot, never separately advanced records/events/run metadata. A failure after
replace may have committed: inspect and retry the exact operation ID. Uncommitted
temporary files are ignored, not interpreted as new state. A short `fcntl` mutex
serializes helper mutations; the durable token keeps ownership between calls.
Direct file writes can bypass these protections. The snapshot is intentionally
small for this trial; history compaction/export is not implemented.

Every invocation saves loaded manifest version, a SHA256 over sorted package
source paths/content (excluding Python/tool caches), effective non-secret config
and its hash. Current source/config changes during an invocation block further
mutations; stop the owning CLI and resume with a fresh invocation. Runtime
identity is the resolved config path plus factory ID, never a global default.
Saved config values are evidence, not authorization. No reset, migrate, external
write, worker-completion or live-intake command exists in this helper.
