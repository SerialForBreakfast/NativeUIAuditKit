# SETTINGS-SWIFT-SPIKE-25 — Python/OpenCV versus Swift/Vision

Assigned October2,2026 during roadmap discussion. One bundled spike ending in an
evidence-informed ADR, not separate handoffs for scaffolding and measurements.
Recorded now; implementation and comparison have not run.

## Question

Can a native Swift implementation provide an equally or more reliable supporting
focus-transition signal than the current Python/OpenCV diagnostic, at practical cost?
These are pipelines, not necessarily two trained models. Vision tracking is a candidate
to verify, not assumed equivalent to OpenCV or assumed to supply focus truth.

## Comparison

1. Inspect available native tracking APIs and deployment support. Implement a small
   offline Swift caller in this repository, retaining the production cropper and the
   full-context guarded Settings rule. Keep body-only masking rejected.
2. Separate pixel arithmetic parity from tracking quality: first feed identical crops
   to both rule implementations, then identical before-boxes/screenshots to OpenCV
   and the selected Vision tracking API. Record API configuration and runtime identity.
3. Freeze membership and thresholds before execution. Reuse the existing five same-screen
   reviewed Settings pairs, include the two page-change exclusions, and the generated
   noise/scroll/content/illumination/duplicate/outline counterexamples. Human after-labels
   and after-boxes are scoring evidence only, never tracker inputs. Measure match
   correctness/IoU, lost or ambiguous targets, per-control arrival/departure/unchanged,
   wrong decisions, abstentions, coverage, eligible action outcomes and cold/warm latency.
4. Report the small development set's support explicitly: only two genuine focus moves;
   related frames and synthetic cases do not establish independent generalization.
   Extend to additional reviewed native transitions only when their existing contract
   and data-use requirements pass. Missing data limits conclusions, not local software.
5. Finish focused tests, actual CLI replay, offline Swift build/test and a Markdown ADR.
   The ADR must recommend adopt/continue/reject from results, identify evidence gaps,
   and define the proposed optional advisory result (measurements, uncertainty, source
   and freshness). Leave permissions and actions with TTR; agreement is not a calibrated
   confidence percentage. Producer requests concern source/contract needs, not builds.

## Execution boundary

Local offline development with resident dependencies and retained inputs. Up to100
retained control pairs and24generated cases, three justified comparisons,300seconds
per comparison/1800seconds total experiment execution and512MiB new outputs. No training
or weight downloads. Freeze exact commands/configuration in the spike report before
running. Live TTR integration and production promotion are later explicit decisions.

## Deliverables

Working Swift diagnostic caller; source-bound comparison tables and failure examples;
parity and negative-path tests; one ADR with recommendation and measured rationale;
one concise handoff updating Tasks.md. A negative result completes the spike if the
failure is explained and the integration recommendation follows the evidence.
