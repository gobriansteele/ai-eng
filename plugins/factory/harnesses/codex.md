# Codex

Verified with `codex-cli 0.166.0-alpha.6`. From the local checkout:

```sh
codex plugin marketplace add "$PWD" --json
codex plugin add factory@ai-eng-local --json
codex plugin list --marketplace ai-eng-local --json
codex -C "$PWD"
```

In a fresh session:

```text
Use $factory-setup. Set up a factory using my Slack MCP connection. Let me choose a factory home and the channels. Show the resolved config.yaml and runtime/ paths before writing.
```

To inspect it later:

```text
Use $factory-status with configuration <factory-home>/config.yaml. Show the loaded version and setup readiness.
```

Codex loads an installed copy under
`~/.codex/plugins/cache/ai-eng-local/factory/<version>`. Change both host manifests
and the helper project version together, refresh the lockfile, then repeat
`codex plugin add factory@ai-eng-local --json`. Verify the version in a fresh
session. This procedure refreshed the tested installations through `0.2.3`;
a source edit alone is not evidence that the installed copy changed.

Setup discovers the current session's integration tools. The accepted live run
used Slack, Jira, and GitHub connectors; it did not perform external writes.
Read checks and exposed write tools are distinct evidence. Dependency bootstrap
may need network/cache access; a sandbox-denied dependency download is a blocker
until a permitted environment or cached locked dependency is available.

CLI fresh-session behavior was exercised. Desktop restart/picker behavior was
not separately exercised. See [phase results](../../../docs/phase-results.md).

References: installed CLI help and
[OpenAI plugin packaging](https://developers.openai.com/plugins/build/plugins).

## Run and resume

In a fresh CLI session:

```text
Use $factory-run with configuration <factory-home>/config.yaml and the loaded package's fixtures/synthetic-resume.json. Single step: save the next-step decision, then stop at an unavailable role. Report the canonical snapshot path.
```

Resume after the original CLI stops with the same config and no fixture. For
normal bounded use request at most three steps (default), or `--max-steps 1..10`.
The shared skill discovers the exact long-lived `codex` CLI ancestor through
`factory_work.py owners`; its helper/shell PID is not the owner. Process
inspection denied by sandbox is unknown: retry the specific command through the
normal host approval mechanism, preserving sandbox settings. Never infer death.

For desktop, dispatch one foreground CLI worker and wait for completion:

```sh
codex exec --skip-git-repo-check --approve-for-me --sandbox workspace-write -C '<factory-home>' 'Use $factory-run with configuration <factory-home>/config.yaml. Resume saved work with --max-steps 3; finish and report the result.'
```

Use an existing selected home and substitute the actual config path. For a new
synthetic test include the explicitly selected fixture in that prompt. `--approve-for-me` retains workspace-write and routes specific required commands
through automatic approval review; it does not disable the sandbox or grant
external-action permission.
The desktop `codex app-server` lifetime is unrelated to the invocation and is
never accepted as owner. If dispatch/inspection cannot run with permitted tools,
report that gap. No background service or scheduler is added. A CLI owner is
valid until the bounded worker stops; switching to Claude requires it to finish
or stop first. Saved approvals are scoped evidence, not transferred tool grants.
