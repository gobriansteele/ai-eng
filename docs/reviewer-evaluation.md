# Reviewer-only Phase 10 evaluation

Do not pass this oracle or expected answers to role workers. These are controlled
evaluations, not production intake or evidence that earlier roles completed. Keep
all homes, Git sources/worktrees, imported manifests, raw outputs and runtime
outside plugin source. Never mutate the accepted Phase 9 homes, code worktrees,
samples or their artifacts. Parent owns version/install/refresh and actual runs.
Static validation cannot establish model independence or review correctness.

## Cases and honest stage import

Use separate homes for Codex and Claude Code for each case. Start from the four
original taskboard sample files, or exact accepted Phase 9 result copies, in new
disposable Git sources. Keep source roots clean after setup. Prepare dedicated
code worktrees for fix cases through an actually observed supported native
mechanism, recording full base/common Git directory, source and worktree
path/HEAD/status, branch, creation provenance and stopped preparer identity.
Read-only dispute/exhausted cases may instead use an explicitly declared disposable
Git candidate checkout, with baseline/controlled seed commits and no factory edit
authorization or factory worktree ownership claim. Omit code.worktree when no
factory worktree exists; the manifest identifies the exact review checkout. Phase 9's documented Codex
native worktree preparation can supply a checkout for either host. Do not silently
fall back to shell worktree creation or edit the accepted Phase 9 resource.

Create independent cases:

1. Seeded defect + unsupported allegation + correction: use the original wrong
   done selector as a deliberately introduced regression in a disposable dedicated
   checkout. Pass raw requirements from fixtures/review/requirements.md and the
   unsupported-input.json allegation, explicitly as unverified controlled input.
   The known regression is reviewer-only knowledge, not a suggested worker answer.
2. Disputed requirement: start with correct open/done/all selection; pass the same
   raw requirements and dispute-input.json. Do not inject the defect here or require
   a successful pass while a consequential product question remains unresolved.
3. Exhausted bound: independent seeded-defect checkout with imported fix_rounds=2.
   Clearly label this as scenario metadata, with prior batch/attempt history
   unavailable. No prior model execution, attempted fix or failed round is claimed.

Before the run, the evaluator captures actual commands/cwd/runtime versions/exit
statuses/raw outputs, full base/HEAD, changed paths, base-to-result and separate
staged/unstaged diffs, exact result copies/hashes including relevant untracked
code/tests/inputs, source baseline and actual resource provenance. Do
not label failing checks passed. Write a readable evaluator-input.md manifest
containing those paths, raw requirements/candidate-claim paths, case ID, explicit
controlled input provenance, absent investigation/plan/design/implementation-role
history, current dirty identity, scoped evaluation authorization and limits. This
is imported input, not a worker result. Dirty seeded code has no reviewed_commit.
The manifest must support fresh read-only review without relying on this oracle.

Generate ordinary begin --fixture JSON outside plugin source using the existing
synthetic-item.json shape: synthetic=true, descriptive controlled-input label,
source_id synthetic:review-evaluation:<host>:<case>, stable subitem_key, no live
source/Jira links, classification bug (or feature for the product dispute), stage
review, status ready, required_role factory-review, next_action naming the focused
review and manifest, artifact_paths mapping evaluator-input to its absolute path,
observed code worktree/branch only, fix_rounds 0 (2 only for the labeled exhausted
case), empty approvals and pending_actions, empty synthetic_cursors. The helper
computes item ID on import. No fake source receipts or completed-role artifacts.
Run factory-run with the explicit fixture and request below; it creates canonical
state through verified-owner begin. Never write/patch work.json directly, import
fake reviewer output, prewrite a verdict or script a role completion. Focused-stage
import uses the manifest/raw requirements instead of invented upstream reports.

## Actual fresh role execution

Verify actual native dispatch availability in both hosts. Codex fresh workers use
fork_turns:none; Claude uses native Agent general-purpose contexts without parent
context fork. Actual names/schema come from the host guide/current tools. Role
prompts explicitly skip global personal-context refresh in this synthetic scope.
They may read scoped inputs, run safe read-only checks and write only their own
runtime evidence. Keep actual dispatch calls/returned IDs, prompts, reports and
available child tool traces. Do not claim hidden-context inspection when only
worker self-report is visible. A role name in a parent summary is not proof of an
independent role. No nested factory-run or canonical mutator by any worker.

Generic initial prompt (substitute only observed paths/case facts):

```text
Use factory-run with --config <home>/config.yaml --fixture <case-fixture.json> --max-steps 3. This is an explicit offline focused review-stage synthetic evaluation using the declared evaluator input manifest; it does not claim prior roles ran. Independently assess this selected controlled implementation against the raw requirements and any supplied unverified claims. Use actual fresh independent review/adjudication and the normal dispute rule; never simulate roles or manufacture output. Preserve all imported provenance, old artifacts, ledgers and counter semantics. Review-only now: no code changes, commits, integrations, installs, pushes, PRs or external writes. Permit only narrow normal owner/helper/path permission review after denial. Finish/release and report actual role identities, evidence, dispositions, exact content and saved outcome.
```

Inspect the complete canonical record/history and actual role reports yourself.
Require two independent complementary reviews over the same fingerprint and a
separate fresh adjudicator. Conclusions must not leak between reviewers. Evidence
must support any accepted defect; every raw reviewer finding/candidate allegation
has a disposition/reason, duplicates keep original IDs/evidence. The network
allegation should not induce a needless code change without supporting evidence.
No simulated secondary findings count as independent reviewers.

The dispute case is an experiment: accept a supported resolution or genuine
human-needed question. Require three fresh independent panelists only if the
adjudicator actually leaves a dispute unresolved; no forced panel on a clean
review and no fabricated disagreement. Inspect raw panel opinions and final
reasoning/tally. A reproducible serious defect cannot be voted away. If workers
resolve without a panel, record that the panel path remains untested and run a
further genuinely unresolved controlled case before claiming that path passed.
Do not tell workers which outcome to produce.

## Fix and re-review

Only after reading the saved accepted batch, authorize a bounded synthetic fix
with direct provenance and the actual selected ID/worktree. Example:

```text
Use factory-run with --config <home>/config.yaml --max-steps 6. This remains an explicit offline focused synthetic review evaluation. For selected item <actual-id>, I authorize the bounded accepted selector fix batch in its existing dedicated checkout <observed-worktree> and prescribed safe local checks. Reuse the saved manifest/raw requirements and existing worktree; verify actual stopped ownership and save any required handoff before editing. Authorization covers only this synthetic local fix and evidence. No local commit, dependency/runtime install, data changes, integrations, push, PR, messages or other external writes. Use the pending batch once, preserve earlier bytes/history, independently review the returned exact content and finish/release at the actual outcome.
```

Verify the pending accepted batch is saved before editing with count still zero.
Authorization/ownership checkpoints are distinct from completed fixes. Changed
code returned for verification increments once; the exact save retry or subsequent
review does not increment. All three existing tests and four CLI selections must
run with Python 3.11+, with raw before/after evidence. The smallest fix changes the
selector, not data or expected outcomes. Required failed-check code return still
counts and blocks; no-code authorization waits do not count. Re-review uses actual
fresh reviewers/adjudication on the corrected fingerprint; old dirty HEAD verdicts
cannot approve changed bytes. A pass should reach follow_pr/blocked with the exact
review artifact, count one, no reviewed_commit for dirty code, no PR or push.

Test the bound separately from the happy path: the exhausted fixture may be
reviewed to establish remaining issues, but must not edit code, reset its count,
claim unseen attempts, mark review passed or open a PR. It waits for Brian with
current evidence, remaining defects and explicitly unavailable imported history.
This tests the count-two policy boundary, not two actual engineer rounds. Claim
two real failed rounds only if separately executed with actual changed-code return
reports and checks; label that path untested otherwise. Any interruption probe must
preserve the same pending batch; never manufacture progress by editing state.

## Resume, scope and acceptance evidence

After each owning CLI exits, fresh same-host and sequential other-host read-only
resume uses only config and explicit offline mode, without the fixture or oracle.
Read/explain the saved implementation/review handoff; no new code/resources or
repeat review for unchanged accepted outcomes/waits. Recheck exact bytes and
reports as needed. Expect zero semantic steps at unchanged follow_pr missing-role
handoff or unchanged human wait. Destination permissions are rechecked; no branch
write takeover is needed just to read. Preserve imported inputs, source/cursor
metadata, artifacts/bytes, history prefixes, counters and approval/action ledgers.
Record actual blocked resumes rather than asserting portability from file format.

Record host versions, plugin version/hash, exact prompts, raw dispatch/report paths,
saved state/transition results, fixture provenance, command results, source and
worktree hashes, fix-round accounting, panel actual use/cost when exposed, failed
cases and unexecuted checks in phase-results.md. Compare reviewer value and cost;
the shared workflow remains the smallest useful arrangement. Native dispatch
probes establish tool capability only; these model-driven role/fix/evidence checks
are still required before Phase 10 acceptance.
