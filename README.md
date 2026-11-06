# Factory

## What it is

Factory is a Claude Code and Codex plugin that takes work from Slack through
investigation, planning, implementation and independent review to a draft pull
request. It saves progress locally so you can stop and resume across sessions.

## How to install it

You need Claude Code or Codex with plugin support, **Python 3.11+** and
**[uv](https://docs.astral.sh/uv/getting-started/installation/)**. Connect Slack in
the host you choose; setup checks access to Slack, GitHub and any linked Jira issues.

### Claude Code

Run these commands **inside a Claude Code session**:

```text
/plugin marketplace add gobriansteele/ai-eng
/plugin install factory@ai-eng-local
```

Choose **user scope** in the installation prompt, then start a fresh session.

### Codex

Run these commands **in your terminal**:

```sh
codex plugin marketplace add gobriansteele/ai-eng --ref main
codex plugin add factory@ai-eng-local
```

Start a fresh session. The registered marketplace name is `ai-eng-local`, including
when installed from GitHub. For updates and host-specific instructions, see the
[Claude Code guide](docs/claude-code.md) or [Codex guide](docs/codex.md).

## How to set it up

In Claude Code:

```text
/factory:factory-setup Help me set up a factory using my Slack connection.
```

In Codex:

```text
Use $factory-setup. Help me set up a factory using my Slack connection.
```

Setup helps you choose a factory home, Slack channels and repository roots, plus
Jira settings if relevant. For example, you could choose `~/factories/work`;
keep it outside your code repositories. Setup shows the resolved paths, creates
`config.yaml` and `runtime/` in that home and checks the current host's access.
You do not need to copy or hand-edit a YAML template.

Keep the configuration path: it identifies your factory in later sessions.
Configuration, findings and work history stay in your chosen home. Each host needs
its own connections and setup checks, even when sharing that home. See the
[configuration reference](plugins/factory/skills/factory-setup/references/configuration.md)
for supported settings.

## How it runs

Start with one real bug report or feature request from a configured Slack channel.
Using the example home above, replace `<channel-id>` and `<thread-link>`:

**Claude Code**

```text
/factory:factory-run Use configuration ~/factories/work/config.yaml.
Import thread <thread-link> from configured channel <channel-id> with --import-thread.
Investigate the request and show me the next action.
```

**Codex**

```text
Use $factory-run with configuration ~/factories/work/config.yaml.
Import thread <thread-link> from configured channel <channel-id> with --import-thread.
Investigate the request and show me the next action.
```

`factory-run` coordinates the work; the component skills handle each part:

| Part | Skills | What happens |
| --- | --- | --- |
| Intake and routing | `factory-watch`, `factory-route` | Read configured Slack threads and identify actionable work. |
| Investigation | `factory-investigate` | Examine relevant code, reproduce problems and save findings. |
| Planning and design | `factory-plan`, `factory-design` | Define expected behavior, checks and technical approach; ask about consequential choices. |
| Implementation and review | `factory-implement`, `factory-review` | Make authorized changes in a dedicated worktree, run checks and obtain independent review. |
| PR follow-up | `factory-follow-pr` | Publish an approved draft PR and examine CI and review feedback. |
| Updates | `factory-report` | Prepare local Slack and linked Jira update drafts. |
| Supporting tools | `factory-status`, `factory-retro`, `factory-maintain` | Inspect progress, propose improvements and preview maintenance. |

Each run advances up to three workflow steps by default, saving its progress. It
stops earlier if it needs your answer or cannot proceed. Once the run stops, invoke
`factory-run` again with the same configuration and ask it to resume. Include your
answer if it left a question.

Without an explicit import, runs check configured channels for new work and
continue saved work. Imports let you select older threads directly. You can resume
in either host after checking setup there.

Factory handles one active item at a time. It asks before editing code, committing,
pushing, opening a PR or sending an update. Updates stay local drafts by default;
Factory does not merge or deploy. To check progress without advancing work, use
`/factory:factory-status` in Claude Code or `$factory-status` in Codex with your
configuration path.

You can run Factory manually or configure a
[recurring run](plugins/factory/skills/factory-run/references/scheduling.md) in your
host. Installation does not start a schedule. The current release has passed
offline checks; live PR publishing and scheduled execution still need validation.

## Troubleshooting

- **Skill missing:** start a fresh session and check installation in the
  [Claude Code guide](docs/claude-code.md) or [Codex guide](docs/codex.md).
- **Setup incomplete:** rerun setup with your existing configuration. It identifies
  missing connections or permissions and preserves saved work.
- **No new work:** confirm the channel was selected during setup. Use
  `--import-thread` with its channel ID and thread link for an older request.
- **Resume is blocked:** inspect `factory-status` with the same config. Answer the
  saved question or resolve the reported access or environment issue, then resume
  after the previous run stops. Repeating a run does not resolve a missing answer.

For development and verification, see [Contributing](CONTRIBUTING.md).
