# Learning records

Use the existing retrospective role to connect actual failures to evaluated
improvements. Records live under `<runtime>/retros/candidates/`; raw transcripts,
private configuration and outputs stay outside plugin source. Canonical work
state, counters, item ownership and engineering waits are unchanged.

Resolve and pin config/local once as usual. Run the loaded package's helper:

```sh
uv run --isolated --frozen --no-dev --project <plugin> python <plugin>/scripts/factory_learning.py inspect --summary --config <absolute-config>
uv run --isolated --frozen --no-dev --project <plugin> python <plugin>/scripts/factory_learning.py record --config <absolute-config> --input <absolute-event.json>
```

Pass `--local <absolute-local>` only when already pinned. Start with `--summary`
for compact keys, status, unreviewed counts and latest issue summaries; read
matching candidates with `inspect --key <key>` for full history/evidence. Missing
or corrupt records are
errors, never permission to replace history. Empty inventory is valid. The
helper locks candidate writes, atomically preserves all earlier events, captures
evidence-file hashes and stamps its actual clock. Do not hand-edit records.

## Observation and identity

At completion or a genuine stop, capture a meaningful failure, user correction,
unexpected required intervention or expensive detour when evidence supports one.
Do not create a candidate per turn, ordinary progress, expected human decision or
routine success. A safe host denial is evidence of a capability limit, not proof
the model ignored its instructions. Existing guidance may need a behavior test
instead of more instructions.

Inspect candidate summaries and evidence first. Choose a stable lowercase key
for the trigger/root cause and expected behavior, such as
`routine-stage-continuation-question`. Version, session and item IDs belong in
the evidence, not the candidate key: the same problem across runs is one issue.
Similarity of wording alone is insufficient to merge distinct causes. Reuse a
stable event ID on an uncertain retry. Changed content or evidence with that ID
is rejected; a genuinely new observation has a new ID.

An observation input has exactly these fields:

```json
{
  "id": "run-two-continuation-observation",
  "key": "routine-stage-continuation-question",
  "kind": "observation",
  "details": {
    "summary": "An authorized run waited for another continue reply",
    "trigger": "Plan and authority were complete; required tools were available",
    "expected_behavior": "Continue implementation under the saved grant",
    "source_version": "Factory candidate revision and host version"
  },
  "evidence": ["/absolute/path/to/original-output.txt"]
}
```

Evidence paths must identify actual nonempty readable files. Preserve those
files; the helper retains their absolute paths and observed SHA256, not a copy
of their private contents. Cite the relevant line range/command in the summary
or source report, and retain original failed output alongside successful retries.
Changed or unavailable evidence prevents an exact retry; reconcile the saved
record and restore its original evidence before retrying rather than changing
the event identity to evade the mismatch.

## Adjudication and fix evaluation

Separate a supported failure from a hypothesis, host limit, user-directed scope,
already-fixed behavior or expected wait. Read counterevidence and current
instructions/code. An adjudication event uses the same top-level fields with
`kind: "adjudication"`; its `details` are exactly:

```json
{
  "disposition": "accepted",
  "reason": "The saved grant and output establish a routine approval question",
  "acceptance_scenario": "Resume a synthetic authorized run; exercise a real missing-fact stop separately"
}
```

Allowed dispositions are `accepted`, `rejected` and `already_fixed`. Evidence is
still required. Rejecting a candidate retains it and its rationale; new evidence
does not silently overturn that disposition. A later reasoned adjudication can.
Capture the concrete failure scenario and a stop/counterexample before a fix.
Expected outcomes belong in evaluator criteria, outside worker prompts.

After a separately authorized change, evaluate the candidate against actual
outputs. Use `kind: "evaluation"` and these exact detail fields:

```json
{
  "outcome": "passed",
  "change": "PR URL or exact candidate revision",
  "reason": "Describe the actual exercised behavior and remaining limits"
}
```

Outcomes are `passed`, `failed` and `inconclusive`. Evaluation requires an
accepted candidate; a pass becomes `verified`, failure `regressed`, and an
inconclusive result remains `accepted`. A linked code change or passing static
suite does not alone prove model behavior improved. Follow the repository's
fresh-host, failure/stop and resume requirements and retain the actual outputs.

New observations after any disposition are counted as
`unreviewed_observations`, preserving the prior outcome. Compare their source
revision and execution evidence with the linked fix before claiming recurrence:
reviewing an older pre-fix transcript later is not a regression. If new evidence
does show the failure on the fixed behavior, adjudicate it and record a failed
evaluation with that evidence. Repeated runs and every disposition remain
readable; never delete rejected evidence or reset history to get a clean result.

This helper records local evidence; it does not validate a model's causal
judgment or authorize changes, external posts, schedules or self-rewrites.
Accepted improvements enter the ordinary authorized implementation/review flow.
Timing comparisons separate human wait, execution and verification where known;
missing measurements stay unavailable. Quality checks and independent review
remain intact when evaluating a faster approach.
