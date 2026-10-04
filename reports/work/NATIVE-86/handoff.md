# NATIVE-86 — action proposal and reusable calibration inputs

Continued on a101851 with all NATIVE84/85 changes preserved. No training, role
admission, capture, runtime restart, export or promotion.

| Outcome | Evidence |
|---|---|
| Software verified |22focused Python; offline Swift build,14XCTest+120SwiftTesting pass|
| Data eligible |24strict action pairs eligible for inspection; exact training role decision pending|
| Integration qualified |Real proposal/automatic-candidate/production-crop CLI paths pass on retained data|
| Model gate passed |Not assessed; proposal coverage is not ranking accuracy|

`propose_native86.py` rebuilds24recorded actions through existing validators and
same RGBA pixel convention as the current corpus. No overlap with44train/5exposed
development.12dark/12light,8stationary/16scrolling, all focus changes. Shared Fixture
ancestry excludes independent final evaluation.36appearance pairs remain outside
this action proposal; they are useful visual examples, not fabricated action records.
Existing corpus/admission and source images remain unchanged.

Exact proposed membership SHA256:
ac3d08727b538b1381140d5ec18be524e5042b1b04d02e4bf0818668b7aea25e.
Proposal file SHA256:
b328e60b8c833788678559243c26b357d8f340ff2399f81a8772a84f9be0cf70.
The decision template says approved:false. Proposed counts68train/5development/0final.

Extended existing `prepare_proposal74.py --calibration-proposal` rather than adding
another extractor. Two native batches40+8frames,2.121s native/10.603s total including
fresh label reconstruction and raster proposals. Both Vision and raster cover48/48
endpoints; Vision12ambiguous, union48ambiguous. Correct candidate existence does not
prove correct selection. Candidate inputs contain only automatic boxes; labels stay
in separate score records.732candidates, input SHA256:
f9c1eef0b3a50a3aaa2bbc3aad4208786257da840efe52fb4d171d3953921e55.

Existing `focus_candidate_ranker.py --derivatives-only` uses the production cropper
and `.build/batch79-derivatives`: cold48misses/48image calls,5.122s; warm48hits/0calls,
0.135s. All tensors and crop hashes exactly match. No simulator setup/teardown.
Derivative manifest SHA256:
75783b71b6925c6c31a6cdd02d712ad51db587ce76ddaa4b5d7365bccfb2b001.
No cached tensor grants a training role or launch approval.

Generated portable test exercises actual inspector entrypoint with48tiny test images,
two fake native replies and no private corpus dependency. Tests cover exact membership,
wrong roles, unapproved status, geometry-only inputs and training-input rejection.
Logs `.build/native86-tests.log` (22tests/0.379s), `native86-candidates.log`,
`native86-derivatives*.log`, `native86-swift-{build,test}.log`; commands exit0.
Actual retained integration is separate from deterministic fake tests. Diff check clean.

SMB not applicable: local preparation changes no producer next action. Prior84/85
small-control request and runtime-recovery request remain in place, not refreshed.

Next substantial tranche: approve or reject these exact24calibration→train roles;
if approved, integrate admission with existing collector, preserve old44/5records,
reuse732encodings, and predeclare one size-aware ranker comparison. Report old/new
training support and unchanged exposed Settings results separately. Do not relabel
shared ancestry or tuned Settings as independent evaluation. TTR runtime cleanup
and future true-small-control coverage remain parallel work, not preparation blockers.
