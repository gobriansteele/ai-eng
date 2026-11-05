# Local software factory

`factory` is a local plugin for Codex and Claude Code. Version `0.3.0` provides
`factory-setup`, `factory-status` and `factory-run`, backed by shared typed helpers.
The orchestrator saves and resumes synthetic post-intake work; live intake and
work-processing roles are not implemented yet.

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

Use `factory-run` with the same explicit config path in either host. A new Phase 3
example requires an explicitly synthetic fixture from the loaded package;
`fixtures/synthetic-item.json` is ordinary input and `synthetic-resume.json` tests
preserved fix counts, approval scope and pending-action fields. These fixtures
represent what happens after intake. Future schedules invoke the orchestrator
with configuration, with live intake added in later phases.

Single-step saves one decision; normal invocation defaults to at most three
saved decisions (`--max-steps 1..10`). Both stop at a wait or missing role. The
current expected result is stage `route`, status `blocked`, required role
`factory-route`; no worker or external action is simulated.

One durable run token covers the whole CLI invocation across helper calls. The
[shared persistence contract](plugins/factory/skills/factory-run/references/persistence.md)
explains owner discovery, CLI commands, retries and repair. Desktop dispatches
one foreground bounded CLI worker in the same harness; its app service cannot
own an invocation. Missing process inspection or dispatch is a visible block.

The canonical file is `<runtime>/state/work.json`, with item, events and run
metadata committed together through atomic replacement. This Phase 3 layout
refines the plan's suggested separate record/events/runs files to avoid split
commits. Schema version 1 supports one synthetic saved item; multiple routed
items require a later compatible migration. Existing setup and cursor files are
untouched. Corruption requests repair preserving files; it never resets work.

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
