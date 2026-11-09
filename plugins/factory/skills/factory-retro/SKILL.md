---
name: factory-retro
description: Review selected outcomes or transcripts, retain deduplicated evidence-backed improvement candidates, and record adjudication and fix evaluations. Does not rewrite skills/configuration or advance engineering work.
---

# Factory retro

Resolve the default once through the [configuration contract](../factory-setup/references/configuration.md#default-resolution-and-pinning),
or reuse pinned config/local paths from the invoking run. Select the requested
outcomes or transcripts; invalid configuration stops with setup/repair guidance.

Read the selected source, decisions and implementation/review/report evidence.
Use read-only inspect for existing canonical state; no run acquisition is needed.
Distinguish supplied execution artifacts from scenario declarations and missing
upstream work. Compare intended and observed behavior, including useful results,
failures, human intervention and evidence that weakens the proposed explanation.
Original failures remain evidence after successful retries.

Use the [learning record contract](references/learning.md) for candidate discovery,
event identity, adjudication and fix evaluation. Deduplicate by cause and expected
behavior. Propose a bounded improvement and concrete acceptance scenario when
supported; when guidance already covers the failure, test its use before adding
more. Evaluate explicitly linked changes against relevant observed behavior and
retain limitations rather than inferring improvement from a commit or static suite.

Report wall-clock intervals, execution intervals and explicit human waits
separately where observed. CLI lifetime is not agent compute time; unavailable
timing, tokens and cost remain unavailable. Cite actual versions and evidence
paths without exposing private content beyond the selected scope.

Return a concise report with scope/outcome, candidate identity/disposition,
supported findings, proposed improvement/verification and any required decision.
Write requested output or an additive artifact under `<runtime>/retros/`, retaining
prior reports. Candidate recording is local bookkeeping; canonical engineering
state and resources remain unchanged. Retro creates no engineering task, external
post, schedule or automatic source/configuration change.
