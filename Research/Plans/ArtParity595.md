# ARTPARITY595 — Fixture-native artwork data for the tvOS detector and FocusRing

Date: 2026-11-07. Owner: Maximum-mini-NUIAK. Task authority: Tasks.md P0 "Visual parity with real apps".
Requested by the maintainer, 2026-11-07: use TTR's new real-looking Fixture scenes to improve the tvOS UI and focus models.
All results stay provisional until Joe reviews them (AGENTS.md, 2026-11-04). No promotion. The detached runner executes training.

## Evidence that sets the target

- Frozen baseline on 8 TTR native-truth frames ([report](../../reports/work/ARTPARITY595/shelf-pair-report.md)): 0/8 correct for v3 and PILLS560 R5.
- FocusRing scores unfocused bright artwork as focused: shelf competitor 1.000, Northstar Sam 1.000 versus focused Alex 0.996, cinema-1 sibling 0.983 versus focused 0.0002.
- A plain background crop scores 0.998. Flat and brushed artwork give identical scores, so detail alone does not explain the failure.
- Real-app evidence (VisualParityAudit): FDR-010 passes 3 of 19 reviewed real positives at 0.85.

## Data sources (TTR `8053ed1b`, Maximum-mini-TTR)

| Family | Launch | Screens | Use |
|---|---|---|---|
| Field Atlas A, B | `--fixture-field-atlas` [`--fixture-art-set-b`] | 2 | train |
| Cinema Programme A, B | `--fixture-cinema-program` [`--fixture-art-set-b`] | 2 | train |
| Field School A, B | `--fixture-field-atlas --fixture-art-series` [`-b`] | 2 | train |
| Field Atlas C, Cinema Programme C, Field School C | `… --fixture-art-set-c` | 3 | test (lineage holdout) |
| Matchday Replay A, B, C | `--fixture-cinema-program --fixture-art-series` [`-b`/`-c`] | 3 | test (series holdout) |

Each screen gives 3 native focus positions (2 artwork actions, 1 text action) and 1 decorative illustration: 36 frames per pass.
Capture driver: TTR `Scripts/qualify-editorial-gallery.rb --field-atlas|--cinema-program` after a Fixture launch with the edition flags.
It brackets each snapshot with native `ui-observe` of all 3 controls and the illustration, then verifies the reopened recording.
Asset lineage: `Docs/Research/ProgrammeEditions-v1/{asset-lineage,followon-lineage}.json`. Holdout is by lineage: no C-edition or Matchday asset enters training.
Real apps (RC561 corpus, NewsTV development frames, VisualParityAudit cases) stay evaluation-only.

Labels (13 roles, rule B): artwork action = `cell`; text action = `button`; decorative illustration = `picture` (non-actionable).
FocusRing crops: focused control = positive; each unfocused control and the illustration = negative; plus a plain-background negative per frame.

## Capture session plan (1 launch of the new build)

1. Build TTR and Fixture at `8053ed1b` in `TTR/.local-work/artparity595` (standing build approval).
2. Check the coordinator is idle and the Simulator `9026ECA9` is clear; run the system-alert check.
3. For each of the 12 screens: terminate Fixture, launch with the flags, run the driver. Budget: about 3 min per screen, 250 MB total.
4. Ingest: copy each run into `dataset/tvos_captures/artparity595/programme/<screen>/`, hash-check, and build sidecars from the observations.
5. Release: disconnect, keep the Simulator booted, restore Fixture without flags.
Expected evidence: 36 PNG + observation sets with `verified_reopened` summaries. Failed screens stay recorded; no blind retry.

## Experiments (fixed before registration)

Common: initialization fixed per model, equal epochs and seed per pair, T89 for the detector (43,200 s guard), the existing FocusRing training path for focus.
Evaluation: the 8 baseline frames, the 12 holdout frames (C editions, Matchday), VisualParityAudit's 19 real positives with their negative and retention panels, and NewsTV development frames.

| ID | Question | Control | Treatment |
|---|---|---|---|
| E1 | Do native artwork screens improve the role detector on real apps? | PILLS560 R5 rows | R5 rows + Programme train frames |
| E2 | Do native focus crops fix FocusRing's unfocused-artwork errors? | FDR-010 data | + Programme focus positives and unfocused/decoration/plain negatives |
| E3 | Does artwork variety matter beyond geometry? | E2 with edition A only | E2 with A + B (same geometry) |
| E4 | Which label for partly visible artwork? | whole-control boxes | visible-artwork boxes (Mosaic, after a later capture) |
| E5 | Do paired focus swaps add beyond single frames? | E2 | E2 + the same screen with focus moved (paired) |

Outcomes:
- Supported (E2, E3, E5): correct selections on the 12 holdout frames rise; unfocused-artwork and decoration false positives fall; the 19 real positives do not lose any of the 3 current passes; negative and retention panels lose ≤ 2 points.
- Supported (E1): NewsTV development cards, pills and focus coverage do not fall; role AP50 on tvos558 without tab bars ≥ R5 − 0.01.
- Contradicted: holdout correct selections do not rise, or real-positive passes fall.
- Inconclusive: any other result. Stop rule: if only Fixture frames improve and real positives do not, stop expansion (VisualParityAudit).
Conditional follow-up: if E2 gains holdout and real positives but loses retention, register a preservation arm with the same budget.

## Capability requests to TTR (sent with the intake receipt)

1. Visual-replay export of the executed detector input and each proposal crop with hashes (receipts list `crop_identity` as unavailable).
2. Batch capture with 1 machine-readable sidecar per frame: all focusable frames in pixels, focused and selected IDs, visible fraction, clipping, role hint.
3. Seeded variation: artwork family, detail level, palette, layout spans, focus target, selection state, scroll offset.
4. Hard-negative fields: decorative/non-actionable, selected-not-focused, text focus, sibling fragment, visible fraction.
5. Asset lineage per tile; confirmation that reserved holdout families never appear in training deliveries.
6. Later: motion and transition sequences with timestamps.

## Amendment — 2026-11-07 18:50: label completeness

The R5 detector finds at least 3 text items per Programme frame outside the 4 labeled elements (a title near y = 74 and footer text near y = 945).
The Programme sidecars are therefore incomplete full-screen labels. Rule: complete screen labels are required for detector training and complete evaluation,
not for registered-control crops (AGENTS.md, 2026-10-25).
- E1 (detector) waits for complete labels: TTR per-frame sidecars (capability request 2) or a labeled review. No detector training on these frames now.
- E2 (FocusRing) proceeds with registered-control crops: focused control = positive; unfocused controls, illustration and a plain patch = negatives.
  It runs as an extra HARDNEG596 arm (`hardneg-programme`) with the same exposure, initialization and seed, using train editions only (A, B; no Matchday).
- Programme test frames (C editions, Matchday Replay) score every HARDNEG596 fit offline after training.
