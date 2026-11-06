# Agent selection

Before each assignment, assess its complexity, uncertainty and consequences.
Choose the least expensive agent and reasoning level likely to complete it
reliably, considering latency and retry cost. Start bounded lookup at low reasoning
when supported; use more for ambiguous diagnosis, design and consequential review.
Reassess when the work changes or substantive failures occur.

Use the host harness's current guidance, available agents and selection controls.
The host owns model capabilities and mappings; Factory does not maintain them.
Select model capability and reasoning effort separately. Respect explicit user
choices; do not inherit the parent's settings merely because they are the default.

Dispatch role work with the selected settings and a focused task/evidence handoff.
Keep routine coordination and deterministic helper calls with the orchestrator.
Pass this policy to workers that delegate. Existing role, ownership, authorization
and retry contracts still apply.

Briefly record the choice and rationale in the existing attempt or run report.
Distinguish requested settings from runtime settings the host actually confirms.
If required selection or dispatch is unavailable, report the capability gap rather
than silently using an unsuitable parent or inventing unsupported controls.
