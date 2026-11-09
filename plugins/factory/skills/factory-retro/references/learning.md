# Learning records

Learning candidates connect failures to evaluated improvements under
`<runtime>/retros/candidates/`; canonical engineering state stays unchanged.
Use the loaded plugin and pinned config/local paths:

```sh
uv run --isolated --frozen --no-dev --project <plugin> python <plugin>/scripts/factory_learning.py inspect --summary --config <absolute-config>
uv run --isolated --frozen --no-dev --project <plugin> python <plugin>/scripts/factory_learning.py record --config <absolute-config> --input <absolute-event.json>
```

Add `--local <absolute-local>` only when pinned. Match through summary inventory;
`inspect --key <key>` returns full history/evidence. Empty inventory is valid.

Input is a JSON object with exactly `id`, `key`, `kind`, `details`, `evidence`.
All text fields are nonempty strings; duplicate JSON members and extra fields fail.

| Field | Contract |
| --- | --- |
| `id` | Stable event identity within the candidate; exact retries reuse it. |
| `key` | `[a-z0-9][a-z0-9-]{0,95}`; identify the cause/expected behavior across runs, not a session or version. |
| `kind` | `observation`, `adjudication`, or `evaluation`. |
| `details` | Exactly the fields for its kind in the table below. |
| `evidence` | Nonempty list of distinct absolute paths to readable, nonempty evidence files. |

| Kind | Exact `details` fields | Values |
| --- | --- | --- |
| `observation` | `summary`, `trigger`, `expected_behavior`, `source_version` | Describe the failure, expected result and observed source revision/version. |
| `adjudication` | `disposition`, `reason`, `acceptance_scenario` | Disposition: `accepted`, `rejected`, `already_fixed`. |
| `evaluation` | `outcome`, `change`, `reason` | Outcome: `passed`, `failed`, `inconclusive`; change identifies the PR or revision evaluated. |

The helper retains evidence paths/SHA256 and supplies `recorded_at` from its clock;
retain the original evidence files outside plugin source. A candidate starts with
an observation. Adjudicate against evidence, counterevidence and current guidance;
existing guidance may need an adherence test rather than another instruction.
Evaluation requires an accepted candidate (`accepted`, `verified` or `regressed`)
and relevant observed behavior: a change or passing static checks alone is insufficient.

## History and outcomes

Inspect before recording; group observations with the same cause and expected
behavior under one key. Record meaningful failures/corrections/detours, not routine
progress or expected scope stops. Each independent observation has a new event ID.
Exact retries preserve event ID, content and evidence bytes. Changed evidence or
content with the same ID fails; inspect/reconcile rather than assigning a new ID
to evade the conflict. Missing requested records/corrupt history fail without replacement.
Writes are locked and atomic; earlier events and rejected decisions remain readable.

Evaluation maps `passed` → `verified`, `failed` → `regressed`, `inconclusive` →
`accepted`. New observations increment `unreviewed_observations` without changing
the prior disposition. Compare source revision and behavior with the linked fix
before declaring recurrence: historical evidence is not a regression. Revise the
outcome through evidenced adjudication/evaluation. Accepted improvements enter
ordinary authorized engineering; local records authorize no fix, external action
or self-rewrite.
