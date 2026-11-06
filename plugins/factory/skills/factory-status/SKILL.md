---
name: factory-status
description: Show the loaded software factory plugin version, implemented skills, and setup readiness for an explicitly supplied configuration. Use for installation or status questions; does not set up or run work.
---

# Factory status

Resolve the plugin root two directories above this loaded skill's containing
directory. Read `.codex-plugin/plugin.json` and `.claude-plugin/plugin.json` there.
Report name, matching version and absolute loaded root. If either manifest is
missing/unreadable/inconsistent, state the limitation without claiming a verified
installed version. Do not use a remembered version or authoring checkout.

Inspect `skills/` in that package. Implemented capabilities are status, setup,
configuration validation, bounded read-only repository discovery, and saved-work
orchestration through factory-run, semantic routing through
factory-route, and bounded read-only Slack intake/manual imports through
factory-watch. Watch coverage includes declared overlap and tracked-thread
rechecks, with connector/index limitations; it is not guaranteed complete.
Scoped bug/feature investigation and existing-work verification are available
through factory-investigate, with durable evidence and no product changes.
Product planning through factory-plan is available, including durable product
questions and direct-answer resume. Technical design through factory-design is
available, including justified small-change skips, durable architectural questions
and self-contained implementation handoffs. Local implementation through
factory-implement is available with explicit selected-item authorization, one
dedicated code worktree, saved ownership and durable diff/check evidence.
Independent review through factory-review uses two fresh complementary reviewers,
a fresh adjudicator and three fresh panelists only for unresolved disputes, with
exact content evidence and two shared fix rounds. PR follow-up, later work roles
and scheduling are not implemented. With an
established config, optionally use
`factory_work.py inspect` read-only to report the selected active item stage/status/next
action and pending item IDs and snapshot path; never acquire an invocation or change work for status.

Without an explicitly supplied or already established config path, say **Setup
not assessed — provide a configuration path or use factory-setup.** Do not search
the machine or infer there is no private configuration.

With a path, use the loaded package's helper `scripts/factory_config.py status
--config <path> --harness codex|claude-code` via `uv run --isolated --frozen --no-dev --project <plugin-root>
python <script> ...`. Identify the current harness from observed context. Pass
`--local` only if the user supplied an override. Read the setup skill's
[contract](../factory-setup/references/configuration.md) for details when needed.
Report invalid configuration, dependency failures and unavailable repositories
truthfully. Show effective config/runtime path and partial readiness/blocks. Saved
capability observations are dated evidence for this config and host, not a fresh
connection check or permission grant. Setup readiness does not imply implemented
work roles. Keep the result short; create no factory records, connections or schedules.
Dependency bootstrap may write uv's isolated cache outside the package, as the
contract explains; use isolated execution and the frozen lockfile.
