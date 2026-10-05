# Native page integration: qualified, preserved failures

## Final result — October4

Historical failures below are superseded by successful frozen-clock capture:
24/24actual UIKitControls/KitchenSink cases pass across two profiles, two themes
and three seeds. Test35.901s,exit0; all48PNG hashes, dimensions, differential bounds
and24sidecars independently audited by scripts/context157.py. Eight seed19
overlays reviewed: tight page indicator bounds in both actual template families.
Evidence: ../IOS-NATIVE-PAGE-150/artifacts/context157-audit/report.json and
context157-frozen.xcresult; raw copied output context157-capture.

The intermediate diagnostic matrix completed24cases with4accepted/20rejected.
Retained failure pixels showed activity-indicator movement outside the page frame.
The fix pauses the owned root layer clock before the visible render, keeps it
paused for the hidden reference, and restores speed/timeOffset/beginTime.
The outside-control guard was not weakened. Failed batches remain intact.

Data eligibility is development qualification only. Native integration qualified
for this matrix; no900training records rewritten and no model gate assessed.
Next: regenerate exactly700UIKitControls+200KitchenSink into a new corpus version,
preserve666manual repairs and all5200evaluation records, validate before training.

## Preserved diagnostic history

Final integrated offline Swift build/test exit0 in .build/native158-{build,test}.log;
12focused Python tests pass; git diff --check passes. Earlier incomplete outcome
statements below are retained history, not the current acceptance status.

Added opt-in contextual measurement to existing UIKit and SwiftUI capture APIs.
Original exported PNG is preserved; a known public UIPageControl is temporarily
hidden in the same window, restored with defer, and RGBdifference>4 yields its
body. Changes outside public control frame expanded1pt reject. Other annotations
are preserved; default annotation behavior unchanged. Owned windows now detach
root controllers on cleanup. No public detector API/model/corpus was changed.

Native build1/2 succeeded on Xcode27.0/27A266a. First test on exact iOS26.5
F3EF9DB8-0B0F-4757-B653-D1628269F6FF completed3light UIKitControls cases and rejected
first dark case with Cocoa259. Exact guard unknown; do not claim animation or a
background cause. Failure evidence includes completed PNGpairs/sidecars and
failure.json under IOS-NATIVE-PAGE-150/artifacts/context157-failed1.
`context157.py --partial` independently verifies hashes, RGBdifference, sidecar
identity and bodies for all3. One rejected and20unattempted cases remain explicit.
First native test exit65; test binary SHA
070fca8aebcca19f7845f37e1c0382ff640acfa49ca9b2bb204c6b4a42e50a1e.

Revised diagnostic implementation retains failed visible/hidden PNGs for an
outside-control difference, reports its pixel location, and accounts for all cases.
Its build passed, but diagnostic launch was denied by SBMainWorkspace/FBS service
as Busy/application preflight failure before any test-start event. No new capture
or qualification followed. Verified exact owned xcodebuild PID60204command, sent
TERM after3m34s waiting, wrapper exited-15. No daemon/simulator shutdown/reset,
download/signing workaround or repeated unchanged attempt. Native integration
remains incomplete. Reconcile app-launch readiness before rerunning diagnostics.

Logs `.build/native-page150/context157-{build,capture}.log` and corresponding
build2/capture2 logs; both xcresult bundles preserved in artifact root.
Offline Swift build/test exit0 in `.build/context157-{build,test}.log`;7focused
Python tests pass. Those do not override failed native qualification.

Parallel useful outcome: verified Big Dog's robust153receipt exactly against
28,924bytes/SHA and retained its start report. Peer reports DTM050PID37337CUDA,
9000updates at23:05:47UTC,15CPU/CUDA/resume checks pass. Shared NUIAK status updated
and read back; worker native-data efficacy remains pending. No SSH or new payload.

Outcomes: software build/offline checks passed; native acceptance incomplete.
Data:3development samples verified, no full batch/training admission. Integration:
UIKit positive prefix only; SwiftUI actual-template path not reached. Model gates:
not assessed. Existing900training records remain unchanged.

Next: finish exact-target readiness diagnosis without service resets; run the
instrumented matrix once ready, fix the evidenced cause, then regenerate exact900
into new version with unchanged5200evaluation hashes. Independently intake/evaluate
worker comparisons when returned; this runtime issue must not block that lane.
