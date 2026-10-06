# BADGE-A worker return — integration review, October 6

Received `badge-a-runtime-return01.tar.gz`: 37,508 bytes, SHA256
`694a365c6a365771b3b44fae47e79458613262646e0dfbd23badf4df354ba0e1`.
Bounded extraction: 18 regular files, 155,188 expanded bytes. All 12 source-file
sizes/hashes match the returned manifest. Original retained in ignored
`artifacts/runtime-return01/`; no source snapshots applied to the working tree.

The proposal preserves nil-profile custom manifests, explicitly filters legacy
badge observations, and checks strict raw channel kinds before tolerant decoding.
Annotation v1.3 is new here; its diff retains v1.2 constraints and appends badge.
These are useful improvements, not yet accepted Apple integration.

## Corrections before integration

1. **Writer/validator disagreement.** `AnnotationWriter.write/buildJSON` maps every
   non-tabBarItem element regardless of selected schema. A captured badge with the
   default `.legacy`, or `.measuredState`, therefore produces an invalid old-version
   sidecar. The new Python guard rejects exactly that output. Reject badge before
   writing unless `.badgeTaxonomy` was explicitly selected; never silently drop the
   label or upgrade the schema. Test the public writer, both old schemas, absence of
   an output file after failure, and preservation of enclosing annotations in v1.3.
2. **Unspecified map identity.** The two hardcoded `ModelTaxonomyBinding.identity`
   digests are neither current map-file hashes nor SHA256 of compact JSON label
   arrays. This alone does not prove they are wrong, but the returned contract/tests
   do not define their derivation. Define canonical bytes, derive expected values
   independently from the frozen map plus append-only extension, and test that ID,
   order or label changes are rejected. Clarify that taxonomy identity and tensor
   channel mapping are different. Explicitly specify/test whether a strict profile
   permits a subset of labels: current validation accepts any nonempty unique subset
   when the confidence width matches. Do not claim complete 42-class binding from
   that check alone.
3. Return the base source revision and per-file base hashes or a patch against it.
   Returned snapshots identify new bytes, not the base, and must not overwrite
   concurrent NUIAK edits. Correct the stale “All 41” test name when testing 42.

Swift syntax/Python tests in the return remain peer evidence. No full Swift run on
an unapplied proposal is claimed. NUIAK owns Apple compilation and integration once
these corrections arrive; Big Dog does not need Apple dependency installation.

Software: changes requested. Data roles: unchanged. Integration: not qualified.
Model gates: not assessed. No badge training, weight relabeling or promotion.

Review/receipt published and read back at
`nuiak/responses/nuiak-20261006-badge-runtime-review01.json`, 2,463 bytes,
SHA256 `ff3be5595a17f2aa7d41f12ec24e335aa6bdfae21e49e8600e7c8bf7d1b83c33`.
Peer acknowledgment and sender cleanup remain separate and unobserved.
