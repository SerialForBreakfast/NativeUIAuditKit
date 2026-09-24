# Machine and producer–consumer operating lessons

Maintained2026-09-23. Read only the section relevant to the assignment. These are
source/evidence-backed procedures, not standing runtime or training permission.
Tasks.md supplies ownership; dated reports supply evidence, not current readiness.

## Build, test and permission diagnosis

- Use [SandboxOperations](../../SandboxOperations.md) to identify the actual writer,
  path, launch context and underlying error. Agent sandbox, app bookmark, signing,
  privacy consent, CoreSimulator service and missing native labels are different
  failures. A green unrelated storage probe does not test the failing screenshot writer.
- Keep explicit logs, DerivedData, module/package caches and temp paths project-local.
  Simulator containers and Apple-managed service storage need explicit setup scope;
  TMPDIR alone cannot contain them. Never spoof HOME or reset services/certificates.
- Discover the matching running app/helper/companion/Fixture and selected Xcode first.
  Installed builds do not need an ad-hoc source rebuild. Source hash, build artifact,
  installed app and running process identities are separate; pin the relevant ones.
- A known execution-context denial calls for scoped approval, not repeated denied
  invocations. A help-only comparison can isolate helper startup; do not replay an
  uncertain mutation as a permissions test. Stop before capture on ambiguous cleanup.
- Native generation uses an exact UUID, not `booted`. Resolve the app container after
  installation and again before retrieval; preserve old output with a new staging
  name. A valid plist is not an executable test plan: use `.xctestrun`, assert the
  named test actually executed and passed, and distinguish skips from successful work.
- Follow [IterationEfficiency](../../IterationEfficiency.md): focused real-behavior
  tests while editing, affected caller/contract checks at interface changes, one full
  offline Swift build/test pass on the integrated final code. Prose-only changes need
  content/link/diff checks, not a rebuild. Reuse evidence only with unchanged relevant
  source, dependencies, configuration and inputs; fresh operation health is not cached.
- Tests generate fixtures or use deliberate versioned fixtures, never a previous
  worker's ignored reports. Preserve failure logs and report runtime stages separately.

Evidence: BP-67,69,76,83 and BP-95 (native dispatch);
[r6 handoff](../../../reports/work/IOS-R6-20260923/handoff.md).

## CoreML and dependency residency

Distinguish import, optimizer initialization, trace, conversion, compile/load and
inference. A fast warmed `import torch` does not qualify AdamW or coremltools startup.
Use bounded readiness probes only within assigned execution scope, with an external
deadline; no automatic installation/download or model run from a diagnostic.

The observed CoreML incident involved dataless dependency files and errno60, not
proof of bad weights or a sandbox defect. Check exact dependency residency/error
before rebuilding/reinstalling. Materialization-request acceptance is not readable
bytes. An approved pinned non-cloud environment resolved the recorded incident;
use that approved interpreter consistently, including child commands. Do not create
a new environment or infer cloud-provider causality from slow import alone.
Freeze dependency versions and verify reference parity after an environment change.
See BP-69 and [residency evidence](../../../reports/work/FOCUS-EXPORT-01/residency-repair.md).

## TTR feature/repair qualification

1. Read the current relevant source contract and retained failure. An older checkout
   does not prove a revision is absent: inspect the exact available Git object read-only
   before asking for transfer/rebuild. Do not fetch/check out/edit TTR without authority.
2. Determine execution host from actual local runtime, not a screenshot or old status.
   If execution belongs to Sillycon, send a scoped SMB request to its agent; no SSH.
   Acknowledgment is not completion or execution approval. If runtime is local, use
   its matched interface rather than requiring a remote handoff unnecessarily.
3. On a changed candidate, record actual app/helper/Fixture identities and active
   workspace; discover supported commands. Retired attestation and old Office-only
   examples cannot override the installed simulator path. No target fallback or
   assumption that localhost:8080 belongs to the selected Fixture.
4. Qualify the repaired boundary with one authorized bounded smoke through capture,
   completed receipt, export, hash verification, actual consumer/crops and postflight.
   Readiness alone is not capture, successful capture not export, integrity not labels,
   valid labels not training eligibility. Keep every failing stage and expected count.
5. Preserve completed jobs if export fails. Use the matching build's documented
   manifest/chunk export when supported and authorized; do not recapture, write an
   app container manually, or weaken access. `evidence_bookmark_stale` after the
   supported refresh is a concrete producer defect, not another signing/prompt loop.
6. Verify fresh target-correlated responsiveness after teardown. Foreground return,
   process presence, accepted cancel and test success do not prove cleanup/health.
   Human interference invalidates the affected capture; record it before any newly
   authorized retry. No automatic unchanged capture retries.
7. Publish one actionable delta: request/job ID, stage, exact artifact/source scope,
   expected/actual behavior, downstream checks already performed and next owner.
   Ask for an actual complete example and negative compatibility cases, not features
   already provided. A repaired build qualifies only the tested scope.

TTR jobs, direct Fixture/simctl generation and native OS XCTest are separate approved
lanes, not transport fallbacks to evade a failure. Share lineage and serialize a
shared runtime. One lane's failure need not stop independent authorized software or
another independently qualified lane. Reuse the existing cropper/trainer.
Evidence: BP-75,77,85,87,89; [genuine v2 smoke](../../../reports/work/TTR-CATALOG-01/smoke-0514/handoff.md).

## Dataset and evaluation invariants

- Preserve source pixels, labels, ledgers and rejected trials. Broken symlinks/old
  metrics do not prove pixels exist; reconstruction is a new version/baseline. Sum
  remaining families by split before resuming; never move preserved groups to fix totals.
- Inspect actual rendered axes and class support, not requested settings/default
  labels. Use prioritized independent/pairwise schedules; fixed font sizes, theme
  aliases and placeholder catalog classes remain explicit coverage gaps. Exhaustive
  decorative diversity is a long-term goal, not a reason to block valid partial diagnostics.
- Group related recipes, journeys, variants and duplicate content across adapters
  before splitting. Different seed/hash/family strings alone do not prove independence.
  Keep failure-driven development and already-scored challenges out of untouched final
  evaluation. Bind reservations to exact source reviews and actual membership.
- Fixture labels require observed focus callbacks and the frame's actual geometry,
  including scale/clipping; requested focus and predictions are not truth. Capture
  brackets describe correlation, not invented atomic framebuffer IDs. Legacy visual
  review is explicitly weaker than native truth. Semantic VoiceOver alignment is separate.
- Use production FocusRing `makeCrop` (16% expansion,256×256), no independent cropper.
  Bound batches by decoded pixels and count, preserving order. Compare same-runtime
  crop pixels before scores; separate same-backend parity from CPU/GPU/ANE differences.
- Report misses, false positives, wrong/no-focus/ambiguous frame decisions, support and
  cold/warm latency; high tile accuracy can hide wrong focus. Temporal differences
  locate change, not necessarily arriving focus: score genuine switches/no-ops too.
- Missing/unsupported metrics are unavailable, not zero. Compare only compatible
  corpus/taxonomy/preprocessing/settings/metric implementations. Weight compression
  proves neither speed nor generalization; enforce5,000,000-byte FocusRing package
  limit, not rounded MiB. Wire receipts must serialize actual backend/artifact and
  scoring dispositions; bundled-resource presence is not executed-model identity.
- Separate software, data-use eligibility, integration and model gates. Development
  success does not waive6,000-pair/coverage/independence/physical-transfer requirements.
  Log approved experiments first, isolate outputs, preserve shipped models, and return
  diagnosis instead of automatically retraining a failed candidate.

Evidence: BP-69–96, [appearance reservations](../../Plans/FocusAppearanceAcquisition.md),
[artifact retention](../../ArtifactRetention.md). Same-volume copies and hash lists
are not an independent backup; ignore rules neither delete nor untrack old artifacts.

## SMB routing

Use the [shared-status skill](../../../reports/coordination/SharedStatusSkill.md) and
its protocol only for a concrete TTR–NUIAK consequence. It defines direct worker
ownership, mount verification, bounded conflicts, request/acknowledgment semantics
and separately authorized transfer receipts. Do not load peer history or publish
unrelated iOS/test progress. The status share is neither a remote shell nor a lock.
