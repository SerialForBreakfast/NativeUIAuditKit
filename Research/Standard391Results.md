# Standard failures and shared evaluation results

Date: 2026-10-14. Scope: S391-01 and S391-02 from the [combined plan](Plans/StandardResearch391.md).

## Decision

Prioritize missed control proposals and matched native movement versus content-change examples.
Do not replace the baseline with the notification candidate. It still loses 6 previous successes in the reviewed comparisons.
Use the new shared adapter for compatible cached comparisons in future jobs.
Do not change current specifications, approvals, or running workers to apply it.

## 1 Verified retained evidence

All 5 STANDARD390 jobs complete. The review verifies their specifications, result receipts, output hashes, producer records, and model identities.
The [case inventory](../reports/work/STANDARD391/verified-r2/inventory.json) preserves 4,734 comparison rows across 8 comparisons.
These rows include repeated and reversed views. They are not 4,734 independent trials.
Training rows remain separate from development and retained evaluation.
Historical OS profile uncertainty remains explicit; these files do not prove that every screenshot uses Standard settings.

### Detector and classification findings

| Measurement | Retained result | Next decision |
| --- | --- | --- |
| Localized reviewed controls | 346 / 583 | Test proposal coverage before assuming the crop classifier is the main problem |
| Missed reviewed controls | 237 / 583 | Prioritize rows and collection items in controlled generation |
| Missed list rows | 115 / 224 | Test wide controls and localization tolerance |
| Missed collection items | 95 / 301 | Test cards across size, position, and decoration |
| Localized focused targets | 21 / 46 | Compare lower-threshold proposals against added rectangle proposals separately |
| Complete-frame focus selections | 4 correct, 3 target-not-localized | Use these 7 frames for limited end-to-end reporting |
| Other frames | 39 with incomplete or nonunique focus truth | Do not claim complete-frame accuracy on them |

The retained records contain 81 role-name disagreements among localized controls.
These require taxonomy mapping review before they become confirmed classification errors.
Unmatched predictions do not establish a false-positive rate when labels are incomplete.

### Transition findings

| Condition | Baseline correct | Notification correct | Important limit |
| --- | ---: | ---: | --- |
| Small native Fixture movement | 0 / 8 | 0 / 8 | One recorded group; additional native transfer remains necessary |
| Native forward views | 592 / 640 | 596 / 640 | Candidate loses 2 previous successes despite the higher total |
| Native reverse views | 592 / 640 | 592 / 640 | Candidate loses 2 and gains 2; aggregate accuracy hides the losses |
| Replay forward views | 660 / 668 | 659 / 668 | Candidate loses 1 previous success |
| Global-change views | 226 / 226 | 226 / 226 | Preserve these successes |
| Left-change views | 155 / 226 | 155 / 226 | Candidate makes 65 false changes |
| Center-change views | 85 / 226 | 85 / 226 | Candidate makes 133 false changes; one gain offsets one loss |
| Identical-neighbor authored cases | 32 / 32 | 32 / 32 | Two small related sets; no new improvement here |

The view names do not establish the location of the focused control.
These are retained comparisons, not new inference or new native captures.

### Explain the 6 losses

All 6 lost cases have unchanged-focus labels.
Their notification scores cross above 0.15 into abstention. None crosses the 0.85 changed threshold.

| Case | Baseline probability | Notification probability | Matched control also loses? |
| --- | ---: | ---: | --- |
| native.npy:343 | 0.03293 | 0.18943 | No |
| native.npy:551 | 0.11390 | 0.15037 | Yes |
| reverse_native.npy:343 | 0.04960 | 0.28545 | No |
| reverse_native.npy:345 | 0.11256 | 0.20023 | No |
| replay.npy:93 | 0.12161 | 0.20553 | No |
| center8.npy:27 | 0.13103 | 0.17386 | Yes |

Four losses occur only in this notification candidate; 2 also occur in its matched control.
This does not establish whether training variation causes them.
The PROGRAM384-D1 multi-seed report has no completed result at this review. Do not substitute HCF crop repeats for that comparison.
Keep all 6 cases in regression reporting. Do not train on these retained evaluation rows or change thresholds to erase the losses.

## 2 Shared evaluation implementation

[evaluation_suite391.py](../scripts/evaluation_suite391.py) reuses the existing `standard390.compare` function.
It supports the current queue's Python-callable interface and a bounded standalone diagnostic CLI.
No scheduler or active worker module changes.

The adapter provides:

- Pinned input and expected-result checks before execution and after resume.
- A bounded decoded-document cache keyed by path and content hash.
- Exact comparison parity against retained per-slice reports.
- Atomic slice files and receipts, with a contract hash for resume.
- Recovery when a crash leaves a slice file without its receipt.
- A lock that prevents duplicate starts in the same output directory.
- Actual progress counts and explicit unavailable ETA.
- Rejection of missing slices, changed support, unknown roles, and conflicting group roles within each source document.
- Immutable completed suite results; later resume does not overwrite the original timing record.

Ancestry checks are limited to the recorded identities. They do not prove that different named groups are unrelated.
The adapter does not run inference, decode screenshots, train weights, or accept models.
It does not batch incompatible encoders or replace a detector evaluation framework.

## 3 Measured efficiency

The [benchmark](../reports/work/STANDARD391/verified-r2/benchmark.json) compares 8 separate processes against 1 shared process.
Both modes read identical pinned comparisons and require exact results.
Three trials alternate execution order. The filesystem cache remains enabled.

| Measurement | Separate processes | Shared process |
| --- | ---: | ---: |
| Median wall time | 0.775 s | 0.259 s |
| JSON decodes per trial | 24 | 20 |
| Document cache hits per trial | 0 | 4 |
| Largest recorded worker memory | 48.1 MB | 57.3 MB |
| Comparison parity | Exact | Exact |

The measured ratio is about 3.0× for this small cached-report workload.
The absolute saving is about 0.52 s per suite. This does not establish a large training or inference speedup.
Shared execution increases peak worker memory here. It remains well below this diagnostic's practical memory needs.
Future image or feature batching needs its own compatibility and performance comparison.

The [resume check](../reports/work/STANDARD391/verified-r2/resume-check.json) reuses all 8 completed slices and recomputes none.
The first benchmark remains preserved. The verified-r2 manifest pins the final adapter with memory reporting.

## 4 Verification

- 56 focused tests pass, including the existing comparison, graph, and evidence tests.
- The real queue child interface passes in an isolated test folder. No second scheduler starts.
- Interrupted receipt writes recover; altered inputs and outputs fail resume.
- Duplicate starts, duplicate comparisons, unknown versions, path traversal, and symlink output tests pass.
- The offline Swift build completes in 9.69 s after cache recovery.
- The serial Swift Testing suite passes 173 tests in 53.224 s. The XCTest suite also passes.
- The first Swift attempt fails because the migrated module cache references the old checkout.
- New isolated module caches resolve that failure without deleting existing caches or changing source.

No model changes, data admission, promotion, or navigation authority follows from these software checks.
The current queue, submitted jobs, approvals, and running processes remain unchanged.

## 5 Next substantial tranche

Implement S391-03's actual fallback entrypoint and separate proposal comparisons.
Prepare P01 for row/card coverage and P02 for matched native movement and content-only changes.
Use the retained loss inventory to define regression consumers, not training membership.
Select a margin correction only after the matched seed report and eligible training examples justify it.
HCF remains a separate optional study.

## Reproduction

Use the resident interpreter with `PYTHONDONTWRITEBYTECODE=1` and `PYTHONPATH=scripts`.
Run `scripts/standard391.py prepare` with a new project-relative output directory.
Run `scripts/standard391.py benchmark` against that directory with `--rounds 3`.
Existing output directories remain immutable; do not overwrite this evidence.
The worker entrypoint is `evaluation_suite391.run`, with its pinned manifest staged as `config.json`.
Future queue jobs need complete dependencies and individual admission through the existing path.
