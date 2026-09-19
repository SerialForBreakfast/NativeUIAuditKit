# Assembled corpus v1

P4-B consumes normalized records and deterministically preserves each source split.
It rejects cross-split equal content or family keys; calibration and held-out records
never enter training. Class weights and coverage derive exclusively from training.
Toy blends are parameterized, not scientific blend decisions; P5-B binds real corpora.
