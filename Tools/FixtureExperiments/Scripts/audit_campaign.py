#!/usr/bin/env python3
"""Audit a fixture campaign and log friction points (ASD-STE100)."""
import argparse
import json
import math
import os
from pathlib import Path
import struct
import sys
import time

def read_json(path):
    return json.loads(Path(path).read_text())

def write_json(path, data):
    path = Path(path)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, path)

def parse_png_dimensions(path):
    with Path(path).open("rb") as f:
        header = f.read(24)
        if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
            return None, None
        w, h = struct.unpack(">II", header[16:24])
        return w, h

def compute_box_iou(b1, b2):
    # b = [x, y, w, h]
    x1 = max(b1[0], b2[0])
    y1 = max(b1[1], b2[1])
    x2 = min(b1[0] + b1[2], b2[0] + b2[2])
    y2 = min(b1[1] + b1[3], b2[1] + b2[3])
    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    if intersection <= 0:
        return 0.0
    area1 = b1[2] * b1[3]
    area2 = b2[2] * b2[3]
    union = area1 + area2 - intersection
    return intersection / union if union > 0 else 0.0

def audit_campaign(campaign_dir, friction_log_path=None):
    campaign = Path(campaign_dir)
    checkpoint_file = campaign / "checkpoint.json"
    if not checkpoint_file.exists():
        return {"status": "error", "message": "checkpoint.json missing"}

    checkpoint = read_json(checkpoint_file)
    jobs = checkpoint.get("jobs", {})
    
    findings = []
    completed_count = 0
    failed_count = 0
    anomalies = []

    for job_id, row in jobs.items():
        state = row.get("state")
        if state == "complete":
            completed_count += 1
            attempt = row.get("attempts", [])[-1]
            attempt_dir = campaign / attempt
            output_dir = attempt_dir / "output"
            
            # Check annotation
            annotations_files = list(output_dir.glob("*_annotations.json"))
            for annot_path in annotations_files:
                annot = read_json(annot_path)
                nodes = annot.get("nodes", [])
                
                # Check for label bleeding / box overlaps among nodes
                for i in range(len(nodes)):
                    for j in range(i + 1, len(nodes)):
                        n1, n2 = nodes[i], nodes[j]
                        b1 = n1.get("focusedBounds", n1.get("unfocusedBounds", []))
                        b2 = n2.get("focusedBounds", n2.get("unfocusedBounds", []))
                        if len(b1) == 4 and len(b2) == 4:
                            iou = compute_box_iou(b1, b2)
                            if iou > 0.05:
                                anomalies.append({
                                    "kind": "label_bleed",
                                    "job_id": job_id,
                                    "nodes": [n1.get("id"), n2.get("id")],
                                    "iou": round(iou, 4),
                                    "detail": f"Box overlap {round(iou*100, 1)}% exceeds 5% bleed threshold"
                                })

            # Check png dimensions
            for png in output_dir.glob("*.png"):
                w, h = parse_png_dimensions(png)
                if w != 1920 or h != 1080:
                    anomalies.append({
                        "kind": "invalid_dimensions",
                        "job_id": job_id,
                        "file": png.name,
                        "dimensions": f"{w}x{h}",
                        "detail": "Expected 1920x1080 canvas"
                    })
        elif state in ("failed", "interrupted"):
            failed_count += 1
            anomalies.append({
                "kind": "job_execution_failure",
                "job_id": job_id,
                "state": state,
                "error": row.get("error", "unknown")
            })

    summary = {
        "campaign": campaign.name,
        "completed": completed_count,
        "failed": failed_count,
        "total_jobs": len(jobs),
        "anomalies_count": len(anomalies),
        "anomalies": anomalies,
        "audited_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

    # Save summary into campaign directory
    write_json(campaign / "audit_summary.json", summary)

    # Append to friction log if provided
    if friction_log_path and anomalies:
        log_path = Path(friction_log_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        current_log = []
        if log_path.exists():
            try:
                current_log = read_json(log_path)
            except Exception:
                current_log = []
        current_log.append({
            "campaign": campaign.name,
            "timestamp": summary["audited_at"],
            "anomalies": anomalies
        })
        write_json(log_path, current_log)

    return summary

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Audit fixture campaign and log friction points.")
    p.add_argument("campaign", help="Path to campaign directory")
    p.add_argument("--friction-log", default="reports/work/friction_log.json", help="Path to friction log")
    args = p.parse_args()
    res = audit_campaign(args.campaign, args.friction_log)
    print(json.dumps(res, indent=2))
