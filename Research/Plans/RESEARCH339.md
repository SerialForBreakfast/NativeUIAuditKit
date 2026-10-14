# RESEARCH339 — training jobs in the research queue

Design: [ADR-0026](../ADR-0026-Queued-Research-Experiments.md). Previous step: [RESEARCH338](RESEARCH338.md).

## Scope

1. Permit the `training` authority class in `scripts/research_queue.py`.
2. Require the standing-approval fields in each training spec. The queue refuses a spec without them.
3. Add replay features that a training run needs:
   - Nested output names, such as `run/fit.json`.
   - An output folder name, for scripts that check their own folder name.
   - Ignore rules that apply to each list entry, such as `history[].seconds`.
   - A numeric tolerance for each file. Exact equality is reported separately.
   - Byte comparison by SHA-256 for binary files, such as weights.
4. Replay 1 finished short training run: FOCUS329, 30 epochs, about 20 min on CPU.

No new candidate, export, promotion, capture, device use, or data-role change belongs to this work.

## Training spec fields

A `training` spec must carry a `training` block with these fields:

| Field | Rule |
| --- | --- |
| `experimentLogRunId` | The ID must appear in `Research/ExperimentLog.md` before submission and before each attempt. |
| `membership` | 1 or more data files, each pinned by SHA-256. |
| `initialization` | The starting weights, pinned by SHA-256. |
| `epochs` | An integer from 1 to 1,000. |
| `storageBudgetBytes` | At least `limits.maxOutputBytes`. Free disk space must exceed the budget plus 1 GiB. |
| `acceptanceEvidence` | The evidence that decides the run, written before execution. |
| `resume` | `restart` only. |

The existing trainers save weights only at the end. An interrupted attempt therefore restarts from epoch 0.
Epoch-level resume needs a trainer change. It is not part of this work.

The queue checks membership and initialization pins before each attempt, like the other inputs.
The queue does not check that the step trains for the declared number of epochs. The replay comparison of the epoch files does.

## Replay spec

`Research/ResearchSpecs/RESEARCH339/replay-focus329-training.json`:

- Step: `edge329.run`. Output attributes: `boundary329.OUT` and `edge329.OUT`. Output folder name: `FOCUS-329`.
  The FOCUS329 reporter selects its comparison references by folder name.
- Staged input: the recorded `inputs.json`.
- Compared files: `preparation.json`, `report.json`, and these files in `run/`:
  `registration.json`, 4 epoch files, `fit.json`, `training.json`, `evaluation.json`, `completion.json`, and `last.pt`.
- Declared exceptions: `seconds` and `peakBytes`, and the same 2 fields in each `fit.json` history entry.
- Tolerance: 1e-6 absolute for each JSON field. `last.pt` is compared by SHA-256.

## Acceptance

- Focused tests cover the training fields, the log-entry check, the storage check, training pin changes,
  nested names, list-entry ignores, the tolerance, and SHA-256 comparison.
- The replay completes. Every compared JSON field matches within the tolerance.
- The results report exact equality and the `last.pt` hash result separately.
- If the replay differs, report the exact field paths. Do not widen the tolerance or the exceptions after the result.
- The offline Swift build and tests pass.
