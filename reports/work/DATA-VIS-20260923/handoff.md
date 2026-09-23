# DATA-VIS inventory — review

Owner: NUIAK architect. Base b3f0546; existing dirty consumer, temporal, retention,
research and report changes preserved. No implementation or dataset bytes changed.

| Outcome | Result |
|---|---|
| Software verified | Not applicable: source-backed inventory/planning only |
| Data eligible | Not newly assessed; incomplete prefix remains incomplete |
| Integration qualified | Not newly assessed; reused retained native render evidence |
| Model gate passed | Not assessed; no inference or training |

## Acceptance evidence

- Source-backed axis matrix and three bounded next assignments:
  Research/Plans/VisualStateCoverage.md. Flags unsupported/partial evidence explicitly.
- Re-read all14,340 sidecars from `.build/debug-output/p0c-resume/r6-verified-prefix`;
  verified each SHA-256 against `reports/work/IOS-COV-20260923/prefix-audit.json`.
  No changed sidecars. Exit0 for both read-only aggregation commands.
- All136,671 annotated element states are enabled=true/selected=false. Writer source
  confirms defaults, not measured state. Do not use these fields as evidence of
  control-state diversity. This does not invalidate their object boxes.
- Exactly five status tuples, each2,868images. Each clock has exactly one battery
  level. Charging occurs only at09:41/100%; operator text only empty orAT&T.
- Theme/profile joint counts: dark/17Pro/3x7,170; light/SE/2x6,570;
  light/17Pro/3x600; dark/SE/2x0. Marginal balance hides missing intersections.
- Theme/type: dark medium2,427/xLarge2,368/xxLarge2,345; light large2,427/
  accessibilityMedium2,368/small2,345. Largest accessibility size30pertheme.
- en_US/LTR13,900 and ar_SA/RTL440. Allportrait/phone,unknown osVersion.
  Accessibility true counts: bold1,000,contrast500,reduceTransparency500,
  buttonShapes500; onOffLabels/smartInvert0. These are metadata counts.
- Revalidated all12 retained r5 status probes' PNG/JSON hashes and image dimensions;
  decoded all PNGs using Pillow. Historical per-axis decoded hashes are distinct:
  battery5,cellular4,Wi-Fi3. Source test holds clock/content fixed. Evidence directory:
  `.build/debug-output/p0c-resume/r5-preflight-evidence/status-axes-C5623A27-A184-4F0D-9351-DC4CE1130059`.
  Reference `reports/work/P0-C/r5-preflight-validation-20260922.json`.
  No new simulator run or claim that every corpus image renders its recorded status.

## Source entrypoints

- GeneratorRunner/GeneratorRunnerTests/GenerateDatasetTests.swift:
  simulatorStates,makeConfig,dynamicTypeSize,testPaintedStatusAxesChangePixelsWithFixedClock.
- NativeUIDatasetGenerator/Sources/GeneratorConfig.swift: controllable configuration.
- NativeUIDatasetGenerator/Sources/AnnotationWriter.swift: effective emitted state.
- NativeUIDatasetGenerator/Templates/ChromeCoverageTemplate.swift: painted status,
  template-specific theme, charging bolt and cellular saturation at four drawn bars.
- NativeUIDatasetGenerator/Templates/ScreenshotCapture.swift: partial trait application.
- Existing APPEAR evaluation/new contract reports: source-supported tvOS axes and gaps.

## Reproduction

Use `.venv-yolo/bin/python` with `PYTHONDONTWRITEBYTECODE=1`; no outputs or caches
outside the repository. Read audit.members, replace each PNG suffix with.json under
the explicit prefix root, verify annotationSHA256 before counting. Count the requested
image keys and generatorProfile.simulatorState values with collections.Counter;
count joints, not just marginals. Count all elements' state values separately.
For the12 probes verify imageSHA256/annotationSHA256 against the pinned report and
Pillow.load plus dimensions. Do not dump high-cardinality filenames into summaries.

Initial exploratory output included filenames and was truncated; subsequent scoped
state/probe aggregation completed successfully. A source search referenced a nonexistent
AnnotationExporter.swift; corrected to the actual AnnotationWriter.swift. Neither
diagnostic changed any source or dataset. Analysis completed in seconds, no external wait.

## Handoff

Inventory scope complete for review, implementation/capture remain separately scoped.
New lesson BP-94 covers joint coverage and default labels. Content/link/diff checks
replace unnecessary package rebuilds for this documentation-only change. Existing
Swift/Python test results were not relabeled as new passes.

Next: VIS-A truthful state/config provenance, then VIS-B independent schedule and
separately authorized probes. Do not modify preserved P0-C membership or launch
training. P0-C still needs the outstanding split-allocation decision. SMB not applicable.
No running processes. Worker-execution and model-workflow skills informed evidence
boundaries; historical skill scaleFill advice was not applied to shipped YOLO.
