# FOCUS319: authored movement and artwork changes

Owner: Maximum-mini-NUIAK. Generation, training, model evaluation, and software verification finish.

## Result and decision

Reject this candidate as a replacement. The authored examples teach useful behavior, but the combined model loses previous successes.

| Measure | DTM085 | FOCUS313 control | FOCUS319 |
| --- | ---: | ---: | ---: |
| Native correct / 640 | 589 | 598 | 581 |
| Native training correct / 548 | 505 | 514 | 491 |
| Inspected development correct / 40 | 33 | 33 | 38 |
| Inspected reserved correct / 52 | 51 | 51 | 52 |
| Replay correct / 668 | 667 | 668 | 646 |
| Reverse native correct / 640 | 582 | 602 | 579 |
| Lighting correct / 226 | 226 | 226 | 226 |
| Left false changes / 226 | 81 | 82 | 53 |
| Center false changes / 226 | 121 | 99 | 136 |
| Tiny changes correct / 4 | 0 | 0 | 0 |
| Placeholder movements correct / 8 | 2 | 2 | 8 |

The candidate gains 16 native decisions and loses 33 against the matched control.
All 33 losses occur in 2 existing training families. Of these losses, 31 become abstentions and 2 become missed changes.
The candidate also loses 22 replay successes against the control. It fails 8 of 24 strength/order regression checks against DTM085.
The separate tiny reverse checks remain 0/4. All 8 identical tiny comparisons remain correct.
These results do not establish independent real-app accuracy. Training and inspected groups remain identified separately.

### What the new examples teach

On authored training pairs, movement correctness rises from 40/80 to 74/80. The other 6 movement decisions abstain.
Artwork-only correctness rises from 8/80 to 63/80. False changes fall from 72 to 14, with 3 abstentions.
Both models correctly classify all 80 identical pairs.
Previously inspected placeholder movements improve from 2/8 to 8/8. Arrival/departure and identical checks improve from 10/16 to 14/16.
This shows limited transfer beyond the training artwork. Shared layouts prevent an unseen-layout claim.

The tiny-case correction changes from negative values near -2 to positive values between 4.97 and 7.55.
The frozen classifier still outweighs that correction. Correct changed decisions require additions between 11.67 and 15.72.
This is a useful signal change, not a successful focus decision. Do not change thresholds to hide the misses.

The smallest authored controls measure 4.6 and 5.6 pixels after preprocessing. The tiny native controls measure 2.93 pixels.
The authored corpus therefore does not close the measured size gap. Its poster and grid controls measure 32 and 26 pixels.

### Next bounded comparison

First, separate the effect of movement examples from artwork-only examples using the current matched corpus.
Measure which training gradients conflict with the 2 affected native families before another fit.
Then test 1 justified loss change with the same update budget, original views, and fixed native checks.
Keep configurable control size and effect strength in the existing FOCUS314 request. Do not request another large corpus yet.

## Data and scope

The existing Maximum-mini-TTR renderer produces 80 renders and 240 unique ordered pairs in 84.10 s.
The corpus contains 80 focus movements, 80 artwork-only changes, and 80 identical pairs.
All 160 PNG files pass hash, dimension, and decode checks. Matching reference images confirm unchanged base scenes during focus movements.
No identical decoded pair has conflicting labels. Reversed pairs remain related examples, not independent trials.

The corpus uses 10 previously reviewed training assets from 5 ARTWORK204 families. No reserved artwork changes role.
Each scene uses 2 artworks across posters, thumbnails, avatars, and backgrounds. This limits realism but controls the appearance comparison.
The image review checks both focus states across all 4 layouts. The authored focus change is visible in these examples.
Grid growth overlaps the subtitle. The corpus can test change classification, but it cannot establish native layout fidelity.
No authored box becomes a native measurement or a training target for localization.

The repeat test reproduces exact focused and unfocused PNG bytes.
An invalid focus ID returns producer exit code 0. The consumer rejects the result with `focus_identity`.
Producer completion alone is insufficient. Preserve this consumer check until the producer reports invalid requests correctly.

## Matched experiment

Use the FOCUS313 2-window architecture and fresh DTM085 initialization. Keep the whole-frame classifier and geometry frozen.
Preserve all 1,820 original views, labels, weights, and original-resolution detail crops exactly.
Add a separate authored loss with weight 0.25. This adds computation without replacing original training examples.
Use 30 epochs, batch 16, seed 42, learning rate 0.0001, and 3,420 optimizer updates.
Use fixed thresholds 0.15 and 0.85. Select the final checkpoint without evaluation-based checkpoint selection.

Each epoch uses 973 authored movement views, 424 artwork-only views, and 423 identical views.
These are repeated exposures to 240 pairs, not 1,820 new examples.
Family exposure ranges from 352 to 397 views per epoch. Do not describe this schedule as perfectly balanced.
The existing original-only FOCUS313 run is the matched control. DTM085 remains a separate reference.
Native training, inspected development, and inspected reserved groups remain separate in reports.
The prior placeholder scenes remain inspected development checks. They do not establish unseen-layout performance.

## Verification and evidence

All 38 focused Python checks pass in 1.34 s. The actual generation command rejects an existing output directory before mutation.
The training loop takes 707.38 s, versus 342.76 s for the original-only control.
Preparation, training, reload checks, and primary evaluation take 936.94 s. Generation takes another 84.10 s.
Sampled training memory remains below 5 GiB. These samples do not measure the exact peak.
The user approves stopping test processes 34178 and 34204. Maximum-mini-NUIAK verifies their identities before stopping them.
The waiting offline build then passes in 0.65 s. The serial run passes 14 XCTest tests and 173 Swift Testing tests.
Swift Testing takes 51.742 s. No service reset occurs. The earlier failure logs remain available.
Logs: `.build/focus319-swift-build.log` and `.build/focus319-swift-test-serial.log`.

Raw evidence stays in ignored storage at `reports/work/FOCUS-319/`.
The plan, corpus, review, training registration, checkpoints, and reports retain hashes.
The corpus manifest SHA-256 is `482bb30a9bf35c759a846c5c4b5ccd8ab2a3c48470822eeb907f2ceed8cb52cf`.
The candidate SHA-256 is `ab3e9e10547e116effa49d9c8949503e361819147ce9e016ec8791c409396a68`.
No source images or models enter Git. No production model changes.

## Coordination

The coordinator stores `nuiak-focus319-result-01` at cursor 148. Forwarding and Sillycon-TTR acknowledgment remain unconfirmed.
The metadata fallback passes exact SMB readback at `nuiak/responses/nuiak-focus319-result-01.json`.
The file has 2,130 bytes and SHA-256 `652234e03975844d431fbc3259681301abbde2a4aaa022cb1bad85a6debef296`.
The update links the existing FOCUS314 request. It does not assign new work or request model installation.
