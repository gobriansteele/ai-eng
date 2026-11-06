# Factory in Claude Code

## Install from GitHub

Inside a Claude Code session:

```text
/plugin marketplace add gobriansteele/ai-eng
/plugin install factory@ai-eng-local
```

Choose user scope to make Factory available across projects. Start a fresh session,
then follow [setup in the README](../README.md#how-to-set-it-up).

Alternatively, install from a terminal:

```sh
claude plugin marketplace add gobriansteele/ai-eng --scope user
claude plugin install factory@ai-eng-local --scope user
```

This is a private repository. Your machine needs Git credentials with access to
it. If adding the marketplace fails, verify repository access before retrying.
For an SSH-based setup, the source can be `git@github.com:gobriansteele/ai-eng.git`.
See Claude Code's [installation documentation](https://code.claude.com/docs/en/discover-plugins)
for authentication and scope details.

## Check the installation

Open `/plugin` and check the Installed tab, or run `claude plugin list` in a
terminal. In a fresh Claude Code session, ask:

```text
/factory:factory-status Use configuration ~/factories/work/config.yaml. Show the loaded version and setup readiness.
```

Use your actual configuration path. Slack, Jira and GitHub access come from this
Claude Code session's connections; installing Factory does not connect accounts.

## Update

Let any active Factory run finish. In a terminal:

```sh
claude plugin marketplace update ai-eng-local
claude plugin update factory@ai-eng-local --scope user
```

Start a fresh session and check status again. Your chosen factory home stores the
configuration and work history separately from the installed plugin.

## Replace a development installation

Run `/plugin marketplace list` and inspect the source for `ai-eng-local`. If it
points to a local checkout, updating it will not switch it to GitHub.

After the current Factory run stops, use `/plugin` → Marketplaces to remove that
local catalog. Claude Code shows which plugins will be uninstalled before you
confirm. Then use the GitHub installation commands above. Keep your factory home
and reuse its configuration; do not rerun setup with a new home to recover work.

## Troubleshooting

| Problem | Check |
| --- | --- |
| Factory commands are missing | Confirm Factory is enabled in `/plugin`, then start a fresh session. |
| Installation exists only in one project | Inspect its scope. User scope makes it available across projects. |
| Setup cannot read Slack | Connect Slack in Claude Code and verify access to the selected channel. |
| A helper cannot run | Check `uv --version` and `python3 --version`; allow the specific required command through normal permission review. |
| A run needs a tool that is unavailable | Read the saved blocker with `factory-status`. Connect or authorize that capability, then resume with the same configuration. |

For source development, see [Contributing](../CONTRIBUTING.md). The packaged
[harness reference](../plugins/factory/harnesses/claude-code.md) is for agents
executing the workflow.
