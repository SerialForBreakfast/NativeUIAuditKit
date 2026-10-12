#!/usr/bin/env python3
"""Monitor and resume utility for research queue jobs (ASD-STE100)."""
import argparse
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import research_queue

def get_queue_stats(queue_dir=None):
    q = queue_dir or research_queue.QUEUE
    jobs_dir = q / "jobs"
    if not jobs_dir.exists():
        return {"total": 0, "complete": 0, "pending": 0, "interrupted": 0, "failed": 0, "jobs": []}

    stats = {"total": 0, "complete": 0, "pending": 0, "interrupted": 0, "failed": 0, "jobs": []}
    for job_path in sorted(jobs_dir.iterdir()):
        if not job_path.is_dir() or not (job_path / "spec.json").exists():
            continue
        job_id = job_path.name
        state, attempts = research_queue.state(job_path)
        last_attempt = attempts[-1] if attempts else None
        stats["total"] += 1
        
        status_str = "pending"
        score = None
        if state == "complete":
            stats["complete"] += 1
            status_str = "complete"
            if last_attempt:
                summary_file = last_attempt / "out/benchmark_summary.json"
                if summary_file.exists():
                    try:
                        summary = json.loads(summary_file.read_text())
                        score = summary.get("metrics", {}).get("accuracy")
                    except Exception:
                        pass
        elif state == "interrupted":
            stats["interrupted"] += 1
            status_str = "interrupted"
        elif state in ("failed", "exhausted"):
            stats["failed"] += 1
            status_str = "failed"
        else:
            stats["pending"] += 1

        stats["jobs"].append({
            "id": job_id,
            "state": state,
            "status": status_str,
            "score": score
        })
    return stats

def show_status():
    stats = get_queue_stats()
    print("========================================")
    print("RESEARCH QUEUE MONITOR")
    print("========================================")
    print(f"Total Registered Jobs : {stats['total']}")
    print(f"Completed Jobs        : {stats['complete']}")
    print(f"Pending Jobs          : {stats['pending']}")
    print(f"Interrupted Jobs      : {stats['interrupted']}")
    print(f"Failed Jobs           : {stats['failed']}")
    print("----------------------------------------")
    if stats["pending"] > 0:
        print(f"Jobs waiting to run: {stats['pending']}")
        for j in stats["jobs"]:
            if j["status"] == "pending":
                print(f"  - {j['id']}")
    else:
        print("All jobs are completed or resolved.")
    print("========================================")

def resume_queue(max_jobs=10):
    print(f"Resuming research queue execution (up to {max_jobs} jobs)...")
    results = research_queue.run(max_jobs=max_jobs)
    print(f"Processed {len(results)} jobs:")
    for job_id, status in results:
        print(f"  - {job_id}: {status}")
    return results

def show_report():
    stats = get_queue_stats()
    print(f"{'Job ID':<35} {'Status':<12} {'Accuracy':<10}")
    print("-" * 60)
    for j in stats["jobs"]:
        acc_str = f"{j['score']:.4f}" if j['score'] is not None else "N/A"
        print(f"{j['id']:<35} {j['status']:<12} {acc_str:<10}")

def main():
    parser = argparse.ArgumentParser(description="Research queue monitor and resume utility.")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("status", help="Show queue status and counts.")
    
    resume_parser = subparsers.add_parser("resume", help="Resume pending or interrupted jobs.")
    resume_parser.add_argument("--max-jobs", type=int, default=30, help="Max jobs to process.")

    subparsers.add_parser("report", help="Show quantitative metrics report.")

    args = parser.parse_args()
    if args.command == "status":
        show_status()
    elif args.command == "resume":
        resume_queue(args.max_jobs)
    elif args.command == "report":
        show_report()
    else:
        show_status()

if __name__ == "__main__":
    main()
