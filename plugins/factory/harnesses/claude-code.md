# Claude Code

Verified with Claude Code `2.1.310`. From the local checkout:

```sh
claude plugin marketplace add "$PWD" --scope local --json
claude plugin install factory@ai-eng-local --scope user --json
claude plugin list --json
claude
```

The marketplace declaration remains in this project's ignored local settings.
In a fresh session:

```text
/factory:factory-setup Set up a factory using my Slack MCP connection. Let me choose the channels and runtime/save-data location. Save the configuration at <private-config-path>.
```

To inspect it later:

```text
/factory:factory-status Use configuration <private-config-path>. Show the loaded version and setup readiness.
```

For this local marketplace, the installed plugin reports `readFromFolder` pointing
to the checkout's `plugins/factory` directory. It also records a versioned cache.
Fresh installed sessions read that source folder; the acceptance runs did not use
`--plugin-dir`.

Change both host manifests and the helper project version together, refresh the
lockfile, then run:

```sh
claude plugin marketplace update ai-eng-local
claude plugin update factory@ai-eng-local --scope user --json
claude plugin list --json
claude
```

Verify the version and loaded root in a fresh session. Updates were exercised
through `0.2.2`; do not edit installed caches manually. For separate source-only
development, `claude --plugin-dir ./plugins/factory` and `/reload-plugins` are
supported, but should not mask an installed-plugin test.

Setup checks this harness's actual connections and permissions. The tested
GitHub MCP connection was unavailable; the existing authenticated `gh` CLI
provided read-only repository checks. No replacement integration was installed.
For noninteractive tests, read tools and local helper execution must be permitted
explicitly. Missing permissions must produce unverified capability evidence,
not an inferred success or an automatic permission change.

See [phase results](../../../docs/phase-results.md) for observations and limits.
References: installed CLI help,
[plugin creation](https://code.claude.com/docs/en/plugins/create), and
[local marketplaces](https://code.claude.com/docs/en/plugins/create-marketplace).
