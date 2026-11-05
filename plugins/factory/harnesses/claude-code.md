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
/factory:factory-setup Set up a factory using my Slack MCP connection. Let me choose a factory home and the channels. Show the resolved config.yaml and runtime/ paths before writing.
```

To inspect it later:

```text
/factory:factory-status Use configuration <factory-home>/config.yaml. Show the loaded version and setup readiness.
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
through `0.2.3`; do not edit installed caches manually. For separate source-only
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

## Run and resume

In a fresh CLI session:

```text
/factory:factory-run Use configuration <factory-home>/config.yaml and the loaded package's fixtures/synthetic-resume.json. Single step: save the next-step decision, then stop at an unavailable role. Report the canonical snapshot path.
```

Resume after the original CLI stops with the same config and no fixture. Normal
bounded use defaults to at most three saved steps; explicit `--max-steps` is 1..10.
The helper discovers the long-lived `claude` CLI ancestor; use that observed PID
rather than a transient helper/shell. Process-inspection or mutation denial is a
block until the specific command can run through normal permission review. Do
not infer owner death or automatically relax permissions.

For desktop, launch one foreground CLI worker from the selected factory home and
wait for its completion, passing the explicit configuration and bound:

```sh
claude -p '/factory:factory-run Use configuration <factory-home>/config.yaml. Resume saved work with --max-steps 3; finish and report the result.'
```

Use the actual config path. Include a selected synthetic fixture only for a new
Phase 3 test. Preserve the CLI's normal reviewed tool permissions; noninteractive
permission denial must be reported rather than bypassed. If the current desktop
cannot launch/authorize this foreground invocation, report the gap. Its CLI owns
the entire bounded run; desktop service and transient shell PIDs do not. This is
not a daemon or schedule. Either harness can resume after the prior CLI has
finished or actually stopped; destination tool permissions must be checked anew.


For saved-source routing, ask the same `factory-run` entry point to use the loaded
package's `fixtures/sources/open-ticket.json` as `--source` with the explicit
configuration. Follow with `related-thread.json`, then repeat it. Use separate
synthetic homes for independent acceptance; keep all runtime records outside the
plugin. Router judgments are shared across hosts; no host adapter or model call
is embedded in the helper. Use `--summary` on mutations to keep repeated history
out of the model context; read full saved source and relevant inventory before
deciding. Legacy post-intake fixtures now wait for missing source evidence.
