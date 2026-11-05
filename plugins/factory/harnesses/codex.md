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
