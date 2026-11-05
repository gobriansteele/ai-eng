---
name: factory-run
description: Run or resume the local software factory from an explicit configuration, saving one step or a bounded invocation across Codex and Claude Code. Collects live Slack intake, routes saved sources and resumes handoffs; investigates scoped code, plans behavior and resumes product questions; stops truthfully at unavailable later roles.
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
and artifact reference. When actionable, save `design` / `blocked` /
`factory-design` and point to the plan; design is absent. Do not implement code
or treat a planning answer as external-action approval. Store decision JSON and
operation ID beside the attempt; reconcile interrupted saves as above. Missing
or partial artifacts do not establish completion. An unchanged human wait or
missing-design block requires no new semantic decision. Finish/release ownership
at the actual wait/block.

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
bound; completed investigation can proceed to planning, which stops at the
absent designer when actionable. Respect genuine waits, no-action and invocation
bounds. An old investigator or planner missing-role block alone must not stop a
now-available role. Explicit offline/synthetic resume stays
offline; never invoke live watch merely because no new fixture is supplied. Call `finish` with the observed stop reason;
on an error, preserve
the saved transition and attempt a truthful `stopped` finish if ownership remains
valid. Never mark completed work for an unsaved decision. Report the routed
source/dispositions, affected item IDs (or zero work), selected
item stage/status/next action, snapshot path, revision, step count/bound and blockers.
The invocation ends when this CLI worker stops; another fresh harness can resume.
