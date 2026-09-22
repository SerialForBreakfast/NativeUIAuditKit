# Sandbox operating guidance review — 2026-09-22

Completed documentation/skill update, no runtime or security changes.

Sources and actionable diagnosis table: [SandboxOperations](../../../Research/SandboxOperations.md).
Researched official Apple file access, inheritance, distribution/notarization,
signing metadata and DTS permissions guidance, plus official OpenAI agent security.
Reviewed supplied write-up against sources rather than treating it as authority.

Updated BP-67 instead of retaining a blanket recommendation to remove App Sandbox;
corrected BP-37/38 guarantees that environment variables eliminate all side effects.
Worker-execution and repository-local TTR skills route permission failures through
the new guide. Fixed TTR's previously broken ../../Research link using the actual
repository-relative path; explicitly labeled the NUIAK-local supplement rather
than claiming a new portable producer skill revision. Existing unrelated edits
preserved; ADR-0010 and training quotas/augmentation were not modified.

Validation: both skill-creator quick_validate calls exit 0; new research/worker
links and changed TTR link resolve; git diff --check exit 0. Case walkthroughs:
restricted export → scoped export without recapture; Finder metadata → artifact
inspection rather than certificates; actual writer denial → producer writer
diagnosis; unresolved native focus → label issue, not permission repair. These
are evidence-based desk checks, not independent live skill benchmarks.

Software verification: documentation/skill structure passed. Data eligibility,
live integration and model gates: not applicable. No Swift build or simulator
test run for prose changes. No permissions weakened, global config changed,
certificates altered, app re-signed, services restarted, or data moved.
Shared coordination not applicable: repository-local operating guidance, no new
producer assignment or runtime result. Producer architecture recommendations are
not published implementation requests or modifications to TVTestRig.

Next: use the receipt template on the next actual operation; measure repeated
denials/approval wait and artifact handoffs before claiming time saved. A deliberate
TTR packaging/entitlement redesign would require its own scoped assignment.
