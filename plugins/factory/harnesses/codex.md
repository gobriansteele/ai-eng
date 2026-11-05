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
