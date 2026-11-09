# Concurrent factory evaluation

Evaluator-only criteria. Keep this guide out of worker prompts. Use synthetic
factory homes and sample Git repositories outside plugin source. Do not inspect
personal factory records, use live channels, publish PRs or send messages.

Install/refresh the candidate package and verify its manifest version in fresh
Codex and Claude Code sessions. New factories use config schema 2 and work schema
4; legacy-specific cases retain config schema 1 until explicit upgrade.

## Independent work and exclusion

Give each host the same neutral task: exercise saved-work orchestration on two
independent synthetic items, record a small progress checkpoint for each, inspect
their state, and end the runs. Separately request an overlapping attempt on one
claimed item. Supply raw inputs and task scope, not expected results or helper
implementation. Retain actual prompts, commands, outputs, plugin roots/versions,
owner identities, state snapshots and limits outside the source repository.

Verify distinct run/item bindings, interleaved saved progress, scoped permissions
and no lost updates. Same-item overlap must refuse without dispatching competing
engineering work or changing the original run. A busy transaction may be retried;
it must reread state. A finished/blocked run releases only its execution/intake
claims. Another item's live run remains unaffected. Item status and run lifecycle
are separate. Ambiguous resume/answer requests must not choose arbitrarily.

## Repository resources and resumption

Use two distinct native prepared worktrees and branches in one sample repository.
Verify actual source/common Git directory, worktree-specific directory and branch
identity. Reservation success for independent items must survive finish/wait and
be reused by a fresh run of the same item, including in the other host. A second
item must not reserve the same worktree via an alias, the same branch, or the
source checkout. Partial multi-resource reservation failure must commit none.
Missing/unknown worktree or prior worker state must remain an honest block.

Shell-created sample worktrees establish helper Git identity behavior only;
they do not prove native host creation/adoption/lifecycle behavior. Record that
distinction. No resource deletion/release or cleanup is implied by finishing a run.

## Intake, failure and upgrade

Provide raw synthetic channel observations and source captures. Competing channel
or receipt claims must not block unrelated items. Independently claimed channels
can commit without whole-factory revision conflicts. Routing a related capture
must preserve a foreign-owned item's lifecycle and increment its version so old
decisions cannot silently commit. Stale routing inventory requires reconsideration.
Incomplete collection leaves canonical bytes unchanged.

Exercise owner death versus alive/unknown state, lost replies before/after atomic
replacement, exact retries, step limits and proposed/uncertain/confirmed action
history using synthetic evidence only. Verify no blind external replay and no
cross-item action mutation. Fresh sessions should resume the intended item with
its original artifact/resource references.

Explicitly upgrade synthetic schemas 1, 2 and 3 after legacy owners stop. Compare
original config/snapshot backup bytes, items, sources, cursors, scopes, artifacts,
old invocation/config hashes and old event values with schema-4 legacy context.
Test interruption after snapshot replacement but before config replacement; retry
must finish with the same originals. Corruption or alive/unknown ownership refuses
without replacing original files. Old plugin versions must reject upgraded
schemas. Existing paths and registry selection remain valid; setup rechecks host
capabilities instead of recreating the factory.

Record which scenarios ran in real fresh hosts, which ran only in helper tests,
and which remain untested. Passing unit/static checks is not model behavior,
native worktree creation, real PR publication or scheduled execution evidence.
