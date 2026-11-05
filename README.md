# Local software factory

`factory` is a local plugin for Codex and Claude Code. Version `0.2.2` provides
`factory-setup` and `factory-status`, backed by one shared configuration helper.
The orchestrator and work-processing roles are not implemented yet.

Setup asks for a private configuration destination, runtime/save-data location,
Slack workspace and channels, and repository discovery roots. It preserves those
choices on reruns. Changing the runtime location requires an explicit choice and
does not move existing records. Real configuration and runtime data stay outside
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
describe supported fields. The helper uses Python 3.11+ and `uv`; its pinned
PyYAML dependency runs in an isolated environment outside the plugin package.

## Verify

Run from this checkout:

```sh
uv run --isolated --frozen --project plugins/factory ruff check --no-cache --config plugins/factory/pyproject.toml plugins/factory/scripts tests
uv run --isolated --frozen --project plugins/factory ruff format --check --no-cache plugins/factory/scripts tests
uv run --isolated --frozen --project plugins/factory mypy --cache-dir /tmp/ai-eng-mypy --config-file plugins/factory/pyproject.toml plugins/factory/scripts/factory_config.py
PYTHONDONTWRITEBYTECODE=1 uv run --isolated --frozen --project plugins/factory python -m unittest discover -s tests -v
```

Skill behavior also requires fresh-session tests in each host. See
[phase results](docs/phase-results.md) for executed checks and limitations, and
[the implementation plan](docs/implementation-plan.md) for later phases.
