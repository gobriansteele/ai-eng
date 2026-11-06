# Factory

## What it is

Factory is a Claude Code and Codex plugin that takes requests from your chat or Slack through
investigation, planning, implementation and independent review to a non-draft pull
request with required CI and automated review resolved. It saves progress locally so you can stop and resume across sessions.

## How to install it

You need Claude Code or Codex with plugin support, **Python 3.11+** and
**[uv](https://docs.astral.sh/uv/getting-started/installation/)**. Slack is optional;
connect it in the host you choose to collect channel requests. Setup checks the
connections needed for your workflow.

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

Setup proposes `~/factories/default/` for your factory's files. You can choose
another location. It creates `config.yaml` and `runtime/` there, helps you select
repository roots and optional Slack channels, and checks your connections.

Factory remembers this choice. Future commands find your factory automatically,
including in a fresh session or the other host. You do not need to supply a
configuration path each time. Each host still needs its own connections.

Your configuration and work history stay in the factory home. A small registry at
`~/.config/ai-eng/registry.json` remembers its location (or under `XDG_CONFIG_HOME`
if you use that setting). Plugin updates leave both intact.

**Already have a factory?** Run setup once with its existing configuration and ask
it to make that your default. For example, in Claude Code:

```text
/factory:factory-setup Use ~/factories/work/config.yaml as my default factory.
```

Existing files and work history stay where they are. For custom paths, a second
factory or lookup details, see the
[configuration reference](plugins/factory/skills/factory-setup/references/configuration.md).

## How it runs

A **work item** is one bug report or feature request that Factory is working on.
A **run** is one invocation of `factory-run`: it reads new input, continues saved
work, saves its progress and stops. A work item can take several runs to finish.

By default, a run continues the selected item through the workflow, saving progress
at each step. It stops for an important unresolved product/architecture decision,
a genuine blocker, or completion. `--single-step` and an explicit `--max-steps`
remain available when you want a bounded run.

Choose how much decision-making to delegate:

| Mode | Behavior |
| --- | --- |
| **Default** | Go end to end; ask important product/architecture questions. |
| **Going to bed** | Explicitly delegate those decisions too; choose a defensible approach and stop only when genuinely blocked. |
| **Restricted** | Pause to approve the implementation plan before edits and the prepared PR before publication. |

For example, in Codex:

```text
Use $factory-run in going-to-bed mode for the course duplication request.
Make the product and engineering decisions needed to finish.
```

In Claude Code, use `/factory:factory-run` with the same request. Modes and scope
are saved per item across resumes. Going-to-bed mode never applies automatically
to unrelated Slack requests. “Investigate only” still limits work to investigation.
Factory reports completion or a needed decision/blocker, without routine approval
check-ins. The host may still show progress, and must remain running to continue.

`factory-run` coordinates these component skills:

| Part | Skills | What happens |
| --- | --- | --- |
| Intake and routing | `factory-watch`, `factory-route` | Read configured Slack threads and identify actionable work. |
| Investigation | `factory-investigate` | Examine relevant code, reproduce problems and save findings. |
| Planning and design | `factory-plan`, `factory-design` | Define expected behavior, checks and technical approach; ask about consequential choices. |
| Implementation and review | `factory-implement`, `factory-review` | Make authorized changes in a dedicated worktree, run checks and obtain independent review. |
| PR follow-up | `factory-follow-pr` | Publish a non-draft PR and resolve required CI and automated review findings. |
| Updates | `factory-report` | Report in the harness and prepare applicable Slack/Jira update drafts. |
| Supporting tools | `factory-status`, `factory-retro`, `factory-maintain` | Inspect progress, propose improvements and preview maintenance. |

Factory works on one selected item at a time. An end-to-end request in default or
going-to-bed mode authorizes its scoped implementation, checks, commits, pushes,
PR publication and necessary fixes. Restricted mode uses checkpoints instead.
Completion means the non-draft PR has passing required checks and resolved
automated review findings on the current head. Factory does not merge or deploy,
and sending Slack/Jira updates still requires specific permission.

### Start in your chat

Describe a bug, idea or requirement directly in your harness:

**Claude Code**

```text
/factory:factory-run Users lose their filters when they return to the results page. Investigate this.
```

**Codex**

```text
Use $factory-run. Users lose their filters when they return to the results page. Investigate this.
```

Factory saves your request and uses the same investigation and planning workflow
as Slack intake. Ideas can start incomplete; Factory asks for the decisions it
needs. Replies and answers continue the saved item across sessions. Results return
in your chat, with no Slack destination required.

Configured Slack channels are still checked during the run. If Slack is unavailable,
Factory reports that gap and can continue with your direct request. You can also
set up Factory without Slack channels.

### Start with a Slack thread

Choose a thread containing a bug report or feature request. An **import** tells
Factory to read that specific thread and save it as input. This lets you choose
an older request instead of waiting for a new message in a configured channel.
Importing does not post to Slack or authorize code changes.

Use the thread's link and its channel ID. The channel must be one you selected
during setup.

**Claude Code**

```text
/factory:factory-run
Use --import-thread to read <thread-link> from configured channel <channel-id>.
Investigate the request and show me the next action.
```

**Codex**

```text
Use $factory-run.
Use --import-thread to read <thread-link> from configured channel <channel-id>.
Investigate the request and show me the next action.
```

You can also start a run without selecting a thread. Factory then checks your
configured Slack channels for new messages and continues any saved work.

### Continue saved work

When a run reaches an explicit limit, needs your answer or encounters a blocker, it
saves its place and stops. After it stops, continue with:

**Claude Code**

```text
/factory:factory-run
Resume saved work.
```

**Codex**

```text
Use $factory-run.
Resume saved work.
```

If Factory asked a question, include your answer. For example, if it asked whether
CSV export should include completed tasks, add: “Include both open and completed
tasks in the export.” It uses that answer with the saved plan; you do not need to
import the thread again or repeat the conversation.

You can continue in a fresh session or the other host. Let the previous run finish
first. When switching hosts, run `factory-setup` to check that host's connections;
it finds the same saved factory.

### Check progress

Status reads saved progress without starting more work. For example:

```text
/factory:factory-status
What is Factory working on, what has it finished, and what does it need from me?
```

In Codex, use `$factory-status` with the same request.

### Run on a schedule

A schedule starts the same `factory-run` request at a chosen interval—for example,
every weekday morning. Each run checks for new Slack input and continues from the
last saved result. The schedule remembers the factory selected when you create
it, even if you later change your default. If Factory needs your answer or approval,
later runs still wait for that response.

Set up recurring execution separately using the
[Factory scheduling guide](plugins/factory/skills/factory-run/references/scheduling.md).
Installing Factory does not create a schedule. Tests with sample work items have
passed; publishing a real PR and running on a schedule still need validation.

## Troubleshooting

- **Skill missing:** start a fresh session and check installation in the
  [Claude Code guide](docs/claude-code.md) or [Codex guide](docs/codex.md).
- **No factory found:** run `factory-setup` to create one or register an existing
  configuration.
- **Saved configuration is missing or invalid:** correct the reported file or use
  `factory-setup` to select the correct configuration as your default. Factory
  stops rather than switching to a different factory.
- **Setup incomplete:** rerun setup. It identifies missing connections or
  permissions and preserves saved work.
- **No new work:** confirm the channel was selected during setup. Use
  `--import-thread` with its channel ID and thread link for an older request.
- **Resume is blocked:** inspect `factory-status`. Answer the
  saved question or resolve the reported access or environment issue, then resume
  after the previous run stops. Repeating a run does not resolve a missing answer.

For development and verification, see [Contributing](CONTRIBUTING.md).
