# Local software factory implementation plan

Build a factory Brian can run on his Mac for one or two weeks, learn from, and change. It must work in both Codex and Claude Code from the first phase. Require a Slack MCP server and let the user select the Slack workspace and channels during setup. `wg-tutor` is an optional example for Brian’s trial, not a product default or restriction. Use skills to do the work, YAML for configuration, and local files to carry work between runs. Add a recurring task after the manual loop works.

This is a proposed implementation plan for review. It does not authorize installation, scheduling, external posts, or product changes. The implementing agent should build one approved phase, demonstrate it, and stop for discussion before starting the next phase. Approval of this document is not approval to build every phase at once.

**Execution update (2026-11-05):** Brian has now asked to continue to the next
phase after each phase passes tests and parent review, repeating that process.
Delegate bounded tranches with model and reasoning effort chosen for the work.
The original discussion pauses below are review checkpoints, not a requirement
to ask again before ordinary implementation. This does not authorize external
messages, product changes, schedule activation, destructive cleanup or other
actions that still need their own concrete approval.

**Release direction (2026-11-05):** Brian has deferred the prepared live PR trial
and will test the finished plugin himself with real work. Continue the remaining
implementation and offline validation, then ship the private plugin for that
manual trial. Unexecuted live-send, hosted-CI, scheduling and cleanup demonstrations
are explicit verification limits, not gates that hold up the offline release.
This does not authorize those external actions, schedule activation or deletion.
Keep validated offline behavior distinct from live behavior Brian has yet to test.

## What we are building

One locally installed plugin, provisionally named `factory`, with a setup skill and an orchestrator as its entry point. No separate `brian-mode` dispatcher. The orchestrator uses role skills as the work requires them.

The first version has one factory workspace and one active work item at a time. Several channels can eventually feed that workspace. Roles are separate instructions, not permanently running agents. Use fresh worker agents where independence or context separation matters, especially implementation and review. Do not create a separate service for each role.

The orchestrator is an agent. Configuration rules such as maximum fix rounds are instructions it is expected to follow. They are not guaranteed by a deterministic workflow engine. Small scripts may validate files, write them safely, and detect an already-running invocation. That does not make the entire workflow deterministic. Tool and host permissions remain separate from the YAML.

Do not build a custom scheduler, queue service, database, dashboard, MCP server, model-routing framework, or distributed worker system for this experiment. Use the connections and scheduling available in each supported harness. If a required capability is unavailable, demonstrate the gap and discuss it before substituting infrastructure.

## Invariant — Works across harnesses

Codex and Claude Code are required targets, not a primary implementation and a future port. Keep one source for role instructions, configuration semantics, work records, and fixtures. The same factory workspace must be resumable in either harness after the previous invocation has stopped. Identical prose or model judgments are not required; the same handoff contracts, evidence requirements, and limits are.

Keep the differences in two small harness guides and the necessary package metadata. These guides explain installation and refresh, skill invocation, worker dispatch, available integration tools, permissions, worktree operations, and scheduling. Start with instructions and manifests; add a wrapper script only for a demonstrated need. Do not build a generic adapter framework.

Shared skills describe capabilities such as reading a Slack thread or starting an independent reviewer. They must not require Codex-specific tool names, chat IDs, UI elements, or scheduler APIs. Harness guides map those capabilities to tools actually available there. Store durable file paths and external IDs in work records; host-specific worker IDs are optional diagnostic metadata, never the only way to resume.

The plugin requires an authenticated Slack MCP server in each harness. Document this dependency in the installation instructions and declare it in host package metadata where supported; do not assume installation transfers credentials or connections. Setup must verify Slack, Jira, GitHub, and local execution separately in each harness, including pagination, thread replies, and required write capabilities. Missing access blocks that capability; a fixture-only run is not proof of a working live integration. Do not assume an OpenAI connector is available in Claude Code or add a new integration service without discussion.

Only one harness may own a running factory invocation at a time. Both use the same workspace lock and state format. Switching harnesses must preserve fix counts, approvals and their scope, pending external actions, and intake cursors. Recheck the destination harness's permissions; do not transfer its tool approvals or relax them to match the other harness.

## Files and ownership

The factory plugin repository starts under Brian’s personal GitHub account, `gobriansteele`, not the `HonorEd` organization. Propose a private repository initially; confirm its name and visibility before creation. Do not create, publish, or transfer it as part of setup. Repository creation and pushing require Brian’s authorization at the implementation step.

The plugin repository owner is independent of the repositories the factory operates on. A plugin hosted under `gobriansteele` can work on authorized HonorEd repositories through the user’s existing access. Do not copy Honor source, credentials, real message fixtures, or runtime records into the plugin repository. Use synthetic fixtures and an example configuration in the plugin repo; keep Brian’s real Honor configuration in a separate private location under version control if desired.

Keep plugin source and configuration under version control. Keep runtime records outside the installed plugin and outside disposable code worktrees. Suggested layout, with final paths chosen during setup:

**Approved layout addendum (2026-11-05):** New setup now asks for one factory home,
suggests `~/factories/<factory-id>`, and derives `config.yaml` plus `runtime/` with
`runtime_path: ./runtime`. Show resolved paths before writing. Existing and
explicitly separate paths remain supported without relocation; the config path
stays the invocation identity. The original layout below records the initial
plan, not the current setup recommendation.

```text
factory-project/                  # Git repository
  plugins/factory/                # Host manifests, shared skills and helpers
    harnesses/                   # Codex and Claude Code operating instructions
  config/example.yaml            # Synthetic example, safe to commit
  config/honor.yaml               # Ignored; real configuration kept private
  config/honor.local.yaml         # Ignored; machine-specific paths only
  fixtures/                      # Synthetic examples safe to commit
  docs/                          # Installation, phase results, operation

~/factories/honor/                # Runtime workspace, not committed
  state/                         # Intake cursor and active-run record
  inbox/                         # Collected source messages
  work/<item-id>/
    record.json                  # Current stage, next action, links, attempts
    events.jsonl                 # Decisions and completed actions
    investigation.md
    plan.md
    design.md                    # Only when needed
    reviews/
    reports/
  runs/                          # Short invocation summaries and config snapshots
  archive/
```

Create files when needed; do not generate empty documents for every possible stage. No credentials in either tree. Real Slack excerpts and investigation evidence stay in the local runtime workspace, not committed fixtures.

Each invocation records the plugin revision and effective configuration. Record a configuration hash and a copy of the effective non-secret values; a Git commit alone is insufficient when there are local or uncommitted changes.

Each item needs a stable internal ID, source links, Jira keys, classification, stage, status, next action, artifact paths, worker reference if applicable, and fix-round count. Add branch, worktree, PR, and reviewed commit when they exist. Use separate stage and status fields so `waiting_for_human` does not erase which step needs help. External actions need their returned IDs and links.

The orchestrator owns current-state updates. Workers return findings and artifacts. A fresh chat must be able to resume from these files without the previous transcript. Jira and GitHub remain authoritative for their live status; reread them before acting on stale records.

## How to deliver each phase

For each phase, provide the changed files, the exact prompt Brian can use, the actual output of that prompt, and the resulting work record. Include one failure or stop case, not just the happy path. Record the result briefly in `docs/phase-results.md`.

The demonstration prompts below describe intended skill behavior; they are not existing commands. The implementing agent must document the invocation syntax that actually works in each harness. Every phase must demonstrate its applicable acceptance checks in both Codex and Claude Code, using separate copies of fixtures so one run does not contaminate the other. Record harness version and pass, fail, or blocked status. A blocked target means the phase is not complete. Also test a sequential cross-harness handoff in phase 3 and an end-to-end handoff before scheduling.

Use automated tests for parsing, state persistence, duplicate handling, and any helper logic. Evaluate skills by running them against examples and checking their decisions and artifacts. Do not substitute frontmatter checks or scripted answers for an actual model-driven demonstration.

## Phase 1 — Plugin and skill scaffolding

**Build:** A plugin installable in both Codex and Claude Code, containing one shared `factory-status` skill. It identifies the installed plugin version, lists implemented capabilities, and says whether a factory is configured. At this phase, the correct answer is that setup is still needed. Include installation and refresh instructions.

Use the supported local plugin formats and installation mechanisms for both installed harness versions. Claude Code documents its own plugin manifest and components; keep host metadata separate while sharing the skills directory. [Claude Code plugin documentation](https://code.claude.com/docs/en/plugins). Official documentation describes skills-only packages and local installation; verify installation here rather than assuming a Cursor manifest works in Codex. The installed copy can differ from source, so demonstrate that an edit reaches a fresh chat. [Plugin packaging documentation](https://developers.openai.com/plugins/build/plugins).

**Run:** “Use factory-status. Show the installed version and whether this machine has a configured factory.”

**Pass:** In each harness, the skill is discovered in a fresh session, identifies its installed version correctly, and reports missing setup without inventing configuration. Change the version, refresh the local installation, and demonstrate the new version. No live integrations are needed.

**Discuss before proceeding:** Confirm the package works and the source location is convenient. Do not spend this phase on branding or public distribution.

## Phase 2 — Setup and configuration

**Build:** `factory-setup`, a small YAML schema and validator, and templates for the runtime directory. Setup discovers existing configuration, asks only for missing choices, validates paths and read access, and preserves prior choices when rerun. It does not enable a schedule. Setup identifies the current harness and writes a capability report for it; running setup in the other harness reuses the same factory configuration without resetting runtime records. Keep harness-specific tool mappings and optional model choices out of shared workflow policy.

Start with these settings only:

| Setting | Proposed starting value |
| --- | --- |
| Factory ID | `honor` |
| Source | User-selected Slack workspace and one or more channels; save stable workspace and channel IDs |
| Jira | `ENG` |
| Repositories | Actual paths and existing project instructions, confirmed in setup |
| Intake start | Time setup completes; historical imports must be explicit |
| Active work items | One |
| Fix rounds | Two total across internal review and PR follow-up |
| External actions | Approval required for tickets, posts, pushes, and PR creation |
| Merge and deployment | Outside this trial |
| Cleanup | Preview only initially |

These are proposed defaults, not permissions Brian has already granted. Configuration records authorization; changing a YAML value does not itself grant authorization or override host restrictions.

Use one narrow local override for filesystem paths. Resolve relative paths against the configuration file, not the current shell directory. Reject unknown settings and unsupported schema versions. Never silently ignore a misspelled limit. Explain which settings are agent instructions and which are enforced by validation or tool permissions. Do not include dollar limits until usage can actually be measured.

Setup checks the Slack MCP connection, discovers accessible channels, and lets the user select one or more by name or link. Resolve selections to stable workspace and channel IDs, validate read access, and save them in YAML. No hardcoded channel names or IDs in skills. Keep a cursor per workspace/channel. Adding a channel starts its own cursor according to the configured intake policy; removing one stops intake without deleting existing work.

**Run:** “Set up a factory using my Slack MCP connection and let me choose the channels.” Rerun setup to add a second channel and remove the first.

**Pass:** The effective configuration and runtime path are visible; the second run preserves data and existing channel cursors. Missing Slack MCP access gives actionable connection instructions. An inaccessible channel cannot be accepted as ready. Selecting a different channel requires no skill or code changes. A misspelled field fails validation. An inaccessible repository is reported as unavailable rather than ready. Setup can finish partially configured, but affected roles remain blocked.

**Discuss:** Review the real YAML together, including repository choice and allowed actions.

## Phase 3 — Orchestrator and saved work

**Build:** `factory-run`. Initially it reads a synthetic work item, determines its next step, and reports that the required role is not implemented. Add only the state operations needed to save and resume that decision. Keep synthetic examples explicitly labeled.

Support a single-step invocation for demonstrations and a bounded normal invocation that advances available work until it reaches a wait, a block, or its configured invocation limit. Persist after each completed step. Do not require the agent to finish an entire ticket in one conversation.

Use atomic replacement for current-state files. A small local lock can refuse a second simultaneous invocation; stale locks require checking whether the previous run is still alive. Do not automatically declare abandoned work safe to restart based on elapsed time alone. These helpers protect local files when used; an agent with direct file access can still bypass them.

**Run:** “Run the factory once against the synthetic inbox. Stop after selecting the next step.” Stop the original invocation, then resume the same item from a fresh session in the other harness. Test Codex to Claude Code and Claude Code to Codex.

**Pass:** Both harnesses identify the same item and next step, preserving the cursor, fix count, approval scope, and pending-action records. An unavailable role is a visible block, not simulated success. A second invocation does not create another item. Demonstrate interruption after a saved transition and resumption without replaying the completed step. Corrupt state produces a repair request, not a reset that loses work.

**Discuss:** Inspect the record directly. It should be understandable without reading a transcript.

## Phase 4 — Router

**Build:** `factory-route`, first against saved source messages. It reads the full available thread, separates actionable items, finds referenced or related Jira work, and checks ownership and linked code activity. Return a disposition and evidence for each item: investigate, already underway, verify existing work, needs clarification, or no action.

A bug and a regression use the same route. A feature takes a different investigation brief. An existing Jira ticket is not proof that engineering work is underway; a Done ticket is not proof of deployment. Uncertain duplicates remain uncertain. Record a proposed ticket locally when ticket creation is not authorized.

**Run:** Route fixtures for conversation only, one bug with an existing ticket, a feature, an ambiguous duplicate, and one message containing three items. Run the same message again, then add a related message from another thread.

**Pass:** No work is created for conversation. The three-item message produces three linked items. Repeated input produces no duplicate work. Related messages can attach to an existing item. Missing Jira access is reported as an incomplete duplicate check, not “no ticket exists.”

Optionally use the earlier wg-tutor report as a manual read-only example after the fixtures pass, if that channel was selected. Its ENG-2850/2851/2852 statuses in the learning kit are historical snapshots; fetch current evidence. Do not recreate those tickets.

**Discuss:** Review the router's actual judgments before adding automatic intake.

## Phase 5 — Watcher

**Build:** `factory-watch`, invoked by the orchestrator. It reads new messages from each configured channel, saves them to the inbox, and advances its cursor only after collection is saved. The router still decides what the messages mean.

Handle pagination and overlapping reads. Deduplicate by Slack workspace, channel, and message timestamp, retain the thread root, and keep the cursor unchanged on a partial fetch. Recheck replies on tracked threads. Verify the connector's ability to discover replies to older untracked roots; if it cannot, document the exact supported lookback and add manual thread import. Do not claim complete channel coverage without that demonstration. Edits and deletions can be a documented v1 limitation.

**Run:** Read a user-selected channel once in read-only mode, run again, and import one historical thread explicitly. Demonstrate a second configured channel with an independent cursor. Use fixtures to test pagination, an interrupted fetch, and a new reply to an older thread without posting test messages to the channel.

**Pass:** Repeated reads do not duplicate items. A failed fetch does not skip messages. Historical import does not rewind the live cursor. The report states precisely which messages and replies were covered.

**Discuss:** Confirm the intake is useful and not noisy. The manual intake-and-routing loop is now usable.

## Phase 6 — Investigator

**Build:** `factory-investigate`, with bug and feature instructions. For a bug, record expected and observed behavior, reproduction steps, environment and revision, evidence, causal hypotheses, and what remains uncertain. For a feature, describe current behavior, the requested change, affected systems, likely implementation areas, and unresolved product choices.

Investigation may use temporary probes and reproduction tests in an isolated checkout. It does not implement the product change. Failed reproduction is a valid result. Keep observed facts separate from hypotheses.

**Run:** Investigate a deliberately broken local sample and a small feature request. Also run a case that cannot be reproduced with available access.

**Pass:** The bug has repeatable evidence and a defensible explanation; the feature identifies concrete code areas and product questions. The unavailable case stops honestly. No product implementation is presented as investigation. Resume from a fresh chat and explain the findings using saved artifacts.

**Discuss:** Read one investigation together. This is the first useful stopping point for trying the factory on real reports, with implementation still disabled.

## Phase 7 — Product planner

**Build:** `factory-plan`. Turn the investigation into expected behavior, scope, acceptance checks, and unresolved decisions. For a clear bug, this can be a few sentences. Features with unresolved behavior wait for Brian's answer; the agent must not invent product policy to keep moving.

**Run:** Plan the sample bug and feature. Include a feature with two plausible behaviors that require a product choice. Answer the question and resume.

**Pass:** The bug proceeds without unnecessary ceremony. The feature stops at the actual decision, saves the answer, and produces acceptance checks that distinguish the chosen behavior from the alternative. No implementation begins.

**Discuss:** Confirm whether the plan is enough for an engineer to act.

## Phase 8 — Technical design when needed

**Build:** A design step that can be skipped with a recorded reason. Use `factory-design` for changes spanning systems, interfaces, storage, or consequential tradeoffs. Cover the chosen approach, touched components, sequencing, compatibility, and verification. Avoid line-by-line coding instructions.

**Run:** Send the small bug and a cross-system feature through the decision. The former should need little or no separate design; the latter should produce one.

**Pass:** Design adds decisions absent from the product plan. A blocked architectural or API decision reaches Brian rather than being silently made. The implementation handoff contains enough context to work without the original conversation.

**Discuss:** Decide whether the separate step earned its cost in these examples.

## Phase 9 — Implementation

**Build:** `factory-implement`. Give the engineer the investigation, approved plan, necessary design, repository instructions, and explicit verification requirements. Use a dedicated code worktree and one branch owner. Resolve worktree creation through the current harness guide; the persisted checkout path must remain usable by the other harness after a deliberate handoff. Follow the repository's commands and conventions. Report plan flaws before forcing an implementation around them.

**Run:** Implement the approved sample bug and run the app or relevant service to demonstrate the changed behavior, along with appropriate automated checks. No push or PR yet.

**Pass:** Show the before-and-after behavior, diff, check results, branch, and commit if authorized. Unrelated files remain untouched. A missing environment dependency is a block, not a successful test. The factory's records survive removing or switching the implementation checkout.

**Discuss:** Inspect the actual diff and evidence, not only the engineer's summary.

## Phase 10 — Independent review and bounded fixes

**Build:** `factory-review`. Reviewers inspect the same implementation revision independently. Combine duplicate findings while retaining evidence. Have an adjudication step decide which findings require fixes, which are dismissed with reasons, and which need human judgment.

Proposed first experiment: two reviewers with complementary concerns, then one adjudicator. For genuinely disputed findings, try the small voting panel discussed with Brian. Agree on its size during this phase; do not pay for a second full team on every clean review. A reproducible serious defect must not disappear solely because it lost a majority vote.

Approved experiment addendum (2026-11-05): Brian selected three fresh independent
panelists for unresolved disputes only. The two initial reviewers and separate
adjudicator are actual independent fresh agents, not orchestrator personas. Keep
raw reports and exact target fingerprints durable, with the orchestrator as sole
canonical state writer. Dirty accepted implementations retain base/HEAD plus full
diff/file hashes and leave reviewed_commit unset. A narrowly explicit focused
synthetic review fixture may import raw evaluation inputs at review with absent
upstream history clearly labeled; it must not fabricate role completion/verdicts.

Use one shared allowance of two fix rounds for the item, including later PR follow-up. A round means an engineer receives a batch of accepted findings, changes the implementation, and returns it for verification. The initial implementation and initial review do not consume a fix round. Changing the commit invalidates verdicts for affected code; record which revision was reviewed.

**Run:** Review a sample with a seeded defect, an unsupported finding, and a disputed finding. Apply a correction and review again. Separately exercise the exhausted-round case.

**Pass:** Supported findings reach the engineer; dismissed findings have reasons. The corrected revision is checked. After two unsuccessful fix rounds, the orchestrator asks Brian for help with remaining issues and attempted fixes. It does not reset the counter or open a PR as if review passed.

**Discuss:** Compare reviewer value and adjudication cost. Keep the smallest arrangement that catches useful issues.

## Phase 11 — PR creation and follow-up

**Build:** `factory-follow-pr`. Once review passes, prepare a draft PR and create it only with the applicable authorization. Record its URL and head revision. On subsequent invocations, read CI and review activity, investigate failures, and send actionable findings to the engineer. Reuse the same fix-round count.

Before retrying an uncertain PR creation or push, inspect remote state. Do not assume a timed-out write failed. Reuse an existing PR for the branch. Treat PR open, CI passed, ready for human review, merged, deployed, and verified as distinct facts. Merge and deployment remain outside the trial.

**Run:** First use saved PR/CI fixtures. Then use a specifically approved test PR to demonstrate live follow-up, including one failing check and one review comment.

**Pass:** The factory distinguishes an actionable failure from an unrelated or flaky check, explains its disposition, and verifies any fix against the new revision. No duplicate PR is created. An exhausted allowance escalates rather than starting another review loop. Nothing auto-merges.

**Discuss:** Confirm how much PR ownership Brian wants during the trial.

## Phase 12 — Reporter

**Build:** `factory-report`. Produce Slack updates for the originating thread and Jira updates from recorded results and refreshed live status. Default to local drafts. Include the result, evidence or PR link, and any decision needed; omit internal agent chatter.

Track each proposed update and, after sending, its external ID. Before retrying an uncertain send, read the destination and reconcile. If the result remains ambiguous, ask for help rather than blindly posting again. A local ledger improves retries but does not guarantee exactly-once delivery.

**Run:** Draft updates for investigation blocked, PR ready, and merged-but-not-verified. Run again with no change. After approval, send one concrete update and verify its destination.

**Pass:** Wording matches actual status. A PR is not reported as a shipped fix. No unchanged duplicate update is proposed. No Slack or Jira write happens without the applicable authorization. Jira transitions use the project's real workflow, not invented status names.

**Discuss:** Review the wording and frequency. Decide whether to grant standing permission for narrowly defined updates during the trial.

## Phase 13 — Scheduled operation

**Build:** One recurring task that invokes the same tested orchestrator with an explicit configuration path. It checks intake and existing work, advances what it can, and saves a short result. Inspect existing automations first. Use a documented scheduling option for the selected harness rather than installing cron or a daemon. Keep the scheduled prompt limited to invoking the shared orchestrator with its configuration path. Demonstrate scheduling in each harness separately; enable only one schedule against the real workspace.

Verify the scheduled environment can load the plugin, read the persistent workspace and repositories, access connected tools, and invoke the required workers. For Codex desktop, local tasks require the machine and app to remain running. [OpenAI scheduled task documentation](https://learn.chatgpt.com/docs/automations). Claude Code distinguishes session-based loops from persistent desktop schedules; choose and test the available local option, documenting session requirements, expiry, and restart behavior. A short-lived loop alone is not proof of an unattended two-week schedule. [Claude Code scheduling documentation](https://code.claude.com/docs/en/scheduled-tasks).

**Run:** First complete one manual end-to-end sample. Then, after Brian approves activation and cadence, observe a scheduled read-only invocation. Exercise a missing connection, a second overlapping invocation, and resumption after a stopped run. Use a shorter temporary cadence for the demonstration if approved.

**Pass:** In both harnesses, the scheduled run uses saved state rather than relying on the original chat. Pause the first harness's schedule before switching to the second, verify no active invocation remains, and show that the second resumes the same records. It does not duplicate active work or reset cursors after a failure. Notification behavior matches Brian's preference: meaningful progress, completion, failure, or required action; quiet when nothing changed. Show how to pause it and confirm that no new work starts after pausing.

**Discuss:** Start the recurring trial only after this demonstration. If unattended permissions prevent progress, report the precise blocker; do not broaden permissions automatically.

## Phase 14 — Retro

**Build:** `factory-retro`. Read completed or blocked work and produce a short account of where the process helped, failed, or needed Brian. Propose a specific instruction, configuration, or test change with supporting evidence. Do not automatically rewrite skills or config.

**Run:** Review one successful run and one failed run together. Routine successes need only a short record; spend more attention on repeated mistakes and expensive detours.

**Pass:** Findings cite actual decisions and outcomes. The proposed improvement addresses an observed problem and has a way to test it. Human waiting time is distinguished from agent work; unavailable token or cost data is marked unavailable rather than estimated as fact.

**Discuss:** Choose one improvement to try, then compare subsequent runs.

## Phase 15 — Cleanup

**Build:** `factory-maintain`, initially producing a cleanup preview. Classify factory-owned worktrees, temporary evidence, stopped processes, and completed records. Archive completed records separately from deleting disposable files. Never infer ownership from a path name alone; use the factory's recorded resources.

Keep decisions, source links, reviews, and final evidence throughout the trial. Preserve dirty worktrees, unmerged branches, active runs, and anything waiting on a human. A merged PR alone does not make an item complete. Do not delete external tickets, comments, or branches as housekeeping.

**Run:** Preview cleanup against a disposable fixture containing a completed clean checkout, a dirty checkout, an active item, and a blocked item. After Brian approves the concrete deletion list, remove only the eligible disposable resources. Run the preview again.

**Pass:** Active, blocked, dirty, and unrelated resources survive. The completed work record remains readable after cleanup, and archived records can be located and restored. Cleanup is repeatable and explains why each resource is retained or removable. No deletion runs on a schedule without explicit authorization.

**Discuss:** Set retention from what actually accumulated during the trial.

## The one or two week trial

Start learning before all phases are done. After phase 6, manually process real reports through investigation and inspect the results. After phase 13, begin the recurring trial with one user-selected channel and one active item; this is a trial starting point, not a plugin restriction. Complete retro and cleanup during that trial; neither needs to delay the first useful run.

For the first few days, require Brian's approval before implementing each selected item and keep external updates as drafts. Once a few items have gone through cleanly, discuss expanding autonomy for a narrowly defined class of work. Do not interpret a calendar milestone as permission.

Track only what will inform a decision: items processed, incorrect routing, duplicate work, investigations that changed understanding, review findings accepted, fix rounds, human interventions, elapsed time by stage, and actual usage when exposed. A short Markdown table is enough.

At the end, decide what to keep, remove, or enforce more strongly. Success means Brian can inspect a run, understand why it took each step, resume it from a fresh chat, and identify where it saved work or created more. It does not require every report to become an autonomous PR.

## References for the implementing agent

This plan governs behavior. Pstack is inspiration, not a dependency or instructions to follow. Consult only the reference relevant to the phase being built; do not import its full workflow, permissions, or Cursor-specific assumptions. Links are pinned to the version inspected for this discussion.

- [setup-pstack](https://github.com/cursor/plugins/blob/bb68f2365eceafa0cb2d253112f675acf5f144cc/pstack/skills/setup-pstack/SKILL.md): borrow the pattern of reading existing choices, validating available capabilities, and making setup safe to rerun. Its output is model-selection instructions, not the broader factory YAML designed here.
- [Orchestrate playbook](https://github.com/cursor/plugins/blob/bb68f2365eceafa0cb2d253112f675acf5f144cc/pstack/skills/poteto-mode/playbooks/orchestrate.md): borrow clear ownership, independent verification, and inspection of actual artifacts. Its scale, dispatch tools, and merge permissions are not requirements for this trial.
- [Benny operating instructions](https://github.com/cursor/plugins/blob/bb68f2365eceafa0cb2d253112f675acf5f144cc/pstack/automations/benny/FOR_AGENTS.md): reference Slack intake, duplicate detection, reproduction before fixing, and reporting to the source thread. Keep our user-selected channels, shared work records, and cross-harness requirement.
- [Worktree cleanup playbook](https://github.com/cursor/plugins/blob/bb68f2365eceafa0cb2d253112f675acf5f144cc/pstack/skills/poteto-mode/playbooks/worktree-cleanup.md): borrow evidence-based decisions about what can be removed, especially checks for uncommitted work and active ownership. Our cleanup approval and retention rules still apply.

Do not add the full pstack skill catalog or a poteto-mode equivalent. Attribute copied source and preserve its license where applicable; borrowing a design idea does not require installing pstack.

## Starting instructions for the implementing agent

Read this plan and the applicable repository instructions. Confirm which phase Brian has approved. Begin with phase 1 only unless he directs otherwise. Use the existing learning kit as reference material, not as installed production code. Its replay program is a teaching example, not the orchestrator.

Do not copy pstack wholesale or inherit its external-action permissions. Reuse specific ideas deliberately, retaining attribution and license obligations if copying source. Keep the skill instructions short and put detailed reference material next to the skill that needs it.

The first handoff back to Brian should be an installed, callable scaffold in both Codex and Claude Code with demonstrated refresh behavior. Do not defer Claude Code support to the end or maintain separate copies of the role instructions. Bring later decisions to the phase where they matter.
