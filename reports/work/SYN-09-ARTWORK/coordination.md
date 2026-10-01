# SYN-09-ARTWORK coordination

Published/read back at **2026-10-01T13:55:00Z** on the OS-verified
`smb://sillycon.local/SharedStatusFile` mount:

- `/Volumes/SharedStatusFile/nuiak/status.yaml`, only `packets.SYN-09-ARTWORK`.
- `/Volumes/SharedStatusFile/nuiak/responses/nuiak-20261001-syn09-artwork-receipt.yaml`.

Duplicate-key-rejecting YAML parsing, immediate pre-write reread and post-write
comparison confirmed unrelated packet/top-level entries preserved. Response bytes
match local `response.yaml`. Exact named archive size/hash/member verification is
receipted. Sender owns cleanup of that one shared copy after verifying receipt;
consumer originals remain local. No producer files or hardware state were modified.

Latest producer snapshot read was2026-10-01T07:20:26Z; treat its runtime state as
historical, not current device readiness. This task used retained artifacts only.
Peer acknowledgment of this new receipt and sender cleanup are not yet observed;
neither blocks completed local QA. No monitor or automatic retry was installed.

Follow-up stays under `nuiak-20261001-corpus-source-layout-contract`: preserve both
reserved source exclusions, retain240as a collection target, and propose genuine
variants for78missing per-slot targets. The new dark-parent/child exclusion is a
consumer reservation consequence, not a failed producer geometry repair. Current
geometry does not need recapture. A smaller approved experiment remains possible
before target completion; this publication authorizes neither capture nor training.
