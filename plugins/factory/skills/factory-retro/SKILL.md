---
name: factory-retro
description: Review selected outcomes or transcripts, retain deduplicated evidence-backed improvement candidates, and record adjudication and fix evaluations. Does not rewrite skills/configuration or advance engineering work.
---

# Factory retro

Resolve the default once through the [configuration contract](../factory-setup/references/configuration.md#default-resolution-and-pinning),
unless this call already carries pinned absolute config/local from an invocation.
Reuse those paths throughout; an invalid default stops with setup/repair
instructions. Select the requested items/runs within that factory, without asking
for its config again.

Read the [learning record contract](references/learning.md). At a run boundary,
retain meaningful failures, user corrections or costly detours as observations;
routine success needs no new candidate. Direct retro requests can also supply
transcripts or existing candidates for adjudication or evaluation of a linked
fix. Use the selected factory's local candidate records; this is not Jira intake
and creates no external issue or engineering task.

Read the selected factory config/items/runs and their actual readable
source, decision, implementation/review/report evidence. Use the loaded helper's
read-only inspect when canonical state exists; no invocation acquisition or
canonical mutation is needed. With an explicit evaluation manifest, distinguish
its raw scenario declarations from actual supplied execution artifacts. Never
invent missing upstream roles or work completed by a failed invocation.

Compare the stated intent with observed outcomes: what helped, what failed, which
human intervention mattered and what evidence supports the causal explanation.
A useful role result or authorization wait is not a completed engineering item.
Routine success needs only a brief account. Spend attention on repeated mistakes,
unsupported assumptions, expensive detours and clear gaps in existing checks.
Read original failed/partial outputs alongside any successful retry; never rewrite
a failed probe as a pass because a later run succeeded.

Inspect existing candidates before proposing an improvement. Reuse the candidate
whose trigger/root cause and expected behavior match; add independent evidence
instead of another issue. Propose one small instruction/configuration/test
improvement when evidence merits it, with the exact observed trigger, expected
behavior and concrete verification. Record its evidence-backed adjudication and
acceptance scenario. Evaluation of an explicitly linked fix records the change,
actual result and limits; an implemented change alone is not a verified fix.
If existing guidance already addresses the failure, propose checking its actual
use rather than duplicating rules. Separate supported conclusions from hypotheses
and acknowledge evidence that weakens them. No automatic skill/config edit,
policy change, new task, external post or code fix follows from a retro.

Report observed wall-clock intervals, invocation execution intervals and explicit
human-wait intervals separately. A CLI's elapsed lifetime is not measured agent
compute time; overlapping or missing timestamps prevent reliable attribution.
Mark unavailable timing, tokens and cost unavailable instead of inventing totals
or estimating them as fact. Cite absolute evidence paths and actual revisions/
versions when exposed; do not expose private content beyond the requested scope.

Return a concise local report: scope/outcome, candidate identity/disposition,
evidence-backed observations, one
proposed improvement and how to test it, timing/cost limits and any decision for
Brian. Write only an explicitly requested output or an additive unique artifact
under <runtime>/retros/, retaining old reports. Candidate recording is permitted
local bookkeeping through the learning helper, not canonical engineering state
mutation. Preserve canonical state, source
links, artifacts, engineering waits, resources and counters. Direct invocation is
retrospective only, never intake/engineering/scheduling. Live trial evidence may
be unavailable; that is a limitation, not a reason to invent it or block the report.
