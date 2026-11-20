# Maximum-mini-NUIAK nightly review for November 14, 2026

The window starts November 14 at 07:45:42.634 UTC and ends November 15 at 07:47:22.022 UTC. The preceding report supplies the start. Post-window admissions belong to the next results window. All results remain provisional.

## What improved

No verified model improvement this review period. Requiring a second control to lose score improves correct abstentions from 0/30 to 30/30 on fixed-focus brightening pairs, with verified boxes on 15 previously inspected native layouts. Both rules found 30/30 forward destinations. Reverse replay adds no independent layouts. Full-screen association, opposing brightness changes and consumer latency remain unmeasured. [Focus test](../reports/work/SWAP646/README.md)

## What we learned

Three saved NewsTV receipts match the FOCUS633 review completion record. Its readback found 2 correct picks and one miss. The distinct combined-rule consumer timing remains open. [Saved decisions](../reports/work/FOCUS633/reviewed.json) · [TTR timing dependency](../reports/work/FOCUS638/ttr-latency.md)

The archived iOS detector recovered 5 named buttons and lost 1 when input size rose from 640 to 960 px. Matches rose from 3/40 to 7/40 across 3 native layout groups. Shipped iOS Standard found 0/8 small and 4/8 enlarged buttons on separate training-source layouts. [iOS comparison](../reports/work/IOS644/README.md) · [Resolution outcomes](../reports/work/research-queue/jobs/ios644-small-controls-button-family/attempts/1/out/benchmark_summary.json)

## What regressed

All 4 tvOS field-width fits missed the keyword field and every one of the 33 shipped button appearances. These represent 3 named controls across 5 related NewsTV flows. Partial references limit false-positive claims. [Per-arm retention](../reports/work/FIELD645/button-retention.md)

## What runs next

Catalog record B405-295 compares 640 and 960 px at confidence 0.50 and IoU 0.50 with the 2 original 300-screen checkpoints. Each seed uses 21 identical development screens, 442 named appearances and 7 flows. A useful result must recover a lost shipped button for each seed, retain each 640 px success and avoid a new action over the known decorative bell. Check that bell using the retained predictions. A pass warrants matched consumer scoring and timing. A loss stops scale changes. Mixed seed outcomes require target-level review. This PyTorch diagnostic has a different operating point from the shipped Core ML comparison. [Exact jobs, pinned inputs and decisions](../reports/work/NIGHTLY-20261115/news647-batch.json)

## Queue health

The active detached runner was waiting before admission. The fresh global snapshot reported 0 ready, 0 running, 440 dependent, 11 otherwise blocked, 129 exhausted, 29 unselected and 8 awaiting approval. This pass admitted 8 exact jobs. For each prefix news647-s371 and news647-s372, the suffixes are -640, -960, -pair and -roles. Four inference jobs were independent. Four scoring jobs depended on their outputs. No exhausted jobs were continued. At 07:54:42 UTC, 5 were complete, 1 ready, 0 running and 2 dependent. The remaining ready inference represented roughly 5–10 s before dispatch overhead. [Global counts](../reports/work/NIGHTLY-20261115/global-counts.json) · [Admissions](../reports/work/NIGHTLY-20261115/news647-admitted.json) · [Batch readback](../reports/work/NIGHTLY-20261115/batch-readback.json)

The review window contained 32 completed attempts and zero recorded failures. Completed execution occupied 21,415 s. Failed execution occupied 0 s. The other 65,084 s had no recorded runner execution. Intervals are clipped to the window and counted once. [Attempt IDs and intervals](../reports/work/NIGHTLY-20261115/attempts.json)

## Blockers and approvals

Settings and Calendar contain 2 drafts and zero saved iOS references. Joe's approval for 4 exact fits takes effect after independent review. Sillycon-TTR confirmed the diagnostic packet readback and requested corruption checks at the training entry. Maximum-mini-NUIAK reported the missing semantic checks at cursor 2208. BigDog-Coordinator had no later message at inspection. Keep those 11 frames diagnostic. [Owner, acceptance tests and remaining tasks](../Tasks.md)

## Priority changes and reasons

Prioritize focus with detected boxes on fresh flows. Include simultaneous opposing brightness changes at fixed focus and retain failed associations. Keep the tvOS detection study bounded to the 2 existing seeds. Stop width-only fits and cutoff-only focus changes. Preserve separate iOS and optional HCF decisions. The catalog validates 294 definitions including B405-295. [Catalog check](../reports/work/NIGHTLY-20261115/catalog-final.json)
