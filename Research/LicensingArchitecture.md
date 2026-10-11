# Licensing and distribution review

Updated October 8, 2026. This document records evidence and release requirements, not legal advice.
The maintainer reviews applicable terms before public distribution.

The maintainer now selects free, open-source distribution under the applicable AGPL conditions.
Follow the [source and release checklist](ModelOpenSourceReleasePlan.md). Preserve existing MIT notices while reviewing combined distribution scope.

October 9: [REVIEW304](ModelLicenseReview304.md) verifies pretrained lineage and records the exact release artifact.
[Third-party notices](../THIRD_PARTY_NOTICES.md) and the full AGPL text are prepared without changing existing model bytes.
The review finds a recorded export version of 8.4.153 and a resident Ultralytics version of 8.4.124.
Do not substitute the resident version for training-era evidence. Public publication remains held pending the distribution decision.

## Current facts

| Component | Recorded terms | Release requirement |
| --- | --- | --- |
| NUIAK Swift code | Repository MIT license | Preserve the license and review third-party notices |
| Bundled YOLO detectors | Export metadata identifies Ultralytics and AGPL-3.0 | Review the applicable license and intended TTR distribution |
| FocusRing weights | From-scratch training; no AGPL field found in the inspected metadata | Confirm architecture, data, tooling, and explicit weight license |
| Research assets and screenshots | Mixed origins and review states | Do not include them without an exact approved inventory |

The compatibility product `NativeUIAuditKit` bundles 3 compiled models.
The new `NativeUIAuditKitRuntime` product has no dependency on model resources.
This package separation does not approve public distribution of any model.
Moving weights to downloads does not by itself change their license obligations.
Absence of a license field does not establish permission to redistribute a model.

## Primary references

Ultralytics describes AGPL-3.0 and Enterprise options for its code and trained models.
Review the actual terms for the intended use. Do not infer a blanket exemption for testing, converted weights, or separate downloads.
[Ultralytics licensing](https://www.ultralytics.com/license) and [legal terms](https://www.ultralytics.com/legal).

This project does not establish whether a particular downstream application satisfies those terms.
The maintainer can obtain qualified legal advice or written permission where needed.
Do not claim that another framework or from-scratch training automatically removes every third-party restriction.

## Approval record for each released artifact

- Identify the exact artifact, version, source revision, and SHA-256 inventory.
- Record architecture, initialization, source data, training software, and export software.
- Include applicable license text and required notices.
- Record the maintainer's decision for the intended repository visibility and downstream use.
- Keep model-quality approval separate from permission to distribute.

No artifact receives public approval from a passing parser, a model score, or its presence in an earlier release.
The release tool checks an explicit approval reference but cannot verify its legal sufficiency.
See [ADR-0023](ADR-0023-Optional-Model-Distribution.md), [release preparation](ReleasePreparation.md), and [provenance](../PROVENANCE.md).
