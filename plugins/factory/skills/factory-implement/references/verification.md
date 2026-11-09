# Verification facts

Every positive or negative execution claim requires supporting observations.
Missing or incomplete records establish unverified execution; they establish
neither that a check ran nor that it did not run. Distinguish a recorded result,
an observed failure to launch or permission denial for a particular attempt,
and an execution whose evidence is unavailable. Evidence about one attempt does
not establish what happened in other attempts. Apply this distinction throughout
reports, tables, summaries and next actions.

Read raw results before describing them. Required timestamps come from the
observed clock or execution metadata; omit optional dates instead of estimating
them. Preserve the scope and limits of each observation.

## Small command capture

Existing host output/logs with equivalent provenance are sufficient. Otherwise,
run a prescribed check through the loaded package's recorder:

```sh
uv run --isolated --frozen --no-dev --project <plugin> python <plugin>/scripts/factory_verify.py --cwd <checkout> --output <new-external-directory> --input <relevant-file> --input <relevant-config> -- <executable> <arguments>
```

Declare the relevant code, tests, configuration and lockfiles; inputs are files,
relative to the command directory or absolute. Parent-traversal components (`..`)
are rejected; supply an unambiguous path instead. Symlinks are read again after
execution so retargeting is not hidden by resolving them once. This is bounded
input evidence, not a fingerprint of the entire repository or undeclared
dependencies. Keep the
new evidence directory outside the source checkout. The recorder refuses to reuse
an existing directory, invokes the supplied argv without a shell, captures raw
stdout/stderr, and writes `command.json` last. It records actual UTC start/end,
monotonic duration, exit code or launch error, Git HEAD/status when available and
before/after SHA256 of the declared files. No environment or credentials are
collected. Normal tool permissions still apply.

Read the final metadata and raw output. Missing or unreadable `command.json`
means capture is incomplete; retain partial files and use a new directory for a justified retry.
A recorded nonzero exit is a failed check. An observed launch error establishes
that the particular attempt failed to launch, without establishing the history
of other attempts. Changed or unreadable inputs require explaining/rechecking
the affected result, even if the command returned zero. Equality of endpoint
hashes does not prove files never changed transiently during execution; keep the checkout stable while checking.
This recorder does not decide whether coverage is sufficient or the feature works.

## Bind claims to the content actually checked

A commit ID alone does not identify dirty tested bytes. Preserve the relevant
input hashes, actual base/HEAD/diff and check outputs. When checks precede a commit,
compare the relevant tested bytes and inputs with the committed result. If they
match, say the checks ran before commit on identical content; never claim a
post-commit execution. A changed commit ID does not itself invalidate equal bytes,
and an unchanged HEAD does not prove dirty inputs stayed equal. Missing inputs or
provenance limit the claim; do not silently broaden a partial-file comparison.

Report recorded successes or failures, observed launch/permission failures and
unverified execution separately. Missing evidence is an uncertainty to retain,
not an outcome or a new claim of nonexecution. A passing helper suite does not
prove a model behavior fix or a service path absent from the exercised scope.
Fresh-host behavioral evaluation retains its own actual outputs, failure/stop and resume evidence. Reviewers correct unsupported claims
from the underlying records rather than vote them through. Reuse equivalent
valid evidence; do not rerun identical checks for decorative timestamp alignment.
