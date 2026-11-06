# Factory in Codex

## Install from GitHub

In a terminal with the Codex CLI installed:

```sh
codex plugin marketplace add gobriansteele/ai-eng --ref main
codex plugin add factory@ai-eng-local
```

Start a fresh Codex session, then follow [setup in the README](../README.md#how-to-set-it-up).
The registered marketplace name is `ai-eng-local` even when its source is GitHub.
This private repository requires Git credentials with access to it.

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
Use $factory-status with configuration ~/factories/work/config.yaml. Show the loaded version and setup readiness.
```

Use your actual configuration path. Connect Slack in Codex and the GitHub/Jira
tools needed for your work. Connections in Claude Code do not carry over.

## Update

Let any active Factory run finish. In a terminal:

```sh
codex plugin marketplace upgrade ai-eng-local
codex plugin add factory@ai-eng-local
```

Start a fresh session and check status again. Your configuration and saved work
stay in the factory home you chose during setup.

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
| GitHub installation fails | Check that your Git credentials can access this private repository. |
| Setup cannot read a channel or repository | Check this session's connections and permissions for the selected resource. |
| Dependency download fails | Check that `uv` and Python 3.11+ are available and that the required download is permitted. |
| The run reports a permission or worker block | Use `factory-status` to read the missing capability. Resolve it through normal permissions, then resume with the same configuration. |

For source development, see [Contributing](../CONTRIBUTING.md). The packaged
[harness reference](../plugins/factory/harnesses/codex.md) is for agents executing
the workflow.
