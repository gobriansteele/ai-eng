# Saved source and routing artifact

For config 2/work schema 4, acquire `receipt:<receipt-key>` before semantic routing
and follow the concurrent route JSON in the [persistence contract](../../factory-run/references/persistence.md).
Findings below are unchanged. The wrapper contains id, reason, receipt_id,
routing, items (NEW items only), and inventory_version; no active_item_id.
Existing-item findings commit receipt associations without replacing lifecycle
fields. Associated items get a new version so their owners reconsider new input.
Only an item owner may later change its workflow or grant execution scope.
The wrapper/update behavior described below applies to legacy schemas 1/2/3;
do not use it to overwrite another concurrent run's item.


The `factory_work.py begin --source <absolute-json>` helper validates and saves
a saved source. Explicit --source demonstrations remain synthetic; live
collection writes sources with `synthetic: false` and intake provenance. Common
source fields are `synthetic` (boolean), `source_id`
(stable thread identity), `version` (immutable capture identity), `link`,
`available_thread` (ordered objects with `id`, `author`, `text`), `availability`
(what was available or missing), and `evidence` (objects with `id`, `kind`, `text`).
Message/evidence IDs are unique within a capture. Read every message and observation.
The watcher supplies immutable live captures and eligibility/coverage separately
from semantic routing. Preserve existing synthetic fields/digests unchanged.

Direct chat requests use `begin --request <absolute-json>` and the same fields,
with `synthetic: false` for real requests and `direct` provenance instead of
Slack `intake`; see [direct intake](../../factory-run/references/direct-intake.md).
Both surfaces share receipt identity, routing and item preservation below.

The receipt key is compact JSON `[source_id,version]`; its `digest` hashes the
entire normalized source with Python `json.dumps(source, sort_keys=True)` and
SHA256. Read the saved digest rather than calculating a different serialization.
Exact capture replay creates no receipt/work duplicate. Same identity/version
with different content is refused; save later replies as a new explicit version.
All prior captures remain evidence.

Return exactly this JSON shape (values below explain fields, not example judgments):

```json
{
  "source_id": "saved stable source identity",
  "source_version": "saved immutable version",
  "source_digest": "saved receipt digest",
  "covered_message_ids": ["every available message ID"],
  "findings": [{
    "key": "stable-descriptive-item-key",
    "classification": "bug",
    "disposition": "investigate",
    "evidence": ["saved message or evidence ID"],
    "reason": "Why the evidence supports this disposition, and limits",
    "duplicate_check": "incomplete",
    "investigation_brief": "Concrete next questions, or null when unnecessary",
    "proposed_ticket": null,
    "existing_item_id": null
  }]
}
```

Classification: `bug`, `regression`, `feature`, `conversation`, `unknown`.
Disposition: `investigate`, `already_underway`, `verify_existing_work`,
`needs_clarification`, `no_action`. Duplicate check: `complete`, `incomplete`,
`not_applicable`; complete describes the supplied bounded check, not omniscience.
Brief and local ticket proposal are nullable strings. `existing_item_id` is a
saved item ID or null; no-action has no associated work. Findings must be nonempty,
keys unique, references valid, and covered message IDs include the entire available
thread. Validation cannot establish whether the model understood the evidence.

The orchestrator wraps this artifact in a route commit with `id`, `reason`,
`receipt_id`, `routing`, `items` (complete changed/new item records), and nullable
`active_item_id`. It copies existing item records before changing justified fields.
New item IDs use `factory_work.stable_id(source_id, finding.key)`; a new item uses
that source/key, `synthetic` matching its source, and the saved source link. Fresh routed items
start with `fix_rounds: 0`, `approvals: []`, and `pending_actions: []`; never copy
the preservation fixture's illustrative counts or permissions into new work.
Include code/artifact references only when observed in supplied evidence. Routing
does not create a worker, worktree or ownership claim. Every actionable
finding has one updated item; no-action has none. Multiple findings may point to
one evidenced existing item. The helper preserves prior source/Jira links, fix
counts, scopes and actions. It does not choose stages, statuses or worker roles.

For a live source, routing may additionally include `observations`, an array of
objects with exactly `id`, `kind`, `text`, `observed_at` (ISO timestamp), `sources`
(unique external IDs/links, possibly empty for unavailable capability), and
`limitations` (explicit bounded coverage/access limits, or "none observed").
Observation IDs must be unique across all messages/evidence and can be referenced
by findings. They are committed immutably with the routing result. Synthetic
routing rejects nonempty live observations; supplied synthetic evidence remains
its only evidence. Current live reads must identify their actual source and
time, including unavailable-capability observations when duplicate/ownership
checks cannot run. A complete duplicate check describes the stated bounded read.
