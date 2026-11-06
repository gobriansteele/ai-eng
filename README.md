# Local software factory

`factory` is a local plugin for Codex and Claude Code. The current source provides
`factory-setup`, `factory-status`, `factory-run`, `factory-watch`,
`factory-route`, `factory-investigate`, `factory-plan`, `factory-design` and
`factory-implement`, `factory-review`, `factory-follow-pr`, `factory-report`,
`factory-retro` and `factory-maintain`,
backed by shared
typed helpers. The orchestrator collects bounded read-only Slack
intake, saves and routes source threads, and resumes legacy work.
It investigates scoped bug/feature reports with durable local evidence and no
product changes. Product planning saves actionable behavior/checks or a decisive
human question. Technical design records justified skips for small clear changes,
resolves consequential architectural questions and produces an implementation
handoff. Explicitly authorized local implementation uses one dedicated code
worktree and saves exact diff/content and verification evidence. Independent
review uses two fresh complementary reviewers, a fresh adjudicator and three
fresh panelists only for unresolved disputes. Accepted corrections share two total
fix rounds with PR follow-up. Draft PR publication requires scoped authorization,
uncertain-action reconciliation and exact reviewed content; follow-up investigates
fresh CI/review activity. Reporting prepares/reuses local originating-thread Slack
and Jira comment drafts without replacing engineering state; exact sends require
scoped authorization and uncertain-post reconciliation. Live delivery is untested;
native scheduling is documented without activation. Retrospectives propose
evidence-based improvements; maintenance defaults to preview, with explicitly
requested additive archive/restore copies. Native deletion is untested.

## Start a manual piece of work

1. In a fresh installed host, ask factory-setup to use your Slack connection and
   choose a factory home, channels and repository roots. Keep its absolute config
   path; the same home resumes across hosts after the previous invocation stops.
2. Select a thread from a configured Slack channel and ask:

   ```text
   Use factory-run with configuration /absolute/factory-home/config.yaml and --max-steps 3. Import this historical thread with --import-thread from configured channel <channel-id>, root/link <thread-root-or-link>. Read the available context, save the work and stop at the actual wait or bounded handoff. Do not implement or publish without applicable authorization.
   ```

   Import preserves the live intake cursor. `--source` is for local synthetic JSON
   files. Jira support enriches linked existing issues and drafts issue comments;
   direct Jira-ticket intake is not an implemented entry point.
3. Read the saved findings/question and answer or authorize the concrete selected
   local implementation when ready. Continue with the SAME config and no fixture.
   Local code permission does not grant commit, push, PR, message, merge or deploy
   permission. Default external updates remain local drafts.
4. Ask factory-report with that config for report-only local drafts; use
   factory-status to inspect the actual stage/wait without advancing work.
   factory-retro reviews evidence and proposes improvements. factory-maintain
   previews recorded resources; no cleanup runs from this quickstart.

Brian owns the real-work trial. Live sends/PR retries, native scheduled execution
and resource deletion remain untested until explicitly exercised. The
[bundled native scheduling runbook](plugins/factory/skills/factory-run/references/scheduling.md)
explains later activation/pause; this release activates none. The
[operational evaluator guide](docs/operational-evaluation.md) records offline checks.

Setup asks for one factory home (suggested: `~/factories/<factory-id>`) and derives
`<home>/config.yaml` and `<home>/runtime/` with `runtime_path: ./runtime`. It shows
both resolved paths before writing, then asks for Slack workspace/channels and
repository discovery roots. Existing configurations and explicit separate paths
remain supported. Reruns preserve choices; changing runtime requires an explicit
choice and does not move records. Real configuration and runtime stay outside
this repository.

Each harness checks its own integrations and writes a separate capability report.
Missing required evidence produces partial setup. Available write tools do not
grant permission to use them. The trial supports one active work item, two total
fix rounds, approval-required external actions, disabled merge/deployment, and
preview-only cleanup. Workflow enforcement remains an agent responsibility.

## Install and use

Follow the [Codex guide](plugins/factory/harnesses/codex.md) or
[Claude Code guide](plugins/factory/harnesses/claude-code.md). Both hosts load the
same `plugins/factory/skills/` source, with separate manifests and marketplace
catalogs. An authenticated Slack MCP connection is required independently in each
host; installation does not transfer connections or credentials.

Finish or stop all active factory CLI sessions before refreshing either plugin.
A refresh can remove a prior versioned cache directory still needed by a running
session. After an interrupted session exits, resume through normal verified-owner
recovery; do not clear its saved token or rewrite state.

The [synthetic configuration](config/example.yaml) and
[configuration contract](plugins/factory/skills/factory-setup/references/configuration.md)
describe supported fields. Copy the example into your selected home as
`config.yaml` before setup or validation; validating the source example in place
correctly rejects its `./runtime` inside this checkout. For example, after copying
and editing it, validate with:

```sh
uv run --isolated --frozen --no-dev --project plugins/factory python plugins/factory/scripts/factory_config.py validate --config "<factory-home>/config.yaml"
```

Pass that same explicit config path to setup/status in either host. Advanced
layouts may use a separate `runtime_path` or `--local <yaml>` filesystem override.
The helper uses Python 3.11+ and `uv`; its pinned
PyYAML dependency runs in an isolated environment outside the plugin package.

## Run saved work

Use `factory-run` with the same explicit config path in either host. With no
synthetic input, it invokes `factory-watch` under one durable invocation owner,
then routes saved intake/resumes work to a bounded stop. Watch reads every ready
configured channel with fixed bounds, a 24-hour overlap clamped to setup start,
fully paginated channel history and available reply discovery, plus complete
tracked-thread rechecks. Collection and cursor commit together. Repeated reads
dedupe by workspace/channel/timestamp. New replies retain their observed root and
full available thread; earlier captures remain immutable history.

Coverage is explicitly bounded. Search indexing/late visibility, private-channel
and bot coverage are not guaranteed. Without reply discovery, older untracked
roots can be missed. Use an explicit `--import-thread` request naming configured
channel and root/link to import historical context without changing live cursors.
Edits/deletions alone do not initiate intake in v1. See the
[collection contract](plugins/factory/skills/factory-watch/references/collection.md).
Setup owns channel selection and starts; adding/removing channels preserves work
and existing cursors. Partial/missing setup blocks affected channels.

The shared router reads full saved threads, trigger boundaries, relevant inventory
and current read-only Jira/ownership/code evidence for live sources. Missing access
remains incomplete. It returns findings; the orchestrator saves explicit updates
and can run the shared investigator within the invocation bound. Investigation
records actual code revision, reproduction commands/output, facts, hypotheses and
unknowns in versioned runtime artifacts. Feature briefs preserve unresolved
product choices for planning. The planner turns findings into expected behavior,
bounded scope and acceptance checks. A clear bug proceeds directly; consequential
product ambiguity saves a question and waits for a direct user answer. Completed
plans advance to the designer when a step remains. Design adds component,
contract, compatibility, sequencing and verification decisions where needed; a
small clear bug can skip a separate design with a durable reason and handoff.
Consequential unresolved architecture/API choices wait for an actual direct user
answer, saved with provenance. Completed/skipped designs advance to the implementer.
It requires applicable explicit selected-item local implementation authorization,
saves authorization/resource ownership before code edits and follows repository
checks in a dedicated worktree. Missing authorization saves a concrete human
request; missing environment/tool capability saves a precise block. Code and
prescribed successful checks hand off to independent review. Supported findings
are adjudicated into one saved pending fix batch. One changed-code return for
verification consumes one shared round, including failed checks; interruptions
resume the same attempt. Exact content is reviewed again after changes. Two
unsuccessful rounds ask Brian for help. A pass hands off to draft PR follow-up,
which verifies exact content and applicable
scoped authorization before publication. It reuses existing PRs, reconciles
uncertain writes and investigates fresh current-head CI/review activity. The same
two rounds cover internal and PR fixes; nothing merges or deploys automatically.

For offline demonstrations select `--source <path>` under `fixtures/sources/`,
legacy `--fixture <path>`, or `--collection <synthetic-json>` under `fixtures/watch/`.
These explicit synthetic/offline requests never call integrations. Raw normalized
watch fixtures exercise pagination, independent channels, failure/retry, overlap,
tracked replies and import; reviewer criteria are in
[watcher evaluation](docs/watcher-evaluation.md).

Sources include conversation, open ticket without code work, a feature, uncertain
duplicate, three requests, related thread, unavailable Jira, active code work and
a later thread capture. Repeat the identical source path to test exact replay;
route `open-ticket.json` before `related-thread.json` to test attachment. Separate
[evaluation criteria](docs/router-evaluation.md) are for reviewers, not router input.

Legacy `--fixture` input remains supported: `synthetic-item.json` and
`synthetic-resume.json` contain post-intake metadata with no original source body.
They now wait honestly for that missing evidence, preserving fix counts/scopes/
actions/cursors. Single-step saves one decision; bounded invocation defaults to
at most three (`--max-steps 1..10`). New explicit sources are routed even when a
previous item is blocked. Older missing-investigator blocks resume when this
role is available, as do old missing-planner and missing-designer blocks.
Completed investigation artifacts are reused across fresh chats. Actual human waits persist until a
relevant answer/evidence arrives. Resume with the same config and a direct
natural-language answer naming the saved item/question (or clearly answering the
selected item's sole pending question); no helper answer flag or new fixture is
needed. New plan/design artifacts save the exact answer/provenance and retain the
earlier question. Product or architectural answers grant no implementation or
external-action permission. Completed design is reused on fresh resume, including
older missing-implementer blocks. An unchanged authorization wait or missing PR-follow-up handoff consumes no
semantic step. Older missing-reviewer blocks resume the available reviewer. Explicit offline resume must remain offline.

For investigation evaluation, copy the tiny deliberately broken local sample
outside plugin source into a disposable Git checkout. Use the raw reports under
`fixtures/investigate/` and follow the separate
[investigator evaluation](docs/investigator-evaluation.md) for exact setup commands,
review criteria and fresh-chat handoff. Never run probes against installed fixtures.
For planner acceptance, reuse those saved investigations and the reviewer-only
[planner evaluation](docs/planner-evaluation.md). Design acceptance reuses the
accepted bug and adds the two-component sample/raw request under `fixtures/design/`;
see reviewer-only [designer evaluation](docs/designer-evaluation.md) for isolated
setup, human-answer resume and preservation checks. Implementation acceptance
reuses the accepted bug homes and actual saved handoffs; see reviewer-only
[implementer evaluation](docs/implementer-evaluation.md) for authorization waits,
worktree preparation, before/after checks and cross-host preservation. Do not
give reviewer oracles to workers. Independent review acceptance uses separate
controlled stage fixtures and the reviewer-only [reviewer evaluation](docs/reviewer-evaluation.md).
Imported raw requirements/content and scenario bounds are explicitly synthetic;
upstream role completion and review verdicts are never fabricated. Legacy Phase 3
fixtures retain their missing-source wait behavior.

Local edit authorization is saved with exact direct-user provenance in immutable
implementation reports; product/design answers alone do not grant it. Local
commit requires separate explicit authorization. One preparation checkpoint
records actual source/common Git directory/base, dedicated worktree/branch and
worker identity before code mutation; it consumes a semantic step. Resolve
creation/adoption and lifecycle through the current harness guide. After an
interruption or deliberate owner handoff, reconcile the same checkout, branch
and result bytes instead of creating replacements. Final evidence lives outside
the disposable code checkout, including the full diff and changed file bytes and
hashes when HEAD is dirty. `reviewed_commit` stays unset for dirty code even after
independent review; the accepted artifact identifies full base/HEAD plus exact
diff/file hashes. Only
a clean exact reviewed commit may populate that field.
Initial implementation consumes no fix round; approvals and external-action
ledgers remain unchanged.

One durable run token covers the whole CLI invocation across helper calls. The
[shared persistence contract](plugins/factory/skills/factory-run/references/persistence.md)
explains owner discovery, CLI commands, retries and repair. Desktop dispatches
one foreground bounded CLI worker in the same harness; its app service cannot
own an invocation. Missing process inspection or dispatch is a visible block.

The canonical `<runtime>/state/work.json` is the inbox and work authority. It
atomically commits inventory, one active ID, source receipts, collection cursors,
history and invocation bookkeeping. Source-only states remain schema 2; the first
verified-owner collection atomically migrates to schema 3. Schema 1/2 inspect
writes nothing; begin migrates 1 to 2 preserving history/handoff metadata.
Both hosts need this phase's plugin to resume schema 3. Corruption requests repair,
never reset. Immutable captures preserve earlier evidence and unrouted intake.

Phase 11 source adds `factory-follow-pr`. Its
[shared contract](plugins/factory/skills/factory-follow-pr/references/follow-pr.md)
defines exact draft requests, authorization, pending-action reconciliation and
fresh remote coverage. Synthetic saved observations live in `fixtures/follow-pr/`
under the plugin; the [evaluator guide](docs/follow-pr-evaluation.md) keeps acceptance
criteria outside role context. Installation and actual both-host/live acceptance
are recorded separately in phase results; source capability is not live proof.

Reporting can be requested without advancing engineering: “Use factory-report with
configuration <factory-home>/config.yaml; report-only, local drafts.” Normal runs
also draft at meaningful saved progress/waits when capacity remains, and reuse an
unchanged request instead of proposing duplicates. Read the
[reporting contract](plugins/factory/skills/factory-report/references/reporting.md)
and [offline evaluator guide](docs/reporter-evaluation.md) for actual evidence and
limits. No invocation itself grants Slack/Jira send or workflow-transition permission.

## Verify

Run from this checkout:

```sh
uv run --isolated --frozen --project plugins/factory ruff check --no-cache --config plugins/factory/pyproject.toml plugins/factory/scripts tests
uv run --isolated --frozen --project plugins/factory ruff format --check --no-cache plugins/factory/scripts tests
uv run --isolated --frozen --project plugins/factory mypy --cache-dir /tmp/ai-eng-mypy --config-file plugins/factory/pyproject.toml plugins/factory/scripts
PYTHONDONTWRITEBYTECODE=1 uv run --isolated --frozen --project plugins/factory python -m unittest discover -s tests -v
```

Skill behavior also requires fresh-session tests in each host. See
[phase results](docs/phase-results.md) for executed checks and limitations, and
[the implementation plan](docs/implementation-plan.md) for later phases.
