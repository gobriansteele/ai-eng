# Observed collection and persistence

The agent performs authenticated host reads. The helper validates and stores
observations; it does not query Slack, route meaning or assert connector truth.
Use the same `uv run --isolated --frozen --no-dev --project <loaded-package>
python <loaded-package>/scripts/factory_work.py` prefix and explicit config,
harness, optional local override as factory-run. Acquire `begin` first, including
on a fresh production workspace with no synthetic input. Keep its observed owner
PID/run UUID across every integration read and helper mutation.

`watch-plan` is read-only. It returns each configured channel's preserved
`start_at`, saved `lower` (or setup start on first read), suggested `scan_lower`,
tracked roots and blocker. The default overlap is 24 hours before lower, clamped
to setup start; a deliberately different bounded overlap may be supplied and
must be reported. Setup starts are authoritative under
`runtime/setup/<factory-id>/channel-starts.json`; no start means no automatic
history. Removed channels stop collection without deleting records. Re-added
channels preserve their old setup start and watcher cursor.

`collect --owner-pid <observed-cli-pid> --run-id <uuid> --decision <absolute-json>
--expected-revision <read-revision> --summary` accepts exactly these fields:

```json
{
  "id": "stable-collection-operation-id",
  "synthetic": false,
  "mode": "live",
  "workspace_id": "configured workspace",
  "channel_id": "configured channel",
  "start_at": "preserved ISO setup start",
  "lower": "saved cursor as seconds.ffffff",
  "scan_lower": "overlap lower as seconds.ffffff",
  "upper": "fixed upper as seconds.ffffff",
  "complete": true,
  "history": [],
  "discovery": [],
  "discovery_note": "Actual capability, query interval, terminal-page evidence and limits",
  "threads": []
}
```

`history` and optional reply `discovery` are arrays of normalized pages. A page
is `{"cursor": null, "next_cursor": null, "messages": []}`; each message has
`ts`, `thread_ts`, `author`, `text`. Use the root's own timestamp as thread_ts
for an unthreaded root. Cursor null means the first request or a verified terminal
response; preserve every intermediate returned cursor. Empty results require an
observed empty terminal page, not an empty history array. An unavailable discovery
capability uses `discovery: []` and a precise limitation in discovery_note.
A supported discovery read that finds nothing uses one empty terminal page.
A full page/count alone never proves completion. Channel/thread read `oldest`
and `latest` use Slack timestamp strings with exactly six fractional digits.
Pass `1700000040.000000` even at a whole second, never `1700000040`, a float or a
truncated fraction. Preserve the same precision for root/message timestamps.
To fetch full thread context, omit oldest or use the actual root boundary; do
not substitute the live scan_lower and omit earlier replies.

Reply-search `after`/`before` instead uses the current search schema's
second-resolution Unix strings. Only those search bounds should be widened to
cover fractional boundary seconds (lower rounded down, upper rounded up).
Inclusive search/read boundaries can return overlap or messages above upper;
the helper dedupes identities and excludes timestamps above the fixed upper.
The declared collection interval remains unchanged. Search-bound rounding is
not a rule for channel/thread `oldest`/`latest`.

Malformed read bounds can return a parent-only thread and an apparent terminal
response. If a read used the wrong precision, refetch with six-digit bounds
before saving, even if the connector claimed terminal. Also reconcile results
that contradict observed replies or capability evidence: check exact query/root/
bounds, then refetch. A parent-only response cannot establish complete context
when observed replies through upper remain unexplained. If corrected reads still
contradict available evidence, report incomplete and do not collect/advance the
cursor. Do not shorten fetches based on a message count or omit a pagination
token. Conflicting same-ID page content refuses the whole collection and needs
a fresh read.

Each thread is `{"root": "seconds.ffffff", "link": null, "pages": [], "complete": true,
"availability": "Exactly what content was available or missing"}`. Its pages
must include the root and every available reply through upper, including old
context; do not pass only the newly eligible reply. Read all pages from the root,
not just replies since lower. Preserve attachment/file descriptions and links in
text; never pretend inaccessible bodies were read. New capture text comes only
from that observed complete read. Earlier immutable captures remain separately
available as history; absent/deleted old messages are not copied into current
context. Edits/deletions alone do not trigger new work in v1.

Live eligibility is unseen message identity inside `(scan_lower, upper]`, never
before/equal to the channel's setup start. Full tracked-thread rechecks additionally
recover unseen replies since setup start, even outside the history overlap. Old
roots and other historical context do not initiate work. Dedupe identity is
workspace + channel + exact message timestamp; retaining context in an earlier
capture also marks that observed identity seen. Each saved source includes intake
provenance, trigger IDs, mode, lower/scan_lower/upper and exact coverage. Source IDs use
`slack:` plus compact JSON `[workspace,channel,root_ts]`; message IDs use the
same prefix with message timestamp. Carry an actual observed thread permalink in link when returned; null means no
observed URL. The source then uses its durable workspace/channel/root identity
as a reference, not a claimed observed permalink. Never invent a workspace domain.
Capture versions are content-derived and immutable. Repeated reads create no new source when there are no unseen eligible
messages. A later new-reply capture retains earlier captures; routing may attach
to existing work without resetting its execution state.

Mode `import` requires an explicitly selected one-thread request, empty history
and discovery arrays, and a fully paginated thread. Select and save the fixed
`upper` in the local draft observation before the first thread read, using six
fractional digits even at whole seconds. Pass that unchanged upper as latest on
all pages; never choose the import boundary after inspecting fetched messages. It accepts historical messages
as triggers and updates seen/tracked state, preserving live cursors. The first
explicit import can promote previously observed historical context into requested
intake; prior import captures dedupe repeated import, independently of live seen IDs. `lower` must
still match the saved live boundary; use watch-plan. No automatic historical
backfill or setup-start change occurs.

A successful collect adds schema 3 to canonical `state/work.json`, atomically
committing collection state (cursor, seen IDs, tracked capture references), immutable
source receipts and the collection event. Each channel fixes its synthetic/live
mode on its first successful collection, even an empty one; never mix fixture
reads and real reads in the same channel/runtime. Use separate test runtime copies. Source receipts are the inbox; there
is no second file authority. Schema 1/2 inspect remains read-only. Begin migrates
1 to 2 as before; first verified-owner collect migrates 2 to 3 with migration and
collection events in one atomic replacement. Old plugin versions cannot resume
schema 3; use this phase's plugin in both hosts. Other work, old events, scopes,
actions, fix counts and illustrative synthetic cursors remain intact.

Collection does not consume semantic step budget. Route/save still consume it.
Every mutator checks whole-invocation owner, effective config/package fingerprint
and revision. Partial/incomplete fetch refuses without changing canonical bytes.
A crash exposes prior state or all collected sources plus cursor. After an
uncertain response inspect and retry the exact same ID/content, even using the
original revision. A changed observation needs a new ID; revision conflicts need
rereading. Never edit/reset corrupt state. Unrouted receipts survive interruption.

Coverage remains bounded: channel history + observed reply search + tracked
threads, with exact intervals/terminal pages saved in the event. Search indexes
may omit or expose replies late; no completeness guarantee exists beyond the
observed data and declared overlap. Private-channel/bot coverage must be checked
independently in each host. Historical import is the fallback for an older
untracked thread. Fixture success is not live-connector evidence.
