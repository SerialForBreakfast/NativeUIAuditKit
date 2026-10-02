# Guarded navigation and Office annotation feasibility — 2026-10-02

Tasks: NAV-VERIFY-01 and ACC-MAP-01. Local development candidate, not a release
or NUIAK build. Source ingestion is through Git; no Git writes were performed.
Private originals and detailed receipts stay in ignored
`.local-work/nav-verify-20261002/`. Relevant navigation lessons: N-002/003,
N-008/009, N-011 and N-016.

## Changes delivered

The shared guarded executor now returns an additive `verification` result to CLI
and MCP: verified/ambiguous/stale/unsupported/interrupted, actual completed steps,
failure step, provenance, age and local-evidence escalation. Planned steps and
acknowledged inputs remain distinct from verified progress. Failed runs do not
return a verified final screen/focus. Missing provider usage is explicitly
`unknown_unmetered`; no token-saving percentage is inferred from payload bytes.

Fixture screen identity now binds measured layout, labels/content, visibility,
scroll container, viewport and offsets, with missing values distinct from zero.
Focus growth and observation clocks are excluded. The v2 observation profile
prevents reuse of older v1 maps without fresh qualification. Hidden/disabled/
explicitly nonfocusable selected semantics and blocking interruptions stop input.
Native Fixture evidence remains an oracle, not visual-model accuracy evidence.
The observation profile identifies the provider contract version, not a measured
accessibility-settings profile; broader profile-aware visual integration remains open.

A live image-enabled replay stopped on stale evidence after crop processing.
The original failed trial and invalidated route are preserved. A second trial confirmed that a fresh re-observation repaired age but review work
still consumed the segment deadline. The final repair moves diff/crop generation
after the guarded batch ends. Originals and native before/after capture brackets
remain synchronous; the after-bracket evidence is the dispatch evidence. No
freshness/deadline relaxation or input retry is introduced. Derivative failure
gets an explicit review-unavailable note without rewriting navigation outcome.

## Office feasibility result

Office was exclusively assigned for this audit after coordination checks. The
bounded run saved 42 frames with SHA-256, serialized action/capture receipts and
observed profile provenance. High Contrast and Hover Text were tested individually;
VoiceOver, Reduce Motion, Reduce Transparency and volume were not changed.

**Disposition: identity-only assistance; do not automatically transfer assisted
bounds to ordinary images.** On one freshly matched Home Settings icon, the
agent-reviewed ordinary body reference was 306×183 pixels, versus 253×151
under High Contrast (approximately 1.21× width). References have approximately
±2 source-pixel edge uncertainty; they are not native physical accessibility bounds or human-approved annotations.
Plain Vision's best same-profile proposal scored IoU 0.850 on the assisted body
and 0.940 on the ordinary body. Copying the assisted proposal onto the ordinary
frame scored only 0.580, with horizontal edge errors approximately +33/−36 pixels.
This particular plain rectangle proposal is not the specialized outline detector.
Neither it nor the outline should be treated as the ordinary focused body.

Hover Text traversal reached the Accessibility page heading and VISION heading
where a remembered ordinary control sequence expected rows. Acquisition stopped
at the correspondence failure; the remaining four-control/profile matrix was
not forced through. Zero automatic matches or training annotations were accepted.
Private file names reflect intended samples and are not proof of observed identity.

Restoration was visually verified: Focus Style Default, Hover Text Off. The owned
capture session was finalized, video/control lease released and Office disconnected.
Final status had no active command/observation/queue and audio was inactive. Office
is released; this report does not assert another owner's availability.

Private review: `office-review.html`, `office-manifest.json`,
`office-geometry.html` and `office-geometry.json`. The review contains full originals
and manually referenced overlays; raw screenshots/OCR/account content are not in
tracked documentation or shared status. The rejected restricted Vision process
failed to create a pixel buffer; retained-image host execution succeeded without
changing device settings or any model upload.

## Acceptance ledger

| Criterion | Evidence / boundary |
| --- | --- |
| Shared CLI/MCP compact result | Focused caller tests include actual StableCLIRunner and MCP handler; native verification and provider usage remain explicit. |
| Stale layout/content/hidden state | Production-port tests mutate these while retaining IDs; no input and no verified final state. |
| Scroll identity | Native semantic payload tests distinguish measured offsets/viewport and unknown telemetry; focus-growth-only changes retain identity. |
| Interruption/cancellation/ownership | Guarded runner and existing batch tests retain failure and forbid further input; selected suites also exercise Settings policy refusal. |
| Image evidence | Original brackets/crops retained; regression proves derivative work stays pending during navigation and retains original hashes after finalization. Initial live stale stop retained. |
| ACC-MAP A1/A4/A5 | 42 hashed frames, profile/action ledger, local overlay review and verified restoration/release. |
| ACC-MAP A2 | One manually matched Home control measured; heading correspondence failure rejects transfer. No automatic identity qualification. |
| ACC-MAP A3 | Growth and scroll observations demonstrate limitations; full duplicate/stale/template-matching matrix remains unqualified because no automatic transfer was promoted. |
| Provider comparison | Not run: no applicable provider/budget authorization for a paired model experiment. No invented token counts. |
| Consumer | NUIAK alignment/admission separate and pending. No binary or new corpus publication. |

The bounded Office feasibility experiment is closed with a negative automatic-transfer
decision. The larger ACC-MAP automation acceptance is not complete. Likewise this
native navigation repair does not complete the five-packet NAV-VERIFY program:
visual cue fusion, held-out visual accuracy, nested/exhaustive mapping and a measured
provider comparison remain separate work. No general Settings or physical autonomous
navigation claim follows from this tranche.

## Next substantial work

Recommended core: NAV-VERIFY-01 with SIM-MAP-04/06 — connect the existing local
perception reports to explicit conflict/actionability refusals, exercise a held-out
Fixture matrix (bright competitors, duplicate/headings, scrolling and interruptions),
and qualify a bounded nested Settings map/resume with honest Mermaid gaps. Keep
native labels as evaluation truth in visual-only runs. Deliver compact failure
packets and a predeclared same-episode efficiency ledger; actual provider usage
requires a budget scope. Optional ACC-MAP follow-on: ordinary-image box proposals
with assisted label context and human correction, never direct outline transfer;
a fresh physical trial requires its own current ownership and operation scope.

## Consumer response and retained-reference inventory

NUIAK packet ACCESSIBILITY-ASSISTED-29 acknowledges the optional provider direction
and TTR control/policy ownership. It requires frame/hash/action/clock identity,
verified versus declared profiles, input versus assistive focus/actionability,
typed bounds and correspondence/restoration evidence. Known identity errors or
clipped bodies fail acceptance regardless of IoU; no universal padding/tolerance
is qualified. Consumer runtime integration is still pending.

Response to `nuiak-20261002-accessibility29-mapping-evidence`: the scoped Office
finding above is the requested failure boundary. Ordinary and assisted frames are
review evidence only, not accepted matched training pairs. Raw pixels and OCR stay
private. This report can be shared separately while Git publication remains with
the user.

Response to `nuiak-20261002-native28-real-reference-inventory`: the retained human
run is the existing `ttr-human-focus-office-e93b12da-20260929.tar.gz`, 895,563,805
bytes, SHA-256 `5b90331e3912e10a966b2407dac93d68cae5a028ef42a5841e9d766b69b5a552`.
Its verified local manifest still hashes to
`73c0e5863ac0301798df1339ea60837b95425f73578d9be26410a9aceac81cbf`:
185 actions, 739 frame records and 420 gap records. Per-frame files/hashes and
actual input associations are in that archive. They do not establish native-effect
identity, reviewed ordinary unfocused body bounds or settled same-control artwork
reference pairs. Prior association audit found only three postInputSettled records;
a timing-ready frame is not an independently reviewed focus reference.
The new Office audit likewise has no admitted native-artwork before/after reference
pair. High Contrast versus ordinary is a profile comparison, not focus ground truth.
Reuse the existing recording for NUIAK's human-annotation inventory before scheduling
new capture; do not infer labels or recopy this archive. No qualified real-artwork
reference pair is claimed by this inventory.

## Live repair progression

- `route-proof-01`: stopped after one input because review processing aged the
  native observation (2022 ms). No subsequent route input; failure retained.
- `route-proof-02`: fresh observation age was 156 ms, but the same work crossed
  the 10-second segment limit. Stopped rather than claiming completion.
- `route-proof-03`: after deferring review derivation, two one-step routes completed
  in 8.082 s total; final evidence ages 36/48 ms. Actual MCP replay retained four
  original frames and eight crops with verified hashes/native brackets. A stale
  revision and a modal both sent zero inputs; modal outcome was `interrupted`.
  Session closed and postflight readiness/ownership cleared. No Simulator restart.
- `scroll-proof-01`: recording/trials succeeded. Retained batch outcome proves both
  moves completed in 9.456 s, but MCP lost its response while the caller used a
  30-second socket allowance. Readiness inventory subsequently timed out, then
  recovered on one read-only recheck with ownership clear; no restart or repeated
  uncertain input. The batch and originals are retained. The repair scopes a
  180-second reply allowance to guarded route MCP calls only; navigation deadlines
  are unchanged and post-navigation derivative work is bounded at 30 seconds.

Validation preparation `campaign-04` was interrupted after a local edit-script
syntax error; it is not a test pass. `campaign-05` passed all 82 selected tests,
including the deferred-derivative/original-hash regression. Later consolidated
validation is recorded below; intermediate candidates are not the final evidence.
- `scroll-resume-01`: after retained outcomes and clear ownership were reconciled,
  final candidate MCP replay completed both routes in 10.712 s and returned normally.
  A new 40-point scroll clipped the first card; native diagnostics reported
  `missing_geometry` / `partially_clipped_bounds`, and the mutation receipt correctly
  stayed `uncertain`. Replay sent zero inputs and returned ambiguous/unavailable.
  The harness expected `origin_mismatch`, so its strict expectation failed; this is
  evidence of safe refusal, not a qualified unchanged-focus transition. Original
  failure receipt is preserved. Session closed, postflight `can_run=true`.

Final consolidated offline lane `campaign-06`: **101 tests passed, zero failures,
zero skips**. `build-reuse-04`, `signing-reuse-04.json` and
`portable-gate-reuse-04.json` qualify the final local signed candidate. Planning
coverage, task actionability, skill validation/self-tests and whitespace checks
passed. The episode ledger records native runs separately from the unrun provider
arm; no token-savings estimate or actual consumer acceptance is claimed.

Final complementary case `scroll-visible-proof-01` kept the focused card fully
visible using a nonfocusable leading label. On the final signed candidate, actual
MCP replay completed both routes in 9.851 s and returned four originals/eight crops,
all hash-checked. The new scroll receipt was **observed**, offset `[40,0]`, focus
still `item-0`. Reusing the old viewport route returned `origin_mismatch` in 388 ms
with zero inputs. Stale revision also rejected before input. Session closed and
postflight was ready with clear ownership. Together, the clipped and fully visible
cases show truthful refusal for missing geometry and viewport mismatch respectively;
they do not claim nested scroll remapping or exhaustive navigation coverage.

NUIAK's additional `nuiak-20261002-accessibility29-profile-priorities` request is
recorded in the existing ACC-PERCEPT-01 plan: High Contrast proposals/profile
receipts first, Hover Text optional, later one-setting comparisons and robustness
variants. ADR0044/0045 now remove categorical exact-box, complete-inventory and
deterministic-shortcut assertions in favor of their existing qualification limits.
These are planning corrections, not newly implemented settings controls.
