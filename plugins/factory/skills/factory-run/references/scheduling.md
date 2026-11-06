# Native scheduling

Use native scheduling only when the user requests it. Do not install cron,
a daemon, a queue or a cloud-to-local state adapter.

At schedule creation, resolve the selected factory once through the
[default resolution contract](../../factory-setup/references/configuration.md#default-resolution-and-pinning),
using the remembered default unless the user supplies a config/local override.
Stop on an invalid selection with its setup/repair instruction. Save the returned
absolute config path and, when non-null, absolute local override in the scheduled
prompt. Do not ask for a config path already remembered by setup. The scheduled
work must keep these pinned paths even if the user later changes the default;
changing an existing schedule's factory requires an explicit schedule update.

Use the installed shared skill with that explicit absolute config and scope:

```text
Use factory-run with configuration /absolute/factory-home/config.yaml. Resume the selected item with its saved execution mode and scope; finish at its endpoint or a genuine blocker.
```

When resolution returned a local override, add `Use local override
/absolute/factory-home/local.yaml` with its actual path. When it returned null,
omit the local override; the explicit config prevents inheriting a later default's
local file. Do not put `resolve the default` in a saved schedule prompt.

Codex can name `$factory-run`; Claude Code can use `/factory:factory-run`. Keep
the scheduled prompt this small: role, permission, persistence and reporting rules
live in the shared skill. Use the persistent factory home as the local project,
not a disposable code worktree. Native notification settings remain separate from
the workflow prompt: notify completion/failure/needed action,
keep unchanged checks quiet.

## Host choices

Codex local tasks need the computer and app running with the local project
available; a cloud/web task cannot directly use this local factory home. When
requested, discover the current native automation tool/schema and inspect existing
tasks before proposing an update, rather than hand-writing automation records or
duplicating a task. Follow the host's recurring-task choice/default; do not assume
an independent project schedule or override heartbeat selection. The CLI alone
does not provide the desktop schedule-management surface. These are documented
capabilities, not an executed scheduler test. [Codex automations](https://learn.chatgpt.com/docs/automations).

Claude Desktop persistent local tasks use the selected folder, saved permission
mode/model and connections; the app must remain open and the machine awake.
Documentation lists Desktop 1.1.5368+; installed CLI 2.1.310 does not establish
Desktop availability. Discover the actual Scheduled/Routines UI and current
capability before promising it. [Claude Desktop scheduled tasks](https://code.claude.com/docs/en/desktop-scheduled-tasks).

Claude Code `/loop` is session-scoped. Recurring tasks expire after seven days;
fixed-task resume and dynamic-loop restoration differ. A running loop is not
proof of independent persistent two-week scheduling. [Claude Code scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks).

## Preflight, activate and pause when requested

First exercise a fresh manual native session on the selected home: installed
plugin/version, exact config/runtime/repo access, this host's actual integrations,
native workers, cached isolated helper runtime and verified CLI ownership. Setup
observations are historical. Missing unattended tools/permissions are precise
blocks; never broaden them automatically. Accepted CLI overlap/interruption and
cross-host tests support persistence, not scheduler execution.

After explicit activation/cadence approval, use the native tool/UI to review the
exact home/prompt/timezone/permissions and existing tasks; enable only one host
against a home. Observe the first requested read-only scheduled run and its real
saved state/owner/tool results. Schedules do not imply bedtime delegation or authorize unrelated new items.
Reuse only the selected item’s saved execution mode and scope.

Pause through the native tool/UI and verify no new invocation starts. Pausing a
schedule does not kill an already running CLI: wait for its finish or an explicit
stop, then verify ownership before switching hosts. The new host uses the SAME
config/runtime and fresh own capabilities, not transferred credentials or chat
memory. No schedule activation/pause/switch test has been executed by this release.
