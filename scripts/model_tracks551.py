"""Read model campaign readiness from the existing task authority and queue."""
import statistics
from collections import Counter

START = '<!-- model-tracks-v1 -->'
END = '<!-- /model-tracks-v1 -->'
STATES = {'implementation', 'human review', 'missing evidence', 'dependency wait', 'ready'}


def report(text, jobs):
    if START not in text:
        return dict(tracks=[], error='Model track definitions are unavailable.')
    section = text.split(START, 1)[1].split(END, 1)[0]
    tracks = []; seen = set()
    for line in section.splitlines():
        if not line.startswith('|') or line.startswith('| Track') or line.startswith('|---'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) != 8:
            raise ValueError('model_track_columns')
        name, task, prefixes, question, inputs, state, owner, action = cells
        if name in seen or state not in STATES or not all(cells):
            raise ValueError('model_track_definition')
        seen.add(name)
        prefixes = [x.strip() for x in prefixes.split(',') if x.strip() != 'none']
        rows = [j for j in jobs if any(j['job'].startswith(p) for p in prefixes)]
        counts = Counter(j.get('displayState', j['state']) for j in rows)
        ready = [j for j in rows if j.get('displayState') == 'ready']
        seconds = 0; unknown = 0
        for row in ready:
            # Same task and job kind only. Training durations cannot estimate reports.
            samples = [j['wallSeconds'] for j in jobs if j['state'] == 'complete' and j.get('wallSeconds')
                       and j.get('task') == row.get('task') and j.get('jobKind') == row.get('jobKind')]
            if samples: seconds += statistics.median(samples)
            else: unknown += 1
        tracks.append(dict(track=name, task=task, question=question, qualifiedInputs=inputs,
            preparationState=state, owner=owner, nextAction=action, counts=dict(counts),
            readyJobs=len(ready), readySeconds=seconds, readyUnknown=unknown,
            runningJobs=counts['running'], actionableBlockers=[dict(job=j['job'], reasons=j.get('readinessReasons', []))
                for j in rows if j.get('displayState') in ('blocked', 'failed', 'exhausted')],
            state='running' if counts['running'] else 'ready' if ready else state,
            timingBasis='Median completed time for the same task and job kind; otherwise unavailable.'))
    return dict(tracks=tracks, error=None, limitation='Preparation is not execution. Tracks can share producer prerequisites.')
