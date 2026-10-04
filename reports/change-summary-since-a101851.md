# Changes since a101851 — Experiments, Optimizations, Docs

Snapshot: October 3, 2026. Includes tracked working-tree changes and new source/test/
handoff files, not just committed files. This is a summary, not a fresh test execution.

## Native-data intake and admission

- Added source-pinned rich native-table and native-collection compatibility, including
  measured visibility and typed exclusions for offscreen, hidden and clipped controls.
  Qualified 60 retained rich/collection pairs plus 12 legacy cases.
- Added coverage auditing and guarded admission for 24 approved native action pairs,
  expanding training from44 to68 pairs while preserving five exposed Settings pairs.
- Extended proposal preparation to bounded multi-call batches; reused candidate
  encodings and existing crop pipelines. Added membership, approval and parity guards.
- Received layout28 and verified 312 case files/56 images. Semantic intake correctly
  remains blocked on unsupported version16 source; receipt verification is not admission.

## Models and diagnostic results

- DTM020's size-aware ranker retained 88/88 old training endpoints and learned48/48
  added endpoints. Exposed Settings improved 2/10→5/10 endpoints and0/5→2/5 pairs.
- Frozen DTM018 change decisions combined with DTM020 boxes yield65/68 confident
  joint training decisions; Settings remains5/5 change decisions and2/5 joint pairs.
- All five incorrect Settings endpoint occurrences have the correct candidate ranked
  second: four tiny distractors and one enclosing region. Shared frames limit independence.
- Rejected fixed paired-score subtraction: Settings5/10→3/10 endpoints and training
  136/136→52/136. No shortcut size filter was adopted.
- Added and tested change-head adaptation, ordered before/after context, explicit
  higher-resolution input contracts, initialization parity and checkpoint replay.
  DTM021/022/023 confident joint training scores were59/68,63/68 and67/68 respectively.
- DTM023's improved fit failed the same-frame check:35/122 confident false changes
  versus zero for DTM018. Retained the prior references; shipped models are unchanged.
- Resolution and source audits found surviving sparse-change signal, stronger no-op
  differences at higher resolutions, and36 native changed pairs without matched native
  no-change examples. These findings narrow the next experiment, not prove a sole cause.

## Preparation and regression coverage

- Reused one verified PNG decode for dimensions and RGBA identity; preserved full
  73-record reconstruction. Endpoint validation measured11.88s→7.02–7.21s.
- Reused already validated baseline frames within a preparation call, reducing source
  checks9031→4661 and one profiled collection36.75s→24.60s. These are stage/single-run
  measurements, not guaranteed end-to-end throughput.
- Added tests for visibility, coverage, admission, rank/change diagnostics, preparation
  identity and signal analysis. Latest RESOLUTION96 handoff records14 focused Python
  tests and134 offline Swift tests passing; other packets record their own checks.
- Updated research, experiment logs, implementation catalog, roadmap, queue, lessons
  and artifact ignore handling; added concise per-tranche evidence handoffs.

## Next planned work

The [integrated plan](../Research/Plans/FocusTransitionLearning49.md#next-integrated-tranche--focus-reliability)
now defines false-change repair, independent candidate-selection diagnosis, and
evaluation/intake readiness. [Tasks](../Tasks.md) owns current execution state.
Derived-negative training approval, genuine native no-ops, version16 source and an
independent final corpus remain distinct prerequisites. Planning does not start a run.

Evidence: [NATIVE84](work/NATIVE-84/handoff.md), [NATIVE87](work/NATIVE-87/handoff.md),
[NATIVE88](work/NATIVE-88/handoff.md), [NATIVE89](work/NATIVE-89/handoff.md),
[PREP91](work/PREP-91/handoff.md), [CHANGE92](work/CHANGE-92/handoff.md),
[CONTEXT93](work/CONTEXT-93/handoff.md), [SIGNAL95](work/SIGNAL-95/handoff.md),
[RESOLUTION96](work/RESOLUTION-96/handoff.md).
