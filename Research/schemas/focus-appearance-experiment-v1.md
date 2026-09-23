# Focus appearance development adapter v1

Internal research contract; not public API or production corpus admission.
Implementation: `scripts/focus_appearance_experiment.py`. Existing assembly CLI
dispatches `focus-appearance-input-v1`; experiment CLI dispatches the sealed
`focus-appearance-experiment-v1`. Legacy protocols retain their original semantics.
The advisory `focus-appearance-proposal-v1` remains unsupported as a trainer input.

## Input and reconstruction

All references are `{path, sha256}`, project-relative, with symlink/path checks.
The input contains `proposal`, `protected`, `additions`, `evaluation`, `selection`.
Proposal/protected audits must have valid content seals. The adapter reconstructs
native/retained membership, receipt labels and runtime crops from original sources;
recomputes the proposal audit and sampling; rejects changed membership or weights.
Known Remotes source membership and visual diagnostic frame inventories remain
hash-bound and excluded. No pickle/model checkpoint deserialization is performed.

Additions use existing assembly source records: `{id, manifest, review}`. A
`focus-source-review-v1` binds every source pair to its original development
partition and related group, with known relationships, reviewer and review reference.
Only reviewed v1.4/v1.5 Fixture development sources are supported as additions.
Original source approval remains unchanged; `originSplit` and `use` make the
experimental proposed training role distinct from source admission.

Native and Fixture are logical sampling buckets; direct and TTR Fixture adapters
must not receive separate source masses. Half the training probability goes to
each bucket, then equal scene/style/control strata, then equal labels. All weights
are positive, sum to one and address exactly the training membership. Partial
duplicates are reported; full duplicate pairs and conflicting crop labels reject.
Related groups, original lineage, raw/crop pixels, reserved families and Fixture
seeds join transitively across capture adapters before partition checks.

## Independent evaluation and checkpoint selection

Each evaluation item supplies `role` (`appearance-validation` or `final-challenge`),
`stratum`, a reviewed `source` and a hash-bound `reservation`. Source review must
declare untouched prior use, known relationships and `independentFamily`.
The reservation has version `appearance-evaluation-reservation-v2`, matching
role/stratum/family, `previouslyUsed:false`, reviewer and reviewReference. This is
a review assertion bound by the future maintainer approval, not authenticated proof
of history. Source evidence and cross-corpus lineage/pixels are still checked.
Existing development-only manifests cannot be promoted by writing these fields.

Require two unrelated connected groups with both labels in each role/stratum:
dense-dark-media, bright-unfocused-artwork, gray-blank-placeholders,
dock-neighbor-focus, photos-buttons. Missing groups are explicit readiness gaps.
The current real input has none. Protected known challenge/visual evidence cannot
be substituted. Final-challenge rows are audited but never returned to training
data loaders or checkpoint selection; scoring them is a separate assignment.

`selection` supplies policy
`minimum-equal-source-validation-bce-retention-floor-earliest-tie`, threshold0.85,
nativeRetentionFloor and a hash-bound reference. Reference version
`appearance-retention-reference-v1` binds model/checkpoint, ordered native retention
membershipSHA256, threshold, reviewer, reviewReference, and complete predictions
(`id`, `label`, finite `probability`). The floor must equal the frozen reference's
sample accuracy. This minimum retain-reference policy is explicit, not an optimized
choice. No default floor or native-only selection is accepted.

The trainer minimizes the mean of native-retention BCE and appearance-validation
BCE only among epochs meeting the floor, preserving earliest ties. With no eligible
epoch, it returns failed_no_eligible_checkpoint and no best.pt; last.pt cannot be
used as an implicit fallback. Reporting thresholds are not tuned during execution.

## Authorization and safe usage

Evaluation reservations now require `appearance-evaluation-reservation-v2`:
the existing role/stratum/family/previouslyUsed/reviewer/reviewReference fields,
plus `source` equal to the exact assembly source record and `membershipSHA256`
equal to `digest(sorted(source_rows, key=id))` before role reassignment.
This binds manifest/review hashes and decoded source membership; it is not proof
that a family is genuinely independent. Existing lineage/coverage/admission checks
still apply. Reservation-v1 evaluation admission is rejected as unbound. Existing
no-evaluation protocols and other experiment contracts are unchanged. No actual
independent evaluation corpus had been admitted under v1.

Assembly publishes immutable membership/configuration/sampling plus protocolSHA256,
but trainingEligible/releaseEligible stay false. Preflight distinguishes valid fixed
configuration from missing data/selection/approval. The production entrypoint rejects
this contract; the explicit experiment path requires `warm-stretch` and a safe new
run name. Approval version `focus-appearance-approval-v1` binds approved:true,
protocolSHA256, runName, arm, reviewer and reviewReference. Files do not confer user
authorization. An actual separately authorized run additionally requires the existing
exact experiment-log entry before model imports. Explicit conflicting configuration
flags reject rather than silently overriding the frozen protocol.

Commands (placeholders are not allocated experiment IDs or permission):

```sh
python scripts/focus_mixed_assembly.py --input INPUT.json --output NEW_ASSEMBLY
python scripts/train_focus_ring_detector.py --experiment-protocol NEW_ASSEMBLY/focus_dataset_manifest.json --experiment-arm warm-stretch --name NEW_RUN --preflight
# Only after evidence review, separate authorization, hash-bound approval and log entry:
python scripts/train_focus_ring_detector.py --experiment-protocol NEW_ASSEMBLY/focus_dataset_manifest.json --experiment-arm warm-stretch --name NEW_RUN --experiment-approval APPROVAL.json --experiment-id LOGGED_ID --execute
```

Use the repository-approved Python environment, project-local caches and logs.
Current real preflight must exit2 with launchEligible:false. This adapter does not
waive 6,000-pair production quotas, six model gates, export parity, physical
qualification or separate promotion. It never launches capture or downloads weights.
