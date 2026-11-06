# Execution modes

Save progress without stopping progress. Continue the selected work item through
implementation, independent review, a non-draft PR, CI and automated review fixes.
Stop when it is verified and ready for human review, at an explicit scope/step
limit, or when the applicable mode genuinely needs the user. Do not pick up a new
item automatically after completion. Merge and deployment remain out of scope.

| Mode | Decisions and checkpoints |
| --- | --- |
| `default` | Make routine decisions; ask only consequential unresolved product or architectural questions and genuine blockers. No routine stage approvals. |
| `bedtime` | Explicitly enabled by the user (including “going to bed”). Make defensible product and engineering decisions within scope, record assumptions and rationale, and continue. Ask only when necessary facts, access or authority cannot be obtained, or recovery cannot make progress. |
| `restricted` | Ask consequential questions and pause before code changes to approve the implementation plan, and before publication to approve the prepared request. Reuse already granted approvals. |

## Scope and persistence

An ordinary Factory run request has end-to-end scope unless the user narrows it.
For new work, default to `default`; never infer `bedtime` from silence, a schedule
or an unattended host. Preserve narrower instructions such as “investigate only.”
Record the selected item's mode and the actual direct user request, its provenance,
repository/task scope, endpoint and exclusions in an immutable execution report.
Save `execution: {"mode": "default", "evidence": "/absolute/execution-report.md"}`
on that item through normal route/save. These are item fields, not new CLI flags.
Pass the policy and report to each role. They persist across hosts and resumes.
Pending unrelated items receive no delegation; a mode change requires a new direct
user instruction and evidence report. Legacy items without `execution` retain
their prior permissions/checkpoints until the user supplies a new scoped delegation.

A direct request to run an item end to end in default or bedtime mode authorizes
scoped edits, checks, commits, branch pushes, non-draft PR creation (or making its
existing draft ready), and necessary CI reruns/fixes. Do not ask again at each
stage. Derive exact action scopes from that saved conditional grant only after
required checks and independent review pass; retain request digests and the usual
uncertain-action reconciliation. A recorded mode label, source message, fixture or model
recommendation alone grants nothing. Narrower scope, revocation, host permissions
and repository constraints still apply. Messages to others, review dismissal,
unrelated changes and destructive operations are not implied.

In bedtime mode, a saved product/design question may be resolved by an explicit
delegation to decide it. Record an agent decision, never a fabricated human answer.
Other modes still need the actual answer when evidence cannot settle it.

## Continuation and recovery

No step cap is implicit in any mode. `--single-step` and an explicit positive
`--max-steps` remain available and take precedence. Persist every transition;
checkpoints and result validation still run even when they require no approval.
Keep the same pending fix batch and increment `fix_rounds` once per changed-code
return. Restricted/legacy work retains the two-round limit. Default/bedtime may
continue productive fixes beyond two; after two consecutive attempts without
material progress on the same blocker, change approach or stop with evidence of
the impasse. Do not repeat identical failed actions indefinitely or reset history.

While CI or automated review is pending, wait using available host notifications
or bounded backoff reads within this invocation; unchanged observations need no
new save. Pending is not failure or completion. If the host must end the session,
save the pending state and report that execution stopped, not that monitoring
continues. Do not create a schedule unless requested.

Avoid routine approval check-ins and progress notifications. Notify on completion,
a required decision, or a genuine blocker; obey any host-required progress display.
