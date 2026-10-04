# CONDITIONED-133 — October4

| Outcome | Result |
|---|---|
| Software verified |Pass:6focused Python,13focused OCR tests, offline build and142native tests explicit-serial. Existing ROI integration assertion unchanged.|
| Data eligible |Existing1299training views unchanged;11retained intervals remain exposed diagnostics, not admitted or independent.|
| Integration qualified |Local OCR regression repaired; model retained-input hashes preserved. No live TTR/capture qualification.|
| Model gate passed |Fail:DTM033original retention202/207; preserve deployed passive models. No export/promotion.|

Started from1bc11ef; preserved pre-existing132handoff/docs/scripts. Research contract
and DTM033run registered before implementation/launch. No Git writes.

## Fixed candidate result

Unchanged DUAL130cached frozen DTM031features,1299views; train-only population std
floor0.001, no centering, base logit unchanged. Zero correction;600epochs Adam0.01,
seed42 CPU2threads/equal-group-means. Persisted scale reload and checkpoint replay
exact;226original identity probabilities remain byte-exact. No peer cases in training.

PID14929,fit0.429631s,total2.570809s. Loss37.838947→0.359956. Original202/207:
old104/108,Settings4/5,Region94/94; failures3,7,19,23,25(3confident,2abstentions).
DTM032had201/207. Scaling is not a sufficient repair; don't rerun unchanged epochs.
Contrast originals179/191(of207) and negatives214/214(of226); dim110/143originals,
bright107/106. Full10condition scores in sealed local result. Gate remains failed.

`NativeUITrainer/focus_ring_runs/conditioned133-dtm033/{execution,result}.json`
pins sources/config/cache/model and records all predictions. CheckpointSHA256
`851dfb86e9c5d0eccb03d1431ad634d21aea6928b5e5e733ce52eb369a5209a8`.

Retained comparison: DTM031misses Survey26 4→5(Balance to Subtitles row) in addition
to DTM030's five prior misses. DTM033recovers5→6screen transition but still misses
4→5,7→8,8→9and both Navbar29moves. Two identical intervals remain unchanged.
Visible screen transitions versus same-screen movement must remain separate; no
claim of native reviewed accuracy from aggregate hint agreement.

## OCR repair

Literal case-insensitive substring remains first. Only multiword all-letter anchors
receive whole-word fallback after removing standalone `'`, `’`, `•` between letter
tokens. Embedded punctuation, signs, numbers, other symbols and punctuated anchors
remain literal. Same policy for required/optional/forbidden; preserve evidence text.
No public API/backend change. Original ROI test unchanged and now passes. New tests
include Wi-Fi,Don't,decimal,slash/plus,missing words,consecutive punctuation and
forbidden-anchor detection. No generic fuzzy matching or punctuation erasure.

## Verification

All Python calls use resident `.venv-yolo/bin/python`,
`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts TMPDIR="$PWD/.build"`.
`-m unittest scripts/test_conditioned133.py scripts/test_dual130.py`:6pass,0.592s.
`scripts/conditioned133.py`:exit0, candidate rejected by reported retention gate.
Native focused `swift test --no-parallel … --filter TextAnchor`:13pass.
Integrated `swift build …` and `swift test --no-parallel …`:exit0,142pass
(14XCTest+128Swift Testing); logs `.build/conditioned133-{build,test,ocr}.log`.
All use project-local cache/config/security/module-cache flags from131/132.
`git diff --check` passes. Default concurrent Vision stall remains unqualified,
not silently fixed by serial test success. No daemons/devices operated.

## Next substantial tranche

Prioritize representation/objective diagnosis with fixed retained regressions and
original gates. Compare baseline-preserving residual strategies, not another blind
normalization/retraining loop; include quantization/localized lighting guard stress.
Retained cases remain exposed diagnostics unless a separately recorded evidence-based
data-role decision is made. TTR receives no new model; OCR source repair can be
adopted after maintainer publication under source-first workflow.

Coordination: owned CONDITIONED-133 packet published/read back at
`/Volumes/SharedStatusFile/nuiak/status.yaml`,2026-10-04T19:45:40Z. Unrelated semantic
fields preserved(hash280f97ca2cb5f3f499827b901bffa6f744953d3b52062f6fe927c8f67a35c87f).
Peer acknowledgment not yet observed. No candidate weights or private data shared.
