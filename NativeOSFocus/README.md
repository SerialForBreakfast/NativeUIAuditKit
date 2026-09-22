# Native OS focus probe

Independent, opt-in tvOS XCTest target. Not part of `swift test`, not a trainer,
and does not use TVTestRig or Fixture services. See
[the execution contract](../Research/Plans/NativeOSFocus.md).

Build from the repository root using project-local temporary and derived data:

```sh
TMPDIR="$PWD/.build/native-os-focus/tmp" xcodebuild build-for-testing \
  -project NativeOSFocus/NativeOSFocus.xcodeproj -scheme NativeOSFocus \
  -destination 'generic/platform=tvOS Simulator' \
  -derivedDataPath "$PWD/.build/native-os-focus/DerivedData" \
  -disableAutomaticPackageResolution CODE_SIGNING_ALLOWED=NO \
  CLANG_MODULE_CACHE_PATH="$PWD/.build/native-os-focus/module-cache" \
  SWIFT_MODULE_CACHE_PATH="$PWD/.build/native-os-focus/module-cache"
```

Execution requires explicit approval for runner installation, native Settings
activation, standard simulator runtime storage and six directional inputs on the
exact assigned UUID. Freshly verify target availability and exclusive interaction;
do not run alongside another capture. No `booted` target, clones, fallback device,
downloads or retries. Use test-without-building, disable parallel testing, enable
test timeouts (120 seconds), and a new project-local result bundle. Preserve failed
xcresults; inspect attachments before deriving any training examples.

The probe leaves Settings foreground. Up/Down reversal is not a restoration claim.
An unchanged focus or ambiguous AX tree stops the probe rather than exploring
more broadly. No Select/Menu/Home inputs are sent.

Evidence: paired PNG/JSON attachments carry native AX observations bracketing the
capture, image hashes, dimensions and timestamps. A terminal-context attachment
records completed input count. Native text may contain personal information;
keep raw evidence local. Host execution records must bind the artifact to the exact
runtime and target. No visual alignment or training eligibility is inferred solely
from a passing XCTest result.

## Bounded root sweep and development intake

`testSettingsRootSweep` is a separate opt-in test: up/down/up boundary-seeking
legs, at most 40 inputs/300 seconds, no Select. It requires the Settings root
context and accepts stable boundary no-ops. Missing focus is observed for up to
ten seconds, never repaired by speculative input. A failed/unfinished sweep
cannot be admitted. Do not run both tests accidentally; use `-only-testing`.

After an authorized run, export its attachments from the retained xcresult and use:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python scripts/native_os_focus_dataset.py \
  --attachments reports/work/OS-FOCUS-02/root-sweep-02/attachments \
  --target 9026ECA9-77DB-4AE6-8FE6-BB239E9571FA \
  --lineage tvos26.5-settings-root-default-layout-development \
  --output NEW_PROJECT_LOCAL_DIRECTORY \
  --model NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/Resources/FocusRingDetector.mlmodelc
```

The example identifies existing evidence, not permission to operate that target.
Output collision fails. Keep partial output after errors. The manifest is immutable;
record visual review separately, bound to `manifestSHA256`. Source/runtime/build
evidence stays with the capture. All pairs are development-only; the existing
training validator deliberately does not accept this as a Fixture manifest.
Repeat sweeps of this layout retain the same lineage, not new evaluation groups.
