# Local software factory

`factory` is a local plugin for Codex and Claude Code. The current source provides
`factory-setup`, `factory-status`, `factory-run`, `factory-watch` and
`factory-route`, backed by shared typed helpers. The orchestrator collects bounded
read-only Slack intake, saves and routes source threads, and resumes legacy work.
Investigation and later roles are not implemented.

Setup asks for one factory home (suggested: `~/factories/<factory-id>`) and derives
`<home>/config.yaml` and `<home>/runtime/` with `runtime_path: ./runtime`. It shows
both resolved paths before writing, then asks for Slack workspace/channels and
repository discovery roots. Existing configurations and explicit separate paths
remain supported. Reruns preserve choices; changing runtime requires an explicit
choice and does not move records. Real configuration and runtime stay outside
this repository.

Each harness checks its own integrations and writes a separate capability report.
Missing required evidence produces partial setup. Available write tools do not
grant permission to use them. The trial supports one active work item, two total
fix rounds, approval-required external actions, disabled merge/deployment, and
preview-only cleanup. Workflow enforcement remains an agent responsibility.

## Install and use

Follow the [Codex guide](plugins/factory/harnesses/codex.md) or
[Claude Code guide](plugins/factory/harnesses/claude-code.md). Both hosts load the
same `plugins/factory/skills/` source, with separate manifests and marketplace
catalogs. An authenticated Slack MCP connection is required independently in each
host; installation does not transfer connections or credentials.

The [synthetic configuration](config/example.yaml) and
[configuration contract](plugins/factory/skills/factory-setup/references/configuration.md)
describe supported fields. Copy the example into your selected home as
`config.yaml` before setup or validation; validating the source example in place
correctly rejects its `./runtime` inside this checkout. For example, after copying
and editing it, validate with:

```sh
uv run --isolated --frozen --no-dev --project plugins/factory python plugins/factory/scripts/factory_config.py validate --config "<factory-home>/config.yaml"
```

Pass that same explicit config path to setup/status in either host. Advanced
layouts may use a separate `runtime_path` or `--local <yaml>` filesystem override.
The helper uses Python 3.11+ and `uv`; its pinned
PyYAML dependency runs in an isolated environment outside the plugin package.

## Run saved work

Use `factory-run` with the same explicit config path in either host. With no
synthetic input, it invokes `factory-watch` under one durable invocation owner,
then routes saved intake/resumes work to a bounded stop. Watch reads every ready
configured channel with fixed bounds, a 24-hour overlap clamped to setup start,
fully paginated channel history and available reply discovery, plus complete
tracked-thread rechecks. Collection and cursor commit together. Repeated reads
dedupe by workspace/channel/timestamp. New replies retain their observed root and
full available thread; earlier captures remain immutable history.

Coverage is explicitly bounded. Search indexing/late visibility, private-channel
and bot coverage are not guaranteed. Without reply discovery, older untracked
roots can be missed. Use an explicit `--import-thread` request naming configured
channel and root/link to import historical context without changing live cursors.
Edits/deletions alone do not initiate intake in v1. See the
[collection contract](plugins/factory/skills/factory-watch/references/collection.md).
Setup owns channel selection and starts; adding/removing channels preserves work
and existing cursors. Partial/missing setup blocks affected channels.

The shared router reads full saved threads, trigger boundaries, relevant inventory
and current read-only Jira/ownership/code evidence for live sources. Missing access
remains incomplete. It returns findings; the orchestrator saves explicit updates
and stops at the missing investigator, a human/existing-work wait, no available
work or its bound. No external writes occur.

For offline demonstrations select `--source <path>` under `fixtures/sources/`,
legacy `--fixture <path>`, or `--collection <synthetic-json>` under `fixtures/watch/`.
These explicit synthetic/offline requests never call integrations. Raw normalized
watch fixtures exercise pagination, independent channels, failure/retry, overlap,
tracked replies and import; reviewer criteria are in
[watcher evaluation](docs/watcher-evaluation.md).

Sources include conversation, open ticket without code work, a feature, uncertain
duplicate, three requests, related thread, unavailable Jira, active code work and
a later thread capture. Repeat the identical source path to test exact replay;
route `open-ticket.json` before `related-thread.json` to test attachment. Separate
[evaluation criteria](docs/router-evaluation.md) are for reviewers, not router input.

Legacy `--fixture` input remains supported: `synthetic-item.json` and
`synthetic-resume.json` contain post-intake metadata with no original source body.
They now wait honestly for that missing evidence, preserving fix counts/scopes/
actions/cursors. Single-step saves one decision; bounded invocation defaults to
at most three (`--max-steps 1..10`). New explicit sources are routed even when a
previous item's missing-investigator block remains active.

One durable run token covers the whole CLI invocation across helper calls. The
[shared persistence contract](plugins/factory/skills/factory-run/references/persistence.md)
explains owner discovery, CLI commands, retries and repair. Desktop dispatches
one foreground bounded CLI worker in the same harness; its app service cannot
own an invocation. Missing process inspection or dispatch is a visible block.

The canonical `<runtime>/state/work.json` is the inbox and work authority. It
atomically commits inventory, one active ID, source receipts, collection cursors,
history and invocation bookkeeping. Source-only states remain schema 2; the first
verified-owner collection atomically migrates to schema 3. Schema 1/2 inspect
writes nothing; begin migrates 1 to 2 preserving history/handoff metadata.
Both hosts need this phase's plugin to resume schema 3. Corruption requests repair,
never reset. Immutable captures preserve earlier evidence and unrouted intake.

## Verify

Run from this checkout:

```sh
uv run --isolated --frozen --project plugins/factory ruff check --no-cache --config plugins/factory/pyproject.toml plugins/factory/scripts tests
uv run --isolated --frozen --project plugins/factory ruff format --check --no-cache plugins/factory/scripts tests
uv run --isolated --frozen --project plugins/factory mypy --cache-dir /tmp/ai-eng-mypy --config-file plugins/factory/pyproject.toml plugins/factory/scripts
PYTHONDONTWRITEBYTECODE=1 uv run --isolated --frozen --project plugins/factory python -m unittest discover -s tests -v
```

Skill behavior also requires fresh-session tests in each host. See
[phase results](docs/phase-results.md) for executed checks and limitations, and
[the implementation plan](docs/implementation-plan.md) for later phases.
