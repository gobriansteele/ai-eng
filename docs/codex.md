# Factory in Codex

## Install from GitHub

In a terminal with the Codex CLI installed:

```sh
codex plugin marketplace add gobriansteele/ai-eng --ref main
codex plugin add factory@ai-eng-local
```

Start a fresh Codex session, then follow [setup in the README](../README.md#how-to-set-it-up).
The registered marketplace name is `ai-eng-local` even when its source is GitHub.

The commands require a Codex CLI with plugin management. Check `codex plugin --help`
if your installed version does not recognize them. See the official
[CLI reference](https://learn.chatgpt.com/docs/cli/reference).

## Check the installation

In a terminal:

```sh
codex plugin marketplace list --json
codex plugin list --marketplace ai-eng-local --json
```

The marketplace source should identify `gobriansteele/ai-eng`, not a development
checkout. In a fresh Codex session, ask:

```text
Use $factory-status. Show the loaded version and setup readiness.
```

Factory finds the configuration remembered during setup. Connect Slack in Codex
and the GitHub/Jira tools needed for your work. Connections in Claude Code do not carry over.

## Update

Let any active Factory run finish. In a terminal:

```sh
codex plugin marketplace upgrade ai-eng-local
codex plugin add factory@ai-eng-local
```

Start a fresh session and check status again. Your factory home and default
selection are stored separately from the installed plugin. If you are upgrading
from a version that required a configuration path, run setup once with that path
and ask it to make this your default factory.

For an existing factory from 0.17.x or earlier, plugin installation alone does
not enable concurrency. Ask factory-setup to upgrade that factory in place and
recheck connections. The explicit upgrade backs up config.yaml and work.json,
preserves existing work, and changes their schemas. No new factory home is needed.
Update both hosts before resuming an upgraded factory; older versions reject it.

## Replace a development installation

If the marketplace listing points to a local checkout, stop any active Factory
run and replace that registration:

```sh
codex plugin marketplace remove ai-eng-local
codex plugin marketplace add gobriansteele/ai-eng --ref main
codex plugin add factory@ai-eng-local
```

Start a fresh session. Keep the existing factory home and configuration to resume
saved work.

## Troubleshooting

| Problem | Check |
| --- | --- |
| Factory skills are missing | Confirm the plugin is installed and enabled, then start a fresh session. |
| Marketplace authentication fails | Check the Git credentials configured on your machine. |
| Setup cannot read a channel or repository | Check this session's connections and permissions for the selected resource. |
| Dependency download fails | Check that `uv` and Python 3.11+ are available and that the required download is permitted. |
| The run reports a permission or worker block | Use `factory-status` to read the missing capability. Resolve it through normal permissions, then resume. |

For source development, see [Contributing](../CONTRIBUTING.md). The packaged
[harness reference](../plugins/factory/harnesses/codex.md) is for agents executing
the workflow.
