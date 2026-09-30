# Related-synthetic admission and run readiness

Owner: current NUIAK admission worker,2026-09-29. Data-use approval recorded in
Research/Plans/FocusRelatedSyntheticAdmission.md and architecture Section8.

## Completed data preparation

-12/12new BULK12 pairs explicitly admitted using existing reviewed-fixture and
  training-extension paths. Original QA/source manifests remain unchanged.
-325training pairs/650crops;9retention pairs/18crops. All644previous samples are
  byte-for-byte identical as row objects in the new assembly;24samples added.
-50/50 logical native/Fixture training sampling retained. No new model execution.
-1,961reserved evaluation sample entries frozen, including real development,
  related SYNTH05 and protected surface metadata. No training frame/crop pixel
  hash intersects that exclusion set. Protection does not depend on new filenames.
-50original synthetic evaluation pairs stay out of training. Their metrics mean
  related-source performance, not independent generalization.1500legacy pairs
  remain unqualified because original/native lineage is absent.
-Five real-development protocols frozen in evaluation-lanes.json:40frames across
  the24frame comparison,8Home/Photos/Settings and8supplement. Real inputs remain
  repeatedly used development evidence, not untouched qualification. Preserve
  incomplete-candidate accounting and separate backend/latency limitations.

## Verification

`assembly-verification.json`: actual existing extension/retention assembly,
prior-row preservation and12admission decisions. Protocol SHA256:
`6699a6e689e33ae916fab21a437b9de0c31a7dd62bce4c2f1881561e77e6adac`.

`actual-negative-checks.json`: real new-member inputs fail when incomplete,
unapproved or entirely evaluation-overlapping;650training sample hashes are
disjoint from reserved pixels. `focused-tests.log`:16existing admission/retention
tests pass. No implementation code changed; full Swift rebuild not required.
New reviewed copies were rendered through existing production16%/256 crop mode,
not a substitute image transform. Checkpoint bytes never deserialized for inference.

Actual trainer CLI: resident focus-export-01 Python, train_focus_ring_detector.py,
--experiment-protocol proposal/focus_dataset_manifest.json --experiment-arm
warm-stretch --name related-synth-development-candidate --preflight. No --execute
or fabricated approval. See trainer-preflight.json and final outcome below.

## Proposed run and next action

[Exact proposal](run-proposal.md): FDR007 warm weights/fresh optimizer,30epochs,
batch64,lr0.0003,seed42,1,800second cap, unchanged18/18retention floor/minimumBCE
selection. Separate real-transfer comparison against shipped/FDR010; report related
synthetic results separately. No run number allocated or training directory created.
This isolates the data addition; it is not a production corpus or release pass.

The next decision is approval of this exact bounded run and subsequent development
comparison, not more data-policy deliberation. TTR runtime repair, new collection
and human annotation are not prerequisites. No export/promotion follows automatically.

## Coordination

Published metadata response:
`/Volumes/SharedStatusFile/nuiak/responses/nuiak-20260929-related-synthetic-admission.yaml`.
Owned RELATED-SYNTH-ADMIT-01 status packet added; unique-key YAML/readback passed.
TTR reports offline timeout/sampling repair complete at20:19:16Z, not deployed/live
qualified; we do not operate its runtime here. Prior BULK12 receipt acknowledged by
producer. New admission-response acknowledgment not yet observed.

## Final outcome

Actual trainer preflight completed20:34Z with expected exit2, empty stderr,
configurationValid=true and exactly one blocker: missing_experiment_approval.
No data/runtime/role blocker remains for this bounded development proposal.
launchEligible=false and executionAuthorized=false accurately preserve the final
run approval boundary. No training output directory exists.

Software verified: pass (16tests plus3actual negative admission checks).
Data eligible: pass for325-pair related-source development training, not production.
Integration qualified: pass for actual assembly/trainer preflight; launch not authorized.
Model gate: not assessed. Full qualification blockers remain explicitly in protocol.

Assigned policy,12-pair admission, retained-inventory review, evaluation separation,
exact proposal and trainer preflight are complete for review. No active subprocesses
remain. Next: approve the exact run/real-development comparison in run-proposal.md;
then record its run ID/approval before execution. No new TTR capture or annotation
is needed to start this bounded experiment.
