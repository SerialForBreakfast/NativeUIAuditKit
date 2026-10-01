# SYN-11 — review handoff and annotator startup repair

Preparation/repair complete; human review remains pending.

| Outcome | Evidence |
| --- | --- |
| Software verified |26Python tests (3cache,23editor interactions), offline Swift build,120Swift Testing+14XCTest pass |
| Data eligible | Not yet: exact564member proposal is unapproved; sampled geometry/source-role acceptance pending |
| Integration qualified | Fresh cached Cocoa loader succeeds; actual annotator launched with the five-image safe queue and remains running |
| Model gate passed | Not run; no real encoding, training, inference, export or promotion |

## Human review

Opened existing
`reports/work/SYN-09-ARTWORK/artifacts/eligible-review/audit/review/batch.json`
with its frozen `combined-queue.json`. No earlier annotation process was found.
Repaired launch process57665remained running; `editor-repaired.log` had no errors.
No automated interaction or human approval was fabricated. Settings/logs stay here.
See [short instructions](review.md); native3/palette4queues remain ready afterward.

## Startup issue and repair

Initial exit134 occurred before an annotation window: Cocoa plugin discovery passed
but loading failed. Explicit QPluginLoader diagnosed QtDBus missing from the cache's
relative`../../lib`path; loading QtDBus exposed QtPrintSupport at the same boundary.
The original installed Cocoa plugin loaded successfully. No annotation was changed.

`human_review_editor.cache_platform_plugins` now preserves`plugins/platforms`and
a validated in-project link to the installed Qt5/lib. Copies remain hash-verified;
wrong library links/collisions and changed plugin bytes are rejected. No installed
wheel, system framework, permissions or environment-wide DYLD setting changed.
Fresh-process repaired-cache QPluginLoader returnedtrue, followed by actual launch.
Old failed cache/log retained. The link is read-only use of existing dependencies,
not an external access service or a relaxation of filesystem scope.

Checks: `.venv-review/bin/python -m unittest scripts.test_review_plugin_cache
scripts.test_human_review_editor_interactions` with PYTHONPATH=scripts, disabled
bytecode/project TMPDIR →26pass, [log](editor-tests.log). Offline Swift commands use
existing in-project caches and disabled automatic resolution; [build](swift-build.log),
[tests](swift-test.log). `git diff --check` passes. Qt offscreen capability notices
in GUI tests are expected; Swift has no warnings/errors.

## Exact proposal, not admission

[Draft](artifacts/admission-proposal.json) has `approved:false`, no reviewer or
authorization evidence, and no accepted geometry/source review. It binds the existing
four source inputs and proposes564unique controls (137focused/427unfocused), with
all764blocked candidates reasoned and excluded.52source-quarantined controls remain
excluded upstream, not silently reconsidered.

The existing weighting function accepts baseline986+564=1550training controls:
1354native,196human, total mass1.0/human0.2. Both labels occur in every new control
class: collectionItem83/305, secondaryButton26/63, listRow24/51, primaryButton2/4,
cancelAction2/4 (focused/unfocused).333evaluation controls remain unchanged.
[Summary](artifacts/proposal-summary.json) binds the unchanged source file hash.
This is feasibility from sealed retained metadata, not a new full corpus/crop audit;
SYN-09/SYN-10retain that evidence. Exact admission will revalidate before execution.

Next: receive saved sampled reviews, reconcile any corrections, bind source-role
acceptance and exact admission, then present encoding/run approval. No real model
activity is implied by finishing this preparation. TTR coordination not applicable:
local annotation repair/proposal changes no producer contract or requested next action.
