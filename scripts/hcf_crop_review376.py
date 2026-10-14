"""Review paired crop results without inference, training, or changed labels."""
import math
from collections import Counter, defaultdict
import research_queue as q

OUT = None


def index_rows(document):
    rows = document.get('rows')
    q.require(isinstance(rows, list) and rows, 'rows_missing')
    q.require(len({row['id'] for row in rows}) == len(rows), 'duplicate_case')
    q.require(all(row.get('role') in ('development', 'retained') for row in rows), 'role_not_reviewable')
    q.require(all(row.get('outcome') in ('correct', 'wrong', 'miss') for row in rows), 'unknown_outcome')
    return {row['id']: row for row in rows}


def summary(rows):
    return dict(frames=len(rows), groups=len({row['group'] for row in rows}),
                gains=sum(row['gain'] for row in rows), losses=sum(row['loss'] for row in rows),
                baseline=dict(Counter(row['baseline'] for row in rows)),
                candidate=dict(Counter(row['candidate'] for row in rows)))


def score_margin(prediction):
    values = prediction.get('scores')
    q.require(isinstance(values, list) and len(values) >= 2, 'scores_missing')
    q.require(all(type(v) in (int, float) and math.isfinite(v) and 0 <= v <= 1 for v in values), 'invalid_score')
    top = sorted(values, reverse=True)
    return dict(top=top[0], runnerUp=top[1], separation=top[0] - top[1])


def review(baseline, candidate, geometry):
    left, right = index_rows(baseline), index_rows(candidate)
    q.require(set(left) == set(right), 'membership_mismatch')
    q.require(baseline.get('proposalMode') == candidate.get('proposalMode') == 'oracle', 'proposal_mode')
    q.require(baseline.get('modelSHA256') and candidate.get('modelSHA256'), 'model_hash_missing')
    rows = []
    for ident in sorted(left):
        a, b = left[ident], right[ident]
        for key in ('sha256', 'group', 'role', 'profile', 'family'):
            q.require(key in a and a[key] == b.get(key), 'identity_mismatch:' + key)
        q.require(a['prediction'].get('cropHashes') == b['prediction'].get('cropHashes')
                  and a['prediction'].get('cropHashes'), 'crop_identity_mismatch')
        row = {key: a[key] for key in ('id', 'sha256', 'group', 'role', 'profile', 'family')}
        row.update(baseline=a['outcome'], candidate=b['outcome'],
                   gain=a['outcome'] != 'correct' and b['outcome'] == 'correct',
                   loss=a['outcome'] == 'correct' and b['outcome'] != 'correct',
                   baselineMargin=score_margin(a['prediction']), candidateMargin=score_margin(b['prediction']))
        frame = geometry.get(ident)
        if frame is None:
            row['geometry'] = None
        else:
            q.require(all(frame.get(k) == a[k] for k in ('sha256', 'group', 'role', 'profile')), 'geometry_identity_mismatch')
            x, y, w, h = frame['boxes'][frame['focus']]
            width, height = frame['width'], frame['height']
            q.require(width > 0 and height > 0 and w > 0 and h > 0, 'invalid_geometry')
            row['geometry'] = dict(body=[x,y,w,h], sourceSize=[width,height],
                relativeArea=w*h/(width*height), center=[(x+w/2)/width,(y+h/2)/height],
                region=f"{min(2,max(0,int(3*(x+w/2)/width)))}:{min(2,max(0,int(3*(y+h/2)/height)))}")
        rows.append(row)
    slices = {}
    for factor in ('profile','family','role','group'):
        slices[factor] = {value: summary([r for r in rows if r[factor] == value]) for value in sorted({r[factor] for r in rows})}
    regions = sorted({r['geometry']['region'] for r in rows if r['geometry']})
    slices['region'] = {v: summary([r for r in rows if r['geometry'] and r['geometry']['region'] == v]) for v in regions}
    return dict(version='hcf-crop-review-v1', **summary(rows), rows=rows, slices=slices,
        models=dict(baseline=baseline['modelSHA256'],candidate=candidate['modelSHA256']),
        modelAccepted=False, deploymentAccuracy=None, noFocusAccuracy=None, physicalAccuracy=None,
        independentTrialCount=None, confoundedChanges=['profile balance','duplicate removal'],
        marginDefinition='Top score minus runner-up score, not a calibrated error probability.',
        limitations=['Known control boxes only.','Inspected development and retained groups only.',
                     'Group counts do not prove independence.','No deployment threshold changes.'])


def duplicate_exposure(crops):
    rows = [r for r in crops['rows'] if r['role'] == 'train']
    groups = defaultdict(list)
    for row in rows:
        groups[row['sha256']].append(row)
    conflicts = [key for key, values in groups.items() if len({v['label'] for v in values}) > 1]
    slices = []
    for profile, label in sorted({(r['profile'],r['label']) for r in rows}):
        values = [r for r in rows if r['profile']==profile and r['label']==label]
        slices.append(dict(profile=profile,label=label,rows=len(values),
            fileIdentities=len({v['sha256'] for v in values}),groups=len({v['group'] for v in values})))
    return dict(rows=len(rows),fileIdentities=len(groups),conflictingFileLabels=conflicts,slices=slices,
        limitation='File hashes measure stored crop reuse. They do not replace decoded-pixel equivalence or independent scene counts.')


def run():
    refs=[]; docs={}
    for dep in q.load(OUT/'dependencies.json'):
        for ref in dep['outputs']:
            path=q.local_path(q.ROOT,ref['path'])
            q.require(q.digest(path)==ref['sha256'],'input_changed')
            docs[(dep['job'],path.name)]=q.load(path); refs.append(ref)
    old=docs[('hcf371r5-80-crop-evaluate','comparison.json')]
    new=docs[('hcf375c-80-crop-evaluate','comparison.json')]
    crops=docs[('hcf371r4-50-crops','crops.json')]
    retained=docs[('hcf371-00-retained','admission.json')]
    geometry={r['id']:r for r in crops['frames']+retained['rows'] if r['role'] in ('development','retained')}
    result=review(old,new,geometry)
    result['trainingExposure']=duplicate_exposure(crops)
    q.save(OUT/'review.json',result)
    q.save(OUT/'sources.json',refs)
