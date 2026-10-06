# Checkpoint-only continuation — October 6

Implemented `scripts/prepare_worker198_supplement.py` for the already assigned
Run027/028 worker comparison. It packages only the verified fixed-last treatment
checkpoint and a pinned metadata manifest, reusing the retained 585 windows.
No training, input transfer, inference, threshold change or promotion was launched.

The production CLI calls existing treatment `ready()` (sealed sources, dependencies,
completion, ten epochs, finite CSV, resolved args and checkpoint hash), then checks
recorded optimizer events against the frozen schedule. Parent manifest and all
1,179 inventory members are validated before writing. The two-member archive is
re-read with exact sizes and hashes. Existing outputs, symlinks, changed inputs and
unfinished/failed runs are rejected. Partial evidence remains on failure.

Verified retained parent SHA256:
`b47e5b11726b05a2c0d7c8c6103fbf15c8779ddf38c78f4ff08fdbb092e700ea`.
Parent: `artifacts/eval02701/payload/manifest.json` within this packet.

## Verification

- `python -m unittest scripts/test_prepare_worker198_supplement.py scripts/test_prepare_worker198_eval.py -v`:
  nine tests pass, 0.033s; no inference. Tests use project-local disposable fixtures.
- Actual parent validation: all 1,179 entries pass; original data roles/settings
  remain identical and inference-only.
- Actual CLI called during live Run028: exit1 at missing sealed completion.json;
  confirmed `artifacts/eval028-not-ready-check` does not exist. This is the expected
  refusal, not a failed training run or permission to restart it.
- Required resident offline Swift build exit0; Swift tests exit0, 132 tests across
  17 suites in 7.086s. Logs `.build/worker198-supplement-{build,test}.log`.
- `git diff --check`: pass. No Git writes, no edits to pinned training sources.

Big Dog terminal02 now acknowledges acceptance of the original 585-record scoring
slice and preserves its original completion timestamp. Deadline repair was accepted
separately. No duplicate request, input bundle or GPU scoring was sent.

## Next actual operation

After Run028's live session is terminal-successful, invoke the supplement CLI with
the parent path/hash above and a fresh `artifacts/eval02801` output. Verify results,
then publish a bounded Run028 request and archive using the existing receipt flow.
Worker must preserve its resident backend/settings, use the accepted external timeout,
bind new Run028 request/output identities and never modify retained Run027 results.
NUIAK still owns paired metrics, backend checks and efficacy decisions. The local
all-MPS comparison stays distinct from CUDA/hybrid diagnostics.

Software verified; data eligibility unchanged; real supplement delivery pending
training completion; model gates not assessed. No continuous mailbox monitor added.

## Actual completion and delivery

Run028 session98307 exited0. Existing readiness checks and supplementary schedule
check passed:10epochs,245optimizer updates,4596.362605seconds. Fixed-last SHA256
`df8e8f18a2d124ebc6207e5c482c81c37c9aed22e7bd87e60fba20f314af8db8`.
The real CLI produced/replayed exactly two archive members at
`artifacts/eval02801/nuiak-worker198-eval028-v1.tar.gz`,37,427,541bytes,
SHA256 `97a85a20e084e76f08fa1e776a93a918e3d3b72eecf060da73c217aaff32387c`.

Archive published/hash-readback verified at `nuiak/nuiak-worker198-eval028-v1.tar.gz`.
Request `nuiak/requests/nuiak-20261006-worker198-eval028.json` also published/readback:
3,386bytes,SHA256`f158ee917c2cfdd067e79250af97d6456918764537c2e9463d28899042a5faea`.
Worker receipt/start remain pending; publication does not prove execution.
No repeated control inference requested. NUIAK local all-MPS comparison launched
separately in session41011, serial arms and existing refinement/extra-proposal paths,
log `.build/style210-evaluation.log`. Session41011 subsequently exited0; matched
results are in `reports/work/IOS-STYLE-210/comparison-handoff.md`. Seven model gates
remain failed; this does not change the worker's fixed inference-only assignment.
