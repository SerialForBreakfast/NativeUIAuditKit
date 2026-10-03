# Real-screen production baseline

Development evidence, not an independent benchmark. Unmatched predictions remain unreviewed, not false positives.

| Reviewed role | Controls | Located IoU .50 | Located IoU .75 | Exact role among located |
|---|---:|---:|---:|---:|
| collectionItem | 301 | 206 | 191 | 167/206 |
| focus:otherFocusable | 20 | 13 | 13 | 0/13 |
| focus:tabItem | 24 | 13 | 0 | 0/13 |
| listRow | 224 | 109 | 107 | 95/109 |
| primaryButton | 13 | 5 | 5 | 3/5 |
| searchField | 1 | 0 | 0 | 0/0 |

Complete-frame focus outcomes: `{'correct': 4, 'focused_control_not_localized': 3}`.

Focus-only roles have no equivalent detector class; exact role comparison is not a new taxonomy mapping.

The bundled production focus model is not FDR021 or the paired-input FDR036.
