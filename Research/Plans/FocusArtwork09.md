# FOCUS-CAMPAIGN-09 — reviewed artwork training comparison

Owner Codex, October 1, 2026. Maintainer explicitly answered “Use the six pairs
for training” after approving all six sampled screens. This reassigns exactly the
six received campaign pairs from producer calibration to consumer development
training. Preserve producer manifests and original roles; it does not reassign the
remaining42 cases or make any synthetic layout an independent test.

Complete exact admission, post-review crop QA, one local prefix-encoding pass for
12 unique owned-target crops, two matched runs and evaluation/reporting. Reuse the
existing partial-detail trainer and resident weights. FDR031 is the1550-control
comparison; FDR032 adds12controls. Both retain identical315development+18retention
controls, seed42, frozen features[:9], trainable features[9:], frozen batch norm,
1152→64→1 head with disabled context columns,32-control microbatches, AdamW,
head LR.01/tail LR.0001,100updates maximum,300training seconds each. Existing
source/label weight continuity policy redistributes fixture mass without changing
OS/human weight. The12 crops are six focused/unfocused target pairs, not312new
independent examples. No augmentation, threshold adjustment or protected-test use.

Reuse historical prefix activations; encode only12detail inputs. Disabled context
features may be zero for additions because this model never consumes that stream.
Verify identical prefix identity, crop hashes and ordered cache membership. Bound
encoding to300seconds and32MiB additions; total outputs≤2GiB, model execution≤1800s.
This assigned comparison uses the local experiment tranche authorization; no new
downloads, device capture, export, promotion or speculative rerun. Compare matched
updates as well as terminal results when time limits yield different update counts.
Report artwork hits, false positives, frame selection and retention separately.
Small same-family development additions cannot establish broad generalization.

Acceptance: actual CLI integration; admission/split/cache failure tests; offline
Swift build/tests; exact evaluation membership and metrics; tail changes with BN
fixed; logged outcomes and updated local/TTR status. Keep FDR021 unchanged.
