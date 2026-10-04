# FLOW123 — deterministic receipt handling; publication primitive gap exposed

Implemented `scripts/shared_transfer.py`: read-only default, explicit named
publish/receive/cleanup, current verified SMB endpoint, namespace/path/symlink guards,
bounded metadata and streamed file validation, current source size/hash, exact
receiver receipt and local-original preservation. Unknown/duplicate transaction
fields rejected; expiry is not accepted as cleanup authority. Atomic exclusive
publication, no replacement fallback; completed staging may resume, partial stage
is preserved. No extraction, training admission, mounting, remote execution or Git.

27Python tests pass (11real-file transfer plus16feedback); offline build and139Swift
tests pass. Tests cover read-only/no-write, real macOS exclusive rename/no overwrite,
completed replay, interrupted/partial staging, wrong receipt request/path/bytes/hash,
missing/altered original, receive receipt without admission, mount/space/namespace/
symlink/traversal/protected-status rejection. Mount mocked only for local fixtures.
Logs .build/transfer123-{tests-final,build,swift}.log; successful checks exited0.

Real CLI inspection: completedv1 local original verified, exact peer receipt verified,
shared copy absent as expected. Consumer-v2 original/shared bytes verified, receipt
missing, so cleanup remains prohibited. These inspection JSON reports are adjacent.

## Important failed live qualification

Used the tool to publish actual assigned workflow metadata, not a dummy transfer.
Staging copy and SHA verification succeeded. Native `renamex_np(RENAME_EXCL)` failed
with errno45/ENOTSUP on the verified SMB mount. A separately bounded atomic hard-link
attempt on that same complete stage also returned45. Neither final file exists;
no ordinary overwriting rename or permission workaround attempted. Both failures
are filesystem-capability evidence, not receipt corruption or producer model failure.

Stage retained:
`nuiak/responses/.nuiak-transfer-16c9c18c12a5f6a9377e822d.partial`,2426bytes,
SHA256 cca029c45e85ff53a192293b660bb1cba55dc156d0e768ed2756499b5c43c7aa.
Local response.yaml and publication.json unchanged. The staged response includes
an intended successful-publication description; it is NOT a final message and
must not be consumed as success. publication-result.json records actual rejection;
publication-readback.json records verified stage/shared absent. No retries until
the supported protocol is reviewed. No cleanup of unresolved staging/model copies.

Published the compatibility finding only through the existing best-effort owned
status patch protocol, not as an artifact. FLOW-TRANSFER-123entry verified/read back,
duplicate-safe parsing and unrelated semantic preservation pass. Peer acknowledgment
pending. This does not make the failed artifact publication successful.

Outcomes: software/local file lifecycle verified; real SMB inspection qualified;
strict SMB outbound publication blocked; no new data/model assessment. Receive
publication is project-local and retains tested exclusive rename; a future assigned
actual archive still needs independent byte-bound intake. No broad completion claim.

Next integrated tranche: agree/test supported immutable transaction-directory or
equivalent publication semantics on both hosts, then use it for the requested
retained survey26case intake/replay/review. Do not sacrifice no-overwrite guarantees,
receipt matching or admission separation to declare the transfer loop complete.
