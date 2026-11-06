---
name: factory-review
description: Independently review a saved factory implementation, adjudicate evidenced findings and return a bounded fix batch or exact-revision review outcome to factory-run. Use for internal factory review and re-review; no PR, push or canonical state writes.
---

# Factory review

Review the selected item's actual implementation through `factory-run`. Read the
[review and fix contract](references/review.md) before dispatch. Use its saved
sources, actionable plan, design/skip, repository instructions, implementation
and verification evidence; verify that the checkout matches the exact result
bytes. Missing inputs or worker dispatch produce an honest review-stage block,
not a self-review or assumed pass. Explicit offline evaluation stays offline.

Use two actual fresh independent reviewers with complementary concerns, then a
separate fresh adjudicator. Keep reviewer conclusions isolated until both return.
Only unresolved disputes go to three further fresh independent panelists; do not
run a second team on a clean review. Resolve host dispatch through the current
harness guide, discovering actual available capabilities rather than inventing
worker tool names. Never simulate multiple roles inside one context. Workers
return durable reports and paths; only the verified invocation orchestrator saves
canonical state. Reviewers, adjudicator and panelists cannot change product code.

Read actual reports and supporting evidence before accepting dispositions.
Supported defects go to the engineer in one batch; every dismissed finding needs
a reason and evidence. A reproducible serious defect cannot be dismissed solely
by majority vote. Record real limits or human questions instead of manufacturing
consensus. Revision/content changes invalidate affected verdicts, including dirty
changes with the same HEAD; fresh review must identify the corrected result.

Initial implementation and review use zero fix rounds. Internal review and later
PR follow-up share two total rounds, following the pending-batch and completion
rules in the contract. Never reset the counter or start an untracked correction.
The implementer follows its existing authorization, ownership and check contract;
review findings grant no new edit permission. No local commit is required for
review. Dirty accepted code is identified by base/HEAD, full diff and exact file
hashes; `reviewed_commit` remains unset for it.

Return immutable reports and a concrete recommendation: fix batch, precise
block/human wait, or pass for the exact reviewed content. After two unsuccessful
rounds, return the remaining issues, attempted fixes and concrete question for
Brian. A pass hands off to available `factory-follow-pr` for exact-content and
authorization checks; no push,
PR, external messages, merge or cleanup follows from this skill.
