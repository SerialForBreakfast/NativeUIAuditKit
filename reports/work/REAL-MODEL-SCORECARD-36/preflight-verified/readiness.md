# Next model experiment readiness

Full-screen diagnostic input prepared: 46 screenshots / 583 controls.
Control height after 640 letterboxing: {'min': 15.068493150684919, 'median': 36.47798742138364, 'max': 241.09589041095887, 'below16': 1}. This measures bodies, not shadow visibility.

## Full-screen experiment prerequisites

- Diagnostic membership is not training admission; acquisition/layout ancestry needs explicit split groups.
- 39/46 frames lack explicit focusable-control completeness; do not treat omissions as unfocused/background.
- Existing tvOS trainer has no wall-time/output-cap enforcement and dry-run actually trains.
- Native26 training uses one artwork-row layout; native wide-row/button coverage intent33 awaits producer mapping.

## iOS retained-prediction diagnosis

Replayed 2,000 withheld screenshots at confidence .25 / IoU .50; no inference or label changes.

| Role | Truth | Any class localized | Correct role | Short side <8px at 640 |
|---|---:|---:|---:|---:|
| imageView | 1900 | 358 | 302 | 0 |
| label | 9165 | 6517 | 6406 | 0 |
| listRow | 700 | 106 | 106 | 0 |
| navigationBar | 800 | 800 | 800 | 0 |
| pageControl | 600 | 0 | 0 | 300 |
| picker | 200 | 200 | 200 | 0 |
| primaryButton | 1366 | 1366 | 1366 | 0 |
| progressView | 200 | 200 | 200 | 200 |
| secondaryButton | 341 | 292 | 0 | 0 |
| secureField | 200 | 200 | 200 | 0 |
| stepperControl | 200 | 200 | 200 | 0 |
| textField | 503 | 503 | 400 | 0 |
| toggle | 1687 | 1670 | 1287 | 0 |

Correction order:

- Retain secondaryButton truth: CardDetail captures an explicit secondary action; do not relabel it cancelAction to match predictions.
- Localize coarse button bodies first; use context/text to distinguish secondary versus cancel. Test on source-family-held-out examples.
- Prioritize listRow/imageView family diversity; synthetic addon success does not establish withheld-family transfer.
- Treat page dots/scroll indicators as resolution/localization errors; test a controlled resolution arm, not a semantic rename.
- Fill independent class coverage before interpreting a full-41-class release gate.
