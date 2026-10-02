# Real transfer diagnosis32

October2 assignment: continue after maintainer confirms all six proposed identities
and focused/unfocused states. Record that confirmation against inventory31 indices
1,2,3,4,5,8; preserve source annotations. Use these12inputs only as development
diagnostics, not training admission or independent evaluation. Native effect/profile
history remains unknown, particularly on rows/tabs.

Three fixed comparisons, frozen FDR036, no optimization/threshold search:
1. Six pairs through the production cropper with a fixed20% window defined by the
   unfocused reference. Report0.5/0.85 and advisory0.15/0.85, per-pair ordering,
   current/reference body containment and neighbor overlaps. Reproduce four Home
   baseline scores against31 to check runtime/model parity.
2. Home neighbor-body neutralization: union of all neighboring annotated bodies
   from both frames, same mask on both crops, exclude the union of target bodies,
   fill128. Record pixel fraction and score changes. This tests sensitivity to
   visible neighboring bodies, not their shadows or every context cue.
3. Home target-body neutralization: union of target bodies, identical mask on both
   frames, fill128. Compare with original and neighbor masks. Artificial masks
   introduce distribution shift; changes support sensitivity, not causal proof.

Independent lightweight comparison: fixed mean-luminance ordering on the same
six approved pairs and Home crops. This is a paired diagnostic, not a single-image
focus classifier, and cannot establish navigation/no-op reliability. No fitted rule.

Maximum24 model inputs, one batch,300seconds model execution,256MiB outputs. Resident
MPS/dependencies only; project-local outputs; host Apple runtime caches as needed.
Pin inventory, labels, model, code, actual crop/runtime and result hashes. Add tests
for union masks, target exclusion, dimensions, membership, invalid scores and fixed
accounting. Full offline Swift build/test at handoff. Deliver grouped Markdown
results and a specific next hypothesis, preserving shipped models and source pixels.

Preflight before any model invocation found four wide Settings references extend
beyond the right screen edge under20%context. Preserve the failed preflight receipt.
Score these only in a separately labeled clipped-context diagnostic using the
existing production makeCrop clamp; record requested/actual window and retained
context fraction. Do not relax the live advisory geometry gate or count these as
fully contained transfer evidence. Remaining four pairs are fully contained.
