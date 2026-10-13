#!/usr/bin/env python3
"""Approve ready jobs into approved-additions.json (ASD-STE100)."""
import fcntl
import json
from pathlib import Path
import research_queue as q

NEW_JOBS = [
    "hcf371r5-70-crop-train",
    "hcf371r5-80-crop-evaluate",
    "hcf371r5-80-detector-evaluate",
    "hcf371r5-81-detector-evaluate",
    "hcf371r5-91-decision",
    "hcf371r5-92-decision",
    "exp-oracle-01-density-threshold",
    "exp-oracle-02-translucent-scrim",
    "exp-rules-01-stroke-contrast",
    "exp-rules-02-elevation-ratio",
    "exp-rules-03-hybrid-gating",
    "exp-cmp-01-four-way-native",
    "exp-cmp-02-dual-profile-loss",
]


def approve():
    approvals_file = q.QUEUE / "approved-additions.json"
    lock_file = q.QUEUE / "approval.lock"

    with lock_file.open("r+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        data = q.load(approvals_file) if approvals_file.exists() else {"version": "research-additions-v1", "jobs": {}}
        jobs_map = data.get("jobs", {})

        added = 0
        for jid in NEW_JOBS:
            spec_file = q.QUEUE / "jobs" / jid / "spec.json"
            if not spec_file.exists():
                print(f"Skipping missing job: {jid}")
                continue
            spec = q.load(spec_file)
            digest = q.text_digest(spec)
            if jid not in jobs_map or jobs_map[jid] != digest:
                jobs_map[jid] = digest
                added += 1
                print(f"Approved: {jid}")

        data["jobs"] = jobs_map
        q.save(approvals_file, data, replace=True)
        fcntl.flock(lock, fcntl.LOCK_UN)

    print(f"Successfully added {added} jobs to approved-additions.json.")


if __name__ == "__main__":
    approve()
