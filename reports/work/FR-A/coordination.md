# FR-A coordination publication

**Publication:** published  
**Destination:** `smb://sillycon.local/SharedStatusFile` → `nuiak/status.yaml` → `packets.FR-A`  
**Published at:** 2026-09-19T23:47:12Z  
**Readback:** passed; YAML schema version 1 and the owned FR-A entry were parsed and verified.

The published consequence is limited to an additive future-capture contract:
`focus-ring-alignment.v1.json` requires source-backed navigation/VoiceOver target IDs,
interaction mode, and expected relation for ADR-0007 examples. The request ID
`nuiak-20260919T234712Z-fr-a-alignment-contract` asks TVTestRig only to acknowledge
whether it can emit those fields. It does not request device operation, capture, transfer,
training, or release.

Peer acknowledgment has not been observed. Publication/readback proves storage only; it
does not establish producer support, integration qualification, or data eligibility.
