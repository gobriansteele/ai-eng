# Saved work and concurrent invocation contract

Use the selected item's [execution mode](execution-modes.md). This contract is
for config schema 2 and work schema 4. Config schema 1 retains its serial behavior;
read [legacy persistence](legacy-persistence.md) only to inspect/resume an old
factory before explicit upgrade. Do not apply schema-4 commands to legacy state.

## Configuration and upgrade

Resolve the factory once through the [configuration contract](../../factory-setup/references/configuration.md),
then pin its absolute config/local paths. Invoke helpers with
`uv run --isolated --frozen --no-dev --project <loaded-plugin> python
<loaded-plugin>/scripts/factory_work.py <command> --config <config> --harness
codex|claude-code [--local <override>]`. Do not borrow another environment.

New factories use config schema 2 (`limits: {fix_rounds: 2}`) and begin creates
work schema 4. For an existing factory, inspect first. An explicitly requested
upgrade uses `upgrade --owner-pid <verified-cli-pid>` with pinned config/local and
harness. It preserves original config and snapshot backups under
`runtime/state/upgrades/<digest>/`, retains legacy state under the schema-4
snapshot's `legacy` field, then replaces the configuration. Old plugin versions
reject the new schemas. Stop legacy owners first; alive/unknown ownership blocks
upgrade. A failure between the state and config replacements is recoverable by
retrying the same upgrade, not restoring/resetting state. Existing paths, channel
starts, cursors, item IDs, artifacts, history and scopes remain intact. Recheck
setup capabilities in each host because the effective config hash changes.
Do not upgrade a real factory as part of an unrelated plugin development test.

## Runs and item claims

`owners` returns verified CLI ancestor identities. Use the exact nearest actual
long-lived Codex/Claude CLI PID; helper/shell PIDs and the desktop app-server are
not owners. Unknown liveness is not death. `inspect` is read-only and returns
`snapshot`, `active_items` and `inventory_version`.

Generate a UUID once and retain it. `begin --owner-pid <pid> --run-id <uuid>` starts
an independent unbound run, never a factory-wide exclusive writer. Optional
`--request <capture>` saves direct intake; `--source <capture>` is synthetic-only;
`--fixture <fixture>` seeds a new explicitly synthetic item. Choose one input.
Exact begin retries preserve the original run and never restart a finished UUID.
No input is needed to resume existing work. Null step caps remain the default;
`--single-step` or positive `--max-steps` explicitly bounds semantic steps.

Before dispatching any item role, claim its execution atomically:

```text
claim --owner-pid <pid> --run-id <uuid> --operation-id <stable-id> --item-id <item-id> --expected-item-version <observed-version>
```

Each unfinished run binds at most one item, and each item has at most one
unfinished run. The binding is immutable within a run. A claim loser must not
start workers. Another run may work on another item concurrently in either host.
Carry item ID, run ID, owner, config/local and scope through every CLI/role packet.
Resume by explicit item ID or unambiguous trusted request/question provenance.
With several candidates, clarify rather than selecting a factory-wide default.
For an explicitly requested queue run, choose an eligible unowned item, claim it,
and reselect after a claim race. Item status is not ownership.

`finish --owner-pid <pid> --run-id <uuid> --outcome <reason>` ends only that run,
releasing its execution and intake claims. Reasons remain single_step,
step_limit, blocked, waiting_for_human, no_available_work, stopped, completed.
An intake-only run can finish without an item. Resource reservations persist.
A crash leaves claims intact. A new run can use `recover --target-run <old-run>
--operation-id <stable-id>` only after the helper verifies the old process is
stopped/replaced; live or unknown owners block recovery. Reconcile any surviving
workers before adopting code write access. Never take over based on elapsed time.

## Item saves and exact retries

`save --owner-pid <pid> --run-id <uuid> --expected-item-version <version>
--decision <json>` accepts the existing `{id, reason, item}` complete copied item
shape. Only the claimed item may change. `reconcile` uses the same item-version
flag and existing reconciliation JSON shape. Helpers load the latest snapshot
inside a short mutex, verify the item version/owner and preserve unrelated items.
Another item's save does not invalidate this item's version. A stale same-item
save refuses and needs rereading. A busy mutex is a retryable transaction conflict.

Retain stable operation IDs and exact payloads, including the original expected
item version, across uncertain replies. Exact committed retries do not consume
another step. Reusing an ID with different content/domain refuses. A later run
may reconcile an exact prior operation only for the same claimed item after the
old run finishes. Begin, claims, resource reservations and collection consume no
semantic steps; route, save and reconcile do. Save/reconcile preserve source
identity, prior approvals/actions, fix history and item-specific execution grants.
New/changed execution grants require readable immutable evidence as before.

The global revision orders events; it is not the precondition for independent
item saves. `--summary` returns a bounded receipt with the current run, active
item/run mapping, item versions and routing inventory version. Do not substitute
global revision for item version. All invocations retain actual plugin version,
package fingerprint, non-secret effective config and hash; config/package changes
block further work by an existing run. Saved evidence never grants host access.

## Shared intake

Before authenticated channel reads acquire `intake-claim --key <key>
--operation-id <id>`, using `channel:` plus compact JSON `[workspace,channel]`.
`watch-plan` returns the exact key and current claim owner. Re-read watch-plan
AFTER acquiring the claim, then fix read boundaries. Skip/report busy channels
while continuing independent direct work. Collect retains its existing observation
JSON; `collect --decision <json>` verifies channel ownership and cursor/start
preconditions, not the global revision. Release it with `release-intake --key
<key> --operation-id <id>` after the read/commit. Finish also releases intake claims.

Before semantic routing acquire the key `receipt:<receipt-key>` where receipt-key
is compact JSON `[source_id,version]`. Capture replay still deduplicates; altered
content under the same source version refuses. Route with this JSON:

```json
{"id":"stable-operation-id","reason":"Evidence","receipt_id":"saved-key","routing":{},"items":[],"inventory_version":"observed-inspect-value"}
```

Use the usual routing findings in `routing`; `items` contains only complete NEW
item records with zero fix rounds and empty code/artifacts/ledgers, without an
execution grant. Existing findings use existing_item_id and commit only the
receipt association, never another item's lifecycle replacement. Read the full
current inventory before choosing associations. Changed routing inventory refuses
commit and requires reconsideration. Release the receipt claim after commit.
Claim a newly routed item before saving its scoped execution grant or running roles.

Related captures increment the associated item's version without changing its
lifecycle. Its owner must reread the associated source receipts before its next
save/reconcile and reassess affected decisions. Discover associations through
`sources[*].item_ids`; item.source_links is not a complete source index. Never
silently inherit another item's permission, erase execution progress, or assert
new source evidence was considered before it arrived. Newly associated evidence
for a finished item is retained for explicit subsequent handling.

## Worktree and branch reservations

Different items may use the same repository in distinct linked worktrees and
branches. Before branch setup reserve the actual detached worktree; before code
mutation reserve its actual branch too. `reserve --decision <json>` takes
`{id, resources:[{item_id,worktree,git_dir,common_dir,branch}]}`. Paths are observed
canonical absolute paths; branch is the full `refs/heads/...` ref or null for a
detached checkout. Verify with Git rev-parse/show-toplevel, absolute git-dir/common-dir
and symbolic-ref; the helper independently observes them under the transaction.
Source checkout mutation is refused. All resources must belong to configured
repositories. A multi-repository reservation is all-or-none.

The same worktree/Git worktree directory or common-directory-plus-branch cannot
belong to two items. Item reservations survive run completion and human waits;
resume adopts the SAME resources after prior-writer and current-byte validation.
Reservations are retained; there is no automatic release/reuse or deletion API.
Unknown/missing resources require repair/restoration, not replacement. Reconcile
uncertain native allocation before retrying. Keep native host creation rules.
Shared ports, test databases, caches and Git refs still require appropriate
isolation or narrow coordination; worktrees alone do not establish that isolation.
Claims coordinate this factory, not unrelated processes/factories.

## Storage and compatibility

The authority remains `runtime/state/work.json`. Schema 4 contains items and
item_versions, source receipts, collection bookkeeping, concurrent invocations,
intake claims, resource reservations and interleaved events. Active item ownership
is derived from unfinished invocations' item_id; there is no global active item.
The immutable `legacy` snapshot retains original schemas 1/2/3 and their old
invocations/events/config hashes. New history replays from that legacy inventory;
validation rejects materialized state inconsistent with replay. Read legacy
history when reconciling old decisions; do not invent historical run-item bindings.

A short file mutex protects the entire read/validate/modify/write transaction.
A temporary file is fsynced and atomically replaces the snapshot; then its
directory is fsynced. Lost replies may mean a commit succeeded: inspect and retry
exactly. Direct writes bypass these protections and are forbidden. No compaction,
database migration or remote exactly-once guarantee is introduced.

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

Implementation needs selected-item local authorization, including an applicable
saved default/bedtime end-to-end grant. Save
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
ordinal beyond the selected mode’s recovery allowance. Reconcile pending evidence/history first on every resume. Increment
exactly once with the owner-gated changed-code return-for-verification save, even
when required checks fail; preserve the same attempt through interruptions. Initial
implementation/review and no-code attempts consume none. Internal and PR
fixes share this count. Corrected successful checks return review/ready; failed
checks remain implement/blocked. At the selected mode’s recovery limit or a demonstrated impasse, save a concrete
block with issues and attempted remedies. Product decisions follow the mode policy. Partial code
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

`reconcile --decision <absolute-json> --expected-item-version <item-version>` uses normal
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
