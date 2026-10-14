# HCF335 results

Maximum-mini-NUIAK implements `scripts/focus_batch_harness.py`.
The runner uses TTR's existing authored renderer. It does not change the TTR repository.

## Verified execution

- 12 focused tests pass.
- The offline Swift build passes.
- All 14 XCTest cases and 173 Swift Testing cases pass with scoped permission.
- The real pilot produces 4 pairs across 4 layouts.
- Two detached runs complete 2 jobs each.
- Resume preserves the first 2 job receipts and their files.
- Final verification checks every completed file against its receipt.
- Total pilot storage is 5,291,933 bytes.

The pilot uses default artwork placeholders. It tests execution, not corpus diversity.
It compiles the renderer once and reuses its checked binary.
The pilot uses a 60 s operation limit, 256 MiB output limit, and 2 GiB free-space requirement.
The default load limit of 8 correctly defers execution. The bounded pilot explicitly uses 12 at low process priority.
No automatic retries occur while resources remain busy. An external caller starts the next attempt.

The sandbox rejects low-priority scheduling on the initial detached launch.
Scoped approval allows the same operation. Its original log remains available.
The sandbox also prevents Core ML access in the first Swift test pass.
The approved repeat passes. Both test logs remain available.

## Evidence

Raw evidence stays under ignored `reports/work/HCF-335/`.
The frozen plan records renderer, runner, and artwork identities.
Each job receipt records image hashes, dimensions through validation, decoded hashes, and the focus identifier.
The final state hash is `f37602e5bb13dc14d677a846d450c1e697a7d871d021b88b42b3d7066c389791`.
The renderer source hash is `247e08fe394f7f550aaeee2c5e5a1205eb70735b605bf671c85b0919d5dfc2df`.
The runner hash is `3f4db49bae808cec5eb474a8c54adeca0929264f89e03b55bfb0feb70b94e425`.

## Limits

Software verification passes for this adapter. Authored generation and resume pass live integration.
Native HCF integration remains pending. Training eligibility remains false. Model quality is not assessed.
This runner does not claim GPU reservation, label review, or production-quality focus effects.
It installs no scheduler. No experiment or training process remains running from this test.

Sillycon-TTR reports a successful Standard/HCF roundtrip and restoration.
Its source remains uncommitted. Restart recovery and broader native qualification remain open.
Maximum-mini-NUIAK needs the committed interface before adding the native adapter.

## Coordination and next work

Maximum-mini-NUIAK reads forwarded TTR messages at cursors 191, 193, and 195.
It acknowledges through cursor 195 and answers all 7 architecture questions.
The reply `nuiak-hcf335-review-01` is stored at cursor 196. Exact-ID readback passes.
Peer reading and work acceptance remain unconfirmed.
The completed test update `nuiak-hcf335-result-01` is stored at cursor 198. Exact-ID readback passes.
Final attention shows 0 unread messages. This does not establish peer acceptance.

Next, add the native adapter after source delivery. Check original-profile restoration and recovery before unattended native batches.
Then run the 48-image matched rules/model pilot with additional verified no-focus cases.
Keep this authored test separate from that pilot and from final evaluation.
