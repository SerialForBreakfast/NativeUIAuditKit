# R-A and BADGE-A offline tranche

R-A supplies an offline matrix validator that requires capture provenance, counts unique
content rather than filenames, separates screenshot count from genuine ground-truth mAP
examples, rejects predictions as labels and duplicate content, and requires a >=500-cell plan.

BADGE-A specifies append-only taxonomy v1.1: `badge` is ID 41 and exclusively a notification/
status dot or count marker. Existing map IDs 0–40, sidecars, and bundled model decoders are
unchanged; future 42-class models must declare their map.

Software verified: PASS (offline contract tests). Data/integration/model qualification: not
applicable. R-B needs an authorized capture window; BADGE-B waits on the accepted 41-class milestone.
