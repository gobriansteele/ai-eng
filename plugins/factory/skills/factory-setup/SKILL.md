---
name: factory-setup
description: Set up a factory home and remembered default, revise its choices, or recheck connection readiness in the current harness. Does not run work or schedule it.
---

# Factory setup

Use the loaded plugin root (two directories above this skill's directory), shared
[configuration contract](references/configuration.md), and its synthetic example.
Identify this harness from observed host context; never guess an integration exists.

For an existing factory, resolve its configuration once using the contract's
[default resolution](references/configuration.md#default-resolution-and-pinning).
Use an explicit user config/home when supplied. For a requested new factory,
use its chosen home or propose `~/factories/default` outside source and target
repositories. Let the user change that home without requiring a separate config
path, runtime path or invented factory ID. A config that does not yet exist in
an explicitly chosen new home is a creation request: prepare its YAML through
this setup flow, then validate it and run setup with the explicit path. Do not
mistake that request for a broken existing factory or select another home.
Derive `<home>/config.yaml` and `<home>/runtime/`, storing
`runtime_path: ./runtime`. Show both resolved absolute paths before writing.
Use `default` as the initial factory ID unless the user chooses another identity.
Do not search the machine for private configs. An invalid existing explicit
config or registered default stops resolution: show the precise repair, or offer
setup of an explicitly chosen valid config with `--set-default`; never silently create a
replacement or reset existing records.

New factories use config schema 2 from the configuration reference. For an existing
schema-1 factory, explain that concurrency requires an explicit in-place upgrade
through factory_work.py upgrade under the persistence contract. It backs up config
and work.json, retains history/resources and does not require a new factory home.
Stop legacy owners first; never auto-upgrade during a readiness-only recheck.
If the desktop has no verified CLI owner, use the harness foreground CLI handoff
for the explicit upgrade/setup request; do not start unrelated factory-run work.
After an explicitly requested upgrade, recheck capabilities using this setup flow.

Read existing choices before asking for missing ones. Preserve fields and all
runtime records, channel starts, cursors, work, and other harness reports on reruns.
Existing configurations keep their paths; never relocate them to adopt this layout.
Explicit separate configuration/runtime paths and a user-supplied `--local`
override remain supported. If an explicit config lacks a runtime choice, ask
whether to use `./runtime` beside it or another location; wait for that choice
before saving. A different runtime
requires explicit user choice; never move or discard old records. Pass the
helper's `--confirm-runtime-change` only after that choice. Missing choices confer
no action authorization.

Discover the current harness's available integration tools and connection state.
Use its relevant harness guide only for observed host-specific details. Slack is
optional: direct chat intake needs no workspace or channels. For chat-only setup,
keep `workspace_id: null`, `channels: []`, and the initial intake start null.
If Slack is wanted but unavailable, report the dependent collection gap and allow
direct intake to proceed; do not substitute a different service. Discover accessible
workspaces/channels and resolve user names or links to stable workspace/channel
IDs. Confirm choices with the user; never hardcode a workspace or channel. An
unknown workspace ID stays null, even if a channel ID is known. Validate read
access to each selected channel. Removing a channel stops future intake, retaining
its previous records. Adding one establishes its own start when verified.

Check capabilities separately with actual tools: Slack identity, channel discovery
and selected channel reads, pagination, thread replies, available Slack write
tools, Jira project read and write tools, GitHub read and write tools, and local
execution. For pagination/replies, use a real read where available; explain an
untested or unavailable check. For writes, inspect exposed tool capability and
permissions without posting/creating anything. Record whether evidence proves a
read or only tool availability; never imply a write was executed or approved.
Do not create external artifacts just to test setup. Missing capabilities produce
partial setup and blocked dependent work, not invented success. Reports contain
short evidence descriptions, never message excerpts, secrets, or token data.
Apply the contract's minimum evidence for each key. A denied or unverified
required probe is `not_checked` or `unavailable`, never `observed` with a caveat.
On a handoff, reuse established workspace/channel IDs and independently verify
channel access in this harness. State that the identity mapping was reused; do
not claim fresh identity discovery or transfer another harness's permissions.
A successful configured Jira project read establishes `jira_read`; optional issue
or site probes can have limitations without invalidating that observed project read.

Ask for repository discovery roots and optional initial target paths. Run bounded
read-only discovery via the helper. Report inaccessible roots/repositories as
unavailable. Show discovered repositories; read and respect their actual local
instructions before any later work, rather than replacing them with plugin rules.
Setup does not run product code or write in those repositories.

Use the shared helper to validate the proposed YAML before saving choices. Use
`setup` with evidence from this harness to record partial or ready setup; see the
contract for commands and report format. Preserve any selected `--registry`
override on the setup write as well as resolution; tests must not write the real
registry after resolving a temporary one. The helper creates only setup metadata,
not a workflow or watcher. The first successful setup remembers this config and
its local override as the shared default. Rechecking it retains that default;
setting up another factory leaves the existing default unchanged unless the user
explicitly chooses `--set-default`. An existing config can be registered in place;
no relocation is needed. Show the selected default and any deliberate change.
Display effective configuration, absolute runtime path,
checked capabilities and remaining blocks. The final readiness summary must match
the helper's `setup_status` and `blocked` output. If evidence is insufficient,
correct its statuses and rerun `setup` before reporting the resulting readiness;
do not describe a helper-ready report as partial only in prose. Make clear that configuration limits
are agent instructions and tool permissions still apply. No schedule, model calls,
repository publication, external writes, or factory work is part of setup.
