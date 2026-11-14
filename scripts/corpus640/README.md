# CORPUS640 renderer and focus-pair checks

This directory contains the original 300-frame UIKit renderer.
`main.swift` has SHA-256 `73ff3834488aae24ade150fb171eec79102181460c97ba406ee7bde46096d1d5`.
The source matches the renderer used for the recorded capture.
This directory does not include captures, labels, or model outputs.

The renderer makes 6 layout families with 10 layouts and 5 states each.
The capture driver uses live Simulator screenshots and records native focus observations.
It does not use the renderer's in-app image path.
The earlier in-app renderer did not match the live Simulator screenshots.
Modal action ownership remains unknown when the public geometry join is unavailable.
A focus observation is not a complete detector label.
The generated layouts and their derivatives retain their assigned training-only role.
Do not treat related states or later cue variants as independent evaluation groups.

## Build

Use macOS, Xcode with the tvOS 26 Simulator SDK, Python 3, and `codesign`.
Run these commands from the project root:

```sh
python3 -B scripts/corpus640/build.py --output .build/debug-output/corpus640-build
python3 -B scripts/corpus640/test_capture.py
python3 -B scripts/corpus640/test_pairing.py
```

The build uses a new project-local directory and does not start a Simulator.
The pairing checks also need NumPy and Pillow in the selected Python environment.
The source hash is checked before the build.
The build receipt binds the source and executable hashes.

## Capture

An authorized, booted tvOS Simulator and exclusive target ownership are required.
Complete the applicable target, alert, cleanup, and permission checks before capture.
The command refuses an existing app installation or an existing output directory.
It does not retry uncertain stages.
After a successful run, it terminates and uninstalls the app that it installed.
It verifies that the owned app is absent before it writes the completion receipt.
After a failed run, it preserves the installation for reconciliation.
If a capture fails, preserve the failure receipt and reconcile the target before another attempt.
Use a fresh project-local output directory:

```sh
python3 -B scripts/corpus640/capture.py --simulator "$CORPUS640_SIMULATOR" --build .build/debug-output/corpus640-build --output reports/work/corpus640-capture
```

You can also set `CORPUS640_SIMULATOR` and omit `--simulator`.
The driver records original images, repeats, native observations, and hash-bound receipts.
It caps each layout group at 800 s and 100 MB of screenshot data.
It caps the full run at 4,500 s and 2 GB.
The driver operates only the app that it installed and launched.
It does not restore the previously foreground app.
Do not run capture from a build or validation test.

## Verify focus pairs

After a complete capture, run:

```sh
python3 -B scripts/corpus640/validate_pairs.py --packet reports/work/corpus640-capture --output reports/work/corpus640-focus-pairs.json
```

The verifier checks source and image hashes, repeated screenshots, and native observations.
It keeps missing focus separate from explicit no-focus.
It excludes partial geometry and unstable screenshots.
It rejects changes outside the 2 focused control bodies.
It excludes identical pixels with conflicting focus IDs and cross-role duplicates.
This strict check can reject valid focus effects outside native bounds.
It does not train a model or change data admission.
