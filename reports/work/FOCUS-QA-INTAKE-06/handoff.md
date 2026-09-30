# Geometry QA and clamp correction intake — 2026-09-30

| Outcome | Evidence |
| --- | --- |
| Software verified | Existing bounded receiver reused; no application/source integration changed. Producer94tests are reported, not rerun here. |
| Data eligible | Diagnostic reports accepted; no new training admission or examples. |
| Integration qualified | Both transfers and55declared members verified; correction agrees with retained consumer evidence. New live CLI/MCP runtime not tested. |
| Model gate passed | Not assessed; no inference, training or promotion. |

## Receipt and semantic checks

Verified expected smbfs endpoint;45GiB project filesystem free. Existing
`synth05_receive.receive` used with exactly the two assigned immutable names/sizes/hashes,
fresh gitignored destination, bounded extraction and5GBreserve. No source code executed
from the handoff. Exact timestamps/size/hash evidence: `received/receipt.json`.

- `ttr-crop-clamp-metadata-20260930-r2.tar.gz`:11230bytes,
  SHA256`b64d1eb7d79894a76c4c64d3c914f905effe480e5bf85475ef99cc9e6e53541e`;
  7declared members verified.
- `ttr-corpus-geometry-qa-20260930-r1.tar.gz`:2313696bytes,
  SHA256`d44a665e57418736e7845df5e251d84a177f4fd2ad4016a710c0457fd94a6bd1`;
  48declared members verified. Included producer sources retained only; no merge
  into NUIAK or edits to TTR.

Revision2supersedes the exact retained audit hash. All64clamp flags true→false;
all other record fields unchanged, all64retained PNG hashes verified, expanded edges
remain in-image within1e-9pixels. Original audit preserved; use revision2for reporting,
not as64new training samples. Existing crop parity remains valid.

QA summaries/artifact hashes and JSONL counts independently reconciled:
- New4pairs:64measured rows,0unavailable,0clipped,64neighbor intersections.
  All64rows match retained source+metadata identity, focus, bounds and crop windows.
- Older44pairs:704rows,352measured wrapper rows and352unavailable artwork rows;
  0clipped,192neighbor rows. Original older source corpus not revalidated in this
  intake; acceptance covers supplied report integrity/accounting, not new provenance.
- Presentation-effect bounds unavailable in all768rows. Thus `needs_review:0` is
  not complete coverage, absence of visible clipping, training eligibility or proof
  that all enlarged focused artwork fits. Neighbor overlap is not automatically a
  defect and no margin change follows from this report.

`semantic-verification.json` records successful checks. First comparison attempted
image-hash-only identity and stopped: repeated pixels can belong to different native
observations. Corrected key includes source filename, metadata hash, element and role;
all64keys unique. No source corruption or label changes inferred from that false start.

## Next

Fresh producer status19:45:47UTC now advertises the matched24proposal and reports
8wide gray native-button slots unsupported (MATCH-APPEAR-01). Proposal archive has
not been received in this two-handoff assignment. Next inspect its21members and exact
geometry/content mapping, return acceptance or specific corrections, and retain those
8blocked slots rather than substitute transparent buttons. No new human annotation.
Capture still requires compatible recipes and fresh bounded target authorization.

No new code means no redundant Swift build/test run. No device action, external
storage work, background job or cleanup performed. Sender owns removal of the two
exact shared archives after checking published receipts; source originals retained.

Published exact receipts and semantic feedback to verified
`/Volumes/SharedStatusFile/nuiak/status.yaml`, owned packet `FOCUS-QA-INTAKE-06`,
19:52:10UTC. Duplicate-key-safe YAML parsing and exact receipt readback pass.
Sender cleanup/peer acknowledgment remain pending; publication does not establish
either. Integration pass in that entry covers receipt/report compatibility only,
not new live CLI/MCP qualification.
