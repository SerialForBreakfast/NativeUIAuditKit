# Replacement corpus retention and recovery

Owner: repository maintainer. Scope: P0-C reconstruction, not historical recovery.

Keep the raw replacement corpus, its immutable validation/member-hash report,
`reconstruction-configuration-r5.md`, both r4/r5 source hashes and exact source
patches, runtime artifact hashes, the r5 prefix/continuation records, capture ledger,
and capture logs/result bundles together. Keep rejected r1/r2/r3 attempts separately;
never merge their files into the replacement corpus. Preserve the complete failed
r4 evidence as well; only its verified manifested prefix enters r5 with explicit
lineage. Retained duplicate candidates in the corpus's `rejected/` directory are
evidence, not accepted corpus members.
Existing historical labels, symlinks,
and Run 009 reports remain unchanged.

## Recovery verification

1. Identify the exact corpus version and SHA-256 of its manifest and validation
   report. Verify each image and annotation against the report's member hashes.
2. Copy into a **new** project-local restore directory. Never overwrite the source,
   historical exports, or another restore. Use the same membership and split paths.
3. Re-run `scripts/validate_reconstructed_corpus.py` with that restore directory
   and a new report path. Compare manifest, membership, and capture-ledger hashes,
   plus every retained rejection's image/annotation hash. Readiness must
   not improve merely because files were copied; known duplicates remain errors.
4. For a bounded recovery drill, restore representative PNG/JSON pairs plus an
   explicit drill manifest and verify every copied byte hash. A subset drill does
   not prove full-corpus recovery and must not be passed to training.

The in-checkout corpus, simulator staging and a same-volume copy are **not an
independent backup**. Before source cleanup or production reliance, the maintainer
must choose and authorize a backup destination, retain complete versioned contents,
and verify a new-location restoration. No external backup is authorized or claimed
by this assignment. Re-rendering from pinned source is a reproducibility recipe,
not a guarantee of identical bytes on a different Apple runtime.

No cleanup command is provided: deletion of staging, rejected trials or source
corpora needs exact-target review and maintainer authority.
