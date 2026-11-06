# Maintenance contract

## Ownership and current evidence

Use the factory's recorded preparation/resources, item/history and host lifecycle
references, not broad filesystem discovery or path-name patterns. A source path,
worktree, branch/common Git directory, resource ID, allocating owner and purpose
must agree with observed Git worktree inventory and actual filesystem identity.
Resolve symlinks and stop if identity/scope differs; do not follow an archive or
cleanup target into unrelated content. Imported fixtures are declared scenarios,
not proof of real factory allocation or real Git/process inspection.

Read canonical revision/active_run and relevant item status/actions first. Check
current owner PID/start/executable/liveness with available permitted inspection;
denied/unknown is not dead. Verify actual worktree HEAD, branch, common Git
directory, staged/unstaged/untracked status and merge ancestry against the intended
base. Stale local/remote refs cannot prove current merge status. Preserve any
unmerged branch even when a PR URL says merged. Recheck state if it changes during
preview. Read-only probes may be unavailable; attribute declared versus observed
facts and retain unknown resources rather than inventing successful commands.

Classify conservatively:

- Retain active/running/unknown owners and all blocked/human-wait/unresolved items,
  pending actions/batches, dirty or untracked work, unmerged branches and unrelated
  or unverifiably owned paths. Do not kill a process, remove a lock or force takeover.
- Completed records can be archive-copy candidates only with actual completion for
  the requested scope, readable final evidence and no unresolved wait/action.
  A merged PR alone is insufficient; no production verification is inferred.
- A disposable clean checkout is a potential native-lifecycle cleanup candidate
  only when recorded/observed ownership agrees, the item is complete, prior owner
  is verifiably stopped, intended branch ancestry is merged, all required evidence
  lives safely outside it and the applicable native operation is actually available.
  Even then, preview grants no execution permission.
- Temporary files are not disposable merely because they look temporary. Retain
  every source/decision/review/final artifact and raw evidence referenced by them.
  Consider only specifically recorded disposable scratch within the requested scope;
  incomplete reference/ownership checks mean retain. A stopped process is an
  observation, not something to terminate or a reason to delete its evidence.

Save preview evidence outside candidate resources, under an explicit output path
or <runtime>/maintenance/previews/. Record source snapshot/revision, exact scope,
observations/provenance/limits and reasons, plus a stable comparison of meaningful
resource/item/Git/owner state. On unchanged repeat, return the same preview/path
with a recheck summary instead of generating another candidate list/artifact.
Exclude fetch timestamps from equality; new observations that change eligibility
need a new immutable preview. Never edit canonical state or existing evidence.

## Additive archive and restore

Archive only on an explicit selected completed-record COPY request. Resolve source
and destination scope first and retain originals. Never overwrite or write archive
DESTINATIONS into canonical state, installed source, active resources or an existing
nonempty destination. Reading/copying a snapshot within the requested scope is
allowed; it does not change canonical state. Copy exact
selected artifacts/record context without following symlinks outside scope. If a
shared canonical snapshot contains other items, copy it only within the requested
scope; otherwise a selected-record export is explicitly derivative, not canonical
state. Preserve raw bytes of original source/decisions/reviews/final reports.

Create a readable index/manifest with original absolute paths, copied relative
paths, file hashes/sizes, source snapshot identity, completion/ownership evidence
and missing inputs. Verify original/copied hashes before reporting success; a
partial copy is incomplete and does not authorize removing originals. Interrupted
retries reconcile the existing manifest and exact matching bytes instead of
overwriting or creating conflicting bundles. Keep every original path/reference
valid; archival copies do not resolve uncertain actions or prove completion.

Restore means copy an indexed bundle into a NEW explicit inspection destination,
verify hashes and provide the path mapping. Do not overwrite files, rewrite report
history/embedded paths, replace <runtime>/state/work.json, reattach ownership or
reactivate work. Restore never changes canonical history; a missing/mismatched
archive is a precise block. Direct archive/restore copies are additive and leave
the default preview_only configuration unchanged.

## Later native removal

Actual removal needs an explicit concrete reviewed eligible-resource list and
operation, current host permission and fresh revalidation immediately before each
native lifecycle call. If state/identity changed, retain and return a revised
preview; approval of an earlier list is not permission to remove a new resource.
Use the host's observed supported lifecycle, recording actual result and surviving
evidence. No generic shell-delete fallback, external branch/ticket/comment cleanup,
scheduled deletion or automatic policy relaxation. This release does not claim a
native deletion was exercised; preview/copy/restore are independently useful.
