---
name: factory-report
description: Report saved results in the harness and draft applicable Slack/Jira updates. Reuse unchanged drafts, preserve engineering state, and send externally only with exact authorization and uncertain-send reconciliation. No automatic Jira transitions, merge, deployment or schedules.
---

# Factory report

For config 2/work schema 4, selected item means this run's explicitly claimed
item. Require that claim before role execution and use expected-item-version
for save/reconcile. Other runs may work on other items concurrently. Keep all
permissions, artifacts and external actions scoped to this item. Read new receipt
associations after a version conflict; never overwrite newer related evidence.

Report on the selected saved item through `factory-run`. A direct report-only
request enters that orchestrator with any user-supplied config/local override;
it resolves the remembered default once. An existing invocation passes its pinned
absolute config/local unchanged, without resolving again. Read the
[reporting contract](references/reporting.md) for destination, deduplication and
send/retry rules. An explicit report-only request prepares/reuses reporting
artifacts without advancing intake or engineering. Workers return artifacts and
recommendations; only the verified invocation orchestrator saves canonical state.
No separate factory invocation or reporting stage is needed.

Read the saved sources, investigation/implementation/review/follow-up evidence,
current engineering wait/next action and prior reporting/action history. In live
mode refresh relevant Jira/PR status and attribute limits; in explicit offline
mode use only declared raw snapshots. Never invent upstream model work, a source
thread, deployment, verification or an external read. A reporting gap does not
erase the actual engineering stage/status/role/next action or shared fix count.

For direct chat intake, return the result and next action in the current harness
and retain the local report. No Slack/Jira destination is required; its absence
is not a reporting blocker or a reason to ask for one. Draft external updates only
for an actual linked destination or an explicit user request. Replying in the
current harness is not an external post and needs no send-approval ledger entry.

For applicable external updates, default to LOCAL DRAFTS for the actual originating
Slack thread and resolved Jira issue comments. Include the useful result, evidence/PR link when available,
and any decision needed; omit worker identities, debate, prompts and internal
process chatter. A blocked investigation needs the concrete missing input; a
ready PR is ready for review, not shipped; merge alone proves neither deployment
nor verification. For a blocked investigation, state the blocker, the unperformed
check and the needed input. Do not add PR/merge/deployment absence claims from
empty records: use “deployment status is unknown” when that is all the evidence
establishes. Before saving, read the actual outgoing text and remove unsupported
existence, absence or success claims. Missing/ambiguous destination stays an unaddressed local draft
with its precise gap. No new channel root, invented permalink or issue transition.

Reuse the same saved draft/request for unchanged meaningful status and destination.
Ignore query timestamps and wording drift when detecting repeats. Save exact
immutable payload bytes and semantic observation identity before asking approval;
no unchanged duplicate artifact/action or repeated semantic save. Separate each
destination's disposition, so one successful update does not claim another sent.

Only applicable direct user permission for the exact draft/destination permits
sending. Recheck actual host access, current truth and scope; save proposed then
uncertain BEFORE calling the write. Confirm only actual returned/refetched ID,
permalink, exact destination/content and attributable request evidence. Same text
alone, another author/thread or incomplete history is not proof. Unresolved
uncertainty blocks resend; authoritative non-application requires its own durable
evidence before retry. The local ledger does not guarantee exactly-once delivery.
No external action is authorized merely by drafting or by invoking this skill.
