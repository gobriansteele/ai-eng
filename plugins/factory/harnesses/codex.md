# Codex

Verified with `codex-cli 0.166.0-alpha.6`. From the local checkout:

```sh
codex plugin marketplace add "$PWD" --json
codex plugin add factory@ai-eng-local --json
codex plugin list --marketplace ai-eng-local --json
codex -C "$PWD"
```

In a fresh session:

```text
Use $factory-setup. Set up a factory using my Slack MCP connection. Let me choose a factory home and the channels. Show the resolved config.yaml and runtime/ paths before writing.
```

To inspect it later:

```text
Use $factory-status with configuration <factory-home>/config.yaml. Show the loaded version and setup readiness.
```

Codex loads an installed copy under
`~/.codex/plugins/cache/ai-eng-local/factory/<version>`. Change both host manifests
and the helper project version together, refresh the lockfile, then repeat
`codex plugin add factory@ai-eng-local --json`. Verify the version in a fresh
session. This procedure refreshed the tested installations through `0.2.3`;
a source edit alone is not evidence that the installed copy changed.

Setup discovers the current session's integration tools. The accepted live run
used Slack, Jira, and GitHub connectors; it did not perform external writes.
Read checks and exposed write tools are distinct evidence. Dependency bootstrap
may need network/cache access; a sandbox-denied dependency download is a blocker
until a permitted environment or cached locked dependency is available.

CLI fresh-session behavior was exercised. Desktop restart/picker behavior was
not separately exercised. See [phase results](../../../docs/phase-results.md).

References: installed CLI help and
[OpenAI plugin packaging](https://developers.openai.com/plugins/build/plugins).

## Run and resume

In a fresh CLI session:

```text
Use $factory-run with configuration <factory-home>/config.yaml and the loaded package's fixtures/synthetic-resume.json. Single step: save the next-step decision, then stop at an unavailable role. Report the canonical snapshot path.
```

Resume after the original CLI stops with the same config and no fixture. For
normal bounded use request at most three steps (default), or `--max-steps 1..10`.
The shared skill discovers the exact long-lived `codex` CLI ancestor through
`factory_work.py owners`; its helper/shell PID is not the owner. Process
inspection denied by sandbox is unknown: retry the specific command through the
normal host approval mechanism, preserving sandbox settings. Never infer death.

For desktop, dispatch one foreground CLI worker and wait for completion:

```sh
codex exec --skip-git-repo-check --approve-for-me --sandbox workspace-write -C '<factory-home>' 'Use $factory-run with configuration <factory-home>/config.yaml. Resume saved work with --max-steps 3; finish and report the result.'
```

Use an existing selected home and substitute the actual config path. For a new
synthetic test include the explicitly selected fixture in that prompt. `--approve-for-me` retains workspace-write and routes specific required commands
through automatic approval review; it does not disable the sandbox or grant
external-action permission.
The desktop `codex app-server` lifetime is unrelated to the invocation and is
never accepted as owner. If dispatch/inspection cannot run with permitted tools,
report that gap. No background service or scheduler is added. A CLI owner is
valid until the bounded worker stops; switching to Claude requires it to finish
or stop first. Saved approvals are scoped evidence, not transferred tool grants.


For saved-source routing, ask the same `factory-run` entry point to use the loaded
package's `fixtures/sources/open-ticket.json` as `--source` with the explicit
configuration. Follow with `related-thread.json`, then repeat it. Use separate
synthetic homes for independent acceptance; keep all runtime records outside the
plugin. Router judgments are shared across hosts; no host adapter or model call
is embedded in the helper. Use `--summary` on mutations to keep repeated history
out of the model context; read full saved source and relevant inventory before
deciding. Legacy post-intake fixtures now wait for missing source evidence.

## Read-only Slack intake

With an explicit config and no synthetic flag, factory-run calls factory-watch
then routes saved intake. Direct watch requests also enter that orchestrator so
one verified CLI token spans all MCP reads. Historical `--import-thread` requests
name the selected configured channel and thread root/link; live cursors stay put.
Explicit `--collection <synthetic-json>` is offline and makes no MCP calls.

Codex exposes currently authenticated Slack capabilities as `slack_read_channel`,
`slack_read_thread` and `slack_search_public`; discover their fully qualified
connector names in this session.
Channel history is newest first and supports oldest/latest, limit and cursor.
Thread reads support root timestamp, oldest/latest, limit and cursor; the root
may repeat on each page, and a displayed total may describe only that page.
For both channel and thread reads, `oldest`/`latest` are Slack timestamp strings
with six fractional digits, including whole seconds (`1700000040.000000`, never
`1700000040`). Do not pass floats or truncate fractional precision. Preserve the
same format for thread root/message timestamps. Full-thread reads must include
older context rather than setting oldest to the live scan boundary.
Follow returned next cursors until terminal, including an empty terminal search
page when required. Never infer completeness from count or a full page.

Public reply search can use the selected-channel filter plus `is:thread`,
fixed after/before Unix bounds and timestamp order. Include bots when supported.
Read tool schemas for the exact filter shape. Search `after`/`before` uses its
schema's second-resolution Unix strings: round the lower bound down and upper
bound up to cover the fractional interval. This widening applies only to search;
channel/thread read bounds retain all six fractional digits. Normalized timestamps
and deduplication enforce the declared collection interval. A reply permalink may expose the older root's `thread_ts`;
read that complete thread rather than treating the reply as its own root.

A read made with malformed bounds must be refetched correctly before collection,
even if the response claims terminal. Reconcile parent-only thread results that
contradict observed replies through upper: verify root/query/bounds and refetch.
If evidence still conflicts, report incomplete and preserve the cursor instead of
saving an asserted complete capture.

Metadata alone is not capability evidence. The parent independently observed
these pagination/reply-discovery capabilities in both hosts for a selected public
channel sample; that does not prove index completeness, private-channel coverage
or bot coverage. Verify selected workspace/channel access and present tool
permissions now. Report unavailable discovery as a precise limitation and retain
manual import; do not replace authenticated host tools with a client/service.
Shared contracts and normalized pages remain host-independent.

## Implementation worktrees

Discover actual tools/help in the current host before creating resources. In
Codex desktop, use the app's `create_worktree` capability for a new managed
worktree: supply the observed source repository as `sourceRoot` and full chosen
base commit as `ref`; inspect existing attached artifacts first. It starts
detached and returns a workspace directory (or pending operation to reconcile).
Use the returned path explicitly; create an unoccupied `codex/<description>`
branch there following applicable repository instructions. Record returned
provenance and actual Git common directory, HEAD, branch and worktree list.
A tool being exposed is not evidence that creation succeeded. If a request
hangs or its result is uncertain, reconcile operation status, attachments and
actual Git worktrees before retrying; never create duplicates.

The installed `codex-cli 0.166.0-alpha.6` advertises `--worktree` in both
`codex --help` and `codex exec --help` as starting a managed worktree session.
The [official CLI reference](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
also supports new local `codex exec --worktree` runs, incompatible with `resume`,
`review`, `--ephemeral` and `--ignore-user-config`. Help alone does not establish
the observed path, branch, base selection, exit persistence or cross-host
usability. Native creation must be verified in the actual environment before
relying on it. On 2026-11-05 parent read-only
`codex exec --worktree --approve-for-me -C <clean-sample-source> ...` probes
created detached clean checkouts for both accepted bug sources at their observed
HEADs; Git worktree inspection confirmed persistence immediately after CLI exit. This verifies
that native preparation path, not indefinite retention or arbitrary-base
selection. The desktop app-tool attempt returned no successful creation result;
Claude native creation remains untested. Do not launch a second factory owner
inside an existing invocation just to obtain a checkout. A desktop/orchestrator
may prepare a worktree before launching the foreground factory CLI, then supply
its actual path and observed provenance for adoption. A CLI that has no working
creation capability and no verifiable prepared checkout saves a precise
implement/blocked capability request; do not silently use `git worktree add`.

The [official worktree documentation](https://learn.chatgpt.com/docs/environments/git-worktrees)
describes detached starts, one branch per worktree and managed cleanup/restoration.
Managed paths can be removed by app lifecycle or retention behavior, so they are
not archival evidence. Preserve preparation, exact diff/content and check outputs
in factory runtime outside that checkout. Do not archive or remove an active
implementation's worktree. If it disappears, stop and request restoration through
the host rather than inventing a new equivalent checkout or claiming tests passed.
These lifecycle details are documentation, not a newly exercised cleanup test.

For a supplied existing dedicated worktree, use its observed path; creation need
not be repeated. Verify common Git directory/base/source, exclusive branch and
prior dirty bytes against saved evidence. The CLI may remain launched from the
factory home and execute code/checks with explicit working directories in that
worktree, retaining runtime access. Request only the normal narrow command/path
permission if needed. Before editing, the orchestrator saves authorization,
preparation and observed code references. Cross-host handoff uses those durable
paths after the old CLI stops, not a Codex chat identifier. Recheck permissions in
the destination; no new branch or worktree is needed to read completed evidence.


## Independent review workers

Keep the factory CLI as the single invocation owner. Dispatch review roles through
actual available native worker tools; role workers never run factory-run or its
canonical mutators. Each gets the same explicit read-only bundle, one role/focus,
a unique runtime output directory and permission limits. No product edits,
integrations, installs or external writes. In isolated synthetic evaluations,
explicitly skip global personal-context refresh and unrelated repository context;
read only scoped evidence and applicable sample instructions. Preserve actual
prompts, returned IDs/reports and observable dispatch provenance. A tool name or
worker's claim alone does not prove it read the bundle; require real input-derived
findings/evidence and report limits of observable isolation.

The 2026-11-05 CLI probe observed `collaboration.spawn_agent` with
`fork_turns: "none"`, two distinct fresh worker IDs and actual read-only shell
reads of an unsupplied file. Discover current tool schemas; use fresh contexts
rather than inherited parent turns. Ambient system/repository instructions may
still apply. Send only the bounded role packet and explicitly permit needed
read-only file/check commands; prohibit nested model CLI substitutes. Wait for
actual returned reports before dispatching adjudication. Native tools may not
appear fully in CLI JSON output, so preserve returned reports/identities and
available raw dispatch evidence without claiming hidden-context inspection.
[Official subagent guidance](https://learn.chatgpt.com/docs/agent-configuration/subagents)
is capability documentation; the probe establishes only its observed file-read
and independent-dispatch behavior, not factory review correctness.


## PR follow-up capabilities

Use the shared [follow-up contract](../skills/factory-follow-pr/references/follow-pr.md)
for required capabilities, current permissions, coverage and external-action rules.

The Phase 11 read-only fresh-session probe observed private repository metadata,
main ref and branch search through the connected GitHub service. Prefer that
connector when sufficient; discover its actual tools in the current session.
Its PR search did not prove complete all-state PR coverage. Supplement that gap
through an actually available authorized paginated API/CLI before an absence or
retry claim. The probe did not establish checks/log/review coverage or execute
any PR/push; write exposure and reported repository permission were observations.
