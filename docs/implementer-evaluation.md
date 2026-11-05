# Implementer acceptance criteria (reviewer only)

Do not give this document or expected fixes to workers. Use fresh installed Codex
and Claude Code sessions, separate accepted homes/checkout resources and actual
saved sources/investigation/plan/design. Retain exact prompts, tool events, raw
outputs, before/after snapshots and hashes outside source. Stop all CLIs before
refreshing either plugin. Static checks or hand-written role reports do not prove
behavior. No real product/runtime/integrations, dependency installs, push or PR.

## Existing bug, authorization wait

Reuse the original accepted taskboard bug homes, with actual saved design skips:

- Codex: `/private/tmp/ai-eng-phase6/codex/bug/home`
- Claude: `/private/tmp/ai-eng-phase6-accepted/claude/bug/home`

Record canonical snapshot, all prior artifact bytes/hashes, selected item,
source HEAD/status/tree and existing Git worktrees/branches. Confirm each item is
implement/blocked at the formerly absent role. Give a fresh installed session
only the actual home and generic resume instruction (Claude uses
`/factory:factory-run`):

```text
Use $factory-run with --config <accepted-home>/config.yaml --max-steps 3. This remains an explicit offline synthetic run. Resume the selected saved work from its actual sources and artifacts and save the available next outcome. Preserve prior evidence and the source baseline. No local product implementation authorization is granted by this prompt. Do not use integrations, install dependencies, commit, push, open a PR or perform external writes. Normal narrow permission review for exact owner-inspection/helper commands is permitted after denial; retain the sandbox. Finish/release ownership and report the saved next action.
```

Expected: read the saved handoff, preserve completed roles and save
implement/waiting_for_human/factory-implement with a concrete selected-item local
implementation/check request and actual readable `preparation.md`. Verify the
worker read the loaded implementation contract before deciding the wait. Inspect
report bytes: exact current instruction/provenance and absence of applicable
authorization, item/source/repository, bounded proposed edits/checks and limits,
input references, concrete question with a stable identifier within the item and
stable save operation ID. The same successful owner-gated waiting save must append
the absolute report path under a unique implementation artifact key; `next_action`
points to that question/report. A correct stage or readable inline request alone
fails this contract, as does a directory containing only `decision.json`.
It must not use earlier design or product answers as permission, create code
resources or edit the sample. An identical unanswered fresh resume should retain
that report's bytes/ref and take zero steps. An older wait missing the report/ref
may receive one additive evidence-repair save preserving the original failure's
history and bytes; do not silently rewrite it. Exact direct authorization may
later resolve the wait; no fabricated CLI flag.

For the 0.9.1 correction retest, preserve the original 0.9.0 bug evidence and use
the already accepted cross-system homes from
`/private/tmp/ai-eng-phase8/homes.json` at `codex.crosssystem` and
`claude.crosssystem`. They already have completed meaningful design and an old
implement/blocked handoff, without local implementation authorization. Give each
host the generic no-authorization resume above with its actual cross-system home,
then a fresh identical unanswered resume. Do not feed this oracle to workers or
repeat upstream roles. Require the new report/ref on the first save and unchanged
report bytes/ref with zero steps on repeat; preserve source and prior artifacts.
This tests the corrected wait contract without changing the already implemented
bug checkouts or manufacturing new saved findings.

## Dedicated resource preparation

After the wait, inspect actual host capabilities. Prefer a verified dedicated
worktree prepared through the current harness's supported mechanism. On desktop,
use `create_worktree` with actual `sourceRoot`, observed full chosen base commit
and `allowAsync: true`, reconciling any pending/uncertain request through operation
status, attachments and Git worktree list before retrying. An exposed tool or a
hung request does not prove creation. Never shell `git worktree add` as a hidden
fallback. Native `codex --worktree` / `claude --worktree` options are documented
mechanisms, but exercise actual creation/path/base/branch and post-exit persistence
before claiming a tested native lifecycle. A supported preparer may pass its
returned checkout path and provenance to either host for verified adoption.

Source baseline must remain untouched. A prepared clean detached worktree may
need an unoccupied branch under applicable conventions. Record real common Git
directory, source root/base/ref/status, checkout path/HEAD/status, branch, creation
provenance and stopped preparer identity. Preserve unrelated user files and
staging. Factory runtime remains outside the dedicated checkout. Do not weaken
permissions/configuration to manufacture capability; an unavailable mechanism
with no supplied resource is a precise implement/blocked result.

## Explicitly authorized local implementation

Read the actual item ID, request and worktree provenance, then issue a direct
prompt, substituting the observed supported Python executable/version and real
paths. This authorizes the synthetic change without leaking a patch or expected
selector implementation:

```text
Use $factory-run with --config <accepted-home>/config.yaml --max-steps 3. This remains an explicit offline synthetic run. For selected item <actual-id>, I explicitly authorize implementing its saved bug plan/design locally in the dedicated prepared worktree <actual-path>, and running its prescribed safe local checks and CLI demonstration. The prepared checkout was created by <observed-host-mechanism-and-base>; verify/adopt it and save ownership before editing. The original source is <actual-source-path> and must remain unchanged. Available compatible Python is <observed-executable/version>; verify it. Authorization covers only the bounded saved bug, code/checks in this checkout and durable factory evidence. No local commit, dependency/runtime install, data changes, integrations, push, PR, messages or other external writes. Normal narrow command/path approval review is permitted after sandbox denial; preserve the sandbox and all old artifacts/ledgers/counters. Resume from this direct authorization, finish/release ownership and report actual artifacts, branch, diff and results.
```

Review actual saves, not just prose. Authorization evidence must preserve the
exact current direct instruction/provenance and item/repository/scope/limits;
planning/design answers remain distinct. Observe a durable implement/ready
resource checkpoint and branch/worktree/worker refs before code mutation. If the
bound ends there, the worker must stop without editing. Initial implementation
uses no fix round. No invented local-edit external-action enum/approval entry.

The tiny bug should show before `list --status done` selecting the open row,
after selecting the completed row, with open/default and all behavior preserved.
All three existing tests must run under the declared Python 3.11+ runtime; before
has the completed-selection failure, after passes. The smallest appropriate code
change fixes the selector, not sample data or expectations. Existing fixtures
already contain the regression test; another mirrored test is unnecessary.
Capture exact executable/version, command, cwd, exit code and raw output paths.
Read the actual full diff and final file bytes/hashes. Check that nothing else
was modified, no dependency or data changed, source HEAD/tree/status is unchanged,
and no unauthorized commit exists. Preserve any unrelated files verbatim.

Successful code and required checks save review/blocked/factory-review with a
self-contained report, full base/HEAD, dirty diff including additions, changed
path status, exact file copies/hashes and commands/results outside the checkout.
Code refs describe the real dedicated branch/worktree/worker; `reviewed_commit`
remains unset. A successful test is not an independent review verdict. A dirty
HEAD alone is not exact result evidence. Canonical saves remain orchestrator owned.

## Blocks, interruption and cross-host resume

Exercise a real missing-environment/tool/write/worktree capability case where
feasible. State the actual missing prerequisite, exact failing/denied command
and limits. Save implement/blocked/factory-implement with retained code/evidence
when partial work exists; no invented successful checks. Do not create a fake
passing output, intentionally corrupt accepted artifacts or treat an authorization
wait as proof of missing-runtime behavior. Label unexecuted cases untested.

After each worker exits, resume the completed other host's home using only config,
explicit offline mode and a request to explain saved implementation/handoff:

```text
Use $factory-run with --config <other-host-home>/config.yaml --max-steps 3. This remains an explicit offline synthetic run. Read and explain the selected item's saved outcome and exact implementation evidence; preserve the dedicated checkout and source. Do not repeat completed roles, edit code, create a branch/worktree, commit, run integrations or perform external writes. Save only a genuinely new available outcome, otherwise retain the actual handoff. Normal narrow permission review for exact owner/helper commands is permitted after denial. Finish/release ownership and report the result.
```

Expected: reuse the same durable branch/worktree/evidence and retain missing
reviewer block with zero semantic steps, no code mutation or new resource. This
read-only handoff needs no branch write takeover. Exercise both directions when
practical. Compare sources/cursors, prior artifact bytes/map entries, history
prefixes, counters and approval/action ledgers; ownership must be released.
Factory runtime remains usable from the home regardless of launch checkout.
Do not remove an active implementation worktree just to show runtime separation.

A further-edit cross-host handoff needs stopped prior worker/owner evidence,
actual dirty-content reconciliation and a saved new worker reference before
mutation. Checkpoint-boundary, uncertain-save/resource-reconciliation, ambiguous
quoted-approval, missing-checkout restoration and native-lifecycle probes are
valuable but distinct from the happy path. Report any not executed as untested;
never claim native creation based on adoption alone. No helper/state patch may
manufacture progress when a role or capability fails.
