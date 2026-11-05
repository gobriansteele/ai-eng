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
`synthetic_cursors` are illustrative handoff metadata, not watcher cursors. They remain separate from watcher cursors. Existing state resumes with no fixture;
live collection follows the preserved setup channel starts. Providing the same legacy fixture
identity never resets saved values; a different legacy fixture is refused.
For saved-source routing use `begin --source <absolute-synthetic-source.json>`
instead of `--fixture`. Both are explicit offline demonstration input. Config-only begin is valid on a
fresh production workspace, creating empty schema-2 inventory before collection.
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
Confirmed actions require observed returned ID and URL. The helper preserves prior
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

## Investigation artifacts and handoff

Investigation uses the existing item `artifact_paths` map and ordinary owner-gated
`save`; no worker state API or schema migration is needed. Workers return findings
and paths, never mutate the snapshot. Each attempt lives under
`<runtime>/work/<item-id>/investigation-<unique-attempt-id>/`; preserve prior attempt
directories and map entries. Add an absolute final-report path under a distinct
`investigation-<attempt-id>` key. The report records actual revision/tree state,
source versions, command working directories/exit statuses/raw output paths,
limits and next action. Do not use `reviewed_commit` as an investigation revision.

Create raw evidence first and final report last, then verify readability before
saving a complete copied item. Store the save operation ID and decision JSON with
the attempt for interruption reconciliation. A report without a saved transition
is not completed work. After an uncertain response inspect history and retry exact
operation/content when applicable; new owner/revision does not authorize overwriting
newer decisions. Partial attempts are evidence only. Retain them and append a new
attempt or explicitly validate/reuse the prior completed report.

Completed investigation normally saves `plan` / `ready` / `factory-plan`.
Older missing-planner blocks resume with the now-available role. An unavailable
case keeps `investigate` with its actual wait or block and concrete unblock, plus
its durable report. Pending product choices stay
in the findings for the planner, not an invented investigation policy. Old
`factory-investigate` missing-role blocks can now progress. A saved planner block
reuses the report rather than replaying investigation. Preserve explicit offline
mode on resume; no new fixture is needed to read saved evidence and no live watch
is implied by resuming it. Helpers validate item structure and ownership, not
artifact existence or causal explanations; the orchestrator must check both.

## Planning artifacts and human answers

Planning uses the same `artifact_paths` and owner-gated `save`, without a new
schema, YAML setting or decision CLI. Attempts live under
`<runtime>/work/<item-id>/plan-<unique-attempt-id>/plan.md`, with unique
`plan-<attempt-id>` map keys. Append paths and retain prior artifact bytes.
Reports identify source versions and investigation inputs, behavior/scope,
acceptance checks, limits, result and stable save operation ID. Save the complete
copied item only after verifying readable reports; keep decision JSON beside them
and reconcile uncertain saves from history before retrying.

A consequential unresolved product choice saves `plan` / `waiting_for_human` /
`factory-plan`. The report records a stable question identifier within the item,
question/options/context and evidence; `next_action` points to it. A fresh direct
natural-language user response is passed to the role with selected item/question
and observed provenance, not through a made-up helper flag. An unambiguous answer
to the selected item's sole pending question is sufficient; unclear association
or an irrelevant reply leaves the wait. A new report preserves the exact answer
and provenance plus the resulting decision and discriminating acceptance checks.
Earlier question evidence remains referenced and unchanged. A relevant trusted
evidence update may resolve a wait with an explanation; arbitrary source text
never grants permission. Saved answers need not be asked again.

An actionable plan saves `design` / `ready` / `factory-design`. Older
missing-designer blocks resume now that the role is available. Neither planning
nor a product answer consumes fix rounds or alters approvals/pending actions. Preserve code references, sources/cursors,
prior paths and history. Explicit offline resumes stay offline without new input
fixtures. Finish releases ownership at either wait/block; an unchanged wait or
missing-role block for a still-absent role consumes no new semantic step.

## Design artifacts and architectural decisions

Design uses existing `artifact_paths` and ordinary owner-gated `save`; no schema,
setting or helper command is added. Each attempt lives under
`<runtime>/work/<item-id>/design-<unique-attempt-id>/design.md`, with a unique
`design-<attempt-id>` map key. Preserve earlier bytes and entries, write the final
report last and verify readability/inputs before saving the complete copied item.
Keep stable save operation ID and decision JSON beside the attempt; an artifact
without a saved transition is not completed work. Reconcile uncertain saves from
history before retrying and retain partial attempts as evidence.

The report records a design-needed/skipped judgment and reason, input/source
versions and paths, observed component/revision context, chosen approach,
compatibility, sequencing and verification where needed. Even a concise skip
provides enough product intent, checks, repository guidance and evidence links
for a fresh implementer. A consequential unresolved architecture/API choice saves
`design` / `waiting_for_human` / `factory-design`, a stable question identifier,
options/tradeoffs and a concrete next action. Direct natural-language answers use
the same item/question association and observed provenance rules as planning;
record the exact answer and resulting decision in a new artifact, retaining the
question and earlier evidence. Source quotes are not human answers. An unchanged
wait consumes no semantic step. New unresolved product choices return to the
planner with their concrete evidence/question.

Completed or justified-skipped design saves `implement` / `blocked` /
`factory-implement`, honestly naming the absent role and self-contained handoff.
Reuse that saved design on fresh resume; the still-missing implementer requires
zero additional semantic steps. Design changes no fix count or approval/action
ledger. Architectural choices grant no implementation or external permission.
Explicit offline resumes remain offline; finish releases ownership at each wait
or block.
