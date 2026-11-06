---
name: factory-follow-pr
description: Publish an exact reviewed non-draft PR with scoped authorization, reuse an existing branch PR, and investigate fresh CI and review activity. Follow CI and automated review through the mode-specific recovery loop; no merge, deployment, comment posting or independent canonical writes.
---

# Factory follow PR

Read the shared [execution-mode policy](../factory-run/references/execution-modes.md)
and the selected item's saved execution report. Apply its decisions, authorization
and stopping rules; mode-specific rules govern the checkpoints below.

A direct request enters `factory-run` with the requested role and any user-supplied
config/local override; the orchestrator resolves the remembered default once.
Under an existing invocation, reuse its pinned absolute config/local and selected
item. Do not resolve again or ask the user for a config path.

Work through `factory-run` on the selected saved item. Read the
[follow-up contract](references/follow-pr.md) before deciding outcomes. Workers
return immutable evidence and recommendations; the verified invocation
orchestrator alone writes state. Read saved review/implementation/preparation,
actual code identity, approvals, pending actions and fix batches before acting.
Resume an old missing-follow-up block through this available role; role
availability alone does not resolve an authorization wait or evidence gap.

For new publication, verify the actual content is exactly what independent review
accepted, prepare the exact non-draft PR/push request, and verify applicable direct-user
authorization, including the saved end-to-end mode grant, and this host's actual permissions. Dirty reviewed code needs
applicable local-commit authorization and captured exact-content equivalence before
publication. A clean exact pass report may establish the reviewed HEAD even if
`reviewed_commit` was conservatively unset; never invent a past field value.
Changed code needs fresh affected review. Local edits, a pass, YAML settings or
exposed tools grant no push/PR permission. Keep a concrete authorization question
and complete reviewable request in a readable report before waiting.

Inspect fresh remote identity and branch PRs before creating or retrying. Reuse
an exact existing PR; recording its observed URL does not mean the factory
created it or needs retroactive creation approval. Reuse may be observed while
missing scope-bound payload evidence leaves an earlier action uncertain.
Save an authorized proposed
action, then reconcile it to uncertain BEFORE calling the remote write. Reserve
enough invocation steps for this checkpoint and confirmation; otherwise stop
before execution. An ambiguous result stays uncertain until fresh remote
observations reconcile it. Never blindly replay or force-push.

Read fresh PR head/base, checks/statuses and logs, reviews and comments with their
actual coverage, timestamps and revision identities. Investigate concrete failures
against the current code; distinguish actionable findings, unsupported allegations,
unrelated failures and observed flakiness with evidence. Old-head results cannot
verify the new head. Incomplete pages/access are limits, never an all-green claim.
Offline/synthetic runs read only the supplied raw snapshots and local authorized
evidence; synthetic IDs and approvals grant no real permissions.

Accepted findings go to `factory-implement` through the same saved pending batch
and authorization/ownership rules as internal review. Save the batch BEFORE
edits, retain the completed count, and reuse it after interruption. Changed code
returned for verification consumes one round, including failed checks; close
that batch atomically with the increment and apply mode-specific recovery. No-code attempts consume
none. New exact content receives independent review before a scoped authorized
push; recheck CI/review on the new remote SHA. At the restricted/legacy limit or a demonstrated impasse, return a concrete
block with attempted remedies; never reset the counter.

Write evidence before a self-contained final report under
`<runtime>/work/<item-id>/follow-pr-<unique-attempt-id>/`. Include input paths,
authorization/provenance, exact reviewed and observed remote identities, tool
calls/raw results/coverage, request content/digest, action IDs, finding dispositions,
fix accounting, limitations and next action. Append unique absolute artifact
paths, retaining earlier bytes/history, sources/cursors, scopes and counters.
A report or action return alone is not a saved transition; reconcile uncertain
helper saves with the same stable operation ID/content.

Continue until the non-draft PR's required checks pass and applicable automated
review findings are resolved on the current head. Pending checks/review require
bounded waits and fresh observations, not a ready claim or a routine handoff to
the user. Follow the contract's completion and host-interruption rules. Report
completion once; no Slack/Jira messages, review replies, merge, deployment or cleanup.
