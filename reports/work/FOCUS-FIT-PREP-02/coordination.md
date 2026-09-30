# Coordination receipt

Verified existing smbfs mount for sillycon.local/SharedStatusFile. Both named
archives received locally2026-09-30T18:43:45Z; receipts preserve exact sizes/hashes.

Published packet FOCUS-FIT-PREP-02 in
`/Volumes/SharedStatusFile/nuiak/status.yaml`, observed18:47:44Z, valid19:17:44Z.
Contains two exact receiver receipts, diagnostic-only intake,64/64production crop
parity, producer clamp-flag correction request
`nuiak-20260930-crop-audit-clamp-flag` and cleanup acknowledgment request.
Only sender may remove its exact receipted shared copies after verifying receipts.

Initial publication readback passed; removing our inserted block reproduces prior
file SHA256`a31e5b3cd5622644b995a01953e8148b9d8fe7685280cb6c21ea582be4b58676`,
proving unrelated bytes preserved at that read. Final timestamp correction is
limited to our packet. Final unique-key safe YAML parse, exact timestamp/readback
and the same unrelated-byte preservation check all passed.
Peer status read was18:15:02Z; no acknowledgment of this new packet observed.
No peer source/executable ran. Original archives and source evidence retained.
