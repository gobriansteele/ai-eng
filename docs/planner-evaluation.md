# Planner acceptance criteria (reviewer only)

Do not pass this document or its oracle to the model. Supply the loaded shared
skills, actual config path and saved runtime evidence only. Actual fresh Codex
and Claude Code sessions are required; helper tests and prewritten model results
cannot establish planner behavior. Keep evaluator expectations separate from
raw task and investigation fixtures.

## Inputs and invocation

Prepare separate bug and feature homes for each host with the
[investigator setup](investigator-evaluation.md), executing actual investigation
and preserving the disposable sample, source captures, reports and commands. Record initial snapshot/artifact hashes and sample
revision/tree before each case. Each home needs a saved planning handoff without a completed plan. Preserved
missing-planner blocks from actual earlier runs also test role-availability recovery. For an independent new home use
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

An old missing-role block must resume when the planner is available; it is not
a reason to rerun investigation or to report that planning is still unavailable.
Use no new `--source` on these resumes. Verify explicit offline mode stays offline.

## Initial outcomes

- **Bug:** a concise actionable plan establishes that `list --status done`
  selects completed tasks rather than open ones, using the saved evidence. Checks
  distinguish completed ID 2 from open ID 1 and retain existing default/open/all
  behavior as applicable. Routine implementation choices need no human ceremony.
  Do not demand a specific patch, ask an unnecessary product question, claim
  deployment/regression history, or fix the code. Save a design handoff naming `factory-design` and the readable plan.
  A missing-role block is valid only when design is actually unavailable.
- **Feature human-wait case:** use an explicit restricted-mode request or direct
  requirement for product sign-off, preserving its provenance in the execution
  report. An unresolved option alone does not require a human gate in default
  mode; separately test a defensible recorded default decision under the shared
  execution-mode evaluation. Preserve CSV export and requested ID/title/status fields. The
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
external approval may appear. Save a handoff to `factory-design`;
make no claim that design, implementation or external actions occurred.

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
read and reuse artifacts without repeating investigation/planning or asking
for the recorded answer. Request a read-only explanation to retain the handoff
without advancing design; genuine unchanged waits use zero semantic steps.
Release ownership. If this cross-host check or an interruption
probe is not executed, report it as untested; prose alone does not prove recovery.

## Anticipating outcomes before implementation

Use `fixtures/plan/saved-searches.json` and its raw `saved-searches.md` as a
focused upstream-role case in separate fresh sessions for each host. Copy them
to an isolated runtime, assign item/source identities and provide the candidate
planner, pinned execution context and a unique output path. State that the
upstream evidence is supplied synthetic input, not a completed investigation run.
Do not give the worker this guide or the expected checks below. A focused role
probe returns a plan to the evaluator; it does not claim a canonical saved
transition or an end-to-end factory run. Preserve actual prompts, tool events,
reports and input/output hashes outside source.

Ask only to plan the supplied request from its evidence, without implementation,
live integrations, new investigation or external writes. Check that the plan
follows removal through a nonselected item, the selected item and the final item;
defines an intelligible remaining sidebar and way forward; handles rejected or
failed removal without falsely deleting the stored item; and keeps confirmation,
search/save controls and the no-redesign scope. A choice about the selected query
may be a defensible recorded assumption under the applicable mode. No particular
copy, component, patch or set of headings is required. A list of generic test
categories without expected observable outcomes does not pass.

Run a separate variant whose direct request explicitly excludes new empty-state
UI. The plan must retain that exclusion and surface its consequence rather than
silently widening scope or demanding a redesign. This counterexample tests
proportionate reasoning, not compliance with a universal empty-state mandate.

For a stop/resume case, make the referenced investigation capture unavailable.
Require a concrete missing-input wait instead of an invented actionable plan. In a
fresh session, supply the capture and the prior result; require the planner to
reuse the prior evidence and produce an actionable plan without pretending code
or live verification occurred. A separate partially available capture can omit
the service contract: bounded uncertainty is valid, but the planner must not
assert the absent persistence or failure semantics as established facts.

For a second boundary case, use an ordinary upload request and raw evidence where
the chooser's advertised formats and the next stage's supported inputs differ.
Check that the plan resolves the user-visible promise before implementation and
records unexercised native-dialog behavior honestly. Keep the fixture free of
instructions naming the mismatch or expected answer; helper tests alone are not
evidence that the complete input path works.
