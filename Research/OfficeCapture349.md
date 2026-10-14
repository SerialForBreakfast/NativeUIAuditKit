# Office capture review — FOCUS349

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

research-host-NUIAK receives 3 sanitized reports from peer-host-TTR.
All names, sizes, and SHA-256 hashes match the transfer offer.
The local originals remain in `reports/work/FOCUS-349/office/`.
The coordinator stores the receipt and request as `nuiak-focus349-office-receipt-01`, cursor 357.
Forwarding and recipient acknowledgment remain separate.

## What the capture establishes

The script checks counts against the case index and the command diagram.
The raw archive now supplies the original pixels and events.
All 121 PNG files pass exact hashes, dimensions, and decode checks. Each image measures 1920 × 1080 pixels.
The archive and 3 supporting files match the sender's sizes and hashes.
The coordinator stores their receipt at cursor 362. Sender cleanup remains unconfirmed.

| Check | Result |
| --- | ---: |
| Saved frame records | 122 |
| Unique image hashes | 121 |
| Commands | 142 |
| Commands with a result frame | 117 |
| Commands without a result frame | 25 |
| Frames marked settled | 7 |
| Result frames without verified settlement | 110 |
| Commands with a fresh before frame | 0 reported |
| Completed command receipts | 141 |
| Failed command receipts | 1 |

Command C126 fails, but frame F113 has a settled role. This does not prove a metadata error.
The screen can settle after a failed command. Neither fact proves that focus moves.
Frames F043 and F045 have the same image hash. Keep both sequence records.
Do not infer identical application state from identical pixels.

The run includes 56 down, 30 right, 16 select, 15 back, 12 left, 11 up, and 2 home commands.
These counts show command coverage. They do not show successful navigation or focus coverage.
HCF, reviewed focus labels, and control bounds remain unavailable.
The queue scores selected visual pairs with 3 fixed models. Those scores select review cases; they do not establish accuracy.

## Original event checks

All 117 reported links use command generation 2 and frame generation 1.
The strict existing audit therefore qualifies no command-linked transition.
This does not prove stale capture. Current TTR source uses separate counters for control connections and video connections.
peer-host-TTR needs to confirm the counter meanings for the capture build.
Do not remove the check before the contract identifies comparable counters.

Recorded result delays range from 1.76 s to 8.28 s. The median is 2.42 s across 117 reported links.
These delays measure recorded timestamps. They do not establish response latency, verified settlement, or focus movement.
No reported result timestamp follows the next command dispatch.
The raw audit keeps these timing observations separate from qualified transitions.

## Image review

research-host-NUIAK surveys 27 distinct frames through 2 private contact sheets.
The images include clipped Home icons, dense game cards, bright detail pages, text panels, video thumbnails, profile choices, and media shelves.
These scenes provide useful variation beyond Fixture placeholders.
The review also finds blank transitions and screensaver content. Neither supplies a focus label by itself.

The existing review tool prepares 8 frames from Home, video, media shelves, and clipped Home grids.
The review package remains private at `reports/work/FOCUS-349/office-review/batch.json`.
No human focus annotations are claimed. Private profile details stay out of published reports.
The entire session stays in one development group, including every derived crop and model score.

## Model disagreements and visual findings

Both queued comparisons finish. All 3 models score the same 21 visual pairs from 1 session.
The models disagree on 4 pairs. FOCUS348 gamma and FOCUS349 make identical categorical decisions on all 21 pairs.
Their probabilities differ, but this does not establish an improvement.

The assistant inspects all 4 disagreement pairs at full image size:

| Case | Visible interaction | FOCUS329 | FOCUS348 gamma | FOCUS349 |
| --- | --- | ---: | ---: | ---: |
| F005–F006 | Home growth moves from Music to Photos | 0.378 | 0.041 | 0.037 |
| F121–F122 | Outlined Home focus moves to the right icon | 0.887 | 0.177 | 0.183 |
| F094–F095 | Small navigation tab changes to a large highlighted content row | 0.803 | 0.088 | 0.100 |
| F001–F002 | Screensaver changes to Home with visible focus | 0.694 | 0.012 | 0.013 |

Values are predicted change probabilities, not confidence in reviewed labels.
The first 3 pairs show visible focus movement. These observations are assistant review notes, not native telemetry or human-confirmed labels.
The fourth pair needs an explicit arrival category. Do not silently classify absent-to-present focus as ordinary movement.
No accuracy total or training admission follows this review.

The review tool now supports an explicit `--include-standalone` diagnostic option.
It prepares all 8 priority images in `reports/work/FOCUS-349/office-priority-review-r3/batch.json`.
The first 2 attempts reject standalone frames. Their failed outputs remain preserved.
Tests confirm that the new option preserves source roles and unknown labels. It still rejects transition frames.
Default behavior stays unchanged. The option grants no command association, settlement claim, or training eligibility.
The earlier diversity review remains unchanged.
Prioritize adjacent growth, edge movement, mixed control sizes, and focus arrival in the next campaign.
Keep the reviewed Office images out of that campaign's training membership.

## Reusable analysis

Use the existing recording audit for the sanitized handoff:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-yolo/bin/python \
  scripts/human_recording_audit.py \
  reports/work/FOCUS-349/office/offer.json \
  reports/work/FOCUS-349/office/new-audit.json --sanitized-summary
```

Select a new output filename. The script preserves previous reports.
It checks exact file hashes before parsing. It does not execute the diagram.
It returns linked command cases, duplicate image groups, missing evidence, and a bounded first review list.
It leaves focus labels unknown. It does not score a model or admit training data.

Use `recording_intake349.py` to verify and extract this offered archive into a new directory.
The script rejects unsafe archive paths, changed hashes, oversized output, and incorrect image dimensions.
It calls the existing recording audit without `--sanitized-summary`.
That mode checks frame timing, command timing, connection changes, and associations.
Use `human_recording_review.py` for reviewed image subsets and the existing annotation editor.
Do not make a second annotation or capture system.

For another approved recording, use its verified offer and a new output directory:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-yolo/bin/python \
  scripts/recording_intake349.py OFFER_JSON NEW_OUTPUT_DIRECTORY
```

Keep the original archive beside its local offer. Do not rerun extraction over an existing directory.
Use the existing queue to score fixed visual pairs. Do not call a model from the intake script.
Combine completed score reports with `report_office349.py OUTPUT_JSON REPORT_JSON [REPORT_JSON ...]`.
The report checks completed attempts, pinned inputs, model identity, membership, probabilities, and duplicate pairs.
It ranks disagreement cases before agreement audits. It never calculates accuracy without labels.

## First useful image review

- Review sensitive content before transfer. Preserve unmodified image hashes for each approved image.
- Inspect F113 and every reported settled frame first.
- Add examples for command types missing from that group.
- Review focus identity and body bounds separately from effect bounds.
- Mark movement, unchanged focus, scrolling, content changes, and unknown cases separately.
- Keep ordinary, HCF, and unknown settings separate. Do not guess HCF from appearance.
- Keep the complete session and related images together in development.

The audit proposes up to 12 cases by metadata. This selection does not establish visual diversity.
The reviewed images determine actual interactions, clipping, artwork, and control sizes.
Do not construct command pairs from neighboring frames without timestamp and association checks.

Missing before frames do not make this capture useless.
Reviewed single frames can test control detection and focus selection.
Humans can also label visual changes between selected images without claiming which command caused the change.
The script proposes those visual pairs separately. It marks their command association false and their focus labels unknown.
Multiple commands can occur between these images. Do not use these pairs to measure command response time.

## Experiments after image review

1. Score reviewed single frames with the existing tvOS detector. Measure missing controls and incorrect bounds.
2. Review focus crops through the existing production cropper. Report wrong selections, abstentions, and missing proposals separately.
3. Score valid before/after pairs with the fixed transition model. Keep missing or ambiguous transitions out of accuracy denominators.
4. Compare command pace with result availability. Original timing data must support any claim about delay or dropped capture.
5. Reproduce specific failures in Fixture. Keep this Office session outside the new training examples.

FOCUS329 remains the transition baseline. FOCUS348 and FOCUS349 remain experiments, not TTR runtime replacements.
The existing model catalog supplies the separate tvOS element detector. Its release status remains review-only.
No physical device operation or new capture occurs in this work.
