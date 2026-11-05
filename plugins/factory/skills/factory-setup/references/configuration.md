# Configuration and helper contract

One shared schema and helper serve both hosts. Resolve the plugin root from the
loaded skill. Invoke `uv run --isolated --frozen --no-dev --project <plugin-root> python
<plugin-root>/scripts/factory_config.py <command> --config <path>`; uv isolates
PyYAML for this project. First use may populate uv's isolated dependency cache
outside the package;
this is separate from factory records. Status/validate/discover do not write
factory records. To warm the dependency cache separately, use the same isolated
command with `python -c 'pass'` instead of the helper. If dependencies cannot be
installed, report the blocker;
never borrow another repository environment or install globally. The embedded
schema below is available in installed packages; do not locate an
authoring checkout to create a configuration.

Commands: `validate` prints effective configuration without writing. `discover`
reads only configured repository roots/paths without writing. `status --harness
codex|claude-code` reads current matching evidence. `setup --harness ... --evidence
<json>` writes setup metadata and establishes an intake start after selected
Slack access is observed. Each command accepts optional `--local <yaml>`. Setup
records an adjacent
`.<config-name>.factory-setup.json` association to remember the selected runtime.
A changed runtime requires explicit user choice and `--confirm-runtime-change`;
this never migrates records. Keep the association with the private configuration.
For a new factory, ask for one home (suggest `~/factories/<factory-id>`) and derive
`<home>/config.yaml` with `runtime_path: ./runtime`. Show both resolved paths before
writing. A selected home establishes both paths; existing or explicitly separate
paths remain valid and are never silently relocated. The config path remains the
explicit invocation identity; there is no home flag, schema field, or registry.
Errors return exit 2 with JSON; partial setup returns exit 0 with explicit blocks.

Schema version 1 requires exactly these fields (no unknown or missing keys):

```yaml
schema_version: 1
factory_id: example
runtime_path: ./runtime
slack:
  workspace_id: null
  channels: [] # once resolved: [{id: CHANNEL_ID, name: selected-channel}]
jira:
  project_key: EXAMPLE
repositories:
  roots: [~/projects/example-org]
  paths: []
intake:
  start_at: null
limits:
  active_work_items: 1
  fix_rounds: 2
actions:
  tickets: approval_required
  posts: approval_required
  pushes: approval_required
  pull_requests: approval_required
  merge: disabled
  deployment: disabled
  cleanup: preview_only
```

Create this YAML at the selected home's `config.yaml` before invoking the helper;
`./runtime` resolves beside that file. If using the authoring checkout's
`config/example.yaml`, copy it into the selected home first. Validating that source
file in place correctly rejects its runtime inside the authoring tree.

Keep real YAML and runtime outside plugin source and disposable worktrees. No
credentials belong in YAML. Factory ID uses lowercase letters, digits and hyphens.
Slack names are labels; IDs are authoritative. `start_at` is system-managed: initially null, then a quoted timezone-qualified ISO
string written by verified setup. Editing or resetting an established start is
rejected using the adjacent config association. Historical intake is not
implemented in this tranche. New channels
always get their own current setup start; historical channel imports need future
explicit import support. Existing starts survive removal/readdition and reruns.
This phase stores starts, not watcher cursors, and never rewrites existing cursors.

All paths expand `~`; relative paths resolve against their containing YAML file,
including an override file in a different directory. A local override may contain
only `runtime_path` and/or `repositories` with `roots` and/or `paths`; lists replace
the corresponding list. Other settings require editing the main config. Explicit
repository paths must resolve inside a configured root, including through symlinks.
Discovery does not follow directory symlinks or descend into found Git checkouts;
select a narrower root when appropriate. It lists repositories, not source code.
Missing/unreadable locations remain configured and are reported unavailable.

Evidence JSON has exactly `harness` and `capabilities`. Harness is `codex` or
`claude-code`. Capabilities must contain each key below plus one
`slack_channel:<id>` per currently selected channel:

- `slack_connection`, `slack_channels`, `slack_pagination`, `slack_thread_replies`
- `slack_write`, `jira_read`, `jira_write`, `github_read`, `github_write`
- `local_execution`

Each value is `{"status":"observed|unavailable|not_checked","evidence":"specific
short observation and its limits"}`. Use one actual status string, not the joined
example. `observed` for a write key means its tool is exposed; evidence must say
whether actual authorization was checked and that no write was executed. A report
records observations supplied by the agent; validation cannot independently prove
connector results or grant tool permission. Preserve unavailable checks explicitly.

Minimum evidence for `observed`:

| Capability | Required observation |
| --- | --- |
| `slack_connection` | A successful authenticated Slack read in this harness for the selected channel/workspace. Initial setup must resolve or obtain the user-selected stable workspace ID. On a handoff, reuse the established ID and verify channel access independently; distinguish reused identity from fresh identity discovery. A configured ID or exposed tool alone is insufficient. |
| `slack_channels` | An actual accessible-channel discovery result resolving selected channel names/links to stable IDs. State the discovery coverage. |
| `slack_channel:<id>` | A successful actual read of that selected stable channel ID in this harness; record the selected workspace mapping and its source. |
| `slack_pagination` | An actual read following a continuation cursor or requesting a subsequent page. Tool exposure alone is insufficient; record the tested operation and coverage. |
| `slack_thread_replies` | An actual thread/replies retrieval, stating whether replies were returned. |
| `jira_read` | A successful actual read of the configured Jira project. Optional site-wide or issue-specific probes are not required; record any limits without implying broader access. |
| `github_read` | A successful actual repository read for a selected target, stating which repository was checked; discovery of local folders alone is insufficient. |
| `local_execution` | A successful actual local helper command in this harness. |
| `slack_write`, `jira_write`, `github_write` | Exposed relevant write tools/commands. State tool exposure only, whether authorization was checked, and that no write was executed. |

A required probe denied by the host or test runner remains `not_checked` when its
result could not be established; use `unavailable` for an observed missing or
inaccessible capability. Do not mark it `observed` merely because another probe
succeeded or prose mentions the denial. Optional probe limitations do not change
a capability whose minimum evidence was actually obtained.

Final readiness must agree with the helper's `setup_status` and `blocked` output.
When observations do not meet these minima, fix the evidence and rerun `setup`;
report the resulting partial status instead of contradicting a ready JSON report.
Ready setup still does not prove write execution, grant approval, or implement
workflow roles.

Setup writes `runtime/setup/<factory_id>/<harness>-<effective-config-hash>.json`,
including `checked_at`, effective non-secret values and their hash. Config changes
retain older reports; another host cannot inherit current-host readiness. Status
uses only the matching hash; observations are historical evidence, not a current
connection guarantee. Recheck integrations before later actions. Minimal
`channel-starts.json` in that same directory retains workspace/channel starts.
Other runtime files/directories are created only by future implemented work.

Unknown settings/schema versions and root escapes are validation errors. Missing
connections/repos are readiness blocks. The fixed limits/actions validate this
trial's supported choices; their enforcement during work is an agent instruction,
not a deterministic execution engine. YAML never overrides host restrictions or
grants external-action approval. Setup readiness also does not mean workflow roles
exist: this tranche implements setup and status only.

Runtime must be outside the loaded plugin/authoring source and all configured or
discovered target repositories. Validation rejects a disposable or source-tree
runtime location before creating any records.
