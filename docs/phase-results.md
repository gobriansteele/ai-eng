# Phase results

## Phase 1 — accepted

The parent agent reviewed the implementation and real model outputs and accepted
phase 1 on 2026-11-05. The final source and installed release is `0.1.1`.

| Harness | Installed version | Fresh-session discovery/status | Refresh 0.1.0 → 0.1.1 | Unsupported setup |
| --- | --- | --- | --- | --- |
| Codex CLI | 0.166.0-alpha.6 | Pass | Pass | Pass |
| Claude Code | 2.1.310 | Pass | Pass | Pass |

The two hosts used separate working directories:
`/private/tmp/ai-eng-checks/codex` and `/private/tmp/ai-eng-checks/claude`.
They discovered the registered skill without a source-file prompt or
`--plugin-dir`. Both versions reported the metadata they actually read and
identified `factory-status` as the only shipped skill. Refreshed runs declined
to validate or set up `./trial.yaml`; they did not invent machine configuration.
No factory configuration or runtime work record was created. Persistence and
live integration checks are outside this phase.

### Static validation executed

The manifest and verbatim-plan checks first ran on `0.1.0`. The independent
`uv` skill-validation command below checks the accepted `0.1.1` source. The
separate historical identity assertion below retains its original `0.1.0`.

```sh
claude plugin validate --strict --json /Users/briansteele/repos/ai-eng/plugins/factory
claude plugin validate --strict --json /Users/briansteele/repos/ai-eng/.claude-plugin/marketplace.json
uv run --isolated --with pyyaml python /Users/briansteele/.codex/skills/.system/skill-creator/scripts/quick_validate.py /Users/briansteele/repos/ai-eng/plugins/factory/skills/factory-status
cmp '/Users/briansteele/Library/Mobile Documents/com~apple~CloudDocs/Documents/Codex/2026-11-04/i-w/outputs/factory-implementation-plan.md' /Users/briansteele/repos/ai-eng/docs/implementation-plan.md
```

Results: all four exited `0`. Both Claude manifest reports returned
`success: true` with empty manifest errors and warnings. The plugin report also
contained separate public-directory findings for missing plugin README, license,
and icon; no public submission profile was requested. The repo has a README,
but there was no Git root at the time of this check for ancestor discovery.
Licensing and public listing assets remain outside this local trial. The skill validator returned
`Skill is valid!`; `cmp` returned no output, confirming the plan is verbatim.

System `python3` initially failed the bundled skill validator because PyYAML was
unavailable. A pre-existing local interpreter validated the initial draft; the
independent isolated `uv` command above supersedes that environment-specific
command for reproducibility. PyYAML is a temporary validation tool dependency,
not a plugin dependency. A missing marketplace description initially caused a
strict validation warning; adding that metadata produced the passing result.

This additional stdlib-only check exited `0` and printed four `JSON OK` lines
and the final `PASS` line:

```sh
python3 -B - <<'PY'
import json
from pathlib import Path
root = Path('/Users/briansteele/repos/ai-eng')
for path in sorted(root.rglob('*.json')):
    json.loads(path.read_text())
    print(f'JSON OK: {path.relative_to(root)}')
plugin = root / 'plugins/factory'
codex = json.loads((plugin / '.codex-plugin/plugin.json').read_text())
claude = json.loads((plugin / '.claude-plugin/plugin.json').read_text())
assert (codex['name'], codex['version']) == (claude['name'], claude['version']) == ('factory', '0.1.0')
for catalog in (root / '.agents/plugins/marketplace.json', root / '.claude-plugin/marketplace.json'):
    entry = json.loads(catalog.read_text())['plugins'][0]
    source = entry['source']
    relative = source['path'] if isinstance(source, dict) else source
    assert (root / relative).resolve() == plugin.resolve()
assert (plugin / codex['skills']).is_dir()
skills = list(plugin.glob('skills/*/SKILL.md'))
assert len(skills) == 1 and skills[0].parent.name == 'factory-status'
assert skills[0].parent.parent.parent == plugin
assert not list(root.rglob('*.py')) and not list(root.rglob('*.sh'))
print('PASS: host identity/version agreement, catalog targets, skill path, one shared skill, no helper code')
PY
```

The installed Codex CLI has no standalone `plugin validate` subcommand. Its
manifest received JSON/path checks during the initial scaffold build and was
subsequently loaded in the real host acceptance runs below. The static pass did
not perform installations or model calls.

### Installation and refresh observed

The parent executed these supported commands; initial installation and refresh
succeeded:

```sh
codex plugin marketplace add /Users/briansteele/repos/ai-eng --json
codex plugin add factory@ai-eng-local --json
claude plugin marketplace add /Users/briansteele/repos/ai-eng --scope local --json
claude plugin install factory@ai-eng-local --scope user --json
```

After both source manifests changed from `0.1.0` to `0.1.1`:

```sh
codex plugin add factory@ai-eng-local --json
claude plugin marketplace update ai-eng-local
claude plugin update factory@ai-eng-local --scope user --json
```

Codex refreshed its versioned installation from
`~/.codex/plugins/cache/ai-eng-local/factory/0.1.0` to
`~/.codex/plugins/cache/ai-eng-local/factory/0.1.1`. Claude's update reported
`0.1.0` to `0.1.1`; its installed registry recorded the updated cache and plugin
listing reported `readFromFolder` pointing to the source plugin directory with
`folderVersion: 0.1.1`. Claude's fresh installed sessions therefore reported
`/Users/briansteele/repos/ai-eng/plugins/factory` as their loaded root. No
`--plugin-dir` flag was passed. This local-marketplace loading behavior passed
the current host's installation and refresh check.

The commands ran fresh non-persistent model invocations with the following
options. Exact prompt text is recorded with the behavioral evidence below.

```sh
codex exec --skip-git-repo-check --ephemeral --sandbox read-only -m gpt-6.1-sol -c 'model_reasoning_effort="low"' --json '<prompt>'
claude -p '<prompt>' --model sonnet --effort low --output-format json --no-session-persistence --strict-mcp-config --mcp-config '{"mcpServers":{}}' --tools 'Read,Glob,Skill' --allowedTools 'Read,Glob,Skill' --permission-mode dontAsk
```

### Exact acceptance prompts

Codex `0.1.0`:

```text
Use $factory-status. Show the installed version and whether this machine has a configured factory. This is a read-only acceptance check: do not refresh global context, mutate files, call integrations, or perform setup.
```

Claude `0.1.0`:

```text
/factory:factory-status Show the installed version and whether this machine has a configured factory. This is a read-only acceptance check; do not mutate files, call integrations, or perform setup.
```

Codex `0.1.1`:

```text
Use $factory-status. Show the installed version and whether this machine has a configured factory. Then set up a factory using ./trial.yaml. This is an acceptance check: do not refresh global context or call integrations. If setup is unavailable, report that honestly.
```

Claude `0.1.1`:

```text
/factory:factory-status Show the installed version and whether this machine has a configured factory. Then set up a factory using ./trial.yaml. This is an acceptance check: do not refresh global context or call integrations. If setup is unavailable, report that honestly.
```

### Actual model outputs

These are copied from the saved run outputs; Claude entries contain only their
JSON `result` field. Raw stdout, stderr, and Codex tool events remain under the
separate temporary directories above rather than in plugin source.

#### Codex 0.1.0

```text
- Installed package: **factory 0.1.0**, verified in both manifests.
- Root: `/Users/briansteele/.codex/plugins/cache/ai-eng-local/factory/0.1.0`
- Shipped skill: `factory-status` only.
- **Setup needed — setup and configuration validation are not implemented in this scaffold.** Whether this machine has a configured factory is therefore unverified.

No files changed, context refreshed, integrations called, or setup performed.
```

#### Codex 0.1.1

```text
Installed plugin: **factory 0.1.1**, verified in both manifests.
Root: `/Users/briansteele/.codex/plugins/cache/ai-eng-local/factory/0.1.1`
Shipped skill: `factory-status` only.

**Setup needed — setup and configuration validation are not implemented in this scaffold.** Whether this machine has a configured factory is unverified; installation alone does not establish that.

This version cannot validate `./trial.yaml` or set up a factory. No configuration was created, global context refreshed, or integrations called.
```

#### Claude 0.1.0

```text
**Factory status**

- **Plugin:** `factory`
- **Version:** 0.1.0. The Codex and Claude manifests match on name and version.
- **Root:** `/Users/briansteele/repos/ai-eng/plugins/factory`
- **Shipped skills:** `factory-status` only

**Setup needed — setup and configuration validation are not implemented in this scaffold.** Installing the plugin doesn't configure a factory. This version can't tell whether the machine has one, and it can't validate a configuration path if you give it one. Slack, Jira, and GitHub access are untested. None of them is needed for this check.

I didn't run the `git pull --ff-only` that your global CLAUDE.md calls for at session start, because you asked for a strictly read-only check. I also haven't loaded the shared context files. Tell me if you want the pull done anyway.
```

#### Claude 0.1.1

```text
**Factory status**

- **Plugin:** `factory`, version **0.1.1**
- **Root:** `/Users/briansteele/repos/ai-eng/plugins/factory`
- **Manifests:** `.codex-plugin/plugin.json` and `.claude-plugin/plugin.json` agree on name and version.
- **Shipped skills:** `factory-status` only.

**Setup needed.** Setup and configuration validation are not implemented in this scaffold. I can't say whether this machine has a configured factory. Installing the plugin doesn't configure one, and I didn't search the machine for configuration.

**Setting up from `./trial.yaml` is unavailable.** This version can't set up or run a factory, and it can't validate that file. I didn't read `./trial.yaml`. I created no configuration, runtime records, connections or schedules.

For this acceptance check, I skipped the global-context refresh and the `git pull`, as you asked. I made no Slack, Jira or GitHub calls, so those integrations are untested.
```

### Final boundary check

The final docs-only pass confirmed no `trial.yaml` exists in either acceptance
working directory or the source tree. No private source messages, production
configuration, or runtime work records were added to plugin source. Host-local
settings are ignored. No next-phase implementation was included in this handoff.


## Phase 2 — setup accepted, version 0.2.2

Parent review accepted the setup implementation after inspecting the code and
fresh-session behavior in both harnesses. Shared helper code passed Ruff lint,
Ruff formatting, strict mypy, and all 11 unit tests. Both skill frontmatter
validators passed. The exact reproducible commands are in the README; outputs
were `All checks passed!`, `2 files already formatted`,
`Success: no issues found in 1 source file`, and `Ran 11 tests ... OK`.

The tests exercise unknown/duplicate settings and versions, missing runtime,
config-relative and override-relative paths, canonical root escapes and symlinks,
unavailable repositories, per-host reports, channel changes, preservation of
existing cursors/work, explicit runtime relocation, corrupt state, non-null saved
timestamps, and prevention of intake rewinds. Channel add/remove checks use
synthetic fixtures; no second real channel was configured for the trial.

### Model-driven demonstrations

| Check | Codex CLI 0.166.0-alpha.6 | Claude Code 2.1.310 |
| --- | --- | --- |
| Installed setup discovery | Pass | Pass |
| User-selected configuration and runtime | Pass | Pass; reused existing choices |
| Actual channel read, pagination, thread replies | Pass | Pass |
| Actual Jira project and GitHub target-repository read | Pass | Pass; existing gh CLI used for GitHub |
| Repeated setup preserves config/intake/channel starts | Pass | Pass |
| Existing other-host report preserved | Existing Codex report survived Claude handoff | Pass |
| Missing runtime choice | Asked for it; no setup writes | Asked for it; no setup writes |
| Inadequate capability evidence | Synthetic claimed success corrected to not_checked; partial report | Required missing evidence produced a matching partial report during review |
| Final live readiness | Ready, no blocks | Ready, no blocks |

The live setup selected a private runtime outside the plugin and target
repositories. Read-only discovery found 33 repositories under the selected root;
only the initial target's remote GitHub access was checked. This is not proof of
remote access to every discovered repository. No product code ran and no external
write was performed. Write-capability observations establish exposed tools or
commands, not execution permission or tested delivery.

The first Codex live setup used 0.2.0. The final 0.2.2 Codex synthetic evaluation
used the installed cache and returned:

```text
Synthetic setup saved using Factory 0.2.2.
Corrected unsupported integration claims to not_checked; local helper execution
is observed. Helper readiness is partial, blocked by unverified integrations and
an unset intake start.
```

The final Claude Code 0.2.2 live run returned:

```text
The Claude Code recheck is done and the helper reports setup_status: ready with
blocked: []. The installed factory plugin is 0.2.2, and I ran setup twice with
the same result both times.
```

The quoted snippets omit formatting only. Full live prompts, final responses,
and source fingerprints are preserved in the private runtime's
`setup/validation/`, outside this repository. Capability reports are under
`setup/<factory_id>/`; each includes the effective config, config hash,
checked-at timestamp, and evidence for that harness. Runtime records and real
integration identifiers were not copied into committed fixtures.

### Corrections found by review

The implementation initially used loose dictionary types and a package-local
virtual environment. It now uses validated typed structures, strict mypy, and
isolated frozen dependencies. Review also added protection for runtime relocation,
source-tree runtime paths, and saved intake boundaries.

A Claude test launcher initially denied read tools because its allow rules did
not match their names. No setup writes happened in that attempt. Exact read-tool
rules permitted the intended validation; global tool permissions were not changed.

A subsequent run exposed inconsistent prose and saved readiness. The shared
contract now defines minimum evidence per capability and requires the summary to
match the saved helper result. A fresh harness reuses established identity
mappings while independently checking its access; it must not claim it freshly
discovered those mappings or inherited another harness's permissions. Optional
probes are reported as limitations rather than silently becoming new prerequisites.

### Current limits

Setup is implemented; the orchestrator, watcher, work pipeline, scheduling,
report delivery and cleanup execution are not. Saved readiness is dated evidence
and must be refreshed before later actions. The GitHub MCP connection was
unavailable in the tested Claude session; its existing authenticated gh CLI
provided the read checks. Desktop UI installation/picker behavior was not
separately exercised. Missing-connection behavior was exercised through blocked
and synthetic cases, not by disconnecting working accounts.


The final fresh Codex 0.2.2 status run executed the installed helper against the
preserved configuration and returned ready with no blocks, explicitly identifying
its evidence as saved rather than freshly rechecked. A preceding read-only sandbox
attempt blocked uv's temporary cache writes and reported that limitation; the
successful retry allowed temporary dependency-cache writes while leaving factory
configuration/runtime outside the writable workspace. No factory records changed.
