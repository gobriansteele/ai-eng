---
name: factory-run
description: Run or resume the local software factory from an explicit configuration, saving one step or a bounded invocation across Codex and Claude Code. Collects live Slack intake, routes saved sources and resumes handoffs; investigates scoped code, plans behavior, designs technical handoffs, implements authorized local changes, independently reviews exact content, adjudicates findings and applies at most two shared fix rounds; stops truthfully at unavailable later roles.
---

# Factory run

Act as the orchestrator: read durable evidence, choose the next step, and save
that decision. Read the loaded plugin's [persistence contract](references/persistence.md)
before running the helper. Resolve the package two directories above this skill's
containing directory; use its scripts and fixtures, not an authoring checkout.

Use the explicitly supplied or established `--config` and optional user-supplied
`--local`. Default to at most three saved steps per invocation. Honor a requested
single step (`--single-step`, one saved decision), or an explicit `--max-steps`
from 1 through 10. These invocation options do not change YAML. A schedule may later invoke this
skill with configuration. An explicit config
with no synthetic input is the production entry point: watch, then route/resume
saved work. `--source`, `--fixture`, `--collection` or an explicit offline/synthetic
request selects an offline demonstration; never call live integrations in that mode.

First inspect saved state and discover the actual harness CLI owner. A durable
run token owns the entire invocation, including time between helper calls. Use
the observed nearest long-lived CLI ancestor's PID, never the helper, transient shell,
`$PPID` guess, desktop app-server, or invented PID. If the desktop has no CLI
owner, dispatch one foreground fresh CLI invocation in the same harness with the
explicit config, this skill, and the requested bound, then wait for its result;
see the harness guide. The CLI worker owns and performs the entire run. If this
capability or required process inspection is unavailable, report the blocker.
When the sandbox denies process inspection or a specific authorized helper
mutation, retry only that command through the host's normal approval mechanism;
never broaden permissions or disable the sandbox automatically.

Generate a run UUID once and retain it for retries; call `begin`. Existing state
resumes without input. For saved-source demonstrations, use the explicitly selected
synthetic JSON as `--source`; it is saved under the invocation owner before routing.
A supplied new source must be considered even when another saved item is blocked.
For legacy post-intake demonstrations `--fixture` remains supported. A new
production workspace needs no synthetic seed. After begin and before handling an
active block, invoke shared `factory-watch` under this same owner/token. In live
mode it checks current host access, collects every ready configured channel and
reports coverage/blockers; `--import-thread` is an explicit historical import. In
offline mode skip live watch; an explicit `--collection <synthetic-json>` passes
that normalized observation through collect. Collection can proceed while saved
work is blocked and does not consume semantic steps. Retain other channels'
successful captures when one is blocked. Do not run a repository workflow or
invent intake evidence. Helper failure blocks work; corruption needs repair preserving the original files. A
live or unknown prior owner blocks takeover regardless of age.

Read canonical `items`, `active_item_id`, source receipts, relevant history,
bounds, scoped approvals and pending actions. There is only one selected active
item; all other saved items are pending. Existing receipt routing is durable:
exact replay reuses it without another decision or item. Consider unrouted saved
receipts first, including a newly supplied source when an active item is blocked.
Invoke the available shared `factory-route` role on the full available saved
thread, observations and relevant inventory. The role returns semantic findings;
you remain the orchestrator and own state updates. Use its routing contract to
wrap the result with complete explicit affected item records, then persist with
`route --decision <absolute-json> --expected-revision <revision>`. Use descriptive
stable finding keys. For live sources, factory-route can gather current read-only
Jira/ownership/code
observations and return auditable observations committed with the routing; missing
access remains an explicit incomplete check. Synthetic sources use only saved
evidence and never live reads. New items start at zero fix rounds with empty
approval and
pending-action lists; include only observed code/artifact references and invent
no worker or worktree ownership. Related sources/later capture versions attach to an existing
item only with evidence; preserve all saved scopes/actions/counters and links.

Choose each affected item's next stage/status/action from the actual findings.
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
claim investigation ran before it does. Select at most one item for active execution. Retain an
existing active item when suitable while saving additional pending items; report
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
`waiting_for_human` stays waiting without a relevant direct answer or evidence;
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
association, just as for planning. An unchanged wait without a relevant answer
or evidence consumes zero steps. Never treat quoted source approval as a direct
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
available. A human design answer grants no implementation or external permission.
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

Missing local implementation authorization requires an actual readable
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
Before code edits, save the complete item at `implement` / `ready` /
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
separately explicit local-commit authorization lives in immutable report context;
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
required checks count too and close that batch at implement/blocked. On a later
authorized resume below two, save a new batch from the concrete remaining accepted
findings/check failures before another edit; a completed batch cannot authorize
further changes. Interrupted partial edits
resume the same pending batch; unchanged/no-code attempts consume no round and
cannot pass. Initial implementation/review consume zero. Internal review and
future PR follow-up share the same two total rounds; never reset it. Re-review
corrected code with fresh independent workers under the review contract.

After two unsuccessful rounds, save a readable escalation report and the actual
review/implement waiting_for_human with remaining supported issues, both attempts,
current exact content and a concrete question for Brian. Imported exhausted
scenario metadata must be labeled; never invent missing prior attempts. Do not
start a third fix or create a PR. A disputed human question retains review /
waiting_for_human / factory-review; a dispatch/evidence gap retains review /
blocked / factory-review. Unchanged real waits consume zero steps and role
availability alone does not resolve them.

A pass needs the complete disposition audit and exact current fingerprint in a
readable final report. Only a clean exact reviewed commit can populate
`code.reviewed_commit`; for dirty accepted code keep it unset and use full
base/HEAD, diff and file/hash evidence. Save follow_pr/blocked/factory-follow-pr
with the report and precise missing-role next action. Follow-up is unavailable:
finish/release with no push, PR or other external action. A fresh read-only resume
reuses this handoff without another review or code ownership transfer.

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
An uncertain external action must be reconciled from live returned IDs before a
retry; no external action is implemented here.

Stop on the first unavailable role, wait, block, completed single step, or step
limit. Otherwise reread saved state and choose another available step within the
remaining bound. A completed route can proceed to investigation within that
bound; completed investigation can proceed to planning and actionable planning to
design, then authorized implementation within the remaining bound. Completed
implementation can proceed to independent review and bounded fixes, then stops
at absent PR follow-up. Respect genuine waits, no-action and invocation bounds.
An old investigator, planner, designer, implementer or reviewer missing-role block
alone must not stop a now-available role. Explicit offline/synthetic resume stays
offline; never invoke live watch merely because no new fixture is supplied. Call `finish` with the observed stop reason;
on an error, preserve
the saved transition and attempt a truthful `stopped` finish if ownership remains
valid. Never mark completed work for an unsaved decision. Report the routed
source/dispositions, affected item IDs (or zero work), selected
item stage/status/next action, snapshot path, revision, step count/bound and blockers.
The invocation ends when this CLI worker stops; another fresh harness can resume.
