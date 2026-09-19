# P5-A handoff — validation-only training preflight

**State:** review-ready (2026-09-19)

## Delivered

- `scripts/training_preflight.py` validates explicit fresh weights or resume
  state, but rejects both together; it checks corpus configuration, all three
  splits, labels, taxonomy, hashes, and output collisions.
- `train_ios_model.py --validate-only` exits before cache setup, Ultralytics
  import, MPS setup, downloads, inference, or training.
- Fresh training now accepts explicit `--initial-weights`; the planned full-frame
  defaults are 150 epochs, cosine scheduling, seed 42, warmup and existing
  full-frame augmentation. `--dry-run` remains real training and is not preflight.

## Outcomes

| Outcome | Result |
| --- | --- |
| Software verified | PASS — 3 deterministic preflight/CLI tests and Python compile pass. |
| Data eligible | FAIL (expected) — no real corpus was bound; valid config reports `launchEligible: false`. |
| Integration qualified | NOT APPLICABLE — no producer or external integration. |
| Model gate passed | NOT APPLICABLE — no inference, training, export, or promotion. |

## Next

P5-B remains blocked on P4-B plus eligible real synthetic and trusted fixture
corpora. The next substantial unblocked packet is P3-A, deterministic regression
selector software on a toy corpus.
