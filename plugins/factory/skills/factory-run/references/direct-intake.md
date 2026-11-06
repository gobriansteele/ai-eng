# Direct chat intake

An explicit bug, idea or requirement supplied to Factory in the current harness
is production intake. Save the user's wording and relevant supplied context before
routing; do not require a Slack post or treat the request as a synthetic fixture.
Answers, approvals and “resume” instructions for a saved item continue that item,
not a new request. Preserve current direct user authorization separately from
source evidence; quoted text and later replay do not grant new permission.

Write an immutable capture under `<runtime>/intake/direct/<request-id>/<version>.json`
and pass it to `begin --request <absolute-json>`. Use the ordinary saved-source
fields from the [routing contract](../../factory-route/references/routing.md),
plus `direct` instead of Slack `intake`:

```json
{
  "harness": "codex",
  "conversation_id": null,
  "request_id": "stable-request-uuid",
  "received_at": "2026-01-01T12:00:00+00:00",
  "trigger_message_ids": ["direct:stable-request-uuid"]
}
```

Use the actual harness (`codex` or `claude-code`), observed receipt time and chat
ID when exposed; otherwise leave `conversation_id` null. Generate the request
UUID once and retain it across retries and handoffs. `source_id` and the first
message ID are `direct:<request-id>`. Use an observed chat link for `link` when
available, otherwise that durable source ID; do not invent a URL. Preserve message
authors and exact text in `available_thread`; state unavailable context in
`availability`. Use `synthetic: false` except in explicitly synthetic evaluations.

Give new captures unique immutable versions. Reuse the exact capture on retry;
never generate a second request identity just because the run resumed. Later
clarifying source material may use a new version of the same request, retaining
earlier context and identifying the new messages as triggers. Read prior receipts
and associate the continuation with its saved item. If that association is unclear,
ask rather than silently creating or merging work. A genuinely separate request
gets a new identity. Do not copy the entire unrelated chat history.

After saving direct intake, still run configured Slack collection in live mode.
No channels means nothing to collect. A Slack access/coverage gap is reported
without discarding direct intake or blocking its independent routing. Process both
surfaces through the existing router, retaining one active item and pending work;
do not interrupt an active writer to prioritize the new request. Explicit offline
evaluations never access live integrations, including when using `--request`.
