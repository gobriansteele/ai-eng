# Independent review and bounded fixes

Focused synthetic stage imports are accepted only through factory-run's explicit
review-evaluation fixture contract. Its readable evaluator manifest/raw requirements
supply the declared review inputs while missing upstream role history remains
visible. Do not demand invented role reports or claim those roles completed.
Imported observed failed checks may be reviewed as evidence; they are never a
successful implementation handoff. Read-only focused cases may identify an
evaluator-supplied disposable candidate checkout in the manifest without claiming
a factory-owned worktree. No edits are authorized there. A fix case still needs
the actual dedicated worktree/ownership and explicit local authorization. Production missing-input handling is unchanged.

## Freeze and evidence

Apply the [verification facts contract](../../factory-implement/references/verification.md).
Check claims against raw executions and tested inputs, including honest reuse of
pre-commit checks on identical content; estimated dates and unchanged HEAD alone
do not establish execution or content identity.

Each attempt lives under `<runtime>/work/<item-id>/review-<unique-attempt-id>/`.
Preserve earlier report bytes and append absolute paths under unique `review-`
artifact keys. Write reports after supporting evidence; keep stable save operation
IDs and decision JSON beside them. Partial worker output is evidence of an
incomplete attempt, not a verdict. Inspect history and actual artifacts after an
interruption before dispatching or saving again; exact save retries retain their
operation ID/content. Existing accepted reports can be reused only with unchanged
inputs, reviewed bytes and independence evidence.

The orchestrator prepares one read-only review bundle: item/source versions,
absolute requirements/plan/design/instruction paths, implementation/preparation
and authorization paths, actual checkout/branch, full base and HEAD IDs, clean or
dirty status, full base-to-result and separate staged/unstaged diffs, changed-path
status, exact result file copies/hashes including relevant untracked code, tests
and other inputs, prescribed command results and known verification limits.
Include relevant unchanged code/context so a patch alone does not hide behavior.
Record a deterministic SHA256 manifest of those input paths/content and the result
diff/files; it identifies the review target even when HEAD is unchanged. Validate
current checkout content before dispatch and after workers finish. No implementation
edits run while that review attempt is active. A missing checkout/content mismatch
blocks acceptance; preserve evidence and explain the mismatch, never overwrite it.

Each report names the bundle fingerprint, role/focus, actual fresh worker/session
identity and invocation provenance when observable, input paths, command/cwd/exit
status/raw outputs when run, limitations and conclusions. Keep prompts and returned
reports durable so a new host can verify independence. Missing actual worker output
cannot be filled by the orchestrator. Worker IDs are diagnostic, not resumption keys.
All workers may write only their own runtime attempt artifacts and run scoped safe
read-only checks; they never call begin/save/route/finish or edit canonical state.

## Independent reviewers and adjudication

Dispatch reviewer A for behavior/correctness and reviewer B for integration,
regression, safety and verification gaps. Adapt focus to the actual change while
covering the whole bounded implementation. Both receive the same raw bundle and
requirements, with no other reviewer's findings, implementation-agent transcript,
evaluator oracle or suggested verdict. An implementation report is evidence of
commands/content, not an authority on correctness. Prefer fresh native workers;
a supported fresh standalone CLI can serve as a role worker if isolation and
parent ownership can be verified. No role worker starts another factory invocation.
If two independent contexts or a fresh adjudicator are unavailable, stop with the
actual capability blocker rather than serial personas in the owning context.

Reviewers report either no supported findings with limits or findings with stable
local IDs, severity, exact path/location, trigger, impact, requirement basis,
evidence/reproduction and uncertainty. Unsupported suspicions can be marked for
checking; they must not become accepted defects without support. Neither a passing
test nor stylistic preference alone proves a correctness judgment.

After both reports return, dispatch one fresh adjudicator with the identical bundle,
both raw reports and their evidence. It may run bounded safe checks. It groups
duplicates into stable issue IDs retaining all original finding IDs/evidence, then
records each disposition: accepted fix, dismissed with specific evidence/reason,
or unresolved with the concrete disagreement/missing fact. Give each a severity,
requirement basis and actionable conclusion. Do not silently drop unsupported or
minor findings, or invent a disagreement to exercise the panel.

Only genuinely unresolved findings go to three fresh independent panelists. Each
gets the same relevant raw bundle, disputed finding/evidence and competing reasons,
but no other panelist's response or requested vote. Each independently returns a
supported disposition and rationale. The adjudicator's original report is immutable;
append a final synthesis with panel reports and explicit tally, reasons and limits.
A majority can settle an evidentiary interpretation only when supported by facts.
A reproducible serious defect remains accepted or a concrete human wait regardless
of tally. A tie, inconclusive evidence, consequential product ambiguity or unsupported
majority remains a wait/block with the specific next question/check. The orchestrator
checks evidence and this safeguard; it does not vote away defects or impersonate
any missing role. No panel runs for already accepted/dismissed findings.

## Pending batch and recovery

One item shares its fix counter across internal review and PR follow-up. Apply
the [execution-mode recovery policy](../../factory-run/references/execution-modes.md):
restricted/legacy work permits two total rounds; default/bedtime continues
productive fixes and stops only at an impasse after changing approach.
A round means the engineer receives one accepted batch, changes implementation
and returns it for verification. Initial implementation/review and unchanged
reviews consume zero. Group currently accepted findings into one batch; avoid a
round per finding. Fix authorization is still required under `factory-implement`.

Before engineering changes, the orchestrator saves the immutable accepted batch
report with `implement` / `ready` / `factory-implement` (or its truthful authorization
wait/block), preserving `fix_rounds` for now. The batch records stable batch/round
attempt ID, count before, proposed ordinal (count + 1), finding IDs, exact input
fingerprint, allowed scope/checks, authorizing evidence, owner and next action.
This is a pending attempt, not a completed round. Never create a second pending batch or count preparation/authorization as a code fix.
All resumes and later PR follow-up must first read pending-batch/history evidence;
finish or explicitly resolve the same pending attempt before considering another.
Unknown/live implementation ownership still blocks mutation.

The engineer reuses the same owned worktree and pending batch, preserving earlier
bytes. It returns an immutable fix report with batch ID, before/after exact content,
changes per finding, commands/results and remaining issues. When changed code is
returned for verification, the orchestrator verifies evidence and increments
`fix_rounds` by exactly one in the same owner-gated save that references the fix
report and its outcome. A changed-code return with failed required checks still
counts: save implement/blocked with the failed-check evidence; a later correction
is another batch/round. The return report closes that batch ID; a completed batch
cannot authorize further edits. A later failed-check correction needs a new saved
batch at the current count, subject to the same mode-specific recovery policy. The orchestrator
may batch the concrete remaining accepted findings/required-check failures for an
authorized correction in this invocation or on resume; no need to invent another reviewer verdict about an
observed failed check. No-code attempts do not count and cannot pass review;
retain the unresolved batch/wait/block with its reason. Do not increment separately
for reviewer verification or an exact save retry.

If interrupted after edits, preserve the pending attempt and partial code; reconcile
its actual content and write the return evidence before completing that same round.
Never restart the batch with a new ID or reset the count to gain another attempt.
A successful changed-code/check return saves review/ready/factory-review with the
new fingerprint and incremented count. Re-review affected code and interactions
with fresh independent reviewers and adjudication; explicitly justify any unchanged
scope verdict reuse. All old reports remain readable but cannot approve newer bytes.

At the applicable recovery limit or demonstrated impasse, save the actual
review/implement block with remaining findings, attempts, current content and
needed input. Keep the counter and evidence; never claim a pass merely because
recovery stopped. Product/architecture ambiguities follow the mode's decision
policy, including explicitly delegated bedtime decisions.

## Saved outcome

The orchestrator reads reports/evidence and rechecks target identity before ordinary
owner-gated save. Preserve sources/cursors, prior artifacts, code ownership, counters,
approvals, pending actions and history. A role/capability block retains review /
blocked / factory-review; a genuine human dispute retains review / waiting_for_human /
factory-review. Unchanged genuine waits/blocks consume zero steps. Availability of
this role resumes an older missing-reviewer block, not a real unresolved question.

A passed final report lists all finding dispositions, exact fingerprint/base/HEAD,
raw role reports, panel use/cost when observed, verification, scope and limitations.
Only a clean exact reviewed commit may populate `code.reviewed_commit`; dirty code
keeps it unset and is identified by its full diff/files/hash manifest in the report.
Invalidate `reviewed_commit` and affected verdicts on subsequent content changes.
A pass saves follow_pr / ready / factory-follow-pr with the reviewed artifact and
exact-content handoff. Follow-up is available and requires its own scoped
authorization before any external action. No judgment about merge, deployment
or production verification
follows from an internal pass. Durable paths and exact evidence, rather than a
host transcript, support subsequent cross-host read-only resume.
