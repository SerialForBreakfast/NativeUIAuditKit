# Focus TTR development test cycle

Owner: current NUIAK model-workflow worker. Authorized by the maintainer's
“Ok do this tranche now” after the benchmark/corpus/train/evaluate/export proposal.
This is development testing, not promotion or autonomous control.

Finish batch03 production QA and freeze the three reviewed batches as a development
benchmark. Preserve labels and source receipts. Apply documented batch12 partitions
and exclusions; uncertain roles and keyboard completeness remain unavailable.
Exclude all trial02 members from training. Compare shipped and FDR-009 at fixed0.85
using the existing role-aware evaluator before deciding the next training corpus.

Audit FDR-009 and newly retained dock qualification pairs. A new run requires
eligible data addressing measured failures; do not repeat FDR-009 unchanged or
silently admit test-only captures. If justified, log and pin one bounded candidate,
compare identical inputs and export/verify only if warranted. Otherwise retain
baseline results and report the exact blocker: model delivery remains incomplete.

No public taxonomy, threshold, shipped-weight or protected-challenge changes.
No new capture implied. Reuse production crops and established CPU inference.
Reports: reports/work/FOCUS-TTR-TEST-CYCLE-01/.
