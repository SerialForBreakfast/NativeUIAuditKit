"""Select unstarted jobs without re-reading completed model artifacts.

This is a scheduling filter, not an approval or evidence check.
The existing readiness and execution checks remain authoritative.
"""
import research_queue as q


def unstarted(selected, queue):
    for ident, digest in selected.items():
        q.require(isinstance(ident,str) and q.ID.fullmatch(ident), 'dispatch_job_id')
        job=queue/'jobs'/ident
        # The normal runner starts only pending jobs. Any attempt needs its
        # existing lifecycle or an explicit successor, not implicit redispatch.
        if q.attempts_of(job):
            continue
        yield ident,digest
