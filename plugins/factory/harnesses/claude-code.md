# Claude Code harness reference

This document contains host-specific instructions for agents running Factory.
For installation, updates and troubleshooting, see the
[Claude Code user guide](https://github.com/gobriansteele/ai-eng/blob/main/docs/claude-code.md).

## Run and resume

In restricted evaluation launchers, native Read/Glob and literal Bash commands
beginning with uv or python3 were separately permitted; ls/cat were not. These
are observed launcher-specific permissions, not defaults for Claude sessions.
Use allowed Read/Glob for startup files, then the loaded package's prescribed
literal uv helper command when its actual permission allows it. A denied ls/cat
is not evidence that all Bash or uv execution is unavailable. Preserve the denial
and distinguish any separately successful helper execution. Do not bypass a
denial of the underlying access/action or change the allowlist; command-pattern
permissions do not revoke separately granted Read/Glob or helper commands.
With that prefix allowlist, issue each command separately using literal paths and
values. A separate permitted `python3 -c 'import uuid; print(uuid.uuid4())'` returns
the run ID; paste the observed UUID into the literal uv helper call. Do not prefix
that call with RID/P assignments, command substitution or a compound command chain.
The observed rejected compound begin command did not test the literal uv mutator;
report it denied only if an actual literal permitted-form helper call fails.

In a fresh CLI session:

```text
/factory:factory-run Use configuration <factory-home>/config.yaml and the loaded package's fixtures/synthetic-resume.json. Single step: save the next-step decision, then stop at an unavailable role. Report the canonical snapshot path.
```

Resume after the original CLI stops with the same config and no fixture. Normal
bounded use defaults to at most three saved steps; explicit `--max-steps` is 1..10.
The helper discovers the long-lived `claude` CLI ancestor; use that observed PID
rather than a transient helper/shell. Process-inspection or mutation denial is a
block until the specific command can run through normal permission review. Do
not infer owner death or automatically relax permissions.

For desktop, launch one foreground CLI worker from the selected factory home and
wait for its completion, passing the explicit configuration and bound:

```sh
claude -p '/factory:factory-run Use configuration <factory-home>/config.yaml. Resume saved work with --max-steps 3; finish and report the result.'
```

Use the actual config path. Include a selected synthetic fixture only for a new
synthetic test. Preserve the CLI's normal reviewed tool permissions; noninteractive
permission denial must be reported rather than bypassed. If the current desktop
cannot launch/authorize this foreground invocation, report the gap. Its CLI owns
the entire bounded run; desktop service and transient shell PIDs do not. This is
not a daemon or schedule. Either harness can resume after the prior CLI has
finished or actually stopped; destination tool permissions must be checked anew.


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

Claude Code independently exposes Slack capabilities under names such as
`mcp__claude_ai_Slack__slack_read_channel`, `slack_read_thread` and
`slack_search_public`; discover actual names/schema in this session, rather than
copying Codex connector names.
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

Check the current host's actual tools and `claude --help`. Claude Code `2.1.310`
advertises `--worktree [name]`; current
[official worktree documentation](https://code.claude.com/docs/en/worktrees)
also describes `EnterWorktree` where available. The native CLI starts a worktree
session on its own branch. Observe actual source/base, common Git directory,
returned path and branch; defaults or a plausible name are not ownership proof.
Creation and usable exit persistence must be exercised before relying on them;
help/documentation alone is not a successful native-creation test.

The documentation distinguishes interactive cleanup prompts from `-p` runs,
which retain their worktrees and may retain locks. Do not call `ExitWorktree`,
remove/unlock, discard or clean up resources as a side effect of this phase.
Interactive runs must retain a checkout needed for handoff. Existing session
locks are not permission to take over: verify that the previous worker stopped
and the checkout has the expected ownership/content. Factory runtime and exact
result evidence stay outside the worktree even when a host retains it. A missing
checkout or unverifiable lifecycle yields a concrete block, not an inferred
successful handoff. Native lifecycle/cleanup claims must be labeled documented
until actually tested.

Avoid launching a second factory invocation merely to create a worktree. A host
orchestrator can prepare a dedicated checkout before the foreground factory CLI
starts, then supply its actual path/provenance. A verifiable prepared worktree
from either host can be adopted; it need not have a Claude branch name. Inspect
canonical code refs, prior preparation artifacts and Git worktree list first.
Verify matching common Git directory, intended base, exclusive branch, observed
HEAD/status and retained content. Do not use the source checkout, duplicate
resources or silently fall back to shell `git worktree add`. Missing actual
native tools/permissions with no prepared checkout saves implement/blocked with
the precise capability request; do not change host settings or bypass permissions.

Launch the owning CLI from the factory home when useful, pass the explicit
config and prepared worktree as context, and run scoped edits/checks with explicit
working directories. If entering a native worktree changes access to runtime,
verify both paths remain usable with normal permissions before editing. Keep
canonical saves with the orchestrator; save authorization/resources before code
mutation. After the old CLI finishes, a fresh Codex or Claude session can read
those durable paths and exact diff/content/check evidence. Further edits require
a verified deliberate owner handoff saved before mutation; explaining a completed
review-stage result does not require new branch ownership or new resources.


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

The 2026-11-05 CLI probe observed native `Agent` with
`subagent_type: "general-purpose"`, two distinct fresh agent IDs and real `Read`
calls on an unsupplied file. Discover the current schema and omit any context-fork
option; provide the explicit packet rather than a prior transcript. Normal CLI
test permissions must include `Agent` alongside required local read/check tools;
missing permission is a capability block, not grounds to bypass checks or change
settings. `--forward-subagent-text` was supported by the tested CLI and surfaced
child evidence in stream output; preserve that when available. Native
[Claude subagents](https://code.claude.com/docs/en/sub-agents) provide separate
contexts. The probe establishes actual dispatch/file reads, not review quality.


## PR follow-up capabilities

Use the shared [follow-up contract](../skills/factory-follow-pr/references/follow-pr.md)
for required capabilities, current permissions, coverage and external-action rules.

A read-only fresh-session probe without GitHub MCP used the existing
authenticated `gh api --method GET` with pagination for branch/all-state PR
listings. This is the demonstrated fallback when this host lacks a sufficient
connector, not a connection inherited from Codex. Discover actual current access
before use. The probe did not establish checks/log/review coverage or execute
any external write; CLI authentication alone grants no push/draft authorization.


## Reporting capabilities

Use the shared [reporting contract](../skills/factory-report/references/reporting.md)
for report-only invocation, draft reuse, exact destination/permission and retries.
Discover this Claude session's own Slack/Jira MCP connections and operation
schemas. The documented Slack reads do not establish reply/comment writes or
complete destination history, and Codex connections are not inherited. Report
actual missing operations; no live message delivery is claimed.


## Native scheduling and maintenance

Read the bundled [scheduling runbook](../skills/factory-run/references/scheduling.md)
when the user requests a native schedule. No schedule/fire is established by CLI
acceptance. factory-maintain uses this host's actually available lifecycle and
recorded resource identity; preview or archive copy grants no removal permission.
CLI /loop and Desktop persistent schedules have different lifetimes; verify this
machine's Desktop capability rather than inferring it from the CLI version.
Worktree retention/cleanup differs between interactive and -p sessions; an absent
native removal mechanism remains a block, never a shell-delete fallback.
