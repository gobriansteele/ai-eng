---
name: factory-run
description: Run or resume factory work using the remembered default or an explicit config. Orchestrates saved intake, engineering roles, PR follow-up and reporting under the selected execution mode while preserving evidence and authorization boundaries.
---

# Factory run

Read the shared [agent-selection policy](references/agent-selection.md) before
dispatching work. Read [execution modes](references/execution-modes.md) before
choosing scope, authorization or a stopping point. Save the selected item’s mode
and scoped delegation, and pass them to every role. Apply agent selection to every
assignment, including foreground coordinators,
direct role requests, retries and resumes. Pass it to workers that delegate further.

Read the [unanswered-decision contract](references/pending-decisions.md) when a
role needs human input. Preserve each unresolved question through unrelated replies,
handoffs and completion checks; a disclosed limitation is not a resolved decision.

Act as the orchestrator: read durable evidence, choose the next step, and save
that decision. For startup files, use already exposed and permitted native file
reading/discovery tools when available. A denied command has its observed scope:
a denied listing/read does not establish that all execution or the prescribed
helper is unavailable. Inspect the actual permission result/allowlist and attempt
the prescribed literal helper command if that distinct operation is already
permitted before declaring its capability unavailable. Do not bypass a denial of
the underlying access/action or broaden permissions; command-pattern permissions
do not revoke separately granted file reads/discovery or helper commands. Report
the precise blocked operation when required access still fails. Under a command prefix
allowlist, issue each already permitted command separately with literal
paths and values. Obtain the run UUID in a separate permitted Python call, then
paste its observed value into the literal helper command. Do not wrap helpers in
shell assignments, substitutions or command chains. Rejection of such a compound
command is not a denial of the required literal helper; report that helper denied
only after its actual permitted-form call fails.

Read the loaded plugin's [persistence contract](references/persistence.md)
before running the helper. Resolve the package two directories above this skill's
containing directory; use its scripts and fixtures, not an authoring checkout.

Resolve the default once using the [configuration contract](../factory-setup/references/configuration.md#default-resolution-and-pinning),
passing an explicit config or local override only when supplied. If this call
already carries pinned config/local context from a top-level entry point, reuse
it without another resolution. Keep the returned absolute config/local paths
fixed for every helper, role and foreground worker in this invocation; never ask
for the config again or consult a changed default mid-run. Resolution errors
stop with actionable setup/repair instructions. Default to no step cap and continue this run's claimed item to its authorized endpoint.
Honor `--single-step` (one saved decision) or an explicit positive `--max-steps`;
a null saved `max_steps` means unlimited. These options do not change YAML. For explicitly requested native
scheduling, read the [runbook](references/scheduling.md); pin the resolved
config/local in the scheduled prompt, with no account schedule activation implied.
A resolved config with no synthetic input is the production entry point: save any
direct request, watch configured Slack channels, then route/resume saved work.
For a new request typed in the harness, read [direct intake](references/direct-intake.md)
and use `begin --request`; this is not an offline flag. Pass its exact capture path
through any foreground CLI handoff. `--source`, `--fixture`, `--collection` or an explicit offline/synthetic
request selects an offline demonstration; never call live integrations in that mode.

First inspect saved state and discover the actual harness CLI owner.
A run begins unbound; capture/collect/route as needed, then atomically claim the
intended item before any item role or action. Saved direct continuation provenance
or an explicit item ID identifies the candidate. Do not assume a global selection.
Read the item version and all associated source receipts after claim acquisition.
For newly routed schema-4 work, save the scoped execution report/grant AFTER claim
and BEFORE item roles, using the observed item version. Route never grants a mode.
Respect a step budget exhausted by routing; resume the saved item/report later. A durable
run token owns the entire invocation, including time between helper calls. Use
the observed nearest long-lived CLI ancestor's PID, never the helper, transient shell,
`$PPID` guess, desktop app-server, or invented PID. If the desktop has no CLI
owner, dispatch one foreground fresh CLI invocation in the same harness with the
pinned absolute config/local context, this skill, and any explicitly requested mode and bound, then
wait for its result;
see the harness guide. The CLI worker owns and performs the entire run; do not add a step cap in the handoff. If this
capability or required process inspection is unavailable, report the blocker.
When the sandbox denies process inspection or a specific authorized helper
mutation, retry only that command through the host's normal approval mechanism;
never broaden permissions or disable the sandbox automatically.

For config schema 1 use the legacy persistence contract and retain serial behavior
until the user explicitly requests upgrade. For schema 4, use item-scoped claims,
item versions and intake/resource reservations from the persistence contract.
Generate a run UUID once and retain it for retries; call `begin`, including
`--request <absolute-capture>` for new direct intake. Existing state
resumes without input. For saved-source demonstrations, use the explicitly selected
synthetic JSON as `--source`; it is saved under the invocation owner before routing.
A supplied new source must be considered even when another saved item is blocked.
For legacy post-intake demonstrations `--fixture` remains supported. A new
production workspace needs no synthetic seed. Unless explicitly report-only as
described below, after begin and before handling an active block, invoke shared
`factory-watch` under this same owner/token. In live
mode it checks current host access, collects every ready configured channel and
reports coverage/blockers; `--import-thread` is an explicit historical import.
No configured channels is a successful no-op. Slack capability gaps do not block
independent direct intake or saved work; report the uncovered channels. In
offline mode skip live watch; an explicit `--collection <synthetic-json>` passes
that normalized observation through collect. Collection can proceed while saved
work is blocked and does not consume semantic steps. Retain other channels'
successful captures when one is blocked. Do not run a repository workflow or
invent intake evidence. Helper failure blocks work; corruption needs repair preserving the original files. A
live or unknown prior owner blocks takeover regardless of age.

For an explicit report-only request (including direct factory-report use), read
[factory-report](../factory-report/SKILL.md) and its reference after begin, skip
watch/collection/routing/code progression, and report on the selected saved item.
Pass actual source/evidence, engineering state, prior report manifests/ledgers,
config/runtime, owner and offline/live mode. No selected item means no work to
report, not a new synthetic item. This is natural-language invocation scope, not
a new helper flag. Do not reinterpret it as permission to send. Finish/release
after reporting; subsequent engineering-role instructions do not apply to this
report-only invocation.

If the selected item is already `follow_pr / done` and no new work or changed
result is requested, reuse its saved completion report and finish without rerunning
review or polling. Do not claim saved observations are fresh remote reads.

Read canonical `items`, this run's item binding, source receipts, relevant history,
bounds, scoped approvals and pending actions. Selection belongs to each run. Inspect active_items and claim an eligible item
under the persistence contract before dispatching any engineering role. Other
unfinished runs may own different items concurrently; never interfere with them. Existing receipt routing is durable:
exact replay reuses it without another decision or item. Consider unrouted saved
receipts first, including a newly supplied source when an active item is blocked.
Acquire the source receipt claim BEFORE invoking factory-route. Invoke that role
on the full available saved
thread, observations and relevant inventory. The role returns semantic findings;
you remain the orchestrator and own state updates. Use its routing contract to
wrap the result with complete NEW item records
and the current inventory_version and persist with `route --decision <absolute-json>`.
For an existing item, save only the receipt association; reread it under that
item's claim before making lifecycle decisions. Release the receipt claim afterwards. Use descriptive
stable finding keys. For live sources, factory-route can gather current read-only
Jira/ownership/code
observations and return auditable observations committed with the routing; missing
access remains an explicit incomplete check. Synthetic sources use only saved
evidence and never live reads. New items start at zero fix rounds with empty
approval and
pending-action lists; include only observed code/artifact references and invent
no worker or worktree ownership. Related sources/later capture versions attach to an existing
item only with evidence; preserve all saved scopes/actions/counters and links.

Choose each new item's next stage/status/action from the actual findings.
Only a claimed item's owner may advance an existing item. New related evidence
changes its item version, requiring that owner to reread before its next save.
For both `investigate` and `verify_existing_work`, the handoff role is exactly
`factory-investigate`. Bug, regression, feature and verification use different
briefs within that one role. Do not invent separate feature-brief or verifier
skill names. The shared investigator is available: save `stage: investigate`, `status: ready`
and `required_role: factory-investigate` with the concrete brief/next action.
An older missing-role block for this role is resumable now; role availability is
not evidence that the underlying investigation completed.
An underway result waits for existing work with a concrete check; clarification
waits for a human with a concrete question. No-action creates no work item. You
may save the route and its truthful ready/wait outcome in one decision; do not
claim investigation ran before it does. Select and atomically claim at most one item per run. Carry its ID through every
worker/CLI and save; no factory-wide selected item exists. An ambiguous resume
or human answer requires association, not arbitrary item selection. Report
the new source's findings even if its items were not selected. Do not discard
unrouted sources or pending work when stopping at the selected item's block.

When an investigation item is selected and a semantic step remains, invoke shared
`factory-investigate` with the saved item, source captures/routing brief, explicit
config/local override, runtime path, prior artifact paths and current offline/live
mode. Workers return artifacts/findings only; all save calls retain this invocation's
verified owner/token. The investigator may read scoped code and reproduce safely
in an authorized isolated checkout, but must not implement a product change.

Read the returned final report and its evidence files before accepting the
handoff. Check that required executions used the repository's declared runtime/tool
prerequisites, with exact executable paths and versions in the evidence. Unsupported
environment observations do not complete required supported-runtime validation:
use an existing compatible environment when available and authorized, or retain a
concrete validation block/limit. Missing, unreadable or partial output is not
completed investigation.
Preserve prior evidence on retry: use distinct attempt directories under
`<runtime>/work/<item-id>/`, and merge new absolute report paths into the existing
`artifact_paths` map under unique `investigation-<attempt-id>` keys. Evidence paths
inside each report are absolute. Keep observed revision/environment in the report;
do not invent a worktree/worker claim or populate `reviewed_commit` from an
investigation revision. Retain source links/captures, counters, scopes, actions,
code references and collection cursors unchanged unless an evidenced addition is
needed. Investigation does not consume a fix round.

For completed bug/feature/verification findings, save `stage: plan`,
`status: ready`, `required_role: factory-plan` and a concrete next action pointing
to the findings and any unresolved product choices. The shared planner is available;
do not ask the investigator to choose product policy. For unavailable reproduction
or a necessary missing input, save the report but retain `stage: investigate`
with `waiting_for_human` and the precise unblock question, or `blocked` and the
actual capability blocker; keep `required_role: factory-investigate`. Failed
reproduction is honest evidence, not a mandatory retry loop. A useful bounded
investigation with remaining uncertainty may hand off to planning when the
report explains that limit; never claim the symptom was reproduced if it was not.

Write the complete save decision JSON beside its attempt artifacts with a stable
operation ID; read/reconcile current history before retrying an uncertain save.
After interruption, inspect prior evidence and saved decisions first. If artifacts
exist but the transition was not saved, validate them and reconcile/save the
handoff under the current revision/owner; only reuse identical operation content
for an exact retry. If a newer state changes the decision, reconsider it rather
than overwriting it. If the completed investigation transition is already saved,
reuse its artifacts for planning within the remaining bound; do not investigate
again. Artifact existence alone is not a state transition.
Only report completion after the artifact is readable and the save succeeded.

When the selected item is at plan and a semantic step remains, invoke shared
`factory-plan` with the full preserved item, source captures, investigation and
prior plan artifact paths, config/runtime and offline/live mode. An old
`factory-plan` missing-role block is resumable now. An actual
`waiting_for_human` stays waiting without a relevant direct answer, evidence, or
explicit bedtime delegation covering the pending decision;
role availability alone does not resolve it. Read its saved question before
interpreting the current user prompt. Pass a direct response verbatim to the
planner with observed provenance and its association to the selected item/question.
Natural-language skill input carries the answer; do not invent a helper CLI flag.
If association or meaning is unclear, retain the wait and ask for the missing
choice. No new source fixture is required for an explicit offline resume.

Read the returned plan and verify its saved inputs and any answer provenance.
Append readable absolute report paths under unique `plan-<attempt-id>` keys,
retaining earlier artifact paths/bytes and source captures/cursors, code refs,
fix counts, approvals/actions and event history. The planner returns findings;
you save the complete item using ordinary owner-gated `save`. Keep a product
question at `plan` / `waiting_for_human` / `factory-plan` with a concrete question
and artifact reference. When actionable, save `design` / `ready` /
`factory-design` and point to the plan; the shared designer is available. Do not
implement code or treat a planning answer as external-action approval. Store decision JSON and
operation ID beside the attempt; reconcile interrupted saves as above. Missing
or partial artifacts do not establish completion. An unchanged human wait
requires no new semantic decision. Finish/release ownership at the actual
wait/block.

When the selected item is at design and a semantic step remains, invoke shared
`factory-design` with the preserved item, sources, investigation, actionable plan
and prior design paths, config/runtime, offline/live mode and relevant repository
context. An old missing-designer block is resumable now; availability does not
resolve a real architectural human wait. Read the saved question before passing
any direct answer verbatim with its observed provenance and item/question
association, just as for planning. An unchanged wait without a relevant answer, evidence or applicable bedtime
delegation consumes zero steps. Never treat quoted source approval as a direct
human answer. No new helper flag is needed.

Read the returned design/skip handoff, validate its inputs, rationale, technical
scope, verification and any answer provenance. A meaningful cross-system design
must add technical decisions beyond repeating the product plan; a small clear bug
can record a concise skip reason with an actionable handoff. Append readable
absolute report paths under unique `design-<attempt-id>` keys and preserve all
prior artifact bytes/paths, sources/cursors, code refs, fix counts, approvals,
actions and history. Save the complete item through the same verified owner and
ordinary `save`, with decision JSON and stable operation ID beside the attempt;
reconcile interrupted saves as above. Workers never write canonical state.
Missing or partial artifacts do not complete design. Retain an unresolved
architectural choice at `design` / `waiting_for_human` / `factory-design` with
its concrete question/artifact; a newly discovered unresolved product choice
returns to `plan` / `waiting_for_human` / `factory-plan`. Evidence/capability
blocks name the actual missing input at the step that needs it.

A completed or justified-skipped design saves `implement` / `ready` /
`factory-implement`, naming its self-contained handoff. The shared implementer is
available. A design answer alone grants no implementation or external permission; reuse
applicable end-to-end authorization from the execution report.
Reuse completed design and resume old missing-implementer blocks; do not repeat
investigation/planning/design merely because implementation is now available.

At implement, first read the loaded [implementation contract](../factory-implement/SKILL.md)
before deciding any outcome, including an authorization wait or capability block.
Do not bypass that contract because code work is not yet authorized. When a
semantic step remains, invoke shared `factory-implement` with the full preserved
sources, investigation, actionable plan, needed design/skip, repository
instructions, prior attempts and code refs, config/runtime and offline/live mode.
Pass applicable current direct user scope verbatim with observed provenance/item
association; also supply this invocation's observed owner/worker identity. Verify
saved authorization context rather than assuming earlier product/architecture
answers authorize code work.

When the execution report or other direct permission does not authorize local
implementation, the wait requires an actual readable
`<runtime>/work/<item-id>/implementation-<unique-attempt-id>/preparation.md`
before saving `implement` / `waiting_for_human` / `factory-implement`. Verify
that report records exact current direct instruction/provenance and absence of
applicable authorization, item/repository, bounded proposed change/checks, limits,
a concrete question with a stable identifier within the item, readable input
references and stable save operation ID. Append its absolute path under a unique
`implementation-<attempt-id>` artifact key in that same owner-gated save, preserving
all earlier entries/bytes; point `next_action` to the report/question. Inline
`next_action` text or `decision.json` alone does not satisfy this report contract.
Only an unchanged wait with its readable referenced report consumes zero steps.
An older wait lacking that report/reference needs one additive evidence-repair
save, preserving its original decision/history; never fabricate missing earlier
provenance. A current authorization can resolve the wait; a source quote cannot.

For authorized resource preparation, read the returned report and verify
authorization, actual Git/common directory/base/path/branch and ownership evidence,
plus host mechanism/lifecycle.
Before branch setup/mutation, atomically reserve observed worktree/branch resources
for this item using the persistence contract. Separate worktrees/branches in the
same repository may be used by other items. Reservations survive run completion;
never adopt another item's resources. Before code edits, save the complete item at `implement` / `ready` /
`factory-implement`, append its readable absolute report under a unique
`implementation-<attempt-id>` key and set only observed code worktree/branch/worker
references. A resource checkpoint consumes one step, so stop without editing if
no step remains. Then pass the successful saved checkpoint to the implementer
for code work within the remaining bound. No worker writes canonical state. If
resources exist after an interrupted preparation/save, reconcile saved history,
reports and actual Git state before retrying; do not create duplicate branches
or worktrees. A valid saved same-owner preparation is reused without a duplicate
step. After a deliberate verified-owner handoff, save the observed new worker
reference and handoff report before further edits; do not take over a live or
unknown worker. A completed review-stage handoff needs no branch write takeover.

Read the implementation report, raw command results and exact revision/content
artifacts before accepting completion. Check scope, prescribed verification and
that the actual checkout matches the captured result; missing/failed required
checks retain `implement` / `blocked` / `factory-implement` with a concrete unblock,
even when code is present. Product/architecture problems return to their actual
plan/design wait with evidence. Append unique preparation/final report paths,
retaining earlier bytes and all source/cursor/history/counter/action/approval
context. Save using ordinary owner-gated `save`, keeping stable operation ID and
decision JSON beside each attempt and reconciling uncertain saves. Local edit or
applicable local-commit authorization (including scoped mode delegation) lives in immutable report context;
the external-action ledger is unchanged. Initial implementation consumes no fix
round. Leave `reviewed_commit` unset: code has not been independently reviewed.

Successful implementation/checks save `review` / `ready` / `factory-review`,
pointing to the self-contained report, actual branch/worktree and exact diff/HEAD
plus dirty-content evidence or authorized commit. Independent review is available;
reuse the saved implementation and resume older missing-reviewer blocks when a
step remains. Do not repeat code work or claim a verdict from checks alone.

At review, read the loaded [review contract](../factory-review/SKILL.md) and its
linked reference before deciding any outcome, including capability blocks. Invoke
`factory-review` with the full preserved item, sources/requirements, plan/design,
repository instructions, implementation/preparation/authorization, exact result
and command evidence, prior review/fix attempts, config/runtime and mode. The
orchestrator retains the only invocation owner/token. Dispatch two actual fresh
independent reviewers, a separate fresh adjudicator, and only for unresolved
disputes three fresh independent panelists. Host guidance maps available native
workers; missing dispatch is review/blocked, never simulated role completion.
Keep reviewer findings isolated until both return. Validate readable raw worker
reports, identity/focus, exact reviewed fingerprint and evidence before accepting
adjudication. Recheck actual code content after review. Changed bytes invalidate
affected verdicts even with unchanged HEAD; preserve the old evidence and review
the new result instead of accepting stale approval.

Append immutable review artifacts under unique `review-<attempt-id>` keys, with
stable decision JSON/operation IDs beside them; reconcile partial/uncertain saves
before reuse. Accepted findings become one pending fix batch with exact target,
IDs, scope, checks and proposed ordinal. Save implement/ready/factory-implement
with that readable batch before edits, retaining the current fix count until
changed code returns for verification. Authorization/ownership still follow the
implementation contract. Do not create another batch while one is pending.
On changed-code return, verify its before/after evidence and complete that same
batch with exactly one increment in the same owner-gated result save. Failed
required checks count too and close that batch at implement/blocked. When the execution mode permits another attempt, save a new batch from the concrete remaining accepted
findings/check failures before another edit; a completed batch cannot authorize
further changes. Interrupted partial edits
resume the same pending batch; unchanged/no-code attempts consume no round and
cannot pass. Initial implementation/review consume zero. Internal review and PR follow-up share the same counter and mode-specific
recovery policy; never reset it. Re-review
corrected code with fresh independent workers under the review contract.

Follow the execution-mode recovery rule: restricted/legacy work stops after two
rounds; default/bedtime continues while making material progress and changes
approach or stops at a demonstrated impasse. Save remaining issues and attempted
remedies at the actual blocked role. A product/design dispute follows that mode's
decision policy; unavailable dispatch/evidence remains a genuine blocker.

A pass needs the complete disposition audit and exact current fingerprint in a
readable final report. Only a clean exact reviewed commit can populate
`code.reviewed_commit`; for dirty accepted code keep it unset and use full
base/HEAD, diff and file/hash evidence. Save follow_pr/ready/factory-follow-pr
with the report and exact-content handoff.
Follow-up is available; an old missing-role block resumes without repeating review
or code ownership transfer. A pass grants no publication authorization.

At follow_pr, read the loaded [follow-up contract](../factory-follow-pr/SKILL.md)
and reference before deciding any outcome, including an authorization wait. Invoke
that shared role with all saved review/implementation/content, authorization,
code refs, pending actions/batches and counter history, config/runtime, actual
owner and mode. Verify its immutable reports and current exact checkout/remote
identities. Reuse observed existing PRs; save code.pr_url plus evidence without
claiming a factory creation action. For a new authorized push/non-draft PR request, append
its exact scoped approval/proposed action via ordinary save, then use the narrow
owner-gated reconcile command to checkpoint uncertain BEFORE execution and confirm
only observed results. Reserve the required steps before starting; a partial or
ambiguous remote read never authorizes retry. Workers return reports; the
orchestrator owns these checkpoints and remote execution coordination. Follow the
contract for authoritative non-application, stable IDs, unchanged request retries
and unknown remote waits. Do not replace pending entries through ordinary save.

Read current-head CI/status/log/review/comment coverage, disposition findings with
evidence, and save a single accepted pending fix batch before implementer dispatch
with the completed count unchanged. Use the existing shared count/close/re-review
rules above, including failed checks counting once and mode-specific recovery.
Re-review corrected content before any scoped authorized fix push; verify its
new remote SHA, not old CI. Append unique follow-pr report paths, preserving old
artifacts/bytes, history, sources/cursors, approval scopes and counts. Save actual
follow_pr blocked/ready/waiting_for_human outcomes with concrete next action;
unchanged observed waits need no repeated step. Continue observing pending CI and automated review within this invocation,
using bounded waits/backoff and preserving unchanged observations without duplicate
saves. Resolve actionable findings through the fix/review/push loop. Only save
`follow_pr / done` with no required role when the PR is non-draft, required checks
pass on the current head and applicable automated review findings are resolved.
Unknown coverage prevents completion. Then report once and finish `completed`;
never merge, deploy or automatically select another item.

When the selected work completes or reaches a genuine block/required human
question, invoke available factory-report for local drafts if a semantic step
remains. Also honor explicit report requests without forcing another engineering
step. Compare stable meaningful observation/destination identity with saved report
manifests first: unchanged status with an existing corresponding report returns
the same payload/request/artifact with zero duplicate save/action. A meaningful
saved outcome without a corresponding report remains eligible for its first draft,
even if engineering was unchanged this invocation because a prior bound deferred
reporting. Read its reporting contract before accepting any
draft or send recommendation. Append only readable unique reporting artifacts
and justified approval/action additions; preserve actual engineering stage/status,
required_role, next_action, code refs, fix_rounds and all unrelated state. A missing
reporting target/refresh/permission stays in the reporting report and invocation
summary, not a replacement engineering wait/role. If the bound is exhausted,
reporting can wait for the next invocation; never exceed it to draft.

Default reporting is local-only, even during a live engineering run. Future sending
needs actual exact-draft/destination authorization, current facts/host access and
the shared uncertainty checkpoints; invoking a run or approving code does not
permit messages. At a report-only outcome, save new reporting evidence within the
bound and finish/release truthfully without advancing engineering. Do not create
a report stage, poll destinations or invent workflow transitions.

A focused report evaluation may explicitly import synthetic:report-evaluation:
via begin --fixture with readable raw status/destination observations and declared
engineering stage/wait/count as scenario metadata. Label absent upstream model
roles, preserve that state, and run only reporting. This grants no completed
investigation/review/deployment, production evidence bypass or real send permission.
Explicit offline resumes remain offline and reuse saved reporting identity.

A focused follow-up evaluation may import synthetic:follow-pr-evaluation: through
begin --fixture with a readable raw snapshot/actual-checkout manifest. It labels
synthetic PR/CI/comments and absent upstream model-role history explicitly. Honor
this declared existing-PR observation scope, not an invented passed review; new
publication still needs genuine exact review. Explicit synthetic/offline mode
stays offline on all resumes. This exception neither grants edit/external
permission nor weakens the legacy missing-source behavior below.

A focused review evaluation may explicitly import a synthetic stage fixture with
`begin --fixture`: its `synthetic:review-evaluation:` source identity, readable
`artifact_paths` input manifest and direct request must clearly identify controlled
raw requirements, checkout/content and observed checks, not completed model roles
or review verdicts. Honor that review-stage entry and its saved offline resumes;
keep imported provenance/absent upstream history visible. This exception grants
no production source bypass or edit permission. Never infer a focused-stage request
from a legacy fixture or manufacture upstream decisions.

Legacy Phase 3 fixtures contain no original message body or duplicate/ownership
observations. Router availability does not create that evidence. Preserve the
item and save an honest route-stage `waiting_for_human` requesting the missing
saved source, without claiming a routing judgment. An unchanged existing wait
or block needs no repeated decision. Never infer a legacy fixture's body from
its source URL, classification or illustrative pending action.

Save a decision with a stable operation ID (reuse the exact ID/content after an
uncertain response), reason, and complete updated item, using the read revision.
After a revision conflict reread and reconsider; never overwrite newer state.
Persist after each completed step. Keep stage separate from status: a human wait
must retain the step needing help. Only this orchestrator writes current state;
workers return artifacts/findings. Tool permission and current user
approval are independent of saved configuration and synthetic approval examples.
An uncertain external action must be reconciled from fresh observations in the
selected mode before retry; actual external actions require the loaded follow-up
contract and applicable authorization.

Stop only at completion, an applicable mode checkpoint or genuine decision/block,
or an explicitly requested step limit. Reassess saved waits under the selected
mode instead of treating every unresolved decision as a mandatory human stop.
Otherwise reread saved state and continue the selected item. A completed route can proceed to investigation within that
bound; completed investigation can proceed to planning and actionable planning to
design, then authorized implementation within the remaining bound. Completed
implementation can proceed to independent review and bounded fixes, then
authorized non-draft PR follow-up when prerequisites hold. Respect genuine waits,
no-action and invocation bounds.
An old investigator, planner, designer, implementer, reviewer or follow-up
missing-role block
alone must not stop a now-available role. Explicit offline/synthetic resume stays
offline; never invoke live watch merely because no new fixture is supplied. Call `finish` with the observed stop reason;
on an error, preserve
the saved transition and attempt a truthful `stopped` finish if ownership remains
valid. Never mark completed work for an unsaved decision. Report the routed
source/dispositions, affected item IDs (or zero work), selected
item stage/status/next action, snapshot path, revision, step count/bound and blockers.
The invocation ends when this CLI worker stops; another fresh harness can resume.


For native recurring invocations, completion/failure or a needed human action merits notification; unchanged checks stay quiet through the
host's separate native notification policy. Do not generate duplicate drafts or
extra work merely to report a tick. Direct factory-retro/factory-maintain requests
are read-only operational activities with their own contracts, not engineering
stage transitions or permission for cleanup/schedule activation.
