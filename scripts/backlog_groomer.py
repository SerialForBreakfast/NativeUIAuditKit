"""Backlog grooming and low-watermark queue maintenance (ADR-0026, ASD-STE100)."""
import argparse
import json
from pathlib import Path
import shutil
import sys

import research_queue as q
import research_readiness as rr

QUEUE_ROOT = q.QUEUE
JOBS_DIR = QUEUE_ROOT / "jobs"
PROPOSALS_DIR = QUEUE_ROOT / "proposals"
QUARANTINE_DIR = QUEUE_ROOT / "quarantine"

LOW_WATERMARK = 10
TARGET_READY = 25


def ensure_directories():
    """Ensure proposal and quarantine directories exist."""
    PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)
    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)


def is_proposal(spec):
    """Check if a specification is a proposal or external placeholder."""
    if spec.get("planningOnly") is True:
        return True
    reqs = spec.get("requirements", [])
    if reqs:
        for r in reqs:
            if "remote-ttr" in r.lower() or "external" in r.lower() or "producer" in r.lower():
                return True
    return False


def segregate_proposals():
    """Move external placeholder specifications to the proposals directory."""
    ensure_directories()
    moved = []
    if not JOBS_DIR.exists():
        return moved
    for job_path in sorted(JOBS_DIR.iterdir()):
        if not job_path.is_dir():
            continue
        spec_path = job_path / "spec.json"
        if not spec_path.exists():
            continue
        try:
            spec = q.load(spec_path)
            state, _ = q.state(job_path)
            if state in ("blocked", "pending") and is_proposal(spec):
                target = PROPOSALS_DIR / job_path.name
                if target.exists():
                    shutil.rmtree(target)
                shutil.move(str(job_path), str(target))
                moved.append(job_path.name)
        except (ValueError, OSError, KeyError):
            continue
    return moved


def quarantine_superseded():
    """Move obsolete, dead, and superseded revision jobs to quarantine."""
    ensure_directories()
    quarantined = []
    if not JOBS_DIR.exists():
        return quarantined

    obsolete_ids = {
        "focus343-identical-neighbors",
        "focus347-07-brightness-detail-content",
        "focus366-control-notifications-3",
        "focus366-notification-notifications-3",
        "hcf357-decode-1",
        "hcf357-decode-2",
        "hcf357-decode-4",
        "hcf361-baseline-fdr021",
        "hcf367-recover-r2",
        "focus364-10-shelf",
        "focus364-12-hero_detail",
        "focus364-20-shelf",
        "focus364-22-hero_detail",
        "focus364-90-decision",
        "hcf371r5-80-detector-evaluate",
        "hcf371r5-90-decision",
        "hcf371r5-91-decision",
    }

    obsolete_prefixes = (
        "hcf371r2-",
        "hcf371r3-",
        "hcf362-",
        "hcf367-",
        "generation352-",
        "generation354-size-",
    )

    for job_path in sorted(JOBS_DIR.iterdir()):
        if not job_path.is_dir():
            continue
        name = job_path.name
        should_quarantine = False

        if name in obsolete_ids:
            should_quarantine = True
        elif any(name.startswith(p) for p in obsolete_prefixes):
            state, _ = q.state(job_path)
            if state != "complete":
                should_quarantine = True
        elif name.startswith("hcf371-") and name not in ("hcf371-00-retained", "hcf371-01-retained-rules"):
            state, _ = q.state(job_path)
            if state != "complete":
                should_quarantine = True

        if should_quarantine:
            target = QUARANTINE_DIR / name
            if target.exists():
                shutil.rmtree(target)
            shutil.move(str(job_path), str(target))
            quarantined.append(name)

    return quarantined


def get_queue_status():
    """Count jobs by status and ready state in the active queue."""
    counts = {"complete": 0, "running": 0, "ready": 0, "pending": 0, "blocked": 0, "exhausted": 0}
    ready_jobs = []
    if not JOBS_DIR.exists():
        return counts, ready_jobs

    for job_path in sorted(JOBS_DIR.iterdir()):
        if not job_path.is_dir() or not (job_path / "spec.json").exists():
            continue
        try:
            st, _ = q.state(job_path)
            if st == "pending":
                readiness = rr.check(job_path.name, QUEUE_ROOT, q.MODULES)
                if readiness.get("ready"):
                    counts["ready"] += 1
                    ready_jobs.append(job_path.name)
                else:
                    counts["pending"] += 1
            elif st in counts:
                counts[st] += 1
            else:
                counts[st] = 1
        except (ValueError, OSError, KeyError):
            counts["blocked"] += 1

    return counts, ready_jobs


def sync_approvals():
    """Sync approved-additions.json to contain active approved jobs only."""
    apps_file = QUEUE_ROOT / "approved-additions.json"
    apps = q.load(apps_file) if apps_file.exists() else {"version": "research-additions-v1", "jobs": {}}
    jobs = apps.get("jobs", {})
    filtered = {
        ident: digest for ident, digest in jobs.items()
        if (JOBS_DIR / ident / "spec.json").exists()
    }
    for job_path in JOBS_DIR.iterdir():
        spec_path = job_path / "spec.json"
        if job_path.is_dir() and spec_path.exists():
            if job_path.name not in filtered:
                try:
                    spec = q.load(spec_path)
                    filtered[job_path.name] = q.text_digest(spec)
                except Exception:
                    pass
    apps["jobs"] = filtered
    q.save(apps_file, apps, replace=True)


def groom_backlog():
    """Execute the full grooming process and return the status delta."""
    ensure_directories()
    segregated = segregate_proposals()
    quarantined = quarantine_superseded()
    sync_approvals()
    counts, ready_jobs = get_queue_status()

    return {
        "segregatedProposals": segregated,
        "quarantinedJobs": quarantined,
        "activeCounts": counts,
        "readyJobs": ready_jobs,
    }


def main():
    parser = argparse.ArgumentParser(description="Groom research backlog and maintain queue readiness.")
    parser.add_argument("--auto-groom", action="store_true", help="Run full backlog grooming sequence.")
    parser.add_argument("--status", action="store_true", help="Print active queue status.")
    parser.add_argument("--quarantine-only", action="store_true", help="Quarantine superseded jobs only.")
    parser.add_argument("--proposals-only", action="store_true", help="Segregate proposals only.")
    args = parser.parse_args()

    if args.quarantine_only:
        res = quarantine_superseded()
        print(f"Quarantined {len(res)} jobs.")
        return

    if args.proposals_only:
        res = segregate_proposals()
        print(f"Segregated {len(res)} proposals.")
        return

    if args.auto_groom:
        result = groom_backlog()
        print(json.dumps(result, indent=2))
        return

    counts, ready_jobs = get_queue_status()
    print("Queue Status:")
    for k, v in counts.items():
        print(f"  {k}: {v}")
    print(f"Ready jobs ({len(ready_jobs)}): {ready_jobs[:10]}")


if __name__ == "__main__":
    main()
