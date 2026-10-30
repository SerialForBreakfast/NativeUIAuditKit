# TEMPORAL544 — Native temporal evidence and before-frame removal

Maximum-mini-NUIAK reviews 2 related native pairs from PROFILE542.
The existing runner completes both original comparisons and both new ablation jobs.
All output hashes pass verification. Standard and model weights remain unchanged.

## Measured result

| Condition | Ordered pair, each of 3 models | Duplicated after frame, each of 3 models |
| --- | --- | --- |
| Unchanged focus | Correct stable decision | Correct stable decision |
| Focus movement | Correct changed decision | Missed change |

Removing the before frame loses the movement success for the baseline, seed42, and seed44.
This supports useful temporal information on this specific pair.
It does not establish destination selection, moving-background robustness, or independent application accuracy.
The 2 pairs share one sample group. Three models do not create three independent samples.
The unchanged pair retains its original expectation mismatch. Observed focus determines its label.

The original comparisons take 3.80 s and 1.35 s.
The new comparisons take 3.84 s and 1.33 s.
These are short diagnostics, not an overnight workload.

## Reusable adapter

`scripts/sdk_temporal_ablation.py` reads a short `sdk-temporal-ablation-v1` request.
Supply `id`, `sourceSpec`, `sourceResult`, and `sourceSummary` as pinned inputs.
The source must be a completed SDK508 temporal comparison with intact outputs.
The adapter verifies membership, models, images, observed identity, labels, and retained probability outcomes.
It reuses ordered-pair predictions and scores only duplicated after frames.
It keeps the original thresholds of 0.15 and 0.85.
It refuses unknown temporal identity and inconsistent retained evidence.

Compile with the existing project interpreter:

```sh
PYTHONPATH=scripts .venv-yolo/bin/python -B scripts/sdk_temporal_ablation.py REQUEST.json --output SPEC.json
```

Register and approve the resulting specification through the existing queue interfaces.
Each job permits 800 s, 100 MB, and 1 attempt. The detached runner owns execution.
Two configuration files pass the same compiler and execute through the same adapter.
No existing worker module changes. No runner restart or capture occurs.

Private requests, tests, admission receipts, and review summaries remain under `reports/work/TEMPORAL544/`.
The focused regression suite passes 57 tests.

## Next scientific decision

Keep the before frame for further temporal experiments. Do not train another seed from this result alone.
The next useful comparison needs content motion with unchanged focus and a separate departure example.
Maximum-mini-NUIAK must qualify those native observations and independent groups before admission.
Existing SDK506 and SDK509 results remain reused evidence, not new jobs.
The general pixel-difference comparator and destination selector remain separate adapter tasks.

Offline Swift build and all 177 Swift tests pass in 25 suites.
The game source build and controlled-content process checks also pass.
