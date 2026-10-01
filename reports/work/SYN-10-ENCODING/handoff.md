# SYN-10 — native feature encoding and trainer integration

Completed for review.89generated Python tests pass; offline Swift build and120Swift
Testing+14XCTest cases pass without warnings. Actual retained CLI validates
configuration and refuses execution with the exact expected blockers (exit2).

| Outcome | Result |
| --- | --- |
| Software verified | Pass: encoding/three-cache join/trainer dispatch and adversarial tests |
| Data eligible | Blocked: sampled geometry/source-role review and exact admission pending |
| Integration qualified | Pass for generated execution orchestration and actual retained blocked preflight; real MPS encoding/run not performed |
| Model gate passed | Not run; no new candidate, inference, retained-data training or export |

## What changed

`scripts/focus_native_body_experiment.py` supplies the separate
`focus-native-body-full-fit-v1` protocol and `native-body-full-fit` trainer arm.
The original diagnostic assembly remains non-executable. No producer change,
recapture, new cropper, backbone, threshold or optimizer was introduced.

- Revalidates the native assembly, admission, pixels, source exclusions and exact
  baseline. Preserves FDR021's986training/333evaluation membership and selector.
- Joins928original features+58reviewed-human features, then admitted native features.
  Existing native80%/human20% weighting is reused. Missing features block training.
- Encoding requires exact protocol/output/limit approval; fixed32-image batches,
  maximum2048controls/300seconds/32MiBcache. These are software bounds, not approved
  live budgets. Current proposed retained budget is1024controls/300seconds/16MiB.
  Deadline is cooperative; allocation snapshots are not peak-memory measurements.
- Reuses the frozen encoder and normalization, checks its state before encoding,
  rejects changed tensor labels/order/dimensions/dtype/nonfinite values/digests, and
  pins torchvision and relevant runtime code. Weights load locally; no download.
- A new post-cache protocol requires a separate run approval and experiment-log
  binding through the existing trainer. No automatic export, promotion or retry.

## Verification

The retained preparation reproduces986baseline training/333evaluation controls,
zero admitted additions,564awaiting-admission candidates and764blocked candidates.
All input seals remain unchanged. Final prepared protocol:
`artifacts/retained-final/protocol.json`, seal
`0d1bdbc552a1ab3487ac747b35e1e23531d5c3e8d2292a5ea989aa9cce9ebd35`.
It is a blocked rehearsal, not an encoding/run authorization. The earlier
`artifacts/retained` rehearsal was superseded when final executable identities
were pinned; its preflight correctly rejected the stale runtime identity.

Reproduce preparation with
`scripts/focus_native_body_experiment.py --inputs reports/work/SYN-10-ENCODING/retained-input.json --output NEW_PROJECT_LOCAL_DIRECTORY`.
The real caller verification is
`scripts/train_focus_ring_detector.py --experiment-protocol reports/work/SYN-10-ENCODING/artifacts/retained-final/protocol.json --experiment-arm native-body-full-fit --name syn10-preflight-only --preflight`.
Use `.venv-yolo/bin/python`, project-local TMPDIR and disabled bytecode as below.
Final [preflight log](trainer-preflight-final.log): configurationValid=true,
launchEligible=false, executionAuthorized=false; missing exact native admission,
no admitted additions, missing native feature cache and missing run approval.
No `NativeUITrainer/focus_ring_runs/syn10-preflight-only` directory was created.

- `PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.build/tmp" PYTHONPATH=scripts .venv-yolo/bin/python -m unittest scripts.test_focus_native_body_experiment scripts.test_focus_native_body_assembly scripts.test_focus_review_continuation scripts.test_focus_full_fit_experiment scripts.test_focus_fit_diagnostic scripts.test_focus_pretrained_experiment scripts.test_focus_learning_experiment scripts.test_focus_mixed_assembly scripts.test_focus_training_extension`
  →89pass ([log](integration-tests-final.log)).11new tests cover the new adapter;
  existing suites cover native admission, protected exclusions, weighting and fit.
  Tests use generated tensors/fake encoder dependencies; existing optimizer tests
  use tiny generated examples, not retained-corpus training or model evidence.
- Real trainer positive dispatch reaches the native cache join and existing full-fit
  runner under substituted execution dependencies. Negative CLI paths block before
  torch import and create no run. Ordinary dataset loader rejects execution bypass.
- Encoding orchestration reads generated256×256crops and writes/verifies a receipt
  using a fake encoder; bad approval, deadline, state and output limits leave no
  successful cache. No real encoding/runtime qualification is claimed.
- Offline `swift build` and `swift test` with in-project caches and automatic
  resolution disabled →pass ([build](swift-build.log), [tests](swift-test.log)).
- `git diff --check` →pass. No source artifacts or model weights changed.

## Next operational path — agent work, not manual JSON work for the reviewer

1. Complete the existing prefilled sampled geometry reviews: SYN-07native3,
   SYN-07palette4, SYN-09safe artwork5. No saved `revision.json` found in their
   audit workspaces at this check. Prior SYN-06human acceptance remains valid.
2. Bind that evidence and source-role decision to the exact native admission.
   Reuse `focus_native_body_assembly.py --admission ...`; do not infer admission
   from this software tranche. A smaller development experiment does not need to
   wait for all240collection targets, but must retain protected exclusions.
3. Prepare `focus-native-body-experiment-input-v1` with the newly admitted assembly
   reference, proposed `encodingBudget` and `newFeatures:null` using
   `focus_native_body_experiment.py --inputs INPUT --output NEW_DIRECTORY`.
   Present exact counts/limits for encoding approval; run `--encode-protocol ...
   --encoding-approval ... --output ...` only after that approval.
4. Put the returned cache/receipt references into `newFeatures`, prepare a new
   protocol, and use the existing trainer's `--experiment-arm native-body-full-fit
   --preflight`. Present the bound one-run comparison for approval and log it
   before `--execute`. No actual run ID, approval or training was created here.

TTR continues the existing78-target genuine content/layout variation request;
there is no new transport or geometry requirement. See [coordination](coordination.md).
