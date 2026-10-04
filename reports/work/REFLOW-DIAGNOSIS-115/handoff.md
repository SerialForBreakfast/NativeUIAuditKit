# REFLOW115 — why identity preservation was insufficient

Software verified: passed. Data roles: unchanged, no new admission. Producer live
integration: not assessed. Model qualification: no new candidate; DTM029 still fails.

## Findings

Viewed and hash-verified both retained row25images: the focused VoiceOver row stays
in place while On becomes Off, the help row disappears and lower rows rearrange.
This is an existing retained historical case, not a new Settings operation or a
VoiceOver semantic-alignment claim. Existing unchanged-focus label remains supported.

DTM029 baseline logit -3.313 becomes positive after a +68.699 residual. Of that,
68.653comes from lower-right cells (pooled rows1–3,columns3–5). Grid cells summarize
features with receptive fields; they are not precise bounding-box attribution.
The failed residual features have cosine0.9455to the closest Region positive versus
0.6686to the closest training negative. This supports a representation/coverage gap,
not causal proof of a particular internal feature.

Mean encoded pixel difference is0.013746. Existing negative examples reach0.014989,
so a general pixel-change-magnitude cutoff would not directly separate this failure.
All44original training negatives and158original positives are enumerated in the
report; negative corrections span -15.392to+2.772. No new class labels inferred.

Independent direction check: all424pairs keep their changed/unchanged/uncertain
decision when reversed. Maximum probability shifts: old training0.03069, related
Settings0.000061,Region0.00186,identical0. This is empirical consistency, not an
architectural symmetry guarantee or generalization result.

## Evidence and verification

scripts/diagnose_reflow115.py is the real frozen-model entrypoint. It validates
source/checkpoint/result hashes, reproduces all original probabilities exactly,
reconstructs correction from channel/grid contributions and preserves source roles.
Report: reports/work/REFLOW-DIAGNOSIS-115/artifacts/audit/report.json
SHA256:bb4732ed92ca794b40144893b30c6f23bf9004b780112edeeac23298fff3e2b8.
Execution2.416seconds,exit0; no training/capture/external wait.
33Python tests and offline Swift build/137tests pass. Logs:
.build/reflow115-build.log and .build/reflow115-test.log. git diff --check passes.
Pre-existing changes, source images and checkpoints preserved; no Git writes.

## Next substantial tranche

1. Frozen focus-local versus full-frame diagnostic on current data, using verified
   boxes only as an explicit oracle upper-bound and actual proposals separately.
   Determine whether local identity evidence separates reflow from focus changes
   before adding a learned focus-conditioned branch. No invented Region body boxes.
2. Reuse TTR's current negative-coverage assignment: match native-list focus-change
   scrolling to unchanged-focus row insertion/removal/reflow with similar visual
   movement. Prefer retained evidence; use safe Fixture controls rather than toggling
   real Settings. Include stable identity and native observations, not requested focus.
3. Freeze new disjoint final groups before any failure-driven admission/fit. Current
   Settings groups are exposed; new filenames from those journeys do not restore
   independence. No threshold changes or promotion from this audit.

Coordination: verified SMB endpoint and published/read back own REFLOW-DIAGNOSIS-115
packet plus nuiak/responses/nuiak-20261004-reflow115-matched-controls.yaml. Duplicate
keys rejected and unrelated state hash preserved. Response SHA256:
fa2849d1a91d1f4882253df195658108beb04b952b34a989d650e0521ade4d24.
Peer acknowledgment unverified; no new artifact delivery or capture request.

Tranche includes the failure/support audit and the separate424pair order-consistency
benchmark. Both complete; further training deferred pending a defined change that
addresses semantic reflow rather than another unchanged optimizer run. Local
focus-local/proposal comparison remains executable next; geometry109 still awaits
conflicting source-box resolution and untouched-final qualification lacks membership.
