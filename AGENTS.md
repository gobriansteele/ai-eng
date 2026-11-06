# AI engineering plugins

Factory is a plugin for Codex and Claude Code. Read README.md for the user workflow
and CONTRIBUTING.md for development and verification.

Keep shared skill instructions under `plugins/factory/skills/`. Host-specific
metadata belongs in the manifests and marketplace catalogs; runtime integration
instructions belong in `plugins/factory/harnesses/`. Maintain one shared workflow.

Write user documentation for someone installing and using the plugin. Keep agent
contracts with their skills and test criteria in the evaluation guides. Do not
add implementation plans, build diaries or internal progress reports to the repo.

Run the checks in CONTRIBUTING.md after helper changes. Validate changed JSON and
skill frontmatter. Test changed skill behavior in fresh Codex and Claude Code
sessions, including a failure or stop case. For packaging changes, verify actual
installation and refresh in both hosts. Report executed checks and limitations
with the change; static validation alone does not establish model behavior.

Use synthetic fixtures for development. Keep credentials, real configuration,
source messages and runtime records outside the plugin source. Add files only
when the implementation needs them.
