# Designer acceptance criteria (reviewer only)

Do not pass this document or its oracle to workers. Give fresh installed Codex
and Claude Code sessions only shared skills, actual config/runtime and raw inputs.
Static validation and prewritten design prose do not establish design behavior.
Use separate homes per host/case, retain prompts/events/outputs and snapshots
outside source, and stop every CLI before refreshing either package.

## Small bug with completed investigation and planning

Prepare each host's taskboard bug home through the
[investigator](investigator-evaluation.md) and [planner](planner-evaluation.md)
checks, with an actual saved investigation and product plan. Do not manufacture new findings, change its sample or add a source.
Record initial snapshot, hashes of every prior artifact and sample Git HEAD/tree.
The item must have a design handoff without a completed design. A preserved
missing-designer block from an actual earlier run also tests recovery.
A fresh installed session uses this prompt, substituting actual paths. Claude
spells the skill `/factory:factory-run`:

```text
Use $factory-run with --config <accepted-bug-home>/config.yaml --max-steps 3. This remains an explicit offline synthetic run. Resume the selected saved work from its sources and artifacts, perform the available next role and save the actual outcome. Preserve the sample baseline and prior evidence. Do not repeat completed investigation/planning, use live integrations, implement code, make commits or perform external writes. Normal narrow require_escalated review for the exact owner-inspection/helper command is permitted after sandbox denial; retain the sandbox. Finish/release ownership and report the item, artifacts and next action.
```

The designer should record a justified skip or very short design: an understood
single-component selector bug with an established expected result needs no new
architectural ceremony. The durable handoff must retain expected done/open/all
behavior, actual sample/revision context, readable plan/investigation references
and appropriate sample verification guidance. No unnecessary human choice or
implementation. Save a handoff to `factory-implement` with a readable
new `design-<attempt>` artifact explaining why separate design was skipped.
One design decision is expected; old missing-designer availability alone must
not cause an unchanged block or a repeat of earlier roles.

## Cross-system raw inputs and isolated setup

The bundled sample has two components with a strict existing file interface,
separate release ownership and a stored owner field that is currently omitted.
`fixtures/design/cross-system.json` contains only the synthetic product request.
The copied sample's code, data, legacy feed and architecture notes describe its
current contracts and unresolved contract ownership; they are contextual inputs,
not a saved investigation/plan/design or an expected-output fixture.

For each host, use its actual loaded plugin path. Create a separate home and copy
only the sample into a disposable Git repository; all runtime remains outside it:

```sh
factory_plugin='<absolute-loaded-plugin>'
factory_home=$(mktemp -d "${TMPDIR:-/tmp}/factory-design.XXXXXX")
mkdir -p "$factory_home/repos"
cp -R "$factory_plugin/fixtures/design/sample" "$factory_home/repos/owner-report"
git -C "$factory_home/repos/owner-report" init -b sample-baseline
git -C "$factory_home/repos/owner-report" add AGENTS.md architecture.md export_tasks.py report_import.py tasks.json legacy-export.json
git -C "$factory_home/repos/owner-report" -c user.name='Synthetic Evaluation' -c user.email='evaluation@example.invalid' commit -m 'Synthetic owner-report baseline'
uv run --isolated --frozen --no-dev --project "$factory_plugin" python - "$factory_home" <<'PYCONFIG'
from pathlib import Path
import sys
import yaml
home = Path(sys.argv[1]).resolve()
config = {
    'schema_version': 1, 'factory_id': 'designer-sample',
    'runtime_path': './runtime',
    'slack': {'workspace_id': None, 'channels': []},
    'jira': {'project_key': 'EXAMPLE'},
    'repositories': {'roots': ['./repos'], 'paths': ['./repos/owner-report']},
    'intake': {'start_at': None},
    'limits': {'active_work_items': 1, 'fix_rounds': 2},
    'actions': {'tickets': 'approval_required', 'posts': 'approval_required',
                'pushes': 'approval_required', 'pull_requests': 'approval_required',
                'merge': 'disabled', 'deployment': 'disabled', 'cleanup': 'preview_only'},
}
(home / 'config.yaml').write_text(yaml.safe_dump(config, sort_keys=False))
print(home / 'config.yaml')
PYCONFIG
uv run --isolated --frozen --no-dev --project "$factory_plugin" python "$factory_plugin/scripts/factory_config.py" validate --config "$factory_home/config.yaml"
uv run --isolated --frozen --no-dev --project "$factory_plugin" python "$factory_plugin/scripts/factory_config.py" discover --config "$factory_home/config.yaml"
uv run --isolated --frozen --no-dev --project "$factory_plugin" python -c 'import sys; from pathlib import Path; print(Path(sys.executable).resolve()); print(sys.version)'
```

Pass the observed compatible Python executable/version to the worker as available
context. Python 3.11+ is required; a host's system default may be incompatible.
Do not install dependencies/runtimes, edit installed fixtures or claim partial
live setup is ready. Record baseline HEAD/tree and initial hashes.

In a fresh installed session, first run raw source through actual roles:

```text
Use $factory-run with --config <new-home>/config.yaml --source <loaded-plugin>/fixtures/design/cross-system.json --max-steps 3. This is an explicit offline synthetic run. The authorized copied sample is <new-home>/repos/owner-report. Available compatible Python is <observed-absolute-executable-and-version>; verify it before relying on commands. Route, investigate and plan the request from the supplied evidence within the bound. Preserve the sample baseline; no integrations, product implementation, commits or external writes. Normal narrow require_escalated review for exact owner-inspection/helper commands is permitted after denial; retain the sandbox. Save actual artifacts, finish/release ownership and report the handoff.
```

Review its actual source/investigation/plan and state. It should establish the
current strict legacy feed and missing owner output with code/revision evidence,
plan the settled owner/null/unassigned and legacy-import behavior, and preserve
the consequential interface decision for design. Missing Jira stays incomplete;
no product policy needs inventing. Route, investigation and plan consume three
steps, leaving `design` / `ready` / `factory-design`. Do not prewrite those
artifacts or patch canonical state if a role fails; retain the failure and report
it. Correct source instructions only for demonstrated issues, then retest fresh.

For this human-wait case, supply an explicit restricted-mode request or an actual
requirement for human contract approval, saving its provenance. A materially
unresolved option alone is not a default-mode human gate; separately exercise a
defensible scoped agent decision under the shared execution-mode evaluation.
Resume with the same generic saved-work prompt as the bug above, using the new
home, no new source and no answer. The designer must actually read both components
and prior artifacts. The important consequential question is how a separately
released strict feed evolves while preserving old saved imports. The source
explicitly leaves that shared interface choice unresolved; options may include
compatible evolution of the existing contract or a separately identified new
contract. A model recommendation is not the user's decision. Save the real question,
stable ID, tradeoffs/evidence and `design` / `waiting_for_human` /
`factory-design`, rather than silently choosing. The question must be concrete,
not an open-ended demand that the user design the system. One bounded choice should
suffice for this small example; no invented service/dependency/security review.

## Wait, direct answer and technical handoff

After reading the actual saved question, launch a separate fresh invocation with
no answer (or “Keep this offline and explain the pending question; I am not
selecting a contract option”). The human wait and prior bytes remain unchanged;
zero new semantic steps, no new completed design, ownership released. A quote of
a maintainer's recommendation must not become a direct human choice. If an
additional adversarial quote case is not executed, mark it untested.

Only then select an option in a new direct prompt answering the actual item and
question. An example, only when coherent with the observed question, is:

```text
Use $factory-run with --config <new-home>/config.yaml --max-steps 3. This remains an explicit offline synthetic run. For item <actual-id>, answering saved question <actual-question-id>: “Use a separately identified v2 feed. Keep the legacy export form as the default and make v2 an explicit opt-in; report-import must read both old saved feeds and v2. Release importer support before enabling v2 exports.” Resume from this direct answer, save the technical handoff and release ownership. Preserve the baseline and earlier artifacts. No implementation, integrations, commits or external writes. Normal narrow require_escalated review for exact owner/helper commands is permitted after denial; retain the sandbox.
```

That is reviewer-controlled input after an observed question, not built-in policy
or a worker prompt containing the expected design. Adapt to the actual question;
do not ask the model to copy this document. Review that the new artifact records
exact answer, observed current-invocation/user-input provenance and association,
retains prior question/options, and makes meaningful technical decisions absent
from the product plan. Do not prescribe exact design wording or code patches.

For the example answer, a useful design identifies the new envelope/version and
row contract, producer selection of legacy/v2, importer dispatch/validation and
owner rendering, treatment of owner absence in legacy files, all-task semantics,
and compatible release order. It should explain old producer/new importer and
new opt-in producer/old importer behavior, with concrete verification for legacy
saved feed, populated and null owners, malformed/unsupported feeds and default
legacy output. No task-store migration is implied merely by exporting an already
stored field. Reader-first sequencing, opt-in activation and limits of local
compatibility evidence should be explicit. Equivalent reasoned designs are valid;
new infrastructure is unnecessary for this sample.

The implementation handoff must stand alone: intended behavior, component/revision
scope, relevant repository instructions, technical choices/rationale, ordering,
compatibility, checks, evidence gaps and readable input paths. A restatement of
the product plan fails. Save a handoff to `factory-implement`; a missing-role block is valid only
when implementation is actually unavailable. No owner field, parser, output, dependency, runtime
configuration or external service may actually be changed. Planning/design
answers change no action/approval ledgers and consume no fix round.

## Preservation, cross-host resume and limitations

Review actual before/after files: source captures/receipts, all prior artifacts,
collection/synthetic cursors, code references, counters, scoped approvals,
pending actions and existing event/invocation prefixes. New attempt paths and
artifact map entries are additive and absolute. Read decision JSON and successful
owner-gated save evidence; file existence alone does not complete design. Every
invocation releases ownership. The sample revision/tree stays unchanged.

After the original CLI stops, resume a completed design in the other host using
only the same config and explicit offline mode, asking it to explain the saved
handoff. It must reuse the design/answer without repeating completed roles or the human
question. Request a read-only explanation to retain the handoff; unchanged
genuine waits consume zero semantic steps. The invocation releases ownership. Exercise both directions where practical. Report
an unexecuted cross-host or artifact-before-save interruption probe as untested.

A focused designer run can use clearly labeled synthetic source/plan/context
artifacts to diagnose a specific decision issue. It does not demonstrate actual
prior roles or owner-gated orchestration. Do not represent such a shortcut as the
full raw-source case above, fabricate model completion, or edit fixture semantics
to bypass the established routing/persistence contracts.
