# Page baseline and exact repair inventory

Existing Run013checkpoint SHA
88c3cffb51b0b29dd71672fb64f6e60be56757e6de507886ef2f5c2ff86dd9b7 evaluated on
all96COMPOSE155images through the existing explicit-manifest exporter, CPU,
640letterbox/confidence.001/NMS.7. Inference exit0,8.6s,all96accounted for.
No new model/training, source pixels, final data or thresholds changed.

Custom pageControl AP50=0. At predeclaredconfidence.25/IoU.5:0hits and48unmatched
page detections. Other40class metrics unavailable because composition annotations
are intentionally page-only; this is not full41class mAP or DS-G8 evidence.
Development recipes are exposed, not an independent final-release holdout.

36images have page candidates at.001;32best-overlap centers lie inside truth.
Median best-overlap IoU.2123,width ratio4.5317,vertical center error.383pixels;
maximum IoU.3089. This supports investigating old container labels, but does not
prove causation or guarantee geometry repair resolves the60candidate-absent images.

Verified all900native r8train image/label hashes and sidecar recipe bindings,
unique IDs,700UIKitControls+200KitchenSink. Frozen repair inventory contains exact
source references and configs; no regeneration yet. Existing UIKitControls is
interactive automatic, unlike qualified noninteractive automatic probes. Resolve
that style through actual-context rendering before native annotation integration.

Evidence under `reports/work/IOS-NATIVE-PAGE-150/artifacts/`:
`page156-{freeze,manifest,predictions,report,diagnosis,repair-inventory}.json` and
`page156-labels/`. Source entrypoint `scripts/page_baseline156.py` supports prepare,
infer,report,inventory,diagnose. All outputs collision-protected, source hashes
bound, exact checkpoint/category/settings verified, failed inference rejects report.

Verification:8focused tests pass; required offline Swift build/test logs
`.build/page156-{build,test}.log`. Software and local evaluation integration verified;
data eligible for scoped development diagnostics. Model gate not passed. SMB not
applicable: no new TTR request or changed navigation authority. Existing worktree
changes, raw captures, old corpora and shipped models preserved.

Next substantial tranche: qualify automatic-interactive and full-width controls in
their actual generator context, integrate tight backing-aware annotations with
owned-window cleanup tests, regenerate exact900into a new version, verify unchanged
5200evaluation members, then one preregistered matched candidate. Use frozen96for
page-only development comparison; preserve separate final qualification requirements.
