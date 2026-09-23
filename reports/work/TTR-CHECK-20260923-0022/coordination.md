# Unpublished producer feedback

## Superseding delivery — 2026-09-23 00:27:51 UTC

Published to verified `smb://sillycon.local/SharedStatusFile` mount,
`/Volumes/SharedStatusFile/nuiak/status.yaml`, packet TTR-SMOKE-20260922-2119.
Safe YAML parse/readback passed;28 packet entries preserved and the three old
requests retained alongside new request
`nuiak-20260923T002751Z-repaired-fixture-artifact`. No peer acknowledgment of this
new request yet. Previous23:06Z publication is also now observed on the share.

Peer00:06Z reports a newer signed Fixture candidate with artifact hashccf5b742;
its location/hash scope/local availability are requested, not inferred from the
failure of our different older candidate. Acknowledged memory-termination identity
request002518 using historical build hashes only, explicitly no crash attribution.
Runtime observations remain00:22Z; status publication is not a new runtime check.

## Historical unpublished state

publication: unpublished

The SMB mount and `/Volumes/SharedStatusFile` are absent at00:22Z. No reconnect,
mount, lookalike directory or write attempted. Previous23:06Z delivery remains
unverified. Readback and acknowledgment are not claimed.

Intended update for NUA packet TTR-SMOKE-20260922-2119:

- Source6093663 geometry/sidecar-v2 repair received through local checkout/handoff.
- Simulator still runs old9bd3859b Fixture; geometry conflict persists there.
- Repaired Fixture candidate46011bb0 dylib is present, but local strict signature
  verification fails resource-fork/Finder-info detritus. Build success/ad-hoc
  metadata does not establish a valid installable artifact. No attributes changed.
- Need valid repaired Fixture/setup authority before direct resumed capture. No
  extra TTR host signing repair is a dependency of the direct lane.
- Request producer preserve source/candidate evidence and provide a signature-clean
  candidate or support the separately authorized clean-copy staging route. No
  re-signing, certificate changes, Office operation or training requested.
