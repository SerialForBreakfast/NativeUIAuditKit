# Production acceptance evidence map

The approved FDR-010 run is a transfer checkpoint, not a full production campaign.
No gate below has been waived. Authoritative requirements:
`Research/FocusRingDetectorSpec.md` §5 and `Tasks.md` FOCUS-DET-05.

| Requirement | Current evidence / remaining work |
|---|---|
| At least6,000 eligible pairs |313 training candidates +9 retention; this is not yet the qualifying corpus. Inventory older archives before collecting replacements; historical counts are not admission. |
| Scene mix |gridMatrix≥2,000;mediaShelf≥1,500;settingsList≥1,000;actionDialog,heroCarousel,focusMaze≥500 each. Canvas presentation is not silently reclassified as an independent scene family. |
| Theme mix |At least20% light and20% highContrast within gridMatrix+mediaShelf; frozen full-corpus inventory required. |
| Hard negatives |Held-out n≥100 across light/highContrast × imageView/collectionItem; each combination nonempty. Training examples cannot satisfy held-out support. |
| Independent appearance validation/challenge |Five strata in each remain unqualified: bright-unfocused-artwork,dense-dark-media,dock-neighbor-focus,gray-blank-placeholders,Photos-buttons. New seeds alone do not establish independence. |
| Accuracy≥99%;FPR≤0.5%;FNR≤1% |Not established on qualifying held-out data. Current real-world benchmark is development-exposed. |
| Precision≥0.98;recall≥0.98 at0.85 |Not established. Report support, misses and false positives rather than a negative-heavy accuracy headline. |
| Hard-negative FPR≤0.5% independently |Unassessed; empty support never passes. |
| CoreML parity and package≤5,000,000bytes |New candidate conditional on measured improvement; no export yet. |
| Actual detector→focus chain |Current benchmark uses human boxes; detection failures, OCR fusion and end-to-end focus selection remain separate. |
| Physical transfer and safe navigation |Observer testing is not autonomous navigation. Need approved task scopes, wrong-action/safe-stop/recovery evidence and rollback before control release. |

## Staged delivery, without open-ended iteration

1. Complete FDR-010 and one same-input comparison. Pass/fail determines whether
   an observer test artifact is justified; no automatic second candidate.
2. Rank failure families, specify exact synthetic variation and minimal real-source
   transfer evidence. Use automated native labels; avoid per-letter or duplicate
   human annotation. Review generated recipe exemplars and audit measured defects.
3. Freeze training/validation/qualification membership before a volume campaign.
   The source-separated qualification set must not become a failure-mining set.
4. Scale the qualified factory to the existing quotas, with resumable accounting,
   deduplication and production crop QA. Requires a scoped capture assignment,
   not blind generation of6,000 siblings or another manual annotation marathon.
5. Train one full candidate only after admission/selection checks, report all six
   gates and physical transfer, then conditional deployment verification. Release
   requires explicit promotion authority; broader navigation retains its own gate.

No reliable calendar date follows from a pair count. The next measurable output is
real-screen improvement or a precise failed transfer pattern, not more tooling alone.
