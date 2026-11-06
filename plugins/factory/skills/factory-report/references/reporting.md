# Reporting contract

## Evidence and destination

Direct chat requests report back in the current harness with a saved local report.
No external destination is required. Missing Slack/Jira targets are gaps only when
an external update is actually requested or applicable to a linked destination;
do not manufacture unaddressed drafts or destination questions for chat-only work.

Read canonical item/history and readable evidence before drafting, including prior
report requests/actions and pending fix batches. Preserve engineering stage,
status, required_role, next_action, code refs, fix_rounds, sources/cursors and old
artifact bytes. Reporting disposition belongs in new reporting artifacts and the
existing external-action ledger, not a replacement engineering stage or status.

Refresh relevant live Jira issue/PR metadata and current-head check/review status
through actually available authorized reads. Retain raw results, time, identities,
coverage and limits. A saved result is historical evidence, not a fresh remote
observation. If refresh fails, a local draft can say what was recorded as of its
observation and what remains unknown; do not assert current readiness/deployment
from stale evidence. Explicit offline/synthetic mode never calls integrations.
A meaningful local report can remain useful when no current remote claim is made.

Resolve Slack workspace/channel/thread root from the item's saved source intake
provenance or an explicitly supplied verifiable target. Multiple originating
threads require explicit target disposition, not silent fanout. Confirm the actual
workspace/channel/thread and permitted destination before sending; a channel name
or source URL alone does not prove them. Use only the originating thread, never a
new channel root as fallback. Resolve Jira site/issue from actual saved issue links
and fresh identity when available; a project or issue key alone does not identify
the site. Draft a Jira comment for the selected related issue; do not fan out to
all mentioned keys. Missing/ambiguous targets yield labeled unaddressed drafts and
specific questions, without invented IDs/links or blocking unrelated engineering.
No local-only file path is a useful recipient evidence link: use a real source/PR
link if available or clearly say the evidence is local and name the useful result.

Use a few direct sentences: actual result, its evidence/link, and the needed
choice or next check. Distinguish investigation blocked, code implemented, review
passed, draft PR open, current-head CI passed, ready for human review, merged,
deployed and verified. Unknown deployment/verification stays unknown after merge.
Do not call a PR shipped or describe an unexecuted check as passed. Unknown is
not confirmed absence: missing PR/deployment evidence does not prove that none
exists. State the gap or omit the unsupported claim. If a saved draft contradicts
its evidence, retain it and create a corrected request with the factual reason;
that correction is meaningful, not stylistic duplication. Omit agent
roles, internal iteration/vote counts, prompts and raw diagnostic chatter. Preserve
material limitations rather than burying them in optimistic wording.

## Durable draft identity and repeat behavior

Use additive immutable files under
`<runtime>/work/<item-id>/reports/report-<stable-observation-key>/`. A readable
report plus a small request manifest records item/input paths, meaningful observed
status/code identity, provenance/coverage, resolved or missing destinations,
reporting disposition, exact payload file paths/digests, stable request IDs and
next reporting action. Append its absolute report path under a unique report- key
in artifact_paths through ordinary owner-gated save; save only reporting evidence
and any justified approval/action additions. Do not overwrite an earlier artifact
or alter engineering fields merely to say a draft was made. Persist after writing
readable evidence; retain stable save decision IDs/content after uncertain replies.

Derive the observation key from item ID, destination/operation identities and
semantic facts needed by the report: actual result/wait/decision, PR/head/check
status, merge/deployment/verification knowledge and evidence identity. Use a stable
canonical serialization and SHA256, or a saved equivalent explicit comparison.
Exclude fetch/run timestamps, artifact-directory names, worker IDs and stylistic
rewrites. Before drafting, inspect previous manifests/actions and compare those
semantic facts. If unchanged, return the SAME saved payload/request/path with no
new draft, action or semantic save. Do not regenerate prose and mistake its new
hash for new progress. Changed meaningful facts or an explicit requested revision
produce a new immutable request version; retain prior versions and identify any
superseded unsent draft, rather than silently sending an old one. Resolve an
uncertain prior send before issuing another update for that same intended event.

A useful minimal manifest has observation_key, observed_facts/provenance,
engineering_state_reference, and requests with stable id, operation, destination
(or null plus gap), payload_path, payload_sha256 and reporting disposition such as
local_draft/unaddressed/awaiting_authorization. This is durable agent evidence,
not a new helper-enforced schema or workflow engine. Sending outcomes are additive
reports plus the existing action ledger; never mutate an immutable draft manifest
to simulate a send. Generate no external pending action merely because a local
draft exists. Each explicitly authorized destination gets its own stable action.
An unchanged explicit repeat can consume zero semantic steps; new evidence saves
consume normal steps and may wait until the next bounded invocation.

## Exact permission, sending and reconciliation

`posts` covers publishing a Slack thread reply or Jira comment. Existing `tickets`
policy is unchanged; this reporter creates no issue, edits no issue fields and
performs no workflow transition. A future explicit transition request needs its
own available real workflow/allowed transition, policy and authorization; do not
map a report phrase such as ready or merged to an invented Jira status.

Read the shared [external-action reconciliation contract](../../factory-run/references/persistence.md#external-action-reconciliation)
for command shape, immutable scopes/history, owner/CAS/steps and exact retries.
Use scope.action posts. scope.target identifies operation plus exact destination,
for example slack:<workspace>/<channel>/<thread_ts>:thread_reply or
jira:<site>/<issue-key>:comment. scope.revision binds the exact serialized outgoing
payload SHA256 AND semantic status/head observation digest. Retain a readable
request/authorization report with actual direct instruction/provenance, exact
payload bytes/destination, author identity expected from this host, limits and
source-of-truth evidence. A generic run, plan, source message, old post approval or
setup write exposure grants no send permission. Reuse applicable direct approval
only within its exact scope, respecting newer restrictions/revocation.

Immediately before sending, recheck current facts/target, exact approved bytes,
actual host write permission and existing reporting/action history. If material
status/head/content/destination changed, prepare a newly scoped draft rather than
send the stale one. Prepare any tool-specific serialized representation before
approval (including Jira document format when required); do not add unapproved
content during conversion. Save the proposed action and matching approval, then
uncertain before execution, reserving confirmation steps as the shared contract
requires. Invoke the authorized write once. Obtain actual returned ID/permalink
and verify the exact destination, resulting content and author/request attribution
through its returned object or fresh read. If required data is missing, remain
uncertain; never manufacture a permalink from memory. Confirmed means the exact
authorized postcondition was observed, not an exactly-once guarantee.

On any uncertain send/resume, read the exact destination and relevant complete
history with actual pagination/time-window limits. Reconcile against request
identity, intended sender/app, destination, exact payload and attempt evidence
such as an observed response ID/client correlation when supported and recorded.
Do not assume a platform/tool supports a client idempotency key or custom metadata.
The same content from another author, in another thread/issue, before this request,
or without distinguishing evidence is not proof this request applied. A plausible
matching post can prevent duplicate sending while uncertainty remains unresolved.
Absent/partial pages, unreadable author/payload, unavailable request attribution
or multiple candidates retain uncertain with a precise reporting wait/question.
No blind repost or replacement action. Only a fresh complete authoritative
observation establishing non-application may restore proposed with durable rationale;
then revalidate scope/current truth/permission before another attempt. Never reset
an action because time passed. Do not delete/edit remote posts to repair uncertainty.

## Invocation outcomes and focused evaluation

An explicit report-only request to factory-run skips watch/route/code progression,
reads the selected item and returns drafts/reporting disposition while preserving
its engineering state. With no selected item, report that absence; do not invent
work. Normal runs may draft at meaningful saved progress, completion or a new
block/human question when a semantic step remains. No-change observations do not
trigger duplicate drafts. A saved meaningful outcome lacking a corresponding
report can receive its first draft later even with no new engineering step.
Reporting runs before finish/release while ownership/capacity remain; its limits
do not erase engineering outcomes. Stop
at the bound/actual handoff; no automatic polling or schedules.

For explicit focused synthetic:report-evaluation: imports only, existing begin
--fixture may supply an ordinary item with raw status/destination observations in
a readable input manifest. Preserve its declared engineering stage/wait/counter
as imported scenario metadata and label absent upstream model-role history. Those
raw observations permit reporting evaluation, not a fabricated completed
investigation/review/deployment or real approval. Offline saved resumes use the
same immutable inputs/report manifests. No helper flag or production evidence
bypass is introduced. Live send testing is deferred to Brian's own trial; record
actual untested capabilities honestly without blocking offline delivery.
