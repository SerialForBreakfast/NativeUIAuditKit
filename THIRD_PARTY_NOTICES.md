# Third-party notices

This file records attribution. It does not approve every possible downstream use.
The repository's MIT license applies to its covered original code. It does not replace third-party model terms.

## Ultralytics YOLO11

The NUIAK tvOS detector uses Ultralytics YOLO11n and pretrained initialization.
Credit: Ultralytics and its contributors.
Upstream source: https://github.com/ultralytics/ultralytics
Upstream terms: https://www.ultralytics.com/license
Recorded model license: AGPL-3.0.
The full license text is [Licenses/AGPL-3.0.txt](Licenses/AGPL-3.0.txt).
Preserve the upstream copyright, license, and warranty notices when distributing covered material.
No separate Enterprise license is established by this repository review.

### NUIAK modifications and export

The project trains the tvOS detector as Run 012 on September 16, 2026.
The run uses 25 epochs and the project's synthetic tvOS corpus.
The project exports the resulting detector to Core ML with embedded NMS.
The compiled model metadata identifies Ultralytics 8.4.153 and coremltools 9.0.
These records describe model lineage. They do not establish a complete source release.
See [the exact review](Research/ModelLicenseReview304.md) for artifact hashes and unresolved evidence.

## NUIAK original code

Copyright (c) 2026 RA11y Contributors.
The [MIT license](LICENSE) contains the original code's permission and warranty terms.
Keep that notice when redistributing covered code. Do not present it as a license for the YOLO weights.

## Other artifacts

The REVIEW304 public draft excludes FocusRing, iOS weights, screenshots, datasets, and transition candidates.
Each additional artifact needs its own provenance and license check.
Tool usage alone does not mean that the tool's code appears inside an exported model.
Inspect the actual distributed files before adding or removing dependency notices.

## Review status

Attribution is not a replacement for source availability or other license conditions.
The current GitHub model draft remains unpublished pending the documented distribution decision.
This file does not relicense NUIAK, TTR, or any contributor's work.
