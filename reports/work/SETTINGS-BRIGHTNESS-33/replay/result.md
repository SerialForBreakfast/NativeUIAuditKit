# Settings brightness comparison

Retained development sequence; generated cases separately labeled. No threshold tuning.

| Method | Correct | Wrong | Abstained | Scorable |
| --- | --- | --- | --- | --- |
| existing | 33 | 0 | 15 | 48 |
| sign | 4 | 41 | 3 | 48 |
| guardedMean | 33 | 0 | 15 | 48 |

Generated exact matches out of14: {'existing': 12, 'sign': 9, 'guardedMean': 12}

| Generated case | Expected | Existing | Sign | Guarded mean |
| --- | --- | --- | --- | --- |
| stability-identical | unchanged | unchanged | unchanged | unchanged |
| stability-small_noise | unchanged | unchanged | arrival | unchanged |
| stability-scroll_only | unchanged | unchanged | unchanged | unchanged |
| stability-highlight | arrival | arrival | arrival | arrival |
| stability-dim | departure | departure | departure | departure |
| stability-scroll_highlight | arrival | arrival | arrival | arrival |
| stability-content_change | unknown | unknown | arrival | unknown |
| stability-illumination | unknown | unknown | unknown | unknown |
| stability-duplicate | unavailable | unavailable | unavailable | unavailable |
| context-neighbor_only | unchanged | unknown | arrival | unknown |
| context-focus_outline | unknown | unknown | arrival | unknown |
| context-content_only | unknown | unavailable | unavailable | unavailable |
| context-highlight | arrival | arrival | arrival | arrival |
| context-scroll | unchanged | unchanged | unchanged | unchanged |
