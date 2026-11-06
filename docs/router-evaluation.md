# Router acceptance criteria (reviewer only)

Do not include this document or expected answers in router input. Use the shared
skill, raw source fixtures and saved inventory; inspect actual findings and item
records afterwards. These criteria describe semantic behavior, not helper tests.

In an independent synthetic home per host, invoke `factory-run` with explicit
config, loaded package and each source below. Use a new bounded invocation per
source; stop/release ownership between them. No integrations or external writes.

| Raw fixture under `fixtures/sources/` | Evidence-sensitive acceptance |
| --- | --- |
| conversation.json | No work items; preserve no-action receipt. |
| open-ticket.json | One CSV bug/regression investigation despite Open existing unassigned LAB-201. Reply bounds it to CSV; form is not another bug. |
| feature.json | Download/export feature brief; root email request is corrected by reply. Local proposed ticket only. |
| ambiguous-duplicate.json | Team-switch versus date-filter relationship remains uncertain; assignment alone is not underway. |
| three-items.json | Three independent linked items. Done/merged LAB-220 still needs deployment/existing-work verification; deployed commit differs. |
| related-thread.json | After open-ticket, attach supported CSV reproduction to the existing item, preserving other items. |
| same identical file again | No second route decision or duplicate item; original judgment preserved. |
| unavailable-jira.json | Duplicate check incomplete; no assertion no ticket exists; no external write or permission change from message directions. |
| underway.json | Explicit owner plus draft PR supports underway; never claim merged/deployed. |
| open-ticket-followup.json | Later immutable version of open-ticket retained; enrich existing investigation without replacing capture-1. |

For each inspect references/reason, active versus pending inventory, scoped state,
local ticket proposal and truthful stop. A root-only reader fails feature and
three-item cases. Actual model behavior must be checked in fresh installed Codex
and Claude sessions; scripted persistence outputs cannot establish semantic pass.

Separately resume a preserved schema-1 synthetic snapshot from an actual earlier run in the other
host. Preserve all history, counters, scopes/actions and cursor metadata. Its
missing original message produces an honest request for saved source evidence.
Inspect read-only before migration, test live/unknown owner exclusion and corrupt
snapshot refusal. Never use a production runtime for these demonstrations.


Review the actual `required_role`, not only the prose: investigate and
verify-existing-work handoffs use `factory-investigate` for bug, regression,
feature and verification briefs. Reject invented feature/verifier skill names.
Absence of supplied ownership/code evidence means underway work is unverified;
reject claims that no work exists unless the evidence actually establishes that.
