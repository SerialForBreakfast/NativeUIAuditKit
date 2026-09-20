# P0-C retired route — WKWebView hard-negative rendering

**Observed:** 2026-09-19 during the authorized isolated `ios-41class-r1` simulator reconstruction on iPhone 17 Pro, iOS 26.5.

## What happened

The serial generator completed normal, accessibility, known-bad, and initial protected-holdout families. It then entered `testGenerateHardNegativeWebContentImages`, which is responsible for 400 `HardNegative_2` examples labelled `webContent`.

For repeated capture attempts, the simulator emitted WebKit process/entitlement failures including:

- failure to acquire the web-browser-engine rendering/networking/webcontent entitlement;
- `WebProcess Background Assertion` failures because the target process did not exist;
- repeated `Client not entitled` errors while attempting process termination;
- GPU/Web process idle exits.

Those failures make it unsafe to assume that a captured PNG actually contains the annotated web content. The current annotation validator can prove PNG/JSON structure and hashes, but cannot fabricate semantic proof that a failed WKWebView rendered correctly.

## Resolution

The reconstruction was interrupted with SIGINT before the simulator container was copied. No generated corpus exists under `NativeUITrainer/reconstructed_corpora/`; the only partial material remains in the explicitly authorized GeneratorRunner simulator staging container and must not be treated as a corpus.

On 2026-09-19 the maintainer retired this failed route entirely. The architecture and P0-C recovery plan now exclude `HardNegative_2`; its `webContent` category remains legacy compatibility metadata only and is explicitly reported as uncovered in the new corpus. The generator, test suite, and expected corpus counts were changed accordingly.

## Non-resumption rule

Do not replace this with a synthetic web-content view and do not reintroduce a WebKit renderer into P0-C. Any future proposal to actively generate `webContent` needs a separate architecture decision, a deterministic rendering strategy, and fresh authorization.

The next P0-C capture begins from a fresh GeneratorRunner app container and excludes all prior partial staging output.

## Current capture blocker

After the native-only route removal and passing UIKit validation, the revised `NativeUIDatasetGenerator` launch was terminated with exit status 137 before it emitted a progress line on 2026-09-19. It created no `NativeUITrainer/reconstructed_corpora/ios-41class-r1` destination and the repository volume remained at 11 GiB free. Do not retry the full capture until the external termination cause is investigated; a blind retry could repeat an operating-system resource kill without producing evidence.

The maintainer subsequently cleared disk pressure, increasing available repository-volume space from 11 GiB (98% used) to 158 GiB (63% used), and authorized one fresh retry. This removes the most plausible environmental constraint but does not reinterpret the first exit 137 as a successful capture.
