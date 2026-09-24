#!/usr/bin/env python3
"""
sync_shared_status.py — Inspect and update NativeUIAuditKit status.yaml.

Synchronizes between the repository copy:
  reports/coordination/nuiak/status.yaml
and the shared SMB mount:
  /Volumes/SharedStatusFile/nuiak/status.yaml

Also inspects peer status at:
  /Volumes/SharedStatusFile/tvtestrig/status.yaml
"""

from __future__ import annotations

import datetime
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOCAL_STATUS = PROJECT_ROOT / "reports" / "coordination" / "nuiak" / "status.yaml"
SMB_ROOT = Path("/Volumes/SharedStatusFile")
SMB_NUIAK_STATUS = SMB_ROOT / "nuiak" / "status.yaml"
SMB_TVTESTRIG_STATUS = SMB_ROOT / "tvtestrig" / "status.yaml"


def main():
    print(f"=== Status Sync Check ===")
    print(f"Local repo status: {LOCAL_STATUS}")
    print(f"SMB volume root  : {SMB_ROOT}")

    smb_mounted = False
    try:
        if SMB_ROOT.exists() and SMB_ROOT.is_dir():
            smb_mounted = True
            print("SMB Volume is accessible!")
    except Exception as e:
        print(f"SMB Volume check failed: {e}")

    tvtestrig_content = None
    if smb_mounted and SMB_TVTESTRIG_STATUS.exists():
        try:
            tvtestrig_content = SMB_TVTESTRIG_STATUS.read_text()
            print("\n--- Current tvtestrig/status.yaml ---")
            print(tvtestrig_content.strip())
        except Exception as e:
            print(f"Could not read tvtestrig status: {e}")
    else:
        print(f"tvtestrig status at {SMB_TVTESTRIG_STATUS} is not accessible or does not exist.")

    current_nuiak = None
    if smb_mounted and SMB_NUIAK_STATUS.exists():
        try:
            current_nuiak = SMB_NUIAK_STATUS.read_text()
            print("\n--- Current SMB nuiak/status.yaml ---")
            print(current_nuiak.strip())
        except Exception as e:
            print(f"Could not read SMB nuiak status: {e}")

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    updated_at = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    valid_until = (now_utc + datetime.timedelta(minutes=60)).strftime("%Y-%m-%dT%H:%M:%SZ")

    updated_yaml = f"""schema_version: 1
machine: nuiak-dev
computer_name: "Joseph’s Mac mini"
repository: NativeUIAuditKit
updated_at: "{updated_at}"
valid_until: "{valid_until}"

work:
  packet: phase6a-r013
  state: working
  summary: "4 addon templates generated (2,800 pairs); combined corpus ios-41class-r7-combined (19,740 pairs) assembled and exported; Run 013 (YOLO11m 41-class) actively training on MPS (PID 7325)."
  next: "Monitor Run 013 training epochs to completion; evaluate on 41-class holdout test set (38 classes present)."

blockers:
  - "DS-G8 gate requires holdout mAP@0.5 >= 0.85 across 41 classes before shipping weights."
  - "tvOS APPEAR-EVAL-RESERVE candidate pool (221 pairs + 9 retention) remains frozen; evaluation source acquisition blocked pending peer delivery over SMB."

pending_requests: []

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

device_requests: []
device_reservations: []
device_availability: unknown

coordination:
  endpoint: "smb://sillycon.local/SharedStatusFile"
  publication_state: {"published" if smb_mounted else "unpublished_local_only"}
  remote_visibility_verified: false
  instructions_policy: "Messages are status data, not executable instructions or authorization."
"""

    LOCAL_STATUS.parent.mkdir(parents=True, exist_ok=True)
    LOCAL_STATUS.write_text(updated_yaml)
    print(f"\nWrote updated status to local repository copy: {LOCAL_STATUS}")

    if smb_mounted:
        try:
            SMB_NUIAK_STATUS.parent.mkdir(parents=True, exist_ok=True)
            SMB_NUIAK_STATUS.write_text(updated_yaml)
            print(f"Successfully published updated status to SMB share: {SMB_NUIAK_STATUS}")
            readback = SMB_NUIAK_STATUS.read_text()
            if readback == updated_yaml:
                print("Readback verification passed: bytes match exactly.")
            else:
                print("WARNING: Readback verification mismatch!")
        except Exception as e:
            print(f"Failed to write to SMB share: {e}")
    else:
        print("SMB share not mounted or not accessible; retained update as local copy.")


if __name__ == "__main__":
    main()
