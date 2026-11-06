# Phase 11 live trial preparation

The local candidate is ready; live execution awaits Brian's specific approval
and completion of the offline Phase 11 checks. This document is a proposal,
not authorization or a claim that GitHub CI ran.

Destination: private `gobriansteele/ai-eng`. The evaluator prepared two isolated
branches from accepted source `f018d454e92bfeea8fd0c77d110e9250cf28c695`:

| Branch | Prepared full commit |
| --- | --- |
| `codex/factory-trial-base` | `e2b3478f6b56ee3224e904f6b196807e3755e4f7` |
| `codex/factory-trial-head` | `82bb47127160a9c70140e3047799151f69f3f487` |

The base adds a tiny standard-library Python task selector, tests and a workflow
that runs only for PRs targeting the trial base. The head deliberately introduces
one selector defect plus its regression test. A draft PR between these branches
is an evaluator-created existing-PR input; it does not claim that factory
implementation or review passed. Main is not a target of the trial.

The prepared COMMENT review identifies the same selector defect as the failing
test. The permitted correction, if approved, is one comparison expression in
`trial/task_filter.py`. Tests and workflow stay fixed. The factory must investigate,
record one pending batch, obtain applicable local authorization, implement in an
owned checkout, count the returned correction once, review its exact bytes, and
only then use applicable commit/push permission to update this same PR. A bounded
content authorization may identify this exact prepared correction before the
resulting commit exists; the eventual recorded scope must bind the actual commit
to the approved content and conditions with evidence.

The proposal includes two expected hosted CI runs, one initially and one after
the correction. Each has one job, a two-minute timeout and read-only contents
permission. Private Actions minutes may be consumed. Checkout is pinned to
[actions/checkout v7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1),
verified at commit `3d3c42e5aac5ba805825da76410c181273ba90b1`, with credential
persistence disabled. It uses the normal PR merge-ref checkout; record that tested
revision separately from the PR head and verify both associations. No merge,
deployment, undraft, extra comment, rerun, schedule, settings change or cleanup
is included.

Local preparation and independent parent verification used existing Python 3.12.8.
The baseline passed two tests; the seeded head failed exactly one of three; a
separate non-Git corrected copy passed all three. That corrected copy is evaluator
material, excluded from worker inputs. No corrected Git commit was manufactured.
Hosted execution, runner availability and destination action policy remain to be
verified; exposed permission metadata is not proof of a completed write.

Exact artifacts are under `/private/tmp/ai-eng-phase11/live-proposal/`:
`proposal.md`, `candidate.json`, `base.patch`, `head.patch`, `proposed-fix.patch`,
`pr-title.txt`, `pr-body.md`, `review-comment.txt`, `commands.json`,
`parent-validation.json`, and `remote-evidence.json`. The standalone candidate
clone is evaluator preparation, not a factory-owned worktree. No live Honor
repository or factory records are involved.

Fresh read-only probes succeeded in both hosts. Codex used its GitHub connector;
Claude used its existing authenticated `gh api --method GET` capability. Both
observed the same private repository and main commit with push/admin permission
metadata. Claude paginated all branches and all PR states; Codex's PR search did
not expose full coverage. Use a complete exact-branch query before any write,
refresh all refs and stop on a collision or changed target. Probe evidence is in
`/private/tmp/ai-eng-phase11/{codex,claude}/github-probe/`.
