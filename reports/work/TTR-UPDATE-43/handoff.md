# TTR-UPDATE-43 — runtime tested, reference delivery received

| Outcome | Result |
| --- | --- |
| Software verified | New v7/v11 planners and seven local audit tests pass; offline Swift build/134tests pass. |
| Data eligible | Transfer/image/focus checks pass; complete native-contract/crop admission blocked by importer compatibility. |
| Integration qualified | Three live appearance captures complete; campaign export to consumer directory fails. |
| Model gate | Not assessed by this runtime/data tranche. |

## What the update unlocks

The running app is built from the **Developer/TVTestRig** workspace, whose source
HEAD is `87e59be5f4f703607503e4ed7917dd771ec438a0` (only local scheme metadata dirty).
The older Documents checkout at46dce7b is not the current runtime source workspace.
This is workspace/source evidence, not loaded-image commit attestation. Running PID65537;
matched helper SHA256 `81be8412dc0a3b7d80599fcd2c5562b3ad5efe2a234c37fe69b97a60d6f4b54b`.

Live exact-target Simulator tests (tvOS26.5; endpoint UUID matched /device):

| Test | Result | Retained case time |
| --- | --- | ---: |
| Version7 native-controls pair | 1 accepted,0rejected |3.230s|
| Version11 rich guide pair | 1 accepted,0rejected |3.392s|
| Version11 rich catalog pair | 1 accepted,0rejected |5.017s|

Full36-case rich and9-case reference example plans compile. Three live samples are
calibration only. Times include case startup/cleanup, not isolated render performance
or a forecast for1000pairs. Postflight reports ready/ownership clear; fresh Fixture
state responds. No owned operation remains active. Normal Simulator/app storage was
used for these small diagnostic campaigns; large spike originals remain on USB.

Campaign IDs end `001043000001` (native) and `001043000002` (rich); full IDs and exact
requests/status are in [runtime](runtime) and the two smoke request JSON files.

## Export gap — successful captures retained

`campaign export` of native campaign to a fresh project-local directory returned
`persistenceFailed`, request `0BA14B17-87EE-49CF-8202-DD5106C44BA4`.
Source shows this writer executes inside the GUI app, unlike caller-owned fixture
chunk export. Destination disk has sufficient capacity and caller host execution
was approved; the error does not reveal the actual failing stage/domain. App folder
access is a hypothesis, not a proven cause. No repeated capture or unchanged export
retry was made. Resume by repairing supported campaign transfer/access with explicit
writer diagnostics, then export these retained campaigns.

## Rich-reference36 independent intake

Exact185,699,046-byte archive received; SHA256
`3105dae538bdffb751e131830da0a4a18a8ecc86794dffcf6094b3d6100b0a98`.
Bounded extraction:235,032,223bytes,669archive entries including directories.
581indexed files verified plus the manifest itself =582files. All36accepted cases
match completed campaign receipts; failed/unattempted history remains excluded.

Independent checks verify72PNG entries/66distinct image hashes, dimensions, native
reported settled focus,12false/true appearance target pairs,12changed-focus and
12unchanged-focus transitions. Inspecting two collage examples confirms visibly
enlarged catalog cards and custom highlighted guide rows. This is useful diversity,
not a substitute for real-app evaluation or full per-body crop qualification.

Existing consumer validators reject all36:

-12appearance pairs: `invalid_metadata: planned_focus`. Planned reference inventory
  includes offscreen controls; our existing admission expects visible inventory or
  the supported composition contract. Explicit exclusion evidence needs a reference
  adapter, not a blanket acceptance of missing bodies.
-24transitions: `case_contract`. Manifest reference renderer groups differ from the
  legacy procedural ancestry gate. The sidecar still declares procedural ancestry;
  clarification was requested. Native-navigation observations also omit exact-request
  focus intent by design, requiring separately validated observed-focus semantics.

The producer Ruby summary intentionally rejects paths outside its own repository;
we preserved that failure and used the NUIAK audit instead. No path restriction was
disabled. [Audit](intake.json), [receipt](received/receipt.json), [tests](tests.log).

## Priority changes and next substantial tranche

1. Implement strict referencePack v1/v2 consumer support: source/recipe identity,
   planned-versus-visible inventory/exclusions, native-navigation capture brackets,
   and ancestry compatibility. Reuse these originals, then production crop QA and
   one grouped review with random samples plus exceptions.
2. Restore caller-compatible export of the three retained local captures. TTR owns
   producer transfer repair; consumer source builds locally, no binary request.
3. Expand native Settings rows and selected/unfocused tabs. Current guide rows have
   custom highlight treatment; native_controls is three card-style buttons, not a
   universal Settings/tab renderer. Freeze scene ancestry before assigning training
   roles and compare on retained real diagnostics after admission.

This tranche completes runtime qualification and compatibility audit, not complete
corpus admission. iOS native pageControl policy/validation remains independent pending
work; the new TTR native-controls pack does not resolve that iOS geometry question.

Shared receipt/request and packet published under `nuiak/`; readback verification
is recorded in coordination.md. Peer acknowledgment and sender cleanup remain separate.
