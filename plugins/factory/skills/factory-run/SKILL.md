---
name: factory-run
description: Run or resume the local software factory from an explicit configuration, saving one step or a bounded invocation across Codex and Claude Code. Supports saved synthetic source routing and post-intake handoffs; stops truthfully at unavailable investigation roles.
---

# Factory run

Act as the orchestrator: read durable evidence, choose the next step, and save
that decision. Read the loaded plugin's [persistence contract](references/persistence.md)
before running the helper. Resolve the package two directories above this skill's
containing directory; use its scripts and fixtures, not an authoring checkout.

Use the explicitly supplied or established `--config` and optional user-supplied
`--local`. Default to at most three saved steps per invocation. Honor a requested
single step (`--single-step`, one saved decision), or an explicit `--max-steps`
from 1 through 10. These invocation options do not change YAML. A schedule will
later invoke this skill with configuration. Saved synthetic inputs exercise the
current implementation; live intake is a later phase.

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
For legacy post-intake demonstrations `--fixture` remains supported. Do not read
live Slack/Jira, run a repository workflow, or invent intake evidence. Helper
failure blocks work; corruption needs repair preserving the original files. A
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
stable finding keys. New items start at zero fix rounds with empty approval and
pending-action lists; include only observed code/artifact references and invent
no worker or worktree ownership. Related sources/later capture versions attach to an existing
item only with evidence; preserve all saved scopes/actions/counters and links.

Choose each affected item's next stage/status/action from the actual findings.
For both `investigate` and `verify_existing_work`, the handoff role is exactly
`factory-investigate`. Bug, regression, feature and verification use different
briefs within that one role. Do not invent separate feature-brief or verifier
skill names. The investigator is not implemented yet, so save a missing-role
block with `required_role: factory-investigate`.
An underway result waits for existing work with a concrete check; clarification
waits for a human with a concrete question. No-action creates no work item. You
may save the route and truthful missing-role/wait outcome in one decision; do not
claim investigation ran. Select at most one item for active execution. Retain an
existing active item when suitable while saving additional pending items; report
the new source's findings even if its items were not selected. Do not discard
unrouted sources or pending work when stopping at the selected item's block.

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
remaining bound. A completed route stops at the actual missing investigator,
wait, no-action or invocation bound. Call `finish` with the observed stop reason;
on an error, preserve
the saved transition and attempt a truthful `stopped` finish if ownership remains
valid. Never mark completed work for an unsaved decision. Report the routed
source/dispositions, affected item IDs (or zero work), selected
item stage/status/next action, snapshot path, revision, step count/bound and blockers.
The invocation ends when this CLI worker stops; another fresh harness can resume.
