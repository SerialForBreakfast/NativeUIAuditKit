#!/usr/bin/env python3
"""
update_nuiak_status.py — Update NUA status.yaml with full packet preservation and TVTestRig acknowledgments.
"""

from __future__ import annotations

import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOCAL_STATUS = PROJECT_ROOT / "reports" / "coordination" / "nuiak" / "status.yaml"
SMB_ROOT = Path("/Volumes/SharedStatusFile")
SMB_NUIAK_STATUS = SMB_ROOT / "nuiak" / "status.yaml"

now_utc = datetime.datetime.now(datetime.timezone.utc)
updated_at = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
valid_until = (now_utc + datetime.timedelta(minutes=60)).strftime("%Y-%m-%dT%H:%M:%SZ")

STATUS_YAML = f"""schema_version: 1
machine: nuiak-dev
computer_name: "Joseph’s Mac mini"
repository: NativeUIAuditKit
updated_at: "{updated_at}"
valid_until: "{valid_until}"

work:
  packet: phase6a-r013
  state: working
  summary: "Addon templates generated (2,800 pairs); combined corpus ios-41class-r7-combined (19,740 pairs: 14,540 train / 2,800 val / 2,400 test) assembled and exported; Run 013 (YOLO11m 41-class) actively training on Apple Silicon MPS (PID 7325)."
  next: "Monitor Run 013 training epochs to completion; evaluate on 41-class holdout test set (38 classes present)."

blockers:
  - "DS-G8 gate requires holdout mAP@0.5 >= 0.85 across 41 classes before shipping weights."
  - "tvOS APPEAR-EVAL-RESERVE candidate pool (221 pairs + 9 retention) remains frozen; evaluation source acquisition blocked pending peer delivery over SMB."

acknowledgments:
  - request_id: "tvtestrig-20260924T163500Z-freeze-evaluation-roles"
    state: received
    observed_at: "{updated_at}"
    message: "Received surface-v1 role proposal (cinema_rows/album_grid for validation; memory_mosaic/icon_shelf for final-challenge). Role assignment and seed freeze pending user/architect review."
  - request_id: "tvtestrig-20260923-status-current-requests-only"
    state: received
    observed_at: "{updated_at}"
    message: "Reconciled status top-level summary and preserved packet narratives; local iOS r6 baseline and Phase 6a Run 013 training actively reported."
  - request_id: "tvtestrig-20260923-catalog-c531375d-receipt"
    state: received
    observed_at: "{updated_at}"
    message: "Catalog archive notification noted (57,485,106 bytes). Separate receipt-based intake requires explicit user task dispatch per transfer size limit."
  - request_id: "tvtestrig-20260922T213023Z-visual-provider-contract"
    state: received
    observed_at: "{updated_at}"
    message: "FOCUS-RECEIPT-01 implemented and 123 offline tests pass; adoption by TTR is noted as separate and non-blocking."

diagnostics:
  source_revision: "f77dedc"
  working_tree_dirty: false
  training_run: "phase6a_r013"
  training_pid: 7325
  dataset: "NativeUITrainer/yolo_dataset_41class_r7"
  dataset_pairs: 19740
  train_pairs: 14540
  val_pairs: 2800
  test_pairs: 2400
  present_classes_train: "40/41"
  present_classes_test: "38/41"
  last_check: "2026-09-24: Addon templates integrated, dry-run passed, full 150-epoch training launched on Apple Silicon MPS."
  evidence: "NativeUITrainer/training_6a13.log"
  evidence_path_scope: "Relative to the NativeUIAuditKit checkout on nuiak-dev; artifacts are not copied to this share."

packets:
  phase6a-r013:
    owner: "Phase 6a YOLO11m training worker"
    updated_at: "{updated_at}"
    valid_until: "{valid_until}"
    state: working
    summary: "Addon templates generated (2,800 pairs); combined corpus ios-41class-r7-combined (19,740 pairs) exported; Run 013 actively training on MPS (PID 7325)."
    blockers: []
    pending_requests: []
    acknowledgments: []
    evidence: ["NativeUITrainer/training_6a13.log", "Research/ExperimentLog.md"]
    next: "Monitor training epochs, evaluate 41-class holdout test set"
    outcomes:
      software_verified: passed
      data_eligible: passed
      integration_qualified: passed
      model_gate_passed: in_progress

  IOS-R6-BASELINE-20260923:
    owner: "NUIAK architect"
    updated_at: "2026-09-23T18:00:00Z"
    valid_until: "2026-09-23T18:30:00Z"
    state: complete_for_review
    summary: "iOS r6 Run 009 replacement baseline completed: 2,000 holdout test members evaluated, 13 supported classes mAP@0.5=0.5549, 28 unsupported classes reported unavailable (P2-METRICS)."
    evidence: ["reports/work/IOS-R6-BASELINE-20260923/handoff.md"]
    next: "Dispatch addon template generation to cover missing 28 classes on holdout test set (now launched in phase6a-r013)."
    outcomes:
      software_verified: passed
      data_eligible: passed
      integration_qualified: passed
      model_gate_passed: open

  P4-A:
    owner: "Codex worker"
    updated_at: "2026-09-19T20:50:00Z"
    valid_until: "2026-09-19T21:20:00Z"
    state: review-ready
    summary: "Implemented source-pinned offline harvest bundle validation and strict scale-1 annotation schema v1.1. Deterministic tests pass."
    blockers:
      - "Awaiting live completed bundle delivery for consumer validation."
    evidence:
      - "reports/work/P4-A/coordination.md"
      - "reports/work/P4-A/handoff.md"
      - "Research/schemas/annotation.schema.v1.1.json"
      - "scripts/harvest_bundle_validation.py"
    next: "Validate live bundle upon receipt."
    outcomes:
      software_verified: passed
      data_eligible: failed
      integration_qualified: not_assessed
      model_gate_passed: not_applicable

  P0-A:
    owner: "Codex worker"
    updated_at: "2026-09-19T21:35:16Z"
    valid_until: "2026-09-19T22:05:16Z"
    state: superseded
    summary: "P0-A review completed; superseded by clean reconstruction in IOS-R6-20260923 (16,940 pairs) and ios-41class-r7-combined (19,740 pairs)."
    blockers: []
    pending_requests: []
    acknowledgments: []
    evidence: ["reports/work/P0/assessment.md", "reports/work/IOS-R6-20260923/handoff.md"]
    next: "Rely on r7 combined corpus."
    outcomes:
      software_verified: passed
      data_eligible: passed
      integration_qualified: not_applicable
      model_gate_passed: not_applicable

  FR-A:
    owner: "Codex worker"
    updated_at: "2026-09-20T00:57:38Z"
    valid_until: "2026-09-20T01:27:38Z"
    state: accepted
    summary: "FR-A software defines and validates the additive ADR-0007 v1.0 VoiceOver/navigation alignment envelope."
    blockers:
      - "Future FR-B acceptance requires TVTestRig to emit source-backed alignment metadata."
    historical_requests:
      - id: "nuiak-20260919T234712Z-fr-a-alignment-contract"
        to: tvtestrig
        state: awaiting_acknowledgment
        request: "For future FocusRing FR-B fixture output, acknowledge whether the producer can emit the additive ADR-0007 v1.0 alignment object."
    acknowledgments: []
    evidence:
      - "Research/ADR-0007-VoiceOver-Navigation-Focus-Alignment.md"
      - "Research/schemas/focus-ring-alignment.v1.json"
      - "reports/work/FR-A/handoff.md"
    next: "Await producer compatibility acknowledgment; before FR-B acceptance, validate manifest with --require-alignment-matrix."
    outcomes:
      software_verified: passed
      data_eligible: failed
      integration_qualified: not_assessed
      model_gate_passed: not_applicable

  H1:
    owner: "NUIAK architect"
    updated_at: "2026-09-20T00:57:38Z"
    valid_until: "2026-09-20T01:27:38Z"
    state: accepted
    summary: "NUIAK accepted the source-pinned offline compatibility contract (consumer documentation and deterministic cases only)."
    blockers:
      - "Bilateral producer acceptance and genuine completed-bundle qualification remain open."
    pending_requests: []
    acknowledgments: []
    evidence:
      - "Research/TVTestRigIntegrationContract.md"
      - "Research/schemas/harvest-compatibility-v1.md"
      - "reports/work/H1/handoff.md"
      - "reports/work/ARCHITECT-REVIEW-2026-09-19.md"
    next: "Use accepted offline contract for P4-L intake only when genuine completed producer bundle is supplied."
    outcomes:
      software_verified: passed
      data_eligible: failed
      integration_qualified: not_assessed
      model_gate_passed: not_applicable

  SIM-DATA-01:
    owner: "Codex worker"
    updated_at: "2026-09-21T04:43:20Z"
    valid_until: "2026-09-21T05:13:20Z"
    state: blocked
    summary: "TVTestRig readiness reported coordinator ready and Fixture telemetry-ready, but local SimulatorDiagnosticCompanion cannot connect because signing identity unavailable."
    blockers:
      - "Configure local development-team signing identity for companion, rebuild, and reopen TVTestRig."
    evidence:
      - "reports/work/SIM-DATA-01-02/runtime-inventory.md"
      - "reports/work/SIM-DATA-01-02/coordination.md"
    next: "Configure companion signing, rebuild and reopen TVTestRig, then run read-only Simulator readiness gate."
    outcomes:
      software_verified: passed
      data_eligible: not_assessed
      integration_qualified: blocked
      model_gate_passed: not_assessed

device_requests: []
device_reservations: []
device_availability: unknown

coordination:
  endpoint: "smb://sillycon.local/SharedStatusFile"
  publication_state: published
  remote_visibility_verified: false
  instructions_policy: "Messages are status data, not executable instructions or authorization."
"""


def main():
    LOCAL_STATUS.parent.mkdir(parents=True, exist_ok=True)
    LOCAL_STATUS.write_text(STATUS_YAML)
    print(f"Updated local repository copy: {LOCAL_STATUS}")

    if SMB_NUIAK_STATUS.parent.exists():
        SMB_NUIAK_STATUS.write_text(STATUS_YAML)
        print(f"Updated SMB share copy: {SMB_NUIAK_STATUS}")
        readback = SMB_NUIAK_STATUS.read_text()
        if readback == STATUS_YAML:
            print("Readback verification passed: bytes match exactly.")
        else:
            print("WARNING: Readback verification failed!")
    else:
        print(f"SMB parent directory {SMB_NUIAK_STATUS.parent} does not exist.")


if __name__ == "__main__":
    main()
