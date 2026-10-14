# RESEARCH340 — corrected evidence and controlled dashboard

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

Owner: research-host-NUIAK. Date: 2026-10-12 UTC.
[Plan](Plans/MeasuredResearch340.md). [Queue](../Tasks.md).

## Decision

The previous dashboard gains are not measured model improvements.
The evaluator assigned scores for 100 jobs. Of these, 75 had completed execution.
Their files remain unchanged. The corrected dashboard excludes their scores and blocks further placeholder execution.
The 4 existing audit/training replays remain replay evidence, not new model gains.

The dashboard now has a prominent current-task panel and authenticated local controls.
It shows actual steps or pair counts, elapsed time, stop controls, and explicit unavailable ETAs.
Static HTML remains read-only. Model acceptance stays separate from job completion.

## Experiments completed

The queue contains 20 new investigation specifications and 4 retained-data extensions.
Six diagnostic jobs complete. They reuse recorded predictions or verified pixels without new training.
The 18 blocked main specifications retain exact missing requirements.
B4 and C3 provide partial cached answers, not complete coverage of their original questions.

| Check | Measured result | Decision |
| --- | --- | --- |
| Artwork precheck | Correct artwork-only decisions vary from 72/128 to 112/128 across 3 families | Preserve family-specific errors; do not claim broad appearance robustness |
| Position precheck | Correct movement decisions range from 66/96 to 78/96 across 4 corners | Add controlled center and edge comparisons before correcting position bias |
| Factor precheck | Small controls with thin, low-contrast effects produce 4/48 correct movement decisions | Prioritize retained detail and effect visibility |
| Boundary check | 469 rows have comparable measurements; 79 remain unavailable | Do not replace original windows; boundary ranking harms 2 content groups |
| Reversal check | 4 disagreements on 640 native-derived pairs; 10 on 668 replay pairs | Preserve the asymmetric failures; do not change thresholds from inspected examples |
| Magnitude check | 384 forward pairs produce 0 matches at the frozen 10% tolerance | The corpus cannot answer equal-magnitude discrimination; generate matched controls |

The factor names `sizePixels` and `widthPixels` refer to the historical reduced coordinate scale.
The corresponding authored control body is 30×45 source pixels; the thin border parameter is 10 source pixels.
The 4/48 result does not describe a literal 3-pixel-wide native control.
Wider effects at low contrast produce 42/48 correct movement decisions for that small size.
Related examples and reversed pairs are not independent trials.

The magnitude job starts from the browser through the actual queue. It completes in about 5 s.
The other 5 cached checks each complete in less than 1 s.
These times exclude prior capture, inference, training, and evidence preparation.

## Physical diagnostic from peer-host-TTR

All 3 offered files match their sizes and hashes. Safe extraction finds 1 PNG, a manifest, and a README.
The PNG hash is `104f802009f2134093dd7171b7f63b53248655efcc3cbdd35b62ae1f1a912fff`.
The image remains development-only. Profile, native observations, and precise accepted boxes remain unavailable.

The shipped tvOS detector and FocusRing score the unchanged image through `nativeui-audit`.
The detector proposes the visible Computers control. FocusRing gives that proposal score 0.08942.
FocusRing instead selects the App Store control with score 0.99805.
Visual review supports Computers from its outer white outline and caption.
This is a useful reviewed disagreement, not a verified native accuracy result.
No image or proposed annotation enters training.

## Candidate decision

No new candidate starts. The cached checks do not repair the missing controlled comparisons.
The strongest next comparison preserves both original windows and adds boundary evidence for thin effects.
The equal-magnitude check needs matched content-only negatives before training.
Do not repeat rejected FOCUS329 or use the old assigned scores to select an architecture.

## Verification and limits

All 97 focused tests pass, including the real measured evaluator through authenticated HTTP.
The offline Swift build passes in 5.72 s.
All 14 XCTest tests and 173 serial Swift Testing tests pass.
Loopback tests require scoped host permission; the initial sandbox denial is preserved.
No package download, Git write, physical-device operation, export, or promotion occurs.

Raw evidence stays in ignored `reports/work/RESEARCH-340` and the existing research queue.
New specifications stay under `Research/ResearchSpecs/RESEARCH340`.
Full experimental qualification remains incomplete where controlled inputs or native observations are missing.
