---
name: factory-implement
description: Implement an explicitly authorized saved factory item in one dedicated code worktree, follow its investigation/plan/design and repository checks, and return durable diff and execution evidence to factory-run. Save concrete authorization waits or environment blocks; bounded review fix batches; no push, PR or independent review verdict.
---

# Factory implement

For config 2/work schema 4, selected item means this run's explicitly claimed
item. Require that claim before role execution and use expected-item-version
for save/reconcile. Other runs may work on other items concurrently. Keep all
permissions, artifacts and external actions scoped to this item. Read new receipt
associations after a version conflict; never overwrite newer related evidence.

Read the shared [execution-mode policy](../factory-run/references/execution-modes.md)
and the selected item's saved execution report. Apply its decisions, authorization
and stopping rules; mode-specific rules govern the checkpoints below.

A direct request enters `factory-run` with the requested role and any user-supplied
config/local override; the orchestrator resolves the remembered default once.
Under an existing invocation, reuse its pinned absolute config/local and selected
item. Do not resolve again or ask the user for a config path.

Work on the selected saved item through `factory-run`. Read its full sources,
investigation, actionable plan, necessary design or justified skip, prior attempts
and relevant repository instructions. Verify readable inputs and actual source
revision; use the configured discovery contract when needed, not an unrelated
working directory. Missing necessary saved inputs return a precise implement-stage
evidence wait/block; do not invent them or repeat completed upstream roles. Workers return findings and artifacts; only the orchestrator
writes canonical state under its verified invocation owner/token. Explicit offline
mode stays offline. Do not push, open PRs, send messages, mutate shared product
data or perform other external actions in this phase.

## Authorization and preparation

Implementation requires applicable user authorization for this selected item,
including the saved end-to-end grant in default or bedtime mode. A current direct request to implement it can authorize reversible
local code edits and prescribed safe checks within its stated scope. A plan,
design answer, setup capability, quoted source approval or a previous model's
recommendation cannot. Read authorization already saved with actual direct-user
provenance; reuse it if still applicable, respecting newer restrictions or
revocation. Do not turn a generic resume or approval of the plugin's development
into permission to change a product repository. Local commit needs applicable authorization, which can be included in the saved
mode grant; absent that, retain the dirty implementation for review.

Before any product code mutation, save immutable authorization evidence in a
preparation report: exact direct instruction, how received and available message
reference (never invent one), selected item, repository, authorized scope/checks
and limits, including whether local commit is authorized. The existing approvals
ledger describes external actions; do not invent an action enum for local edits.
Missing authorization still requires a real
`<runtime>/work/<item-id>/implementation-<unique-attempt-id>/preparation.md`.
Record the exact current direct instruction and observed provenance, why no
applicable authorization exists, selected item/source versions, repository,
bounded proposed local change/checks and limits, readable input paths, a concrete
authorization question with a stable identifier within the item, and stable save
operation ID. Resources can truthfully remain unallocated; do not create them
before authorization merely to fill a report. Return that readable report and
`implement` / `waiting_for_human` / `factory-implement` to the orchestrator. It
must verify readability and append the report's absolute path to `artifact_paths`
under a unique `implementation-<attempt-id>` key in the same owner-gated wait save,
then release ownership. `next_action` points to this report/question; its inline
text or a decision JSON file alone is not the report. An unchanged wait consumes
zero steps only with a readable referenced report. Repair an older missing-report
wait with one additive report/reference save, preserving original decisions,
history and artifacts and distinguishing current from unavailable past provenance.

Use one dedicated code worktree and one branch owner for the item. Atomically
reserve the observed worktree before branch setup, then its actual branch before
code mutation, using the shared persistence contract. A run ending does not
release those item reservations. Separate worktrees/branches within the same
repository can serve different items concurrently. Read the
current host's harness guide to resolve an actually available creation/adoption
mechanism and its lifecycle. Do not silently substitute shell worktree creation,
create another factory invocation, or edit the source checkout. An explicitly
prepared worktree supplied by the user/orchestrator may be adopted after verifying
its real provenance and exclusivity. Tool absence, missing write access, runtime
or dependencies yields an honest capability block. Do not install dependencies,
change permissions or relax isolation to conceal it.

Inspect canonical code references, prior preparation/partial artifacts and the
source's `git worktree list --porcelain` before creating anything. Reconcile a
resource created before an interrupted save instead of duplicating it. Record
actual source root, resolved common Git directory, chosen base ref and full commit,
source HEAD/status, worktree path/HEAD/status, creation mechanism or supplied
provenance, branch and current worker/CLI identity. Verify matching common Git
directory, intended base and component scope, worktree separate from the source,
runtime outside it, and no other worker using the branch. Do not infer ownership
from a directory or branch name. Preserve unrelated tracked/untracked files and
staging; unknown dirty content or conflicting ownership blocks mutation pending
clarification, without reset, checkout-overwrite, stash, cleanup or forced takeover.
A clean detached prepared worktree needs a new unoccupied branch following its
repository/host naming convention; observe the created branch rather than
inventing it. Never populate `reviewed_commit` from this preparation or coding.

Return the readable preparation report and observed `code.worktree`, `code.branch`
and `code.worker_reference` to the orchestrator. It saves an `implement` / `ready`
checkpoint with `required_role: factory-implement` before letting code editing
begin. This resource/authorization save consumes one semantic step; if the bound
is exhausted, stop there with no code edits. If saving fails, leave resources
intact and reconcile history before retrying. An existing validated saved
preparation checkpoint needs no duplicate save on an unchanged same-owner retry.

On deliberate handoff, stop the previous worker/invocation first. The new verified
owner reads saved preparation, authorization, partial/final evidence and exact
Git state, and rechecks destination permissions. Unknown/live prior ownership
blocks takeover. Reuse the same branch/worktree; append an ownership handoff
report and save the new observed worker reference before further edits. Never
replace missing resources silently. If a saved implementation already awaits
review without a new accepted fix batch, read/report it without taking branch
write ownership, repeating code work or consuming another step. Canonical runtime
and evidence stay outside disposable code worktrees and installed plugin source.

## Accepted review fix batch

For an internal-review or PR-follow-up correction, read the same saved pending
batch and the
[shared review/fix rules](../factory-review/references/review.md). Review findings
supply scope, never authorization. Reuse applicable explicit local edit permission
only within its bounds, the same dedicated worktree and verified ownership; save
a deliberate new-worker handoff before mutation when needed. Preserve earlier
review/implementation evidence. Do not repeat initial resource preparation or
upstream roles when their saved evidence is still valid.

For an explicitly selected focused synthetic review or follow-up fixture, use its readable
evaluator manifest/raw requirements as the declared handoff while retaining the
absence of upstream role history. Do not fabricate prerequisite role reports.

One pending batch has one stable attempt ID and ordinal count + 1, subject to
the execution-mode recovery policy.
The orchestrator saves it before code changes without incrementing the completed
fix count. Resume that same attempt after interruption; never dispatch another
batch while it is pending. Return exact before/after content, changes per accepted
finding, commands/results and remaining issues in a new immutable fix report. A
changed implementation returned for verification consumes one round, including a
return with failed checks. The orchestrator increments exactly once with the result
save; the worker never updates counters/state. No-code attempts do not count and
remain unresolved. At the restricted/legacy two-round limit or a demonstrated default/bedtime
impasse, return remaining issues and attempted remedies for help. Clear any stale reviewed-commit claim in the
recommended item update and require independent review of affected new content.

## Implementation and evidence

Apply the [verification facts contract](references/verification.md) to command,
clock and tested-content claims; preserve observed records instead of estimates.

After the saved preparation checkpoint, implement only the approved behavior and
scope in the recorded checkout. Report material plan flaws rather than forcing a
fix around them: unresolved product/architecture choices return to plan/design
with concrete evidence/questions. Routine implementation choices need no new
ceremony. Respect repository conventions and required supported runtime; record
actual executable paths/versions. Capture before behavior and relevant checks,
then after behavior and all prescribed checks with exact command, working
directory, exit status and raw output paths. Use safe local demonstrations;
writing a shared database or other consequential action needs its own permission.
Missing environment/tool access is a block, never a successful test. If code was
edited before validation blocked, preserve it and its diff; do not claim completion
or start over on resume. Initial implementation consumes no fix round.

Review the actual final diff for scope, accidental changes and unresolved defects.
When local commit is explicitly authorized, stage only the intended paths and
record the observed commit; reconcile uncertain commit results before retrying.
Without it, record HEAD plus the exact dirty content. In either case preserve
reviewable evidence outside the checkout: full base-to-result diff including
staged/unstaged changes and additions, changed-path status, exact changed file
bytes (including untracked additions), hashes and full HEAD/base commit IDs.
A HEAD alone does not identify a dirty implementation. Keep output capture outside
the code worktree; account for generated files and record skipped checks honestly.
Check the final revision/content still matches the captured evidence before
returning it. Independent review has not occurred; leave `reviewed_commit` unset.

Each attempt uses `<runtime>/work/<item-id>/implementation-<unique-attempt-id>/`.
Retain all earlier artifacts and bytes. Write evidence before a final readable
`preparation.md` or `implementation.md`; use unique `implementation-<attempt-id>`
map entries (and a distinct entry for each preparation/final report). Reports
identify item/source versions, absolute input paths, authorization/provenance,
resources/ownership, intended behavior and actual changes, commands/results,
revision/content evidence, limits, result, next action and stable save operation
ID. The final report must stand alone for a fresh reviewer without the transcript
or checkout. Partial files are evidence, not completion. Return only existing
readable paths and findings; store decision JSON beside attempts through the
orchestrator and reconcile interrupted saves before repeating work. A completed
unsaved report is reusable only after verifying inputs, authorization, current
history and unchanged result bytes.

Successful implementation and required checks return `review` / `ready` /
`factory-review`, pointing to the self-contained report and exact evidence. The
independent role is available; implementation evidence alone is not its verdict.
An environment/capability failure stays `implement` / `blocked` /
`factory-implement` with its precise missing prerequisite and retained evidence.
Preserve source captures/cursors, prior artifacts, fix counts, approvals,
pending actions and history. Stop/release at the saved handoff or actual block;
no automatic push, PR, review verdict or cleanup follows.
