---
name: factory-run
description: Run or resume the local software factory from an explicit configuration, saving one step or a bounded invocation across Codex and Claude Code. Phase 3 supports synthetic post-intake fixtures and visibly blocks at unavailable work roles.
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
later invoke this skill with configuration; synthetic input is only a Phase 3
post-intake test fixture, not the future production interface.

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
resumes without a fixture. For a new Phase 3 demonstration only, use an explicitly
selected synthetic fixture. Do not read live Slack/Jira, create production work,
run a repository workflow, or invent an intake result. Helper failure blocks work;
corruption needs repair preserving the original files, never initialization over
existing state. A live or unknown prior owner blocks takeover regardless of age.

Read the current item, events, bounds, scoped approvals and pending actions.
Select the next action yourself from the evidence. A new unclassified item needs
`factory-route`; inspect available skills in the loaded package. If that role is
absent, save stage `route`, status `blocked`, required_role `factory-route`, and a
concrete next action explaining the missing role. Do not claim a worker ran, an
external status was checked, or a role completed. Preserve source identity,
links, fix counts, scoped approvals, pending actions and cursor metadata. Existing
blocked records need no repeated decision when nothing has changed.

Save a decision with a stable operation ID (reuse the exact ID/content after an
uncertain response), reason, and complete updated item, using the read revision.
After a revision conflict reread and reconsider; never overwrite newer state.
Persist after each completed step. Keep stage separate from status: a human wait
must retain the step needing help. Only this orchestrator writes current state;
future workers return artifacts/findings. Tool permission and current user
approval are independent of saved configuration and synthetic approval examples.
An uncertain external action must be reconciled from live returned IDs before a
retry; no external action is implemented here.

Stop on the first unavailable role, wait, block, completed single step, or step
limit. Otherwise reread saved state and choose another available step within the
remaining bound. In Phase 3 a missing router stops the normal invocation after
one decision. Call `finish` with the observed stop reason; on an error, preserve
the saved transition and attempt a truthful `stopped` finish if ownership remains
valid. Never mark completed work for an unsaved decision. Report item ID, stage,
status, next action, snapshot path, saved revision, step count/bound and blockers.
The invocation ends when this CLI worker stops; another fresh harness can resume.
