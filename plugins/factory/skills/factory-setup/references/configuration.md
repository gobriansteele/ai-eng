# Configuration and helper contract

One shared schema and helper serve both hosts. Resolve the plugin root from the
loaded skill. Invoke `uv run --isolated --frozen --no-dev --project <plugin-root> python
<plugin-root>/scripts/factory_config.py <command> [--config <path>]`; uv isolates
PyYAML for this project. When host permissions allow prefix-scoped commands, run
each helper as a separate literal `uv` call with actual paths and values, without
wrappers, shell assignments, substitutions or command chains. A denial of such a
wrapper is scoped to that command and does not establish that the separately
allowed literal helper is denied; try its permitted form before reporting it
unavailable. Respect any underlying access/action denial and retain the host's
normal permissions.

First use may populate uv's isolated dependency cache
outside the package;
this is separate from factory records. Status/validate/discover do not write
factory records. To warm the dependency cache separately, use the same isolated
command with `python -c 'pass'` instead of the helper. If dependencies cannot be
installed, report the blocker;
never borrow another repository environment or install globally. The embedded
schema below is available in installed packages; do not locate an
authoring checkout to create a configuration.

Commands: `validate` prints effective configuration without writing. `discover`
reads only configured repository roots/paths without writing. Its `repositories`
result includes discovered repositories under effective `repositories.roots` plus
explicit `repositories.paths`; paths does not narrow roots. With user authorization
for a root, discovered repositories within it remain in scope even when absent
from paths. A bounded role search can leave them unsearched; that is not evidence
that they are unconfigured or unauthorized. `status --harness
codex|claude-code` reads current matching evidence. `setup --harness ... --evidence
<evidence-file.json>` writes setup metadata and establishes an intake start after selected
Slack access is observed. Each command accepts optional `--local <yaml>`. Setup
records an adjacent
`.<config-name>.factory-setup.json` association to remember the selected runtime.
A changed runtime requires explicit user choice and `--confirm-runtime-change`;
this never migrates records. Keep the association with the private configuration.
For a new factory, propose `~/factories/default` and let the user change the home;
derive `<home>/config.yaml` with `runtime_path: ./runtime`. Show both resolved paths
before writing. A selected home establishes both paths; existing or explicitly
separate paths remain valid and are never silently relocated. There is no home
schema field. Errors return exit 2 with JSON; partial setup returns exit 0 with
explicit blocks.

Slack collection is optional. With no selected channels, direct chat intake works
with `slack.workspace_id: null`, `slack.channels: []` and `intake.start_at: null`.
Slack capabilities remain honestly recorded but do not affect readiness in that
configuration. When channels are selected, collection needs their usual access
and preserved starts. A partial setup blocks only the work needing each missing
capability, not unrelated direct intake.

## Default resolution and pinning

Every top-level user-facing skill resolves once before accessing factory state:

```text
uv run --isolated --frozen --no-dev --project <plugin-root> python <plugin-root>/scripts/factory_config.py resolve-config [--config <user-path>] [--local <user-local>] [--registry <registry-path>]
```

`resolve-config` is read-only. It returns absolute `config_path`, `runtime_path`,
nullable absolute `local_path`, `factory_id`, and `source` (`explicit`, `registry`,
or `conventional`). Resolve in this order:

1. An explicit user config wins for this invocation. It does not change the
   registry or inherit another factory's remembered local override.
2. Otherwise use the registry's default config and remembered local override.
   An explicit `--local` overrides the remembered local for this invocation.
3. Only when the registry is absent, try `~/factories/default/config.yaml`.
4. If neither exists, report setup needed and enter or suggest factory-setup.

The shared registry lives at `$XDG_CONFIG_HOME/ai-eng/registry.json` when that
variable is set, otherwise `~/.config/ai-eng/registry.json`; `--registry` is an
explicit test or location override. It remains outside the package and is shared
by both hosts. If a caller supplies `--registry`, retain its absolute path for
this setup flow and pass the same override to `setup` writes as to resolution;
a temporary/test registry must never become a write to the real registry.
`factory_work.py` does not accept or need a registry argument: it uses pinned
config/local only. The registry schema is `{"schema_version":1,"default_config":"/absolute/config.yaml","default_local":null}`;
`default_local` may instead be an absolute override path. This stores paths, not
credentials, tool permissions or runtime records.

Invalid explicit config/local, unreadable or malformed registry, and invalid or
missing registered defaults are errors. Stop with the offending path and an
actionable repair or explicit setup/`--set-default` instruction. Do not fall back
to another home, search for private configs, or reset/move runtime. A missing
conventional config with no registry means setup is needed. A broken conventional
config still needs repair. Explicit valid config may bypass an unrelated broken
registry for an invocation; it never silently repairs that registry.

Pin the returned absolute config and local (including its absence) for this whole
invocation. Pass explicit `--config <config_path>` and, when non-null,
`--local <local_path>` to every helper, role, fresh worker and foreground CLI.
Internal roles reuse that context instead of resolving again. A default switch
cannot redirect active work. A resumed top-level request resolves anew unless
it already carries an explicit pinned config, as scheduled prompts do.

`setup --harness ... --evidence <evidence-file.json>` registers the first successfully saved
setup as default, including its selected local override. Rechecking the same
factory retains the default. Setup of a second factory preserves the first
unless the user explicitly selects `--set-default`. Existing configurations may
be registered in place. To deliberately change the default or repair a broken
registry, use `setup --config <valid-config> [--local <yaml>] --set-default
--harness ... --evidence <evidence-file.json>` after the user's choice. This changes only the
remembered selection; it never relocates configs or runtime. Other commands,
including `resolve-config`, status and explicit invocation overrides, do not
write the registry.

## Configuration schema

New factories use schema version 2 with exactly these fields (no unknown or missing keys).
Schema 1 remains supported for legacy serial factories until explicit upgrade:

```yaml
schema_version: 2
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

For an explicitly requested new factory home, create this YAML at its
`config.yaml` before validating or invoking setup with that explicit path. A
missing new config in this creation flow is not an invalid existing selection.
Do not overwrite a config already there; read its choices first.
For existing homes, resolve before accessing state. `./runtime` resolves beside
the config file. If using the authoring checkout's
`config/example.yaml`, copy it into the selected home first. Validating that source
file in place correctly rejects its runtime inside the authoring tree.

Keep real YAML and runtime outside plugin source and disposable worktrees. No
credentials belong in YAML. Factory ID uses lowercase letters, digits and hyphens.
Slack names are labels; IDs are authoritative. `start_at` is system-managed: initially null, then a quoted timezone-qualified ISO
string written by verified setup. Editing or resetting an established start is
rejected using the adjacent config association. New channels get their own
current setup start. Explicit historical thread imports use factory-watch and
do not change that start or the live cursor. Existing starts survive
removal/readdition and reruns. Setup never rewrites existing watcher cursors.

All paths expand `~`; relative paths resolve against their containing YAML file,
including an override file in a different directory. A local override may contain
only `runtime_path` and/or `repositories` with `roots` and/or `paths`; lists replace
the corresponding list. Other settings require editing the main config. Explicit
repository paths must resolve inside a configured root, including through symlinks.
Discovery does not follow directory symlinks or descend into found Git checkouts;
select a narrower root when appropriate. It lists repositories, not source code.
Missing/unreadable locations remain configured and are reported unavailable.

Write the evidence JSON to a file and pass its path to `--evidence`. The JSON
has exactly `harness` and `capabilities`. Harness is `codex` or
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
factory-run additionally uses the canonical runtime/state/work.json snapshot;
see its persistence contract. Setup leaves saved work and existing cursors alone.

Unknown settings/schema versions and root escapes are validation errors. Missing
connections/repos are readiness blocks. Schema 2 removes the factory-wide active_work_items limit; fix_rounds and actions
retain their existing policies. Schema 1 requires its original limits and remains
serial. Upgrade with the work helper through the saved-work contract; setup
rechecks capabilities after upgrade without recreating the factory. Limits/actions validate the
supported choices; their enforcement during work is an agent instruction,
not a deterministic execution engine. YAML never overrides host restrictions or
grants external-action approval. Setup readiness also does not mean workflow roles
exist: inspect the loaded skills and current factory-status capability report
before choosing the next role.

Runtime must be outside the loaded plugin/authoring source and all configured or
discovered target repositories. Validation rejects a disposable or source-tree
runtime location before creating any records.
