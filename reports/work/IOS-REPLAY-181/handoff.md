# IOS181 — complete case audit and next comparison

Completed without new inference, capture or training. Existing019/020/021predictions
validated against pinned model/corpus/settings and every case counted.49.049s audit.
Diagnosis seal d456df73daf40baf1a77464b580c634ae3e22b5516cb9c00237c2f78ef4f741a.

## Findings

Against020,021sheet false positives:191spatially retained,268introduced,44resolved;
one lost true positive restored. Cancel:85retained,174introduced,0resolved, no new
true positives. Sheet errors:400OnboardingPage,50GalleryPage,9NotificationCenter;
median false score.869. Cancel errors:158CardDetail,101WizardStepFlow; median.763.
These high-confidence errors do not justify a blind longer run or threshold tweak.
Spatial association uses IoU.5 and is diagnostic, not stable object identity.

Page development loses10hits, gains0 versus020;15new FP,2resolved. Retained page
set loses17hits but gains60 (net43), with6newFP and10resolved. Distribution-specific
tradeoffs would be concealed by a single aggregate. All33fit geometry misses are
KitchenSink. Scroll gains50operating hits with58newFP; AP remains below019.

Full lists cover2400images ×4classes ×3models plus96page images ×3models; totals
exactly reconcile support/TP/FP/FN with published metrics. No reliance on the scorer's
first100error examples. Raw confidence/boxes, dimensions, truth and dispositions
remain in `artifacts/diagnosis.json` for reproducible geometry/ranking inspection.

## Proposal and decision

Do not increase epochs now. Replace only80empty replay fillers with80nonempty train
members selected deterministically using inverse current class-image support,
selected family support and image ID. Keep216fit +136positive replay unchanged.
Selected39KitchenSink,24RichContentFeed,17SystemNavigationShell. All432image/label/
annotation hashes, split ancestry and pixel exclusions verified; no changed roles.
Selection never used held-out error families or confidence. This is a hypothesis
about useful labeled context, not proof that hard negatives are harmful.

`artifacts/proposal.json` seal
e1f0b6a4dfddd4ecd42ebf499db0ecc8ef25867bbbd8949021078f401dc5882c.
Same019initializer,10epochs,540minibatches/69updates and179gates. New isolated
staging/config plus complete decoded-image/label launch preflight remain required;
proposal deliberately launchEligible=false. No run ID or training process allocated.

## Verification / outcomes

8focused tests passed: counts, duplicate detections, spatial association, empty
cases, collision, deterministic selection, pixel deduplication, exhaustion and
catalog-backed native family provenance. Actual audit and proposal CLI exit0.
Initial proposal attempts failed before output on missing inline family fields;
resolved from the pinned source catalog without inventing metadata or changing
canonical rows. Full offline Swift build and serial142tests passed; logs
`.build/diagnose181-integrated-*`. No Git writes; pre-existing edits preserved.

Software verified. Data retains existing training roles; proposal is not launch
admission. Local analysis integration verified; live TTR/model gates not assessed.
No new candidate, promotion or shared iOS noise. Companion182completed exact TTR
pilot transfer/receipt; semantic intake remains separate. Big Dog180ack unobserved.

Next substantial tranche:184qualified positive-context run and full matched report;
independently183source/schema pilot intake when its prerequisites are available.
