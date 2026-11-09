# Watcher reviewer criteria

This is an evaluation oracle for reviewers, not role input. Give fresh model
sessions only shared skills, explicit synthetic config/start records and raw
selected files under `plugins/factory/fixtures/watch/`. Keep each host's runtime
separate. No MCP calls, model answers or expected classifications belong in those
raw fixtures.

Use `factory-run --config <synthetic-home>/config.yaml --collection <path>` in the
host's normal skill invocation syntax. The helper uses `collect --decision`, not
a separate Python watcher process. Config has workspace `T_SYNTHETIC`, channels
`C_SYNTHETIC_ONE` and `C_SYNTHETIC_TWO`; setup starts in runtime are respectively
`2023-11-14T22:13:20+00:00` and `2023-11-14T22:13:45+00:00`. Keep these test choices
outside production and installed source. Setup creates the runtime shape; a
fixture-only isolated test may seed these explicitly synthetic start observations.

| Sequence | Reviewer check |
| --- | --- |
| partial.json | Fails incomplete, saves no sources/cursor; invocation can truthfully finish. |
| first.json | Two full thread captures, root/reply pagination overlap deduped; source for older root triggered only by its new reply. First collect migrates 2 to 3 atomically. |
| second-channel.json | Independent second cursor and capture; existing first cursor/work retained. |
| repeat.json | First cursor advances, no new capture or work for repeated IDs. |
| followup.json | One later capture on the older root; both late-visible reply at 45 (below previous cursor 50) and new reply at 60 are triggers; full current context retained, prior capture unchanged. |
| manual-import.json | Explicit old thread imported; first cursor stays at 70. Repeating import creates no duplicate capture/work. |

After each capture, the semantic router owns item separation/disposition, using
only synthetic saved evidence. Old context cannot create new work by itself.
A later capture should attach to evidenced existing work and preserve execution
state; additional unrouted captures can remain pending at a bounded stop. All
investigation/verification handoffs name `factory-investigate`. A genuine
missing-role block must name the unavailable role; available roles may continue
within the requested bound. An active block must not prevent collecting another channel.

Verify canonical state directly: one claimed item per run with independent owners preserved, immutable source
receipts, no reset fix counts/scopes/actions, exact trigger IDs, independent
cursors, coverage limits and released invocation owner. Error/lost-reply tests
must expose prior state or sources plus cursor together. Inspect old 1/2 records
without writing; do not claim schema-3 handoff to an older installed plugin.

Live acceptance is separate: use a user-selected real channel, repeat its read,
and explicitly import one historical thread in each host without posting a test
message. Record exact observed bounds, pagination, reply-discovery limitations,
current Jira/code reads or incomplete capability evidence, and runtime effects
privately. Fixture success does not establish live integration success.
