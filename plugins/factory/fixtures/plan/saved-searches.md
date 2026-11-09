# Saved-search dashboard: supplied investigation evidence

This is raw synthetic upstream evidence for a focused planning evaluation. It is
not an actual investigation run or an expected plan. The evaluator copies it into
a separate runtime and assigns the concrete item/source identities.

## Request and current behavior

The dashboard shows saved searches in a sidebar. Choosing one runs its stored
query in the results pane; the selected saved-search ID also appears in the URL.
The search field and Save search control remain visible above the sidebar. Users
can run an unsaved query without choosing a saved search.

The sidebar currently renders the following server response as linked rows,
highlighting the selected ID:

```json
[
  {"id": "s1", "name": "Recent orders", "query": "created:week"},
  {"id": "s2", "name": "Unpaid orders", "query": "paid:false"}
]
```

The renderer maps rows directly to links. There is no other rendering branch.
Loading a saved search and running a query are separate requests. The results
pane displays the current query and its results until another query is run.
There is no Remove action today.

## Available service contract

`DELETE /saved-searches/{id}` already exists. A successful request returns 204
only after deleting that user's saved search. A 403, 500 or connection failure
leaves it stored. `GET /saved-searches` lists the persisted searches. No restore
endpoint or undo behavior exists.

The dashboard can run any of the listed queries without retaining the saved
search. No policy requires saved-search history to be kept. No additional
repository or hosted environment is available in this focused evaluation.
