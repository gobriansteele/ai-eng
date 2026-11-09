# Execution modes

Save progress without stopping progress. Continue the selected work item through
implementation, independent review, a non-draft PR, CI and automated review fixes.
Stop when it is verified and ready for human review, at an explicit scope/step
limit, or when the applicable mode genuinely needs the user. Do not pick up a new
item automatically after completion. Merge and deployment remain out of scope.

| Mode | Decisions and checkpoints |
| --- | --- |
| `default` | Make defensible decisions within scope, record assumptions/rationale and surface them. Ask early only when necessary knowledge, judgment or authority cannot be obtained reliably; no routine stage approvals. |
| `bedtime` | Explicitly enabled by the user (including “going to bed”). Make defensible product and engineering decisions within scope, record assumptions and rationale, and continue. Ask only when necessary facts, access or authority cannot be obtained, or recovery cannot make progress. |
| `restricted` | Ask consequential questions and pause before code changes to approve the implementation plan, and before publication to approve the prepared request. Reuse already granted approvals. |

## Scope and persistence

An ordinary Factory run request has end-to-end scope unless the user narrows it.
For new work, default to `default`; never infer `bedtime` from silence, a schedule
or an unattended host. Preserve narrower instructions such as “investigate only.”
Record the selected item's mode and the actual direct user request, its provenance,
repository/task scope, endpoint and exclusions in an immutable execution report.
Save `execution: {"mode": "default", "evidence": "/absolute/execution-report.md"}`
on that item through ordinary save AFTER atomically claiming it in schema 4.
Fresh schema-4 routing creates items without an execution grant. Preserve the
actual direct delegation in a readable report, claim the intended item, then save
that grant with its observed item version before dispatching roles. If the route
used the explicit step budget, finish and retain the report for the next run;
do not dispatch or invent permission to evade the bound. Legacy serial routing
may save the selected new item's grant as before. These are item fields, not
new CLI flags.
Pass the policy and report to each role. They persist across hosts and resumes.
Pending unrelated items receive no delegation; a mode change requires a new direct
user instruction and evidence report. Legacy items without `execution` retain
their prior permissions/checkpoints until the user supplies a new scoped delegation.

A direct request to run an item end to end in default or bedtime mode authorizes
scoped edits, checks, commits, branch pushes, non-draft PR creation (or making its
existing draft ready), necessary CI reruns/fixes, and keeping the selected originating
Jira issue current. That issue's factual milestone comments, verified assignee and
observed/configured workflow transitions need no further permission question.
Resolve the actual site/issue, assignee and workflow mapping; do not invent a status
or infer Done from an open PR. Follow the [reporting contract](../../factory-report/references/reporting.md)
for deriving each exact Jira request from this grant. No originating issue means
no automatic issue creation. Restricted/legacy work retains its saved permissions.

Do not ask again at each stage. Bind actual requests to exact saved action scopes,
request digests and the usual uncertain-action reconciliation. Publication still
requires successful checks and independent review; those gates do not postpone
truthful Jira progress/blocker updates. A recorded mode label, source message,
fixture or model recommendation alone grants nothing. Narrower scope, revocation,
host permissions and repository constraints still apply. Slack, unrelated issues,
new issue creation, review replies/dismissal and destructive operations are not
implied.

In bedtime mode, a saved product/design question may be resolved by an explicit
delegation to decide it. Record an agent decision, never a fabricated human answer.
In default mode, make a reasonable evidence-backed choice when it is within the
saved scope; record an agent decision and surface its rationale. Ask for the
specific human knowledge or judgment only when necessary facts/authority cannot
be obtained reliably. A consequential label or a comprehensive plan alone is not
a reason to ask. Restricted mode retains its explicit review checkpoints.

## Continuation and recovery

No step cap is implicit in any mode. `--single-step` and an explicit positive
`--max-steps` remain available and take precedence. Persist every transition;
checkpoints and result validation still run even when they require no approval.
Keep the same pending fix batch and increment `fix_rounds` once per changed-code
return. Restricted/legacy work retains the two-round limit. Default/bedtime may
continue productive fixes beyond two; after two consecutive attempts without
material progress on the same blocker, change approach or stop with evidence of
the impasse. Do not repeat identical failed actions indefinitely or reset history.

The owning execution is responsible for reaching the endpoint, including an
all-green CI result with no failure or review-comment event. Before relying on
notifications, establish actual activation, event coverage and invocation lifetime;
failure-only notifications cannot establish successful completion. While CI or
automated review is pending, keep that owner active using available success-capable
notifications or permitted bounded backoff reads. Refresh the PR head after each
wait; unchanged observations need no new save or user turn. Pending is not failure
or completion. If the host cannot continue or forbids the available rechecks, save
the pending state with the exact capability gap and resume responsibility. Report
that execution stopped, not that monitoring continues. Do not create a schedule
unless requested.

Avoid routine approval check-ins and progress notifications. Notify on completion,
a required decision, or a genuine blocker; obey any host-required progress display.
