# Synthetic competitor repair intake — 2026-09-29

## Verified result

Received the newly published545488-byte source archive
`ttr-synthetic-repair-0ef89d79-20260929T045402Z.tar.gz`.
SHA2564069730b65dec563dc836fb4de5e0f51b873e86d81306326c7aafa3dd90610d9.
All158 archive members passed bounded safe extraction;1942758 expanded bytes.
All22 proposed file sizes/hashes and available base hashes match the manifest.
Original archive retained, sender cleanup not performed. Approximately34GiB free.

The source now implements competitor_v1 pairs, explicit v3 metadata, native-image/
native-button/custom focus configurations, a candidate custom-scale repair, and
campaign guards against unresolved cleanup across old and new campaign IDs.
These are source findings and producer-reported tests, not local runtime passes.

## Consumer probe

The actual existing consumer rejects the producer's exact supplied native-image
competitor recipe with appearance_fields (focus unsupported). An in-memory probe
removing focus still rejects canvas_fields (pairing unsupported). Removing both
new fields accepts the legacy canvas canonical identity. These probes do not
modify captured evidence or relax admission. The bundle validator also explicitly
rejects sidecar3, and crop intake requires sidecar2. No v3 admission claimed.

Required integration is explicit dispatch, not stripping new fields:

1. Validate focus configurations and exact Swift sorted-JSON/base64 canonical
   identity, including numeric representation, omitted/null optionals and families.
   Obtain emitted producer vectors for native_image/native_button/custom modes.
2. Retain legacy neutral-reference v2 behavior. For v3, require competitor_v1,
   distinct eligible competitor ID, target unfocused and exactly that competitor
   focused in the negative scene, then target focused in the positive scene.
3. Validate all four native endpoints, per-state geometry, hashes, recipe identity,
   generation and host-time order. Preserve pairing mode/competitor identity through
   normalized binding and production crop manifest; do not turn competitor evidence
   into a neutral baseline or claim directional navigation.
4. Test actual emitted bundles plus identity tampering with recomputed hashes,
   target-as-competitor, missing/extra focus, missing target/geometry, changed recipe,
   unordered brackets and incomplete target accounting. Replay legacy bundles.
5. Run bounded rendered qualification before bulk capture; verify scale-only and
   combined effects visually, then native-image/button cases and competitor crops.

## Source reconciliation and execution boundary

Against the current Max TTR checkout:4 files match base,3 are new,14 differ from
both base and proposal,1 base-tracked planning document is absent. Differences
include older canvas/native-focus prerequisites and local changes; this is not
proof of14 merge conflicts. Do not overwrite the checkout with the archive.
Reconcile cumulative source by context against the retained canvas handoff first.
No producer files edited, app replaced, Simulator/Office operated or models run.

The archive explicitly supplies no real v3 capture bundle; tests use mock pixels.
The existing factory contract requires representative exports before semantic
adapter admission. Source preparation and capture acceptance are distinct.
Requested the maintainer's bounded local Debug integration/replacement and named
Simulator window (20 minutes/1GB, no Office or release build). No approval response
has been recorded in this intake report. Live execution cannot begin from peer
status or earlier dock-repair approval alone.

## Outcomes

- Software: source integrity and current-consumer incompatibility verified;
  adapter implementation and local build/test remain pending.
- Data: source-only delivery; no new rendered training data.
- Integration: unqualified v3; legacy acceptance unchanged.
- Model: not assessed; no training, export or promotion.

Evidence: competitor-v3-receipt.json, competitor-v3-reconciliation.json,
competitor-v3-compatibility.json and gitignored received/competitor-v3/source/.
No executable NUIAK changes, so no redundant Swift build/test performed.

Receipt and exact compatibility gaps published/read back in verified shared
`nuiak/status.yaml`, packet SYNTH-COMPETITOR-INTAKE-01, at05:51:57Z.
Duplicate-key YAML validation passed; unrelated content hash preserved:
6a91a32708e91530f680904c91e7d54681161f53888b868a5e746022748c27d9.
Peer acknowledgment and sender cleanup not claimed. git diff --check passed.

Next owner actions: producer supplies emitted identity vectors and representative
v3 success/rejection exports; local integrator reconciles/builds under the requested
deployment window; NUIAK binds the versioned adapter and production crop acceptance.
Do not expand training volume until this path works end-to-end. No need for humans
to annotate synthetic controls individually.
