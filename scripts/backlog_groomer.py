"""Read-only backlog report (ADR-0026, RCA-20261013-01).

The groomer reports queue state. It never creates, approves, moves, or deletes a job.
An empty queue is reported as starvation. It is never filled with generated work.
Quarantine is an explicit, receipted action in `queue_quarantine.py`.
"""
import argparse
import json

import research_queue as q
import research_readiness as rr


def is_proposal(spec):
    """Return True when a specification still waits for an external producer or is planning only."""
    if spec.get("planningOnly") is True:
        return True
    for requirement in spec.get("requirements", []):
        text = requirement if isinstance(requirement, str) else json.dumps(requirement)
        if any(word in text.lower() for word in ("remote-ttr", "external", "producer")):
            return True
    return False


def queue_report(queue=q.QUEUE, modules=q.MODULES):
    """Count jobs by state and readiness. Read-only."""
    jobs = queue / "jobs"
    counts = {}
    ready, proposals, unreadable = [], [], []
    for job in sorted(jobs.iterdir()) if jobs.exists() else []:
        if not job.is_dir() or not (job / "spec.json").exists():
            continue
        try:
            spec = q.load(job / "spec.json")
            state, _ = q.state(job)
        except (ValueError, OSError, KeyError) as error:
            unreadable.append(dict(job=job.name, reason=str(error)[:200]))
            continue
        if state == "pending" and rr.check(job.name, queue, modules).get("ready"):
            state = "ready"
            ready.append(job.name)
        counts[state] = counts.get(state, 0) + 1
        if is_proposal(spec):
            proposals.append(job.name)
    return dict(counts=counts, readyJobs=ready, proposals=proposals, unreadable=unreadable,
                starvation=not ready,
                message="No useful ready experiment. Report starvation; do not generate work." if not ready else None)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print the full report as JSON.")
    args = parser.parse_args()
    report = queue_report()
    if args.json:
        print(json.dumps(report, indent=2))
        return
    for state, count in sorted(report["counts"].items()):
        print(f"  {state}: {count}")
    print(f"Ready jobs ({len(report['readyJobs'])}): {report['readyJobs'][:10]}")
    if report["starvation"]:
        print(report["message"])


if __name__ == "__main__":
    main()
