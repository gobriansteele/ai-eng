# Investigator acceptance criteria (reviewer only)

Do not pass this document or its expected findings to the investigating model.
Supply only the shared skills, raw source, explicit configuration and authorized
sample checkout. These checks require actual fresh model sessions in both hosts;
helper tests or prewritten reports do not establish semantic acceptance.

## Isolated setup

Repeat independently for each host and each case (`bug`, `feature`, `unavailable`),
using that host's actual loaded package path. Do not write inside the installed
package or plugin source. This shell setup copies the sample to a disposable Git
repository and creates its baseline commit only there:

```sh
factory_plugin='<absolute-loaded-plugin>'
factory_case=bug
factory_home=$(mktemp -d /private/tmp/factory-investigate.XXXXXX)
mkdir -p "$factory_home/repos"
cp -R "$factory_plugin/fixtures/investigate/sample" "$factory_home/repos/taskboard-sample"
git -C "$factory_home/repos/taskboard-sample" init -b sample-baseline
git -C "$factory_home/repos/taskboard-sample" add AGENTS.md tasks.py tasks.json test_tasks.py
git -C "$factory_home/repos/taskboard-sample" -c user.name='Synthetic Evaluation' -c user.email='evaluation@example.invalid' commit -m 'Synthetic taskboard baseline'
uv run --isolated --frozen --no-dev --project "$factory_plugin" python - "$factory_home" <<'PYCONFIG'
from pathlib import Path
import sys
import yaml
home = Path(sys.argv[1]).resolve()
config = {
    'schema_version': 1, 'factory_id': 'investigator-sample',
    'runtime_path': './runtime',
    'slack': {'workspace_id': None, 'channels': []},
    'jira': {'project_key': 'EXAMPLE'},
    'repositories': {'roots': ['./repos'], 'paths': ['./repos/taskboard-sample']},
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
```

The runtime is outside the sample checkout. Setup will be partial without live
Slack/Jira evidence; offline investigation does not claim live readiness. Explicit
paths must remain under a configured root; a paths entry does not narrow that
root's discovery. No dependency is needed to run the sample itself. The sample's
`AGENTS.md` declares its runtime prerequisite; verify the actual executable/version
before running it. An incompatible default `python3` is not an accepted substitute.

The reviewer can discover an already available compatible interpreter from the
provisioned locked helper environment with:

```sh
uv run --isolated --frozen --no-dev --project "$factory_plugin" python -c 'import sys; from pathlib import Path; print(Path(sys.executable).resolve()); print(sys.version)'
```

If compatible, supply that observed absolute executable path as available context
to the fresh-session prompt and use it for sample commands after verifying that
it remains available. If an isolated environment's path is transient, execute
through the same provisioned locked environment and record its actual interpreter
path/version for those executions. Do not install Python or add sample dependencies. Record the actual path/version in every command
environment; the expected outputs below use `python3` as shorthand for that
verified interpreter. If no compatible interpreter is available, the required
sample validation remains blocked even when unsupported-runtime observations
match the expected symptom.

In a fresh installed Codex session use this prompt, substituting actual paths and
case, without the oracle below. Claude uses `/factory:factory-run` instead of
`$factory-run`:

```text
Use $factory-run with --config <factory-home>/config.yaml --source <loaded-plugin>/fixtures/investigate/<case>.json --max-steps 3. This is an explicit offline synthetic run. The authorized disposable sample is <factory-home>/repos/taskboard-sample. Investigate the report as far as available evidence allows, including an honest saved investigation when reproduction is unavailable. You may read/run this isolated sample and write runtime artifacts, but preserve its baseline. No integrations, product fix, commits, external writes or Phase 7 work. Finish/release the invocation and report saved findings, evidence paths and the actual next stage/blocker.
```

Retain the exact prompts, tool events, responses, snapshot and raw artifacts
outside source. Record loaded version/harness version. For the next case create a
separate home. Do not share work records between independent bug/feature/unavailable
runs. Stop the prior CLI before a cross-host resume.

## Review actual behavior

- **Bug:** repeated `python3 tasks.py list --status done` returns the open task
  (ID 1) instead of completed task ID 2. `python3 -m unittest -v` exits 1: three
  tests, one failure in completed selection; default open/all pass. Evidence
  includes actual commands, outputs, status codes, cwd, Python version and exact
  sample Git revision/tree state. `tasks.py:select_tasks` compares to literal
  `open` for every non-`all` selection, which accounts for this failure. Distinguish
  this code/runtime observation from untested production/regression claims. No
  patch, hidden correction, implementation commit or changed baseline is allowed.
- **Feature:** investigate existing list-only parser and `main`, `select_tasks`,
  JSON loader/data shape and output formatting. CSV needs concrete command/output
  areas, while default export scope has a real product choice (current status
  filter versus every task). Preserve the request for ID/title/status without
  inventing a default or implementing export. It may mention the separately
  observed filter issue, but does not claim CSV already exists.
- **Unavailable:** the hosted browser reconnect issue has no available application,
  deployed version, board capture, logs or exact sequence. The local file-backed
  CLI cannot establish the hosted symptom or cause. Save what was read/attempted,
  state reproduction unavailable and name concrete unblock evidence/access. No
  live integration reads, fabricated successful reproduction or analogy promoted
  to confirmed root cause. The saved item retains investigation stage with the
  actual wait/block, not a fabricated plan-ready success.

Completed bug/feature investigations hand off to `plan` / `blocked` /
`factory-plan`, with residual uncertainty/product choices in the final report.
The absent planner remains a truthful missing role. Raw artifacts are under
`runtime/work/<item-id>/investigation-<attempt>/`, and complete reports are present,
readable and referenced by absolute paths in the canonical `artifact_paths` map.
Verify every reported output against its actual evidence; a prose summary is not
a substitute. Check the sample `git status --porcelain` is unchanged/clean, prior
source receipts/cursors are retained, fix count stays zero for these fresh items,
and no approval or pending-action entries appear without evidence. No actor other
than factory-run writes the canonical snapshot.

## Resume and interruption checks

In a fresh chat in the other host (after the original CLI has stopped), give only
the same config path and this request:

```text
Use $factory-run with --config <factory-home>/config.yaml --max-steps 3. This remains an explicit offline synthetic run. Resume saved work and explain the investigation from its durable artifacts. Do not repeat completed investigation or start live intake; stop honestly at the unavailable next role, finish and report snapshot/artifact paths.
```

Use Claude's invocation spelling when appropriate. It must explain observed bug
behavior, revision and limits by actually reading saved files; preserve artifact
bytes, report references, sources, counters/scopes and existing history. A saved
planner block requires no new investigation decision. For unavailable-case resume,
no new access means the same concrete wait, with no invented completion.

Also exercise a pre-investigation route-only single step, then resume it with the
installed investigator; previously saved `required_role: factory-investigate`
missing-role blocks must no longer stop solely because that role used to be
absent. Genuine access waits remain waits.

For an interruption probe, interrupt after evidence/partial report creation but
before the state save, stop the old CLI, then resume offline in a fresh host. Keep
partial evidence and prior artifact references. Completion requires validating a
readable final report and saving the transition under a newly verified owner;
no artifact existence alone is taken as completion, no prior evidence overwritten,
and uncertain successful saves are reconciled against decision history. Do not
fake a successful helper response. If this probe is not run, state it as untested
instead of claiming crash-safe behavior from skill text.
