# Minimum host version for optional TTR models

Owner: Maximum-mini-NUIAK. Date: October 8, 2026.

## Decision

Set both NUIAK package manifests to macOS 14. Keep Swift tools 6.0.
Do not raise TTR's macOS 14 minimum. Keep model use optional regardless of OS version.
This change permits package integration at that deployment target. It does not qualify every model on macOS 14.

SwiftPM requires a dependency's deployment target to be no higher than its consumer's target.
An application setting cannot remove that package constraint. A runtime availability check does not fix package resolution.
See [SwiftPM platform rules](https://docs.swift.org/package-manager/PackageDescription/PackageDescription.html#supportedplatform).

## Evidence boundaries

| Check | Meaning |
| --- | --- |
| Root package builds with macOS 14 minimum | Source availability and the actual target graph pass on the current SDK |
| Root tests run on macOS 27 | Current-host behavior passes; this is not an older-host test |
| Standalone models load on macOS 27 | Current artifacts load on this host only |
| Executable records `minos 14.0` | The binary targets macOS 14 |
| Actual macOS 14 execution | Not yet verified |
| Signed TTR sandbox | Not yet verified |

Maximum-mini-NUIAK uses macOS 27.0.1, arm64, with the resident Xcode toolchain.
The root build and all 161 tests pass with the macOS 14 target.
The standalone test loads all 3 bundled models on this current host.
The actual root `ModelFreeProbe` runs without selected models and reports a typed unavailable error.
The deployment target describes the runtime OS. It does not guarantee that the current Xcode runs on that OS.
Do not claim Intel execution or newer model-format compatibility from this Apple Silicon test.

## TTR policy

- Link `NativeUIAuditKitRuntime` for optional model use without bundled model resources.
- Start with models disabled and no automatic network request.
- Keep OCR and other independent TTR capabilities available when NUIAK has no selected model.
- Use explicit trusted models and record their exact identities.
- Report unavailable when loading, host compatibility, or model validation fails.
- Keep model results in observer mode until their separate qualification passes.
- Do not convert an unavailable focus model into score zero.

On macOS 14, keep model inference experimental or disabled until that host passes the required checks.
This policy does not block building or reviewing TTR with the macOS 14 deployment target.
Do not hard-code macOS 15 as a proven model minimum. It also lacks direct runtime evidence here.
Each model's catalog records its own tested hosts and restrictions.

## Remaining acceptance

Run startup without models and without network access on an actual macOS 14 host.
Then test approved model loading, fixed-frame inference, unavailable results, restart, and the signed TTR variants.
Record OS build, architecture, source commit, model hashes, preprocessing, and each result.
If no macOS 14 host is available, report that limitation. Do not install or downgrade an OS automatically.
Compilation success removes the package-version blocker. Host testing removes the runtime qualification blocker.
