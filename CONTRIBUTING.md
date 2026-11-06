# Contributing

Start with the [README](README.md) for the user workflow. This guide covers changes
to the plugin itself.

## Source layout

| Path | Contents |
| --- | --- |
| `plugins/factory/skills/` | Shared skills and their runtime contracts |
| `plugins/factory/scripts/` | Python helpers for configuration, saved work and intake |
| `plugins/factory/harnesses/` | Agent instructions for host-specific execution |
| `plugins/factory/fixtures/` | Synthetic inputs for behavior tests |
| `tests/` | Python unit tests |
| `docs/` | Installation guides and behavior evaluation criteria |
| `.agents/` and `.claude-plugin/` | Plugin marketplace catalogs |

## Develop locally

Clone this repository and install [uv](https://docs.astral.sh/uv/getting-started/installation/)
with Python 3.11 or later. Run the commands below from the repository root.

Claude Code can load the source directly for development:

```sh
claude --plugin-dir ./plugins/factory
```

For Codex, register the checkout and install its plugin:

```sh
codex plugin marketplace add "$PWD"
codex plugin add factory@ai-eng-local
```

The development and GitHub catalogs share the name `ai-eng-local`. Check your
registered source before switching between them; the [Claude Code](docs/claude-code.md)
and [Codex](docs/codex.md) guides explain how. Use a separate factory home with
synthetic data for tests. Do not test against personal or team runtime records.

## Check helper changes

```sh
uv run --isolated --frozen --project plugins/factory ruff check --no-cache --config plugins/factory/pyproject.toml plugins/factory/scripts tests
uv run --isolated --frozen --project plugins/factory ruff format --check --no-cache plugins/factory/scripts tests
uv run --isolated --frozen --project plugins/factory mypy --cache-dir /tmp/ai-eng-mypy --config-file plugins/factory/pyproject.toml plugins/factory/scripts
PYTHONDONTWRITEBYTECODE=1 uv run --isolated --frozen --project plugins/factory python -m unittest discover -s tests -v
```

For documentation changes, check commands, relative links and Markdown formatting.
Model runs are unnecessary unless the change affects skill behavior.

## Check skill behavior

Use fresh sessions in both hosts. Exercise the changed behavior, a failure or stop
case, and resumption from saved work. Keep prompts, outputs and runtime evidence
outside this repository; report what ran and what remains untested with the change.
Evaluation guides contain expected results and must stay outside the worker's
prompt so a test measures behavior rather than repetition of an answer.

| Area | Evaluation guides |
| --- | --- |
| Execution modes | [Decisions, checkpoints and completion](docs/execution-modes-evaluation.md) |
| Agent selection | [Dispatch, capability limits and resume](docs/agent-selection-evaluation.md) |
| Intake | [Watcher](docs/watcher-evaluation.md), [router](docs/router-evaluation.md) |
| Understanding the request | [Investigator](docs/investigator-evaluation.md), [planner](docs/planner-evaluation.md), [designer](docs/designer-evaluation.md) |
| Code and review | [Implementer](docs/implementer-evaluation.md), [reviewer](docs/reviewer-evaluation.md) |
| Delivery and operations | [PR follow-up](docs/follow-pr-evaluation.md), [reporter](docs/reporter-evaluation.md), [maintenance](docs/operational-evaluation.md) |

Synthetic tests do not establish live publishing or scheduled execution. Live
tests need a specific target and authorization for the actions they will perform.

## Release a change

Before pushing changes to the shipped plugin to `main`, bump its version.
Keep the versions in both plugin manifests and
`plugins/factory/pyproject.toml` aligned, and refresh `plugins/factory/uv.lock`.
Validate changed JSON and skill frontmatter. Install or update the package in both
hosts, then verify the loaded version and behavior in fresh sessions. Do not edit
installed caches to make a check pass.

Keep the README focused on installation and use. Document implementation contracts
alongside the relevant skill, not in the onboarding instructions.
