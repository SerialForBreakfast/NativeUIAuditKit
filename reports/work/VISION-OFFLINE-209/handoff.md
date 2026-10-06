# Vision verification isolation — October6

No library or test assertions changed. Existing full native run waited in Vision's
controlled-capacity queue; its sample and exit143are retained in ART191evidence.

Three subsequent checks:

1. Existing same-image test alone:1passed/0.091seconds.
2. Existing FrameSimilarity suite with explicit `--no-parallel`:8passed/0.279seconds.
3. Entire native suite with explicit `--no-parallel`:132passed in17suites/4.100seconds,
   no filter or exclusions. Session84078exit0.

Logs `.build/vision209-{single,suite,full}.log`. Commands use `--build-system native`,
`--skip-build`, `--disable-automatic-resolution`, project-local scratch/config/cache/
security/TMPDIR/module caches and scoped execution permission. Successful build already
recorded in `.build/schema4-build-scoped.log`; skip-build does not substitute for it.

This establishes a verified full-suite execution path, not a proven concurrency root
cause: explicit serialization, prior single-test initialization and cached system state
are confounded. Do not claim an OS Vision bug or silently change production compute
units. Native build engine is deprecated; it is a current workaround for the separate
swiftbuild Finder-metadata signing failure, not a permanent architecture choice.

Full offline verification blocker cleared for this integrated tranche. If the wait
recurs, capture exact command/runtime and isolate one request before remediation.
No model gate/data admission changes, service resets, certificate edits or test removal.
