---
name: factory-setup
description: Set up or revise a local software factory configuration, verify available connections in the current harness, and report partial readiness. Use for initial setup, channel selection changes, or rechecking setup; does not run work or schedule it.
---

# Factory setup

Use the loaded plugin root (two directories above this skill's directory), shared
[configuration contract](references/configuration.md), and its synthetic example.
Identify this harness from observed host context; never guess an integration exists.

Start with a configuration path the user supplied or previously established in
this conversation. For a new factory, use the supplied home or ask once when it
is missing, suggesting `~/factories/<factory-id>` outside source and target
repositories. Derive
`<home>/config.yaml` and `<home>/runtime/`, storing `runtime_path: ./runtime`.
Show both resolved absolute paths before writing; the selected home establishes
both choices. Do not add a home setting or search the machine for private configs.

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
Use its relevant harness guide only for observed host-specific details. If Slack
MCP is unavailable, explain how to connect/authenticate a Slack MCP server in this
harness and rerun; do not substitute a different service. Discover accessible
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
contract for commands and report format. The helper creates only setup metadata,
not a workflow or watcher. Display effective configuration, absolute runtime path,
checked capabilities and remaining blocks. The final readiness summary must match
the helper's `setup_status` and `blocked` output. If evidence is insufficient,
correct its statuses and rerun `setup` before reporting the resulting readiness;
do not describe a helper-ready report as partial only in prose. Make clear that configuration limits
are agent instructions and tool permissions still apply. No schedule, model calls,
repository publication, external writes, or factory work is part of setup.
