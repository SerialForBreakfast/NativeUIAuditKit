# RESEARCH338 — research queue replay qualification

Date: 2026-10-11 (UTC).
Design: [ADR-0026](ADR-0026-Queued-Research-Experiments.md). Plan: [RESEARCH338](Plans/RESEARCH338.md).

## Decision

The research queue reproduces 3 finished FOCUS audits exactly. It is qualified for `diagnostic` jobs on local hardware.
Training, capture, export, and promotion jobs remain refused until their own qualification.

## Delivered

- `scripts/research_queue.py`: `submit`, `run`, `status`, and `summarize`, with the `python-callable` adapter.
- `scripts/test_research_queue.py`: 14 focused tests with synthetic modules.
- 3 frozen replay specs in `Research/ResearchSpecs/RESEARCH338/`.

The tests cover these conditions:

- Spec errors, refused authority classes, unsafe paths, and changed inputs.
- Job identity conflicts, output reuse, lock contention, and timeouts.
- Interrupted attempts, the attempt limit, and skipping of completed jobs.
- Module-closure hashing, replay matches, replay differences, and required reasons for allowed differences.

## Replay results

Each replay ran the recorded scripts unchanged. The adapter redirected their fixed output folders to a new attempt folder.
The recorded FOCUS folders stayed unchanged; their file hashes match the specs after the run.

| Job | Compared files | Result | Replay time | Original time | Imported repository modules |
| --- | --- | --- | ---: | ---: | ---: |
| FOCUS329 boundary audit | registration, audit | All fields match | 160.5 s | 163.4 s | 131 |
| FOCUS330 detector-centered audit and report | audit, report | All fields match | 84.3 s | 85.9 s | 133 |
| FOCUS331 boundary-region audit and report | registration, audit, report | All fields match | 95.4 s | 98.7 s | 134 |

The largest numeric difference in any compared field is 0. Both registration files are byte-identical.
The allowed differences were fixed before the run:

- `seconds` in each audit (wall time).
- `audit.sha256` in each report (it hashes the replayed audit, including its `seconds` field).

The 3 jobs take 340 s together. They use no detector call, training, device, or data-role change.
The environment is Python 3.13.2, NumPy 2.3.5, PyTorch 2.13.0, and Pillow 12.3.0.

## Sensitivity check

A copy of the FOCUS331 replay audit had 1 coverage value changed by 1e-12.
The comparison reports `rows[300].measurements.boundary.coverage` and a maximum difference of about 1e-12.
The copy also reports 2 path differences. The copy sits in a different folder, but its references still point to the original attempt folder.
These 2 path differences belong to the test, not to the queue.

## Findings

- The original records name 1 to 3 script hashes. The audits import 131 to 134 repository modules.
  The queue now records every imported module's hash. [BP-115](BestPractices.md) records this lesson.
- File times show that every imported module predates its original run. With exact output agreement, this supports reproducibility.
  It does not prove that unrecorded module versions were identical at the original time.
- Fixed output folders block reuse. The adapter's output redirection removes that block without editing recorded scripts.

## Limits and next work

The queue currently runs on local hardware. Distributed execution needs a bundle transfer and an executor qualification.
The replays are training-free. A training adapter needs checkpoint resume, epoch budgets, and standing approval first.

Recommended next steps, in order:

1. Add the `training` authority class with standing-approval fields and a resumable epoch checkpoint.
2. Replay 1 short finished training run, for example a 30-epoch FOCUS candidate. Compare its metrics within a declared tolerance.
3. Add a `screen` extractor that records 1 primary metric per job, so `summarize` can rank ideas by effect, interval, and cost.

No training, capture, or model changes occurred.
