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


## Factory-home refinement — accepted, version 0.2.3

New setup uses one selected factory home, deriving `config.yaml` and `runtime/`
with `runtime_path: ./runtime`. It shows the resolved paths before writing and
preserves existing explicit layouts. There is no new schema field or helper
command. The source example now requires copying outside the source tree before
validation; validating it in place correctly fails the existing durable-path check.

Parent review accepted the shared instructions, documentation and two regression
tests. Ruff lint and formatting, strict helper mypy, and all 13 unit tests passed.
The new tests execute setup/status from another working directory and retain
support for a separately configured runtime through a local override. The setup
skill frontmatter validator passed; production helper code did not change.

Fresh installed sessions in Codex CLI 0.166.0-alpha.6 and Claude Code 2.1.310 used
independent synthetic homes. Each received a selected home, factory ID, repository
root and Jira label, with integrations deliberately unavailable. Both created
`<home>/config.yaml`, preserved the literal `runtime_path: ./runtime`, resolved it
to `<home>/runtime`, and returned partial setup rather than invented readiness.
Neither requested separate configuration and runtime choices. Codex verified both
loaded manifests at 0.2.3; Claude reported the version from its own manifest only.
Parent metadata validation confirmed both manifests agree.

The existing private factory was migrated separately using a fixture-tested,
local-only operation. Original configuration, association, input evidence and
runtime files were archived under the new runtime with a migration receipt.
All 13 original runtime files were verified byte-for-byte. Both capability reports
were carried forward for the changed runtime path with their observations and
original check timestamps unchanged; historical report files were retained. This
was not a new integration check. Intake and channel starts were preserved.

Both fresh host sessions then ran read-only status against the migrated factory
and returned ready from the preserved evidence. Codex compared contents and
modification timestamps of all 38 existing factory files before and after its
status check; none changed. Parent verification independently rechecked the
original file hashes and both carried report timestamps after the host tests.

Exact prompts/results and the migration receipt remain in the private runtime.
The Claude synthetic run also left a disposable evidence scratch file in its
isolated temporary test directory after its cleanup command was denied. No plugin
source or real factory state was affected by that scratch file.

## Phase 3 — accepted, version 0.3.0

Added shared `factory-run`, typed `factory_work.py`, and two explicitly synthetic
post-intake fixtures under the loaded package's `fixtures/`. The ordinary fixture
starts unclassified; the resume fixture carries one illustrative fix round,
scoped synthetic approval and proposed action. Neither represents live intake or
permission for real work. The agent chooses the next role; an unavailable router
must become a visible route/blocked record. Normal invocation defaults to three
saved steps (explicit range 1..10); single-step allows one. No YAML changes,
live intake, work roles or schedules were added.

Parent reviewed the persistence/owner design before implementation. The sole
canonical `runtime/state/work.json` snapshot commits item, history and invocation
bookkeeping together with file fsync, atomic replace and directory fsync. This
refines the original suggested separate record/events/runs layout to avoid split
commits without a transaction engine. Schema version 1 is deliberately limited
to one synthetic saved item; later routing of multiple pending items needs a
reviewed compatible migration. Setup/channel-start and existing cursor files
are preserved; `synthetic_cursors` are illustrative fixture metadata only.

A short fcntl mutation mutex protects a durable whole-invocation token. Mutations
verify the nearest actual harness CLI ancestor, PID/start identity and executable;
process inspection uses full-width ps with normalized C locale/UTC timezone.
Alive or unknown owners block, irrespective of elapsed time. Codex's desktop
app-server is rejected. Guides describe one foreground bounded CLI worker from
desktop, using ordinary permission review. Parent acceptance below exercised bounded CLI dispatch from this desktop
session and fresh model-driven behavior in both hosts. Native desktop UI/picker
behavior was not separately tested.

Executed from the checkout in the isolated frozen project environment:

```sh
uv run --isolated --frozen --project plugins/factory ruff check --no-cache --config plugins/factory/pyproject.toml plugins/factory/scripts tests
uv run --isolated --frozen --project plugins/factory ruff format --check --no-cache plugins/factory/scripts tests
uv run --isolated --frozen --project plugins/factory mypy --cache-dir /tmp/ai-eng-phase3-mypy --config-file plugins/factory/pyproject.toml plugins/factory/scripts
PYTHONDONTWRITEBYTECODE=1 uv run --isolated --frozen --project plugins/factory python -m unittest discover -s tests -v
uv run --isolated --frozen --project plugins/factory python /Users/briansteele/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/factory/skills/factory-run
uv run --isolated --frozen --project plugins/factory python /Users/briansteele/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/factory/skills/factory-status
```

Results: lint passed; four Python files already formatted; strict mypy passed
for both helper files; all 32 tests passed; both changed skills validated.
The suite includes both harness-order resumptions at the persistence boundary,
source deduplication, cumulative fix rounds, scoped-record preservation, revision
conflict, corruption refusal, unknown/live owner exclusion, actual subprocess
mutex contention and actual process death. Failure injection before replacement
leaves the complete prior snapshot. Failure after replacement leaves the complete
committed snapshot; retrying the same decision ID does not consume another step.
Begin and finish retries are likewise idempotent. These boundary tests do not
substitute for fresh model-driven skill demonstrations.

A separate no-prompt process smoke test started the installed Codex CLI with
`exec --skip-git-repo-check --json -` and Claude CLI with `-p`, keeping stdin open.
Both full native executable identities were accepted, then verified dead after
termination/wait. No model prompt or model call was supplied. The initial macOS
combined ps columns truncated executable names; full-width comm-last plus a
separate argument read fixed that observed failure. A regression also preserves
CLI prompts containing the word app-server without accepting the actual service.

No installs, real factory runtime mutations, product repository writes, external
calls, commits or pushes were performed by this implementation agent. Parent owns
candidate metadata/installation and remaining actual host acceptance evidence.


### Parent acceptance

Refreshed installed factory 0.3.0 with `codex plugin add factory@ai-eng-local
--json` and `claude plugin update factory@ai-eng-local --scope user --json`.
Fresh sessions used Codex CLI 0.166.0-alpha.6 with gpt-6.1-sol/medium and Claude
Code 2.1.310 with its sonnet alias (reported claude-sonnet-5-5)/medium. Codex loaded
its versioned plugin cache; Claude loaded the registered local source folder.
Both observed version 0.3.0 and saved the package source fingerprint.

Each host independently ran the installed `factory-run` on the loaded
`fixtures/synthetic-resume.json` in a separate synthetic home. Actual result:
`item-cef6818e93db732933b7ccbb`, stage `route`, status `blocked`, required role
`factory-route`, one saved decision and ownership released. The missing router
was not simulated. A new invocation in the other host resumed the same config
without a fixture: both directions preserved the entire item and synthetic
cursor object, saved zero additional decisions, and ended at revision 5 with no
active owner. Both bounded resume invocations used a maximum of three steps.

Both fresh hosts also inspected separate deliberately corrupt snapshots. Each
stopped for repair; parent verification confirmed all 43 original bytes remained
unchanged. No reset or repair was performed.

For real process contention and interruption, the test controller paused its own
Codex CLI immediately after the first decision was committed (revision 2).
A separate Claude invocation's `begin` refused with “Another invocation still
owns this workspace”; the canonical snapshot remained identical. The controller
verified the recorded PID/executable, terminated only that test CLI, waited for
exit, then launched fresh Claude. Its helper verified owner death, recorded
`interrupted_owner_dead`, and resumed without replay. Final state had one
decision, fix count 1, unchanged approval/action/cursor fields, and no active run.

The parent independently reran lint, formatting and strict typing: passed.
All 32 tests passed after narrow permission escalation for the two tests needing
`ps`; the initial sandbox run reported those restrictions rather than skipping
checks. A first Claude model test stopped on a denied compound inspection shell
command; a fresh retry used the already-permitted Read/Glob and uv/python tools.
A contention attempt similarly stopped on raw ps denial; a fresh attempt used
the helper's built-in owner verification. No global permissions were changed.

Exact prompts, JSONL traces, final responses, before/after records and parent
assertions are local test artifacts under `/private/tmp/ai-eng-phase3/`;
`verification.json` records the five preservation/corruption checks, and
`interrupted/contention-verification.json` records the unchanged live-owner case.
The reproducible test launcher and assertion script are
`/private/tmp/ai-eng-evaluate.py` and `/private/tmp/ai-eng-verify-phase3.py`.
These are disposable synthetic acceptance artifacts, not the real factory's
runtime. No Honor runtime records, live integrations or product repositories were
changed. Live routing/intake remain later phases.

## Phase 4 — accepted, version 0.4.2

Added shared `factory-route` for semantic saved-thread triage and connected it to
`factory-run`. The role returns evidence-backed findings; the orchestrator alone
chooses complete current-state updates and the selected active item. Scripts
validate source/result contracts, associations, deduplication and safe persistence;
no script classifies reports or chooses workflow transitions. Nine explicitly
synthetic saved-source fixtures include corrected replies, separate requests,
Open/unassigned Jira without code, uncertain duplicates, actual ownership/code
activity, Done/merged without deployment, missing Jira access and untrusted
message directions. Reviewer expectations live separately in
`docs/router-evaluation.md`, not raw role input.

Schema 2 keeps one canonical atomic snapshot with items, nullable selected active
ID, saved immutable source captures, routing receipts, events and invocations.
New explicit sources may route into pending records while existing work is
blocked. Source/thread identity plus immutable capture version and full-content
digest permit exact replay and retained later replies. Related sources attach
only through explicit agent-authored associations; the persistence boundary
preserves execution artifacts, code, fix counts, approvals and actions unchanged
on related-item routing. No-action has a source/disposition receipt and no work.
Proposed tickets remain local strings in the saved routing artifact.

Schema 1 remains readable without a write. Verified-owner `begin` migrates only
after prior owner liveness is resolved. The original item, history entries,
invocations, scopes/actions, counters and cursor metadata survive; a migration
event is appended in the same atomic snapshot. Legacy post-intake fixtures have
no source body and now honestly wait for missing evidence. Mutator `--summary`
avoids printing the full growing history after each operation.

Executed from the checkout (all using the isolated frozen project environment):

```sh
uv run --cache-dir /private/tmp/ai-eng-checks/uv-cache --isolated --frozen --project plugins/factory ruff check --no-cache --config plugins/factory/pyproject.toml plugins/factory/scripts tests
uv run --cache-dir /private/tmp/ai-eng-checks/uv-cache --isolated --frozen --project plugins/factory ruff format --check --no-cache plugins/factory/scripts tests
uv run --cache-dir /private/tmp/ai-eng-checks/uv-cache --isolated --frozen --project plugins/factory mypy --cache-dir /private/tmp/ai-eng-checks/mypy --config-file plugins/factory/pyproject.toml plugins/factory/scripts
PYTHONDONTWRITEBYTECODE=1 uv run --cache-dir /private/tmp/ai-eng-checks/uv-cache --isolated --frozen --project plugins/factory python -m unittest discover -s tests -v
uv run --cache-dir /private/tmp/ai-eng-checks/uv-cache --isolated --frozen --project plugins/factory python /Users/briansteele/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/factory/skills/factory-route
uv run --cache-dir /private/tmp/ai-eng-checks/uv-cache --isolated --frozen --project plugins/factory python /Users/briansteele/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/factory/skills/factory-run
uv run --cache-dir /private/tmp/ai-eng-checks/uv-cache --isolated --frozen --project plugins/factory python /Users/briansteele/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/factory/skills/factory-status
```

Results: `All checks passed!`; `6 files already formatted`;
`Success: no issues found in 3 source files`; `Ran 42 tests ... OK`;
all three skills returned `Skill is valid!`. The initial sandbox unit run exposed
process-inspection denial in two existing tests; the complete final suite passed
with narrow escalation for those real `ps` checks, not skipped tests. Ten new
tests exercise multi-item/no-action persistence, full source references, exact
repeat/version retention, related-record preservation, CAS and lost-route-reply
idempotency, legacy read-only/migration preservation, live/unknown owner refusal,
corruption refusal and migration failure before/after atomic replacement.
Manufactured test routing artifacts exercise persistence, not semantic judgments.
A failure exposed shared mutable route/history payloads; append now copies them
so later mutations cannot rewrite committed in-memory history.

At the implementation-agent handoff, fresh installed model demonstrations,
candidate installation and parent review remained pending. The exact independent-source prompt
and ordered semantic checks are in `docs/router-evaluation.md` and the harness
guides. This candidate does not establish router judgment quality or installed
behavior. No real runtime, product repository, integrations, external writes,
model calls, global settings, dependency changes, version bump, commits or pushes
were performed by this implementation agent.

### Parent review correction before model acceptance

The parent found that retrying `begin` assumed one begin event without validating
that lifecycle invariant. Both schema readers now require exactly one begin per
invocation, one finish for finished metadata and none for an active invocation,
with events ordered around begin/finish. The migration marker may precede its new
invocation's begin. Missing/duplicate begin/finish corruption is refused as a
repair request with original bytes unchanged, rather than reaching an uncaught
`StopIteration`. A separate regression verifies active schema-1 owner death:
old finish is appended before new migrate/begin, with prior history preserved.

After this helper-only correction, the same Ruff lint/format, strict mypy and
complete unit commands above passed: six formatted Python files, three typed
scripts and **44 tests OK**, including the narrowly escalated real process
checks. Related-item routing still requires artifact paths, code references,
fix count, approvals and pending actions unchanged. No fixture or skill semantics
changed in this correction; fresh installed model acceptance remains pending.

The final contract review also made fresh routed-item defaults explicit and
validated: zero factory fix rounds and empty approval/pending-action ledgers.
New work cannot inherit the legacy preservation fixture's illustrative scopes or
counters. The related-source test now establishes prior synthetic execution state
through an explicit validated save before checking preservation. Observed existing
code/artifact references remain allowed; role instructions forbid inventing
worker/worktree ownership. The added regression refuses each inherited field
without modifying the prior snapshot. Final gates passed again: Ruff lint and
format (six Python files), strict mypy (three scripts), **45 tests OK** including
real process checks, both affected skill validators, and diff whitespace check.


### Installed semantic acceptance and corrections

Parent refreshed both installed plugins to 0.4.0 and ran fresh sessions with
Codex CLI 0.166.0-alpha.6 / gpt-6.1-sol medium and Claude Code 2.1.310 / sonnet
medium. Each host used an independent synthetic home and the installed skills,
without evaluator expectations or live integrations. Eleven invocations routed
conversation, an open-ticket bug, its repeat, feature, ambiguous duplicate,
three independent requests, underway work, unavailable Jira, related thread,
its repeat, and a later capture of the original bug.

Parent inspected actual saved findings and asserted every checkpoint. Both
produced eight items from nine immutable source captures, eleven finished
invocations, nine routing decisions and one selected active item. Conversation
created zero work. The three-item source produced three distinct linked items.
Both repeats preserved the entire inventory/receipts and consumed zero new steps.
Related and later-capture sources attached to the original CSV item. Jira access
failure remained an incomplete duplicate check, and the embedded instruction to
publish a ticket/disable approvals caused no action. Done/merged was not treated
as deployment. Feature briefs followed the correcting reply's download request,
not the withdrawn email request.

Actual Phase-3 records were then resumed in fresh installed sessions in both
hosts. Parent verified schema 1-to-2 migration, verbatim old events/invocations,
unchanged identity/links/fix count/scopes/actions/cursors, and a route-stage human
wait for the missing original source. Neither fabricated a source or judgment.
Claude completed the migration but its evidence-copy `cp` was denied by the test
launcher; parent copied the finished snapshot byte-for-byte and verified it.
The runtime migration itself was successful in both hosts.

Semantic review caught two instruction defects in the first Claude suite: it
invented feature-brief/verifier skill names and described missing ownership
observations as proof that no work was underway. Version 0.4.1 explicitly uses
`factory-investigate` for investigation and verification across all brief types,
and requires bounded, calibrated absence wording. Helpers did not change.
Both modified skill validators passed; both installed copies were refreshed.
Fresh focused sessions reran feature, three-item and unavailable-Jira sources.
Both produced five items from three captures; every actual handoff named
`factory-investigate`, fresh authorization/action ledgers were empty, fix counts
were zero, and the saved reasons described underway work as unverified. Missing
Jira remained incomplete. Each run stopped truthfully at the unavailable
investigator and released ownership. The original full-suite failures remain
visible in the local evidence; they were not edited into passing records.

Codex's focused run initially supplied a list for the artifact-path mapping. The
helper rejected it without saving; the model corrected the draft and completed
the run. Several read/shell forms were denied by the intentionally narrow test
launcher; permitted read/Python/helper commands completed the checks. No global
permissions changed. Trace inspection found no MCP calls in any fixture session.

Exact prompts, outputs, checkpoints and assertions are under
`/private/tmp/ai-eng-phase4/`. `verification.json` records full-suite structural
checks, `legacy-verification.json` records migration preservation, and
`focused-verification.json` records the corrected handoffs/evidence wording.
The assertion script is `/private/tmp/ai-eng-verify-phase4.py`; the launcher is
`/private/tmp/ai-eng-evaluate.py`. These are disposable synthetic test artifacts.
No Honor runtime, product repository, live source or external service changed.
Live collection is the next phase; this acceptance establishes saved-source
routing and local persistence only.

Final packaging review found the status helper still omitted saved-source routing
from its capability list. Version 0.4.2 corrects only that report plus package
version metadata; the 0.4.1 routing instructions and persistence behavior remain
unchanged. Required lint, formatting, strict typing and all 45 tests passed again.
Both hosts were refreshed to 0.4.2. Fresh processes ran each installed package's
status helper, confirmed matching manifests and the corrected capability/workflow
report, and left the synthetic canonical snapshots byte-for-byte unchanged.
`status-verification.json` records this check. Model-driven routing acceptance is
the 0.4.1 focused run above; the final report-only change was checked directly.

## Phase 5 candidate — watcher source verification (not installed acceptance)

Added shared `factory-watch` plus typed normalized-page collection in
`factory_collection.py`; `factory_work.py` now supports config-only begin,
read-only watch-plan and owner-gated collect. Canonical work.json remains the
inbox/work authority. First successful collection migrates schema 2 to 3 atomically
with its immutable captures, seen ledger, per-channel synthetic/live mode, tracked
roots, coverage and cursor. Schemas 1/2 inspect remain read-only; source-only
work remains schema 2. Existing handoff metadata/history and synthetic cursors
are preserved. No split source/cursor commit or second work authority was added.

Collection accepts observed paginated history and optional reply discovery,
requires complete new/tracked thread rechecks, preserves root and full currently
observed textual context, and records trigger IDs separately from old context.
Repeated root/pages dedupe; terminal restart, incomplete fetch and conflicting
same-ID content refuse. Explicit imports can promote previously seen context
once without changing live cursors. Per-channel mode is fixed even on empty reads;
synthetic source-file input cannot bypass the live collector. Observed permalinks
are retained, with durable workspace/channel/root identity as an honest non-URL
fallback. Current capture text never unions deleted/absent old messages; older
immutable captures remain history. Edits/deletions alone do not trigger intake.

The orchestrator invokes watch before handling blocked work, then routes/resumes
within semantic bounds. Live routing can save timestamped read-only observations
with source references and access/search limitations; synthetic runs stay offline.
Both status skill and configuration-helper workflow report now include watcher
capability. Investigation still stops at `factory-investigate`; no later role,
external write, schedule or integration service was added.

Raw synthetic observations are under `plugins/factory/fixtures/watch/`; reviewer
criteria are separate in `docs/watcher-evaluation.md`. There are 21 new unit tests,
66 total including the original 45. They cover independent channels, multipage
history/thread/search overlap, failure then retry, exact replay, late-indexed
replies below the prior cursor (including an untracked root), tracked old roots,
no-discovery coverage limits, manual imports, partial setup/channel removal and
re-addition, mode isolation, corruption, cross-host state preservation and failures
before/after atomic replacement. Real subprocess lock/liveness/locale tests ran;
none were skipped.

Executed from `/Users/briansteele/repos/ai-eng`, using isolated frozen uv and
`--cache-dir /private/tmp/ai-eng-checks/uv-cache` throughout:

- Ruff check over `plugins/factory/scripts tests`: passed.
- Ruff format check over `plugins/factory/scripts tests`: passed (8 files).
- Strict mypy over all four helpers with cache at
  `/private/tmp/ai-eng-checks/mypy`: passed.
- `PYTHONDONTWRITEBYTECODE=1 uv run --isolated --frozen --cache-dir /private/tmp/ai-eng-checks/uv-cache --project plugins/factory python -m unittest discover -s tests`: 66 passed.
- System skill-creator quick_validate for watch, run, route and status: passed.
- JSON parsing for all six watch fixtures and `git diff --check`: passed.

This entry records candidate source/helper checks only. Fresh model-driven
Codex/Claude fixture acceptance, installed refresh, and actual read-only live
collection/repeat/import acceptance are delegated to the parent and remain to be
recorded separately. No model calls, live integration calls, real runtime edits,
version bump, installation, product changes, commits or pushes were performed by
this implementing agent. Search/index/private/bot completeness is not claimed.

### Phase 5 candidate instruction correction after initial live trials

Parent acceptance exposed a read-bound ambiguity: an integer-string thread
`latest` produced a parent-only terminal response, while the parent observed
replies/cursor using the equivalent six-fractional-digit Slack timestamp.
Shared watch instructions/contract and both harness guides now distinguish
channel/thread `oldest`/`latest` (`seconds.ffffff`, including whole seconds) from
reply-search `after`/`before` (schema-specific Unix seconds). Search widening
applies only to search. Malformed read bounds or contradictory reply evidence
require corrected refetch before collection; unresolved contradiction blocks
cursor advancement even after an apparent terminal response. Prior failed live
acceptance evidence and private runtimes were not edited by this agent.

The second-channel fixture now honestly describes unavailable discovery when
`discovery: []`; it no longer claims a terminal search occurred. Router guidance
also clarifies that explicit import grants eligibility, while full thread meaning
still decides whether an answered/settled question needs work.

Only instructions/guides and that synthetic provenance note changed; helpers,
models, schemas, dependencies, version and installations did not. Repeated isolated
frozen checks passed: Ruff lint and format (8 files), strict mypy (4 helpers), both
changed skill validators, fixture JSON/provenance check, all 66 unit tests including
real process checks, and git diff whitespace validation. Fresh installed/live
retests remain parent-owned; this entry does not claim they passed.

### Phase 5 candidate scope/reporting correction

Shared router guidance now obtains effective repository scope with
`factory_config.py discover --config <same-config>` and any supplied `--local`.
The linked configuration contract explicitly explains that discovered repositories
under roots remain in scope and explicit paths adds to that set rather than
narrowing it. Bounded searches may select relevant repositories; other in-scope
repositories are unsearched, not unconfigured or unauthorized simply because
absent from paths. Discovery/access limitations remain explicit evidence.

Manual-import instructions and contract now require selecting and saving the
fixed six-fractional-digit upper in the local draft observation before the first
thread read, then reusing it as latest across every page. No helper/schema or
runtime change was made. This implementing agent touched no private runtime,
installation, version or prior failed evidence.

Validation repeated with the same isolated frozen uv commands/cache: Ruff lint,
format check (8 files), strict mypy (4 helpers), watch/route/setup skill validators,
all 66 unit tests including real process checks, and git diff whitespace check
passed. Fresh focused scope/contract behavior in both installed hosts is
parent-owned and is not claimed by these source checks.

### Phase 5 parent acceptance — Factory 0.5.2

Parent reviewed the collection, replay/migration, source-provenance and skill
changes, then ran installed model sessions in both hosts. Codex CLI was
0.166.0-alpha.6 with gpt-6.1-sol/medium; Claude Code was 2.1.310 with
Sonnet/medium. Each test used its own private temporary factory home.

The complete offline suites ran on 0.5.0: partial, first, second-channel, repeat,
followup, historical import, repeated import. Both ended with five routed
captures, four items, nine seen identities and seven finished invocations.
The partial rejection left canonical bytes identical before finish bookkeeping.
Channel cursors advanced independently; repeated reads created no duplicate
captures; a late-visible reply below the prior cursor and a fresh reply attached
to the existing report; imports preserved live cursors. Earlier capture bodies,
digests, routing, fix counts and action/approval records remained intact.
Codex routed one pending capture per blocked invocation, while Claude initially
routed two; both retained remaining work and respected the three-step bound.
All selected work stopped honestly at the unavailable investigator.

Live acceptance found and corrected a real connector failure: a whole-second
thread `latest` argument returned only the parent with an apparent terminal
response. Repeating that read with six fractional digits returned replies and a
cursor. The initial Codex 0.5.0 live run was rejected, not counted as success.
0.5.1 explicitly separated decimal Slack read bounds from whole-second search
bounds, required refetch on malformed/contradictory reads, and clarified that
historical import does not revive settled requests.

Fresh 0.5.1 live runs in both hosts completed two automatic reads followed by an
explicit historical import. Each automatic read returned terminal empty history
and reply-search pages after the preserved setup start. Each import retained
seven unique messages across three pages, preserved the live cursor and routed
the conversation to no-action with zero work items. Current bounded Jira/code
observations and their limits were saved privately. Separate independent probes
in both hosts demonstrated discovery of replies whose roots predated the search
window, including following an empty terminal search page. This establishes the
observed public-channel capability, not complete indexing/private/bot coverage.

One Claude import selected its upper bound after fetching. Its old messages were
all below that bound, but this did not establish the required ordering. A focused
fresh import subsequently saved the upper before the first connected read and
used that exact decimal `latest` on all three pages; parent audited the actual
call order and final state. A preceding focused attempt stopped safely before
reads because its shell spelling did not match the launcher's existing narrow
allowlist. The retry used the already-permitted literal uv/python3 commands;
permissions were not broadened. The failed attempts remain in private evidence.

0.5.2 adds explicit repository discovery before live code scope checks: configured
roots and explicit paths form a union. A bounded search leaves other discovered
repositories unsearched; it does not make them unconfigured. It also makes the
pre-read import-boundary step explicit at the import instruction, fixes the
second-channel fixture's absent-discovery note and removes an obsolete setup
capability statement. Helper logic is unchanged from the tested collector.

Parent verification on the final source includes all 66 unit tests (including
real process checks), Ruff lint/format, strict mypy, skill/JSON validation and
`git diff --check`. Both hosts refreshed through their normal local plugin
installation commands. Final fresh 0.5.2 preflights independently checked actual
repository discovery, root/path scope semantics, import-boundary order and the
loaded version; both discovered the same 33 repositories with no unavailable
paths. Status correctly refused setup readiness in these copied preflight homes,
which intentionally lacked the saved setup association for their non-null intake
start; validate/discover succeeded and no setup readiness was claimed. The full live suites were not repeated for these final guidance
clarifications; the focused checks cover the changed behavior.

Private evidence (not committed):

- `/private/tmp/ai-eng-phase5/{codex,claude}/suite/`: exact prompts, events, seven
  checkpoints and byte-identical partial snapshots.
- `/private/tmp/ai-eng-phase5/verification.json`: parent schema replay, counts,
  preservation, cursor and related-source assertions.
- `/private/tmp/ai-eng-phase5-live/{codex,claude}-accepted/`: exact live prompts,
  tool calls, normalized observations, routing and three checkpoints each.
- `/private/tmp/ai-eng-phase5-live/verification.json` and `read-bound-audit.json`:
  parent live-state assertions and actual read argument precision.
- `/private/tmp/ai-eng-phase5-live/claude-import-retry/verification.json`: focused
  import ordering, three identical upper arguments, full capture and released owner.
- `/private/tmp/ai-eng-phase5/{codex,claude}/scope/`: final installed preflight.

Normal entry points are `$factory-run --config <factory-home>/config.yaml` in
Codex and `/factory:factory-run --config <factory-home>/config.yaml` in Claude
Code. Use an explicit `--import-thread` with selected configured channel and root
for historical intake. For the reproducible offline evaluation, use
`--collection <loaded-plugin>/fixtures/watch/<fixture>.json` with the isolated
synthetic configuration described in `docs/watcher-evaluation.md`. Actual outputs
and resulting canonical records are in the evidence locations above.

Watcher acceptance is complete. Investigation remains the next tranche; no
scheduled operation or external write was exercised by these tests.


## Phase 6 — candidate, parent acceptance pending

The candidate adds one shared `factory-investigate` role for bug/regression,
feature and existing-work verification. It reads configured repository instructions,
discovers the root/path union, records actual code revision/environment and raw
command evidence, and distinguishes observations, hypotheses and unknowns. Local
probes are limited to authorized isolated checkouts; no product fix or external
write is part of investigation. Failed/unavailable reproduction stays explicit.

`factory-run` now dispatches the investigator (including older missing-role blocks),
verifies durable reports and saves the existing `artifact_paths` map using the
same verified CLI owner/token. Completed findings stop at the absent `factory-plan`;
unavailable evidence retains investigation with a concrete unblock. Artifacts and
partial attempts are retained across fresh-chat resume; an unsaved report alone
is not completed work. Explicit offline resume stays offline. No persistence or
configuration schema, helper process semantics, dependency or framework was added.
Only helper capability/workflow reporting changed.

The raw reports and deliberately broken standard-library sample live under
`plugins/factory/fixtures/investigate/`. The sample must be copied into a disposable
Git checkout outside plugin source before use; reviewer-only setup/oracle and
fresh-chat prompts are in `docs/investigator-evaluation.md`. They cover repeatable
completed-task selection failure, CSV scope ambiguity and a hosted reconnect case
that the local sample cannot reproduce. Existing router/watcher evaluation results
remain historical acceptance for those phases, not proof of investigator behavior.

Static/helper checks and parent fresh-session model acceptance are recorded below
as they execute. This candidate is not an accepted Phase 6 release until both
hosts' actual artifacts and stop/resume behavior pass parent review. Version bumps,
installation, live probes and publication remain parent-owned.

### Candidate validation executed

From `/Users/briansteele/repos/ai-eng`:

```sh
uv --cache-dir /private/tmp/ai-eng-checks/uv-cache run --isolated --frozen --project plugins/factory ruff check --no-cache --config plugins/factory/pyproject.toml plugins/factory/scripts tests
uv --cache-dir /private/tmp/ai-eng-checks/uv-cache run --isolated --frozen --project plugins/factory ruff format --check --no-cache plugins/factory/scripts tests
uv --cache-dir /private/tmp/ai-eng-checks/uv-cache run --isolated --frozen --project plugins/factory mypy --cache-dir /private/tmp/ai-eng-checks/phase6-mypy --config-file plugins/factory/pyproject.toml plugins/factory/scripts
PYTHONDONTWRITEBYTECODE=1 uv --cache-dir /private/tmp/ai-eng-checks/uv-cache run --isolated --frozen --project plugins/factory python -m unittest discover -s tests
```

All exited 0. Ruff: `All checks passed!`; format: `8 files already formatted`;
mypy: `Success: no issues found in 4 source files`; unittest: `Ran 66 tests in
0.460s`, `OK`, with no skips. The unit run used narrow escalation for the existing
real-process ownership checks. Helper logic/contracts did not change; no new
helper regression tests were justified by the capability-text-only edit.

The system `skill-creator/scripts/quick_validate.py` ran for `factory-investigate`,
`factory-run` and `factory-status` via isolated frozen no-dev plugin Python (with
`-B`); all three exited 0 with `Skill is valid!`. A standard-library JSON parse
checked all 26 repository JSON files, and `factory_source.source` accepted each
of the three new raw source fixtures. `git diff --check` exited 0.

A separate copied sample smoke check ran under
`/private/tmp/ai-eng-phase6-sample-check/taskboard-sample` with bytecode disabled.
Two actual `python3 tasks.py list --status done` calls both exited 0 and returned
`1\topen\tDraft workshop agenda`. Default open and all selectors exited 0;
`python3 -m unittest -v` exited 1 with exactly three tests and one completed-selection
failure. Both source and copied baseline file hashes stayed unchanged. Exact
commands, stdout/stderr and statuses are in the sibling `evidence/commands.json`
and individual output files; these are fixture checks, not a model investigation
or a claim of fresh-host acceptance. The sample's failure is deliberate and is
separate from the passing 66 helper tests.

Not executed in this implementation tranche: installed fresh-host model runs,
cross-host artifact resume, interruption-at-artifact-production probe, live
integrations, version/install changes or publication. These remain explicit
parent-owned acceptance checks; no result is inferred from skill text.


### Runtime prerequisite correction — fresh-host acceptance pending

Parent review rejected the initial Claude `0.6.0` acceptance run as incomplete:
its sample observations honestly identified Python `3.9.6`, which does not satisfy
the sample's declared Python prerequisite. Discovering a newer helper interpreter
without using it for the sample did not resolve that gap. The initial Codex
sample observations used Python `3.12.3`, a supported runtime; parent retains that
evidence subject to its other acceptance checks. These are parent-observed model
results, not a completed acceptance claim by the implementation worker. The
worker's earlier fixture smoke test likewise did not record its interpreter path
and version and is not supported-runtime validation evidence.

The shared investigator now requires checking declared runtime/tool prerequisites
before relying on executions, discovering an existing compatible environment when
the default fails them, and recording the exact executable/version for every
command environment. Unsupported observations remain evidence but do not satisfy
required supported-runtime checks. Missing compatible environments produce a
concrete validation block/limit. `factory-run` verifies this prerequisite when
accepting findings. No sample-specific version is hardcoded into shared guidance;
no runtime install, dependencies, schema or helper behavior changes were added.
The evaluation guide explains how the reviewer can identify an already available
compatible interpreter through the provisioned locked helper environment.

Parent owns fresh Claude reruns and cross-host handoffs after repackaging. The
prior model artifacts remain historical evidence; this correction does not
retroactively make unsupported executions valid.


Correction validation: the changed investigator/run frontmatter both passed the
system `quick_validate.py` through isolated frozen no-dev plugin Python; both
exited 0 with `Skill is valid!`. `git diff --check` exited 0. This correction
changes only skills/evaluation/results prose; no helper, metadata, fixture or
schema changed, so the previously passing helper checks were not repeated.

A new copied-sample fixture smoke used the already available locked helper Python
`3.12.8` (Anaconda build), satisfying the declared sample prerequisite. Raw command
environments record the exact executable
`/private/tmp/ai-eng-checks/uv-cache/builds-v0/.tmpxIOUXN/bin/python` and full version
at execution time. Two done-filter calls reproduced the same open-task output;
three sample tests again had exactly the deliberate one failure. Copied/source
baseline bytes remained equal. Actual commands/statuses/stdout/stderr/environment
are saved at
`/private/tmp/ai-eng-phase6-sample-supported-check/evidence/commands.json`.
This is supported-runtime fixture verification, not fresh-host model acceptance.
The evaluation guide accounts for transient isolated-environment paths when
reusing an already available interpreter.

### Phase 6 parent acceptance — Factory 0.6.1

Parent reviewed the shared investigator, run integration, sample and raw reports.
Existing owner-gated save/artifact_paths contracts were sufficient: there is no
new state schema, workflow engine or dependency. Status skill and helper both
report investigation available and planning absent. Runtime reports preserve
facts, hypotheses, raw command evidence, examined revision, limitations and next
action, with distinct attempt paths.

Fresh installed Codex and Claude sessions each investigated independent bug,
feature and unavailable cases, using separate factory homes and disposable sample
Git baselines. Codex CLI 0.166.0-alpha.6 used gpt-6.1-sol/medium; Claude Code
2.1.310 used Sonnet/medium. The sample has three tests with one deliberately
failing completed-task filter test. Its failure is reproduction evidence, not a
passing product test suite. No sample fix was made.

| Case | Observed result in both hosts | Saved handoff |
| --- | --- | --- |
| Bug | Repeated done selector returned the open task; code hardcodes open for every non-all selector; two other tests pass. Revision/tree state and command outputs support the local explanation. | plan / blocked / factory-plan |
| Feature | List-only CLI rejects export; concrete parser/selection/output/test areas identified; requested fields preserved and default task inclusion remains unresolved. | plan / blocked / factory-plan |
| Unavailable | Hosted reconnect loss cannot be established from an unrelated local file-backed CLI. Missing version, sequence, board/session and logs are concrete unblock evidence; local failure is not promoted to the hosted cause. | investigate / waiting_for_human / factory-investigate |

Each initial case saved two semantic steps within the default bound of three,
one source, one item and readable investigation artifacts. Parent replayed all
canonical snapshots and independently verified original baseline HEADs/clean
working trees, source records, absolute report paths, zero fix rounds and empty
approval/action ledgers. Reports were read against actual raw command logs.

The first Claude 0.6.0 run used default Python 3.9.6 despite the sample's declared
Python 3.11+ requirement. It reported that limitation honestly, but parent rejected
it as supported-runtime acceptance. 0.6.1 now checks declared runtime/tool
prerequisites before relying on executions, discovers existing compatible
environments without installing or changing permissions, and records executable
and version. Fresh Claude runs used the existing Python 3.12.8 interpreter from
the locked uv environment. Codex's original runs used supported Python 3.12.3 and
remain valid evidence. Unsupported observations are distinguished from required
validation. A relaunch also made the isolated test's no-global-refresh instruction
explicit after an ambient startup rule caused a safe stop before any case began;
its denied unrelated pull was not authorized by broadening test permissions.

Parent made a refresh timing error: installing 0.6.1 removed the versioned Codex
0.6.0 cache while its final case still needed the old helper for finish. Its report
and investigation wait were saved at revision 3, but the owner remained active.
After that CLI exited, a fresh 0.6.1 invocation verified owner death, recorded
interrupted_owner_dead and finished the same wait at revision 6 with zero new
semantic steps. Parent verified unchanged items, sources, prior event prefix,
artifact bytes and baseline. This is observed post-save interruption recovery,
not a claimed successful finish of the initial run. README now requires all
active CLI sessions to stop before package refresh, even with versioned caches.

Fresh cross-host bug resumes then passed in both directions on 0.6.1. Each read
and explained the other host's saved report/raw evidence without the original
transcript, retained plan/blocked, used zero new steps, and released ownership at
revision 6. Parent verified exact item/source/prior-invocation/event preservation,
unchanged artifact files (18 in one home, 17 in the other), and clean baselines.
A separate interruption between artifact creation and state save was not injected;
no claim of tested orphan-artifact reconciliation is made here.

Checks passed: all 66 helper unit tests (including actual process checks), Ruff
lint and formatting, strict mypy, six skill frontmatter validations, fixture/source
JSON validation and git diff --check. No helper logic changed after those checks;
the runtime correction affects shared instructions and reviewer guidance. Both
hosts were refreshed through their normal local plugin commands, and fresh
sessions observed the installed versions.

Private acceptance evidence is outside source:

- `/private/tmp/ai-eng-phase6/codex/{bug,feature,unavailable}/`: original 0.6.0
  case prompts, baseline identities, reports and snapshots. The unavailable
  snapshot is the preserved interrupted record, not its final recovery.
- `/private/tmp/ai-eng-phase6-accepted/claude/{bug,feature,unavailable}/`: final
  0.6.1 supported-runtime records and evidence; exact session prompt/events in
  the sibling `suite-retry/` directory.
- `/private/tmp/ai-eng-phase6/verification.json`: parent six-case structural,
  state, path and baseline assertions, including final recovery where required.
- `/private/tmp/ai-eng-phase6/recovery/codex/`: old and recovered snapshots,
  exact recovery prompt/output and preservation verification.
- `/private/tmp/ai-eng-phase6/resume/{codex,claude}/` and its `verification.json`:
  exact fresh-session prompts, responses, before/after state and artifact hashes.
- Initial unsupported/runtime and startup-stop evidence remains under
  `/private/tmp/ai-eng-phase6/claude/` and the accepted tree's original `suite/`.

For an offline sample use `$factory-run --config <home>/config.yaml --source
<loaded-plugin>/fixtures/investigate/bug.json --max-steps 3` in Codex, or
`/factory:factory-run` in Claude, with explicit offline instructions and the copied
sample/config from `docs/investigator-evaluation.md`. Substitute feature.json or
unavailable.json for the other cases. For a fresh resume provide the same config,
explicit offline mode, and ask it to explain saved findings without replaying
investigation. Actual outputs and work records are in the evidence above.

Investigator acceptance is complete. Product planning is the next tranche.
