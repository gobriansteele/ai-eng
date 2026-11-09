# Saved work and invocation contract

Apply the selected item’s [execution mode](execution-modes.md) to decisions,
authorization and recovery. Legacy items without execution metadata retain their
existing checkpoints; mode-specific delegation governs the human waits below.

Use `uv run --isolated --frozen --no-dev --project <loaded-plugin> python
<loaded-plugin>/scripts/factory_work.py <command> --config <path> --harness
codex|claude-code [--local <yaml>]`. Dependencies/cache behavior matches the
[configuration contract](../../factory-setup/references/configuration.md).
Resolve the user-facing default once through the configuration contract, then
pass its pinned absolute config and optional local override explicitly to every
work-helper call. `factory_work.py` requires that explicit config; it never reads
the registry. A later default change cannot redirect this invocation. Do not
borrow another environment.

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
Under command-prefix permissions, make the permitted Python call separately and
paste the observed UUID and resolved paths literally into each permitted helper
call; do not wrap the helper in assignments, substitutions or command chains.
For a new synthetic test only:

```text
begin --owner-pid <observed-cli-pid> --run-id <uuid> --fixture <loaded-plugin>/fixtures/synthetic-item.json --single-step
```

To test preservation instead, select `fixtures/synthetic-resume.json`; its one
fix round, illustrative approval scope and proposed action are explicitly
synthetic. They grant no real permissions and claim no external execution.
`synthetic_cursors` are illustrative handoff metadata, not watcher cursors. They remain separate from watcher cursors. Existing state resumes with no fixture;
live collection follows the preserved setup channel starts. Providing the same legacy fixture
identity never resets saved values; a different legacy fixture is refused.
For saved-source routing use `begin --source <absolute-synthetic-source.json>`
instead of `--fixture`. Both are explicit offline demonstration input. Config-only begin is valid on a
fresh production workspace, creating empty schema-2 inventory before collection.
`begin --request <absolute-direct-capture.json>` accepts real direct chat intake
with [direct provenance](direct-intake.md), or explicitly synthetic direct test
input. Choose only one of `--request`, `--source` and `--fixture`. The request is
saved atomically under the verified invocation owner before Slack collection;
capture and exact retry consume no semantic step. Source receipt replay/conflict
rules apply unchanged, and `--source` remains synthetic-only.
A new source can be saved even when an active item is blocked. Read
[the router contract](../../factory-route/references/routing.md) for source and
result fields. `route --decision <absolute-json> --expected-revision <revision>`
uses the same owner/run arguments as save. It commits the agent-authored result,
explicit item updates and selected active ID together and consumes one step.
No-action commits a receipt/disposition audit with zero work items.

Exact source identity/version/content replay reuses its receipt and routing;
repeated captures cannot silently reroute or reset items. Conflicting content
under the same immutable version refuses. A distinct version of the same thread
is retained separately; the router reads prior captures/items and may attach with
evidence. All source bodies and local ticket proposals stay inside runtime.

Schema 2 uses `items` keyed by stable ID, nullable `active_item_id`, and `sources`
keyed by compact JSON `[source_id,version]`. There is no mirrored current item.
Only the selected item advances through ordinary `save`; a route may add/update
several associated items while retaining one selected active ID. Additional
saved items are pending. The helper validates explicit changes; the agent chooses
workflow transitions, active selection and stop reasons.

Schema 1 is still readable. `inspect` returns a validated compatibility view
with the original schema number and inventory projection; it writes nothing.
Only `begin`, under a verified owner and after checking prior owner liveness,
migrates to schema 2 in its atomic snapshot. The legacy item, events, invocations,
fix count, scopes/actions and cursor metadata are preserved. Legacy events remain
verbatim and a migration event is appended. No source body is fabricated. Other
mutators require schema 2 or 3; use a fresh begin to migrate. Corrupt schema 1 is
refused before any replacement; live/unknown owners prevent migration.

Normal `begin` has no step cap (`max_steps: null`). An explicit positive
`--max-steps` sets a cap; `--single-step` is equivalent to 1. Old numeric limits
remain intact in saved invocations. All modes still save progress after each step.
Both hosts need the updated plugin before resuming null caps or execution metadata. No YAML limit is added. The run UUID is the
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
`approvals`, `pending_actions`, and optional `execution` with `mode`
(`default`, `bedtime`, `restricted`) and an absolute `evidence` report path. New or
changed execution metadata requires a readable, nonempty immutable authorization
report; a changed mode needs a new report. Routing may set it only for a newly
selected item, never unrelated pending items or an existing item. Use an ordinary
owner-gated save for an explicit selected-item mode change. Status is `ready`, `blocked`, `waiting_for_human`
or `done`; the helper does not choose stages or roles. Artifact/worktree paths
are absolute. `code` can contain branch, worktree, pr_url, reviewed_commit and
worker_reference when observed. Durable paths/links are the handoff; a host worker
ID alone is insufficient. Approval scope is exactly action/target/revision with
an ID and evidence; a pending action additionally carries status
proposed/uncertain/confirmed, nullable returned_id/returned_url and evidence.
Confirmed actions require observed returned ID and URL. Ordinary save preserves prior approvals/actions verbatim; the narrow
external-action reconciliation command below handles evidenced status transitions. The helper validates structure;
it cannot prove human permission, remote state, or artifact existence.

The helper enforces one active invocation, revision CAS, step bounds, stable
identity, nondecreasing fix rounds (at most one increment per save), preserved source/Jira links and prior
scoped approval/action entries. Legacy/restricted work cannot start a third fix;
default/bedtime uses the mode-specific progress/recovery rule. Duplicate decision ID with identical content
returns saved state without consuming another step, even with an old revision.
Reusing an ID with different content fails. Use a stable ID for the logical
transition across interruptions; read history before choosing a new decision.

`finish --owner-pid <pid> --run-id <uuid> --outcome <reason>` releases ownership.
Reasons: single_step, step_limit, blocked, waiting_for_human, no_available_work,
stopped, completed. Retrying the same finish is idempotent. A crash before finish leaves the
token active; a later `begin` may mark it interrupted only after verifying the
owner is dead or its PID now has a different observed identity. An alive owner
blocks even when it seems idle; unknown ownership blocks until inspection/repair.
No elapsed-time takeover. Stop the original CLI before switching harnesses.

The only authority is `<runtime>/state/work.json`, containing items, selected active ID, saved source receipts,
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
Saved config values are evidence, not authorization. No standalone reset/migrate, external write or worker-completion command exists.
`watch-plan` and owner-gated `collect --decision <observation-json>` implement
[bounded collection](../../factory-watch/references/collection.md). The first
collection adds schema 3 and its collection field, migration event, immutable
source receipts and cursor in one atomic replacement. Collection consumes no
semantic step; route/save keep their configured bound. Inspect supports schemas
1/2/3 read-only; other mutators support 2/3. Old plugin versions must be refreshed
before resuming schema 3. Failed/incomplete reads change no canonical bytes. Add `--summary` to mutators to print a bounded receipt (path,
revision, IDs, invocation metadata) instead of repeating the whole history.
Inspect the saved source and relevant inventory in the canonical file when
needed; never edit it directly.

## Role evidence contracts

Investigation, planning, design, implementation, review and reporting retain the
shared [role evidence contracts](persistence.md#investigation-artifacts-and-handoff).
For a legacy run use the owner/global-revision helper syntax above, not schema-4
claims/item-version flags. There is one shared role workflow; this reference
only preserves the legacy persistence format and invocation rules.
