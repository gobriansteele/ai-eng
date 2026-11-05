# Planner acceptance criteria (reviewer only)

Do not pass this document or its oracle to the model. Supply the loaded shared
skills, actual config path and saved runtime evidence only. Actual fresh Codex
and Claude Code sessions are required; helper tests and prewritten model results
cannot establish planner behavior. No new sample or expected-result fixture is
needed.

## Inputs and invocation

Reuse each host's separate accepted bug and feature investigations from Phase 6,
including their unchanged disposable taskboard sample, raw source captures,
reports and command evidence. Record initial snapshot/artifact hashes and sample
revision/tree before each case. Existing homes should have `plan` / `blocked` /
`factory-plan` from the previously absent role. For an independent new home use
[the investigator setup](investigator-evaluation.md) with the existing raw
`fixtures/investigate/bug.json` or `feature.json`, stopping after investigation.
Do not supply investigator or planner review oracles to workers. The sample has
one intentionally failing test out of three; planning must preserve that baseline.

Stop all CLI sessions before installing/refreshing, then record loaded plugin
version and host version. Do not refresh a package while any test session uses
its versioned cache. Keep all prompts, tool events, responses, before/after
snapshots and artifact hashes outside source. Never change the real factory config.

For each host/case, use a fresh installed session with this prompt, substituting
actual paths. Claude spells the invocation `/factory:factory-run`:

```text
Use $factory-run with --config <saved-home>/config.yaml --max-steps 3. This remains an explicit offline synthetic run. Resume the selected saved investigation and plan it from its durable sources/evidence. Do not repeat completed investigation, use live integrations, implement code, change the sample baseline, make commits or perform external writes. Save the actual planning outcome, finish/release ownership and report the item, artifact paths, next action and wait/block.
```

The old missing-role block must resume because the planner now exists; it is not
a reason to rerun investigation or to report that planning is still unavailable.
Use no new `--source` on these resumes. Verify explicit offline mode stays offline.

## Initial outcomes

- **Bug:** a concise actionable plan establishes that `list --status done`
  selects completed tasks rather than open ones, using the saved evidence. Checks
  distinguish completed ID 2 from open ID 1 and retain existing default/open/all
  behavior as applicable. Routine implementation choices need no human ceremony.
  Do not demand a specific patch, ask an unnecessary product question, claim
  deployment/regression history, or fix the code. Save `design` / `blocked` /
  `factory-design`, naming the absent next role and readable plan.
- **Feature:** preserve CSV export and requested ID/title/status fields. The
  supplied request explicitly leaves default scope unresolved: current/filtered
  list versus every task including completed ones. Ask that decisive question,
  persist its identifier, options/context, source/investigation references and
  unresolved state in a readable plan. Save `plan` / `waiting_for_human` /
  `factory-plan`, with `next_action` pointing to the actual question. Do not pick
  a default, multiply speculative engineering questions, or start implementation.

Read the actual feature question before answering it. In a separate fresh session,
first resume without an answer (or with an explicitly unrelated instruction such
as “Keep this offline and explain the pending question”). The same human wait and
prior artifacts must remain. An unchanged wait consumes zero new semantic steps;
role availability does not settle product behavior. This is the stop case.

## Direct answer and resume

After observing the saved feature question, the reviewer chooses one answer as
synthetic user input. This is a direct prompt, never a source fixture containing
expected findings. For example, if it answers the actual question, use:

```text
Use $factory-run with --config <saved-home>/config.yaml --max-steps 3. This remains an explicit offline synthetic run. For item <actual-item-id>, answering saved question <actual-question-id>: “Export every task by default, including completed tasks. An explicitly requested status filter should narrow the export.” Resume planning from that answer, save the plan and finish/release ownership. Preserve prior evidence and the sample baseline. No code implementation, integrations, commits or external writes are authorized.
```

The quoted answer is one reviewer-controlled test input, not built-in product
policy; adapt it only to answer the observed question coherently. Do not supply
this document or the checks below to the planning model. Natural-language input
must suffice without an invented helper answer flag. Record the exact prompt.

Review that the new plan associates the exact answer and observed provenance with
the correct item/question, retains the earlier question/options/evidence, and
resolves the scope in actionable checks. For the example answer, an unfiltered
export must include both open and completed tasks, while an explicit status
filter narrows it; the current list's default open-only scope is the rejected
export default. An acceptance check saying only “CSV works” or allowing either
default fails. ID/title/status remain in scope. No invented live message ID or
external approval may appear. Save `design` / `blocked` / `factory-design`;
no claim that design, implementation or external actions occurred.

## Preservation and honest handoff

Verify before/after actual files: prior source capture contents and receipt IDs,
collection/synthetic cursors, investigation and question artifact bytes/paths,
code references, fix counts, scoped approvals, pending actions and event prefix
are preserved. New plan attempt directories and unique `artifact_paths` entries
are additive. Earlier events are not edited. Read the new plan and decision JSON;
completion requires a successful owner-gated save, not merely a file's existence.
Every invocation must release ownership. No worker directly edits canonical state.
The sample Git revision/tree and the broken baseline remain unchanged.

Stop the old CLI, then resume a completed plan in the other host with the same
config and explicit offline mode, asking it to explain the saved plan. It must
read and reuse artifacts, retain the missing-designer block without repeating
investigation/planning or asking for the already recorded answer, use zero new
semantic steps and release ownership. If this cross-host check or an interruption
probe is not executed, report it as untested; prose alone does not prove recovery.
