# AI engineering plugins

This repository contains the local software factory plugin for Codex and Claude
Code. Read `docs/implementation-plan.md` for the design and
`docs/phase-results.md` for implemented capabilities and verification evidence.

Keep shared skill instructions under `plugins/factory/skills/`. Put host-specific
metadata and invocation details in the manifests, marketplace catalogs, and
`plugins/factory/harnesses/` guides. Maintain one shared workflow across hosts.

Deliver reviewable tranches. Review the actual changes and execution evidence
before moving to the next tranche. The design document records requirements;
it does not grant permission for external actions.

Run the lint, formatting, strict typing, and unit checks in `README.md` after
helper changes. Validate changed JSON and skill frontmatter. Test skill behavior in fresh Codex
and Claude Code sessions, including a failure or stop case. When packaging
changes, demonstrate installation and refresh in both hosts. Record commands,
actual results, and any blocked checks in `docs/phase-results.md`; static checks
alone do not establish working behavior.

Use synthetic fixtures. Keep credentials, real configuration, source messages,
and runtime records outside the plugin source. Add files only when needed by the
current implementation.
