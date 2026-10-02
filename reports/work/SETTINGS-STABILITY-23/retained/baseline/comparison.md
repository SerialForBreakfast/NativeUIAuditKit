# Recorded Settings signal comparison

Retrospective development diagnostics. Native OCR supports correspondence; human review supplies focus labels.

| Signal | Correct | Wrong | Abstained | Scorable | Coverage |
|---|---:|---:|---:|---:|---:|
| brightness | 4 | 0 | 44 | 48 | 8.0% |
| growth | 0 | 0 | 48 | 48 | 0.0% |
| combined | 4 | 0 | 44 | 48 | 8.0% |

## Action results

| Frames | Titles | Status | Reviewed changes | Combined correct / scored |
|---|---|---|---|---|
| 299→303 | settings → settings | retrospective-diagnostic | {'unchanged': 9, 'departure': 1, 'arrival': 1} | 2 / 11 |
| 310→319 | settings → accessibility | screen-change-excluded | {} | excluded |
| 378→386 | voiceover → voiceover | retrospective-diagnostic | {'unchanged': 9} | 0 / 9 |
| 387→391 | voiceover → voiceover | retrospective-diagnostic | {'unchanged': 9} | 0 / 9 |
| 409→416 | accessibility → accessibility | retrospective-diagnostic | {'unchanged': 7, 'departure': 1, 'arrival': 1} | 2 / 9 |
| 446→456 | settings → apps | screen-change-excluded | {} | excluded |
| 482→488 | apps → apps | retrospective-diagnostic | {'unchanged': 10} | 0 / 10 |

## Interpretation

All arms use identical pixels, before-bounds, tracking, semantic membership and fixed thresholds. Unavailable tracking counts as abstention when semantic truth exists.
Changed screen titles are excluded from same-screen focus-switch scoring. Partial/unknown endpoint completeness prevents whole-screen accuracy claims.
This repeatedly examined recording is development evidence, not an independent benchmark or runtime focus-identity qualification.

## Failures and uncertain controls

| Frames | Row | Expected | Brightness | Growth | Combined | Tracking |
|---|---|---|---|---|---|---|
| 299→303 | general | unchanged | unknown | unavailable | unknown | matched |
| 299→303 | profiles and accounts | unchanged | unknown | unavailable | unknown | matched |
| 299→303 | video and audio | unchanged | unknown | unavailable | unknown | matched |
| 299→303 | screen saver | unchanged | unknown | unavailable | unknown | matched |
| 299→303 | notifications | departure | departure | unavailable | departure | matched |
| 299→303 | airplay and apple home | arrival | arrival | unavailable | arrival | matched |
| 299→303 | remotes and devices | unchanged | unknown | unavailable | unknown | matched |
| 299→303 | accessibility | unchanged | unknown | unavailable | unknown | matched |
| 299→303 | apps | unchanged | unavailable | unavailable | unavailable | ambiguous_texture |
| 299→303 | network | unchanged | unknown | unavailable | unknown | matched |
| 299→303 | system | unchanged | unknown | unavailable | unknown | matched |
| 378→386 | voiceover | unchanged | unknown | unavailable | unknown | matched |
| 378→386 | voiceover help | None | unavailable | unavailable | unavailable | ambiguous_texture |
| 378→386 | navigation style | unchanged | unknown | unavailable | unknown | matched |
| 378→386 | verbosity | unchanged | unknown | unavailable | unknown | matched |
| 378→386 | audio ducking | unchanged | unknown | unavailable | unknown | matched |
| 378→386 | voice | unchanged | unknown | unavailable | unknown | matched |
| 378→386 | pronunciations | unchanged | unknown | unavailable | unknown | matched |
| 378→386 | speech rate | unchanged | unknown | unavailable | unknown | matched |
| 378→386 | use pitch | unchanged | unknown | unavailable | unknown | matched |
| 378→386 | rotor | unchanged | unknown | unavailable | unknown | matched |
| 387→391 | voiceover | unchanged | unknown | unavailable | unknown | matched |
| 387→391 | navigation style | unchanged | unknown | unavailable | unknown | matched |
| 387→391 | verbosity | unchanged | unknown | unavailable | unknown | matched |
| 387→391 | audio ducking | unchanged | unknown | unavailable | unknown | matched |
| 387→391 | voice | unchanged | unknown | unavailable | unknown | matched |
| 387→391 | pronunciations | unchanged | unknown | unavailable | unknown | matched |
| 387→391 | speech rate | unchanged | unknown | unavailable | unknown | matched |
| 387→391 | use pitch | unchanged | unknown | unavailable | unknown | matched |
| 387→391 | rotor | unchanged | unknown | unavailable | unknown | matched |
| 387→391 | darill | None | unavailable | unavailable | unavailable | ambiguous_texture |
| 409→416 | voiceover | unchanged | unknown | unavailable | unknown | matched |
| 409→416 | zoom | unchanged | unknown | unavailable | unknown | matched |
| 409→416 | hover text | unchanged | unknown | unavailable | unknown | matched |
| 409→416 | display | unchanged | unknown | unavailable | unknown | matched |
| 409→416 | motion | departure | departure | unavailable | departure | matched |
| 409→416 | audio descriptions | arrival | arrival | unavailable | arrival | matched |
| 409→416 | switch control | unchanged | unknown | unavailable | unknown | matched |
| 409→416 | tap to navigate | unchanged | unknown | unavailable | unknown | matched |
| 409→416 | mono audio | unchanged | unknown | unavailable | unknown | matched |
| 482→488 | automatically update apps | unchanged | unknown | unavailable | unknown | matched |
| 482→488 | automatically install apps | unchanged | unknown | unavailable | unknown | matched |
| 482→488 | automatically download in app conte on | unchanged | unknown | unavailable | unknown | matched |
| 482→488 | offload unused apps | unchanged | unknown | unavailable | unknown | matched |
| 482→488 | tv | unchanged | unavailable | unavailable | unavailable | low_texture |
| 482→488 | music | unchanged | unknown | unavailable | unknown | matched |
| 482→488 | computers | unchanged | unknown | unavailable | unknown | matched |
| 482→488 | fitness | unchanged | unknown | unavailable | unknown | matched |
| 482→488 | podcasts | unchanged | unknown | unavailable | unknown | matched |
| 482→488 | photos | unchanged | unavailable | unavailable | unavailable | ambiguous_texture |
