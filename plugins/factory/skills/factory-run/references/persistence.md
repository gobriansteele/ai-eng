# Saved work and invocation contract

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
Confirmed actions require observed returned ID and URL. Ordinary save preserves prior approvals/actions verbatim; the narrow
external-action reconciliation command below handles evidenced status transitions. The helper validates structure;
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

Completed or justified-skipped design saves `implement` / `ready` /
`factory-implement` with a self-contained handoff. Reuse saved designs and resume
old missing-implementer blocks now that this role is available. Design changes no
fix count or approval/action ledger. Architectural choices grant no implementation or external permission.
Explicit offline resumes remain offline; finish releases ownership at each wait
or block.

## Implementation authorization, resources and evidence

Implementation uses existing `artifact_paths`, observed `code` references and
ordinary owner-gated `save`. No schema, helper command or external action enum
is added. Attempts live under
`<runtime>/work/<item-id>/implementation-<unique-attempt-id>/`; append distinct
absolute report paths for preparation and final evidence under unique
`implementation-<attempt-id>` keys. Preserve all prior bytes. Final reports are
written after their evidence, with stable save operation IDs and decision JSON
beside attempts. Partial artifacts are not a completed canonical transition.

The trial needs explicit selected-item local implementation authorization. Save
its exact direct instruction, observed provenance, repository/item scope and
limits in immutable report context. Planning/design answers and source quotes
are not authorization. Reuse applicable saved direct-user evidence, respecting
newer restrictions. The existing approvals ledger supports external actions,
so it remains unchanged for local edits or separately explicitly authorized
local commit. Read the loaded `factory-implement` contract before deciding even
an implement-stage authorization wait or capability block. Without authorization,
write a real `implementation-<unique-attempt-id>/preparation.md` under this item's
runtime work directory. It records exact current direct instruction/provenance,
absence of applicable authorization, item/source/repository, bounded proposed
local change/checks and limits, readable inputs, concrete question with a stable
identifier within the item, and stable save operation ID. Resources may remain
unallocated. The orchestrator verifies that readable report, appends its absolute
path under a unique `implementation-<attempt-id>` artifact key, and saves
`implement` / `waiting_for_human` / `factory-implement` in the same owner-gated
transition; `next_action` points to its question/report. Inline next-action text
and decision JSON alone are insufficient. An identical unanswered wait consumes
zero steps only when its saved report/reference is readable; an older malformed
wait gets one additive evidence-repair save preserving original history/artifacts
and never inventing past provenance. Capability/environment blocks retain
implement/blocked and name the missing prerequisite; no successful-check claim
without execution.

Resolve worktree creation/adoption through the current harness guide. Before
code mutation, save an implement/ready preparation checkpoint with observed
`code.worktree`, `code.branch`, `code.worker_reference` and the report. It records
source root/common Git directory, exact base ref/commit, source and worktree
HEAD/status, actual creation/supplied provenance, authorization, worker identity
and exclusivity. Runtime/evidence remain outside the code worktree. This save
consumes a step; no code edit occurs if the invocation ends there. A valid saved
same-owner preparation needs no new save. If creation/save was interrupted,
reconcile artifacts, history and Git worktree/branch state before retrying;
never create a second resource just because a save response was lost.

A deliberate host/worker handoff first stops the prior invocation/worker, then
verifies current Git bytes, ownership and destination permissions. Save the
new observed worker reference plus an additive handoff report before further
code edits, reusing the same branch/worktree. Live/unknown ownership, conflicting
dirty work, unavailable worktree or unverifiable provenance blocks mutation;
never force takeover or silently replace resources. Merely explaining a completed
review-stage implementation does not need branch write takeover.

The final report carries readable source/investigation/plan/design paths,
authorization/preparation, intended and actual behavior, exact commands/cwd/exit
statuses/raw output paths, runtime/tool versions, full base and HEAD IDs, changed
path status, full diff including staged/unstaged and added content, exact changed
file copies/hashes, limits and next action. A dirty HEAD alone is not a revision
of implemented code. Validate actual result bytes against evidence before save;
keep that evidence outside disposable code checkouts for fresh review. Local
commit is optional and requires explicit authorization; never push/open a PR.

Successful code and prescribed checks save `review` / `ready` / `factory-review`
with the report and exact result evidence. Resume older missing-reviewer blocks
through the now-available role, reusing resources/evidence without repeating code
work.
`reviewed_commit` stays unset; initial implementation consumes no fix round.
Preserve sources/cursors, ledgers, counters and history. Required missing/failed
checks keep the item at implement/blocked, retaining any code and partial evidence.
Reconcile unsaved completed reports from current history and exact result bytes
rather than repeating implementation. Finish releases the canonical owner at the
actual wait/block; no cleanup or later external action is implied.


## Independent review and fixes

Read `factory-review` and its [review/fix contract](../../factory-review/references/review.md).
Review uses existing artifact paths, code refs, counters and ordinary owner-gated
save; no schema, command or role-owned state API is added. Only the invocation
orchestrator writes state. Save immutable raw worker reports, prompts, target
fingerprint, evidence, adjudication/dispositions and any panel responses under
unique review attempt paths. Directly changing canonical JSON to simulate a
verdict, review role, pending fix or exhausted counter is forbidden.

Two actual fresh independent reviewers precede a separate fresh adjudicator.
Three further independent fresh panelists consider only unresolved disputes.
Check host dispatch capabilities; no orchestrator persona simulation. No worker
starts another factory invocation. A reproducible serious defect cannot be dismissed
solely by votes. Missing raw reports/evidence are an incomplete review. Recheck
full base/HEAD plus diff/file hashes before accepting a verdict; a dirty HEAD is
not an exact result identity. Content changes invalidate affected verdicts. Dirty
accepted code keeps reviewed_commit unset; clean exact reviewed commits may set it.

Save one pending accepted batch before engineering changes with unchanged completed
fix_rounds and a stable proposed ordinal/attempt ID. No second pending batch or
ordinal over two. Reconcile pending evidence/history first on every resume. Increment
exactly once with the owner-gated changed-code return-for-verification save, even
when required checks fail; preserve the same attempt through interruptions. Initial
implementation/review and no-code attempts consume none. Internal and PR
fixes share this count. Corrected successful checks return review/ready; failed
checks remain implement/blocked. After two unsuccessful rounds, save a concrete
human escalation with issues/attempts instead of a third fix or PR. Partial code
and evidence remain preserved. A pass saves follow_pr/ready/factory-follow-pr;
that role is available and rechecks exact content before publication. Unchanged handoff/wait reuse consumes zero semantic steps.

For explicitly requested focused synthetic review evaluations only, existing
begin --fixture can import a review-stage item with synthetic:review-evaluation:
source identity and readable input manifest in artifact_paths. The manifest labels
controlled raw requirements, actual checkout/base/HEAD/diff/file hashes, observed
command outputs, direct evaluation scope and missing upstream role history. Neither
it nor the fixture can claim model-completed implementation/review or grant actual
permission. A reviewer-only exhausted scenario may import fix_rounds=2, clearly
labeled as scenario metadata with unavailable prior history, never invented fix
reports. Honor the imported stage and offline saved resumes rather than running
legacy source routing. Ordinary production sources and legacy Phase 3 fixtures
keep their existing contracts; this creates no generic missing-evidence bypass.


## External action reconciliation

Role-specific truth/authorization checks are in the
[PR contract](../../factory-follow-pr/references/follow-pr.md) and
[reporting contract](../../factory-report/references/reporting.md). `posts` includes
Slack thread replies and Jira comments; tickets policy is unchanged, and ticket
creation/workflow changes are outside these roles. No new config enum is added.
Ordinary save preserves every prior approval and pending-action entry verbatim.

For a genuinely authorized outbound request, ordinary owner-gated save appends a
stable approval and proposed action with exact matching action/target/revision
scope and immutable request/permission evidence. Save the readable payload and
actual direct-user authorization/provenance first. Scope identifies the exact
operation/destination, content and relevant revision/status. Exposed tools and
configuration are not permission. Do not reuse an action ID for changed scope or
replace unresolved uncertainty with a new action. Reserve at least two semantic
steps for uncertainty and confirmation AFTER proposal; otherwise stop before
execution. A later save may record additional observed references.

`reconcile --decision <absolute-json> --expected-revision <revision>` uses normal
verified owner/run/config/harness flags and exactly this shape:

```json
{"id":"stable-reconciliation-operation-id","reason":"Observed evidence and decision","item_id":"selected-stable-item-id","action":{"id":"existing-action-id","scope":{"action":"posts","target":"exact-destination-and-operation","revision":"exact-payload-and-status-digest"},"status":"uncertain","returned_id":null,"returned_url":null,"evidence":"/absolute/immutable-attempt-report.md"}}
```

Only one EXISTING selected-item pushes/pull_requests/posts entry changes. ID/scope
stay unchanged; a matching saved approval scope is required. Allowed transitions
are proposed→uncertain, uncertain→confirmed or uncertain→proposed. No
proposed→confirmed shortcut, confirmed mutation or arbitrary ledger editing.
Confirmed requires actual observed returned ID+URL; other transitions carry null
returned identity. New evidence must be an absolute readable immutable report;
historical replay checks structure without loading old files. The helper cannot
prove human permission, platform semantics, payload/author match or remote truth.

Persist uncertain BEFORE remote execution, then verify the successful checkpoint,
current applicable authorization and exact request before invoking the write once.
Confirmation needs the observed exact authorized postcondition and attributable
identity/destination/content under the role's contract, not merely a plausible
similar object. Record observations separately when they support reuse/duplicate
avoidance but cannot confirm all scope-bound fields. A crash/timeout/unknown result
stays uncertain. Inspect fresh relevant remote state with actual coverage before
retry. Only durable fresh authoritative NON-application evidence can restore
proposed; then recheck current scope/permission before another uncertainty checkpoint.
Ambiguity stays uncertain and asks for help, never blind replay or elapsed-time
reset. A ledger supports retries; it is not an exactly-once remote guarantee.

Reconciliation consumes one semantic step, uses owner/config/fingerprint checks,
CAS and atomic history, and preserves every unrelated item field, including
engineering stage/status/role/next action and fix count. Save/route/collect/reconcile
IDs share one namespace including legacy history. Exact same-domain/content retries
return committed state without another step, even after a lost response; changed
content/domain reuse fails. Reread/reconsider revision conflicts. Keep immutable
request/report bytes and prior ledger states in event history. Schema1 migration
and schema2/3 layouts remain unchanged; both hosts need the supporting helper.

## Reporting artifacts

Reporting is an additive activity, not an item-stage transition. Read factory-report
and its reference for stable observation/request identities, unchanged draft reuse,
exact message permission and destination reconciliation. Ordinary report saves
append absolute immutable report/manifests while preserving the engineering
stage/status/required_role/next_action, code refs, shared fix count and unrelated
history/ledgers. Drafts themselves create no external pending action. Explicit
report-only requests skip intake/engineering and unchanged requests consume zero
semantic steps. Focused synthetic:report-evaluation: fixture imports label raw
status/destination observations and absent prior model roles; they grant no real
permission or completed upstream work. Legacy missing-source and review/follow-up
imports retain their existing boundaries.
