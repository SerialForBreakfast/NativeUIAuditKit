"""Audit repeated pixels without changing capture events, labels, or data roles."""
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import subprocess

from PIL import Image
import research_queue as q

OUT = None


def groups_report(rows, pixel_key, crop=False):
    q.require(rows and len({r['id'] for r in rows}) == len(rows), 'empty_or_duplicate_ids')
    groups = defaultdict(list)
    for row in rows:
        q.require(row.get('role') and row.get('group'), 'missing_role_or_group')
        groups[pixel_key(row)].append(row)
    duplicates = []
    for members in groups.values():
        if len(members) < 2:
            continue
        roles = sorted({r['role'] for r in members})
        labels = {json.dumps(r['label'] if crop else dict(focus=r['focus'], boxes=r['boxes']), sort_keys=True)
                  for r in members}
        duplicates.append(dict(ids=[r['id'] for r in members], roles=roles,
            groups=sorted({r['group'] for r in members}), conflictingLabels=len(labels) > 1))
    slices = []
    for role, profile in sorted({(r['role'], r['profile']) for r in rows}):
        subset = [r for r in rows if (r['role'], r['profile']) == (role, profile)]
        slices.append(dict(role=role, profile=profile, observations=len(subset),
            uniquePixels=len({pixel_key(r) for r in subset}), groups=len({r['group'] for r in subset})))
    hard = [g for g in duplicates if len(g['roles']) > 1 or g['conflictingLabels']]
    return dict(observations=len(rows), uniquePixels=len(groups), extraPixelCopies=len(rows)-len(groups),
        duplicateGroups=duplicates, hardConflicts=hard, slices=slices,
        largestMultiplicity=max(map(len, groups.values())),
        metadataIntegrityPassed=not hard, trainingApproved=False,
        decision=('Hold affected model comparisons for review.' if hard else
                  'No exact conflict found. Review repeated weighting and similar scenes separately.'))


def inputs(config):
    refs = list(config.get('manifests', []))
    if (OUT/'dependencies.json').exists():
        for dep in q.load(OUT/'dependencies.json'):
            q.require(q.digest(q.ROOT/dep['result']['path']) == dep['result']['sha256'], 'changed_result')
            refs.extend(dep['outputs'])
    documents = []
    for ref in refs:
        path = q.local_path(q.ROOT, ref['path'])
        q.require(q.digest(path) == ref['sha256'], 'changed_manifest')
        if path.name == config['manifestName']:
            documents.append(q.load(path))
    q.require(documents, 'missing_manifests')
    return documents, refs


def checked_image(row, root):
    path = Path(row['path'])
    q.require(path.resolve().is_relative_to(root), 'outside_corpus')
    q.require(q.digest(path) == row['sha256'], 'changed_image')
    with Image.open(path) as image:
        q.require(image.width*image.height <= 40_000_000, 'image_too_large')
        return image.convert('RGB')


def vision_pairs(rows):
    q.require(rows and all(r['role'] == 'development' for r in rows), 'vision_development_only')
    cases = sorted({r['case'] for r in rows})[:3]
    selected = sorted([r for r in rows if r['case'] in cases], key=lambda r:r['id'])
    index = {(r['case'], r['profile'], r['focus']): r for r in selected}
    q.require(len(selected) == 24 and len(index) == 24, 'need_three_complete_cases')
    pairs = []
    def add(a, b, kind):
        pairs.append(dict(id=f'pair-{len(pairs):03d}', before=a['id'], after=b['id'], kind=kind))
    for case in cases:
        for i in range(4):
            a=index[case,'hcf',f'item-{i}']; add(a,a,'identical')
            add(a,index[case,'standard',f'item-{i}'],'profile-change')
        for profile in ('standard','hcf'):
            for i in range(3):
                add(index[case,profile,f'item-{i}'], index[case,profile,f'item-{i+1}'],'focus-movement')
    for a,b in zip(cases,cases[1:]):
        for i in range(4):
            add(index[a,'hcf',f'item-{i}'],index[b,'hcf',f'item-{i}'],'different-scene')
    return selected, pairs


def distance_report(pairs, measured):
    index={p['id']:p for p in pairs}
    q.require(len(index)==len(pairs) and len(measured)==len(pairs) and
              {p['id'] for p in measured}==set(index),'pair_membership')
    results=[]
    for row in measured:
        pair=index[row['id']]
        q.require(all(pair[k]==row[k] for k in ('before','after')),'pair_order')
        d=row['distance']; q.require(isinstance(d,(float,int)) and math.isfinite(d) and d>=0,'invalid_distance')
        results.append(dict(pair,distance=d))
    counts=[]
    for threshold in (0,.001,.01,.05,.1,.2,.5):
        counts.append(dict(threshold=threshold, flaggedByKind=dict(Counter(
            r['kind'] for r in results if r['distance']<=threshold))))
    return dict(pairs=results, operatingPoints=counts, selectedThreshold=None,
        automaticExclusion=False, decision='Keep focus movements and profile pairs even when Vision reports similarity.')


def run():
    cfg=q.load(OUT/'config.json'); docs,refs=inputs(cfg)
    rows=[r for d in docs for r in d['rows']]
    mode=cfg['mode']; root=Path('/Volumes/training-drive/data/NUIAK/HCF371')
    if mode=='frames':
        report=groups_report(rows,lambda r:(r['width'],r['height'],r['decodedSHA256']))
        report['pixelsRechecked']=False
        report['hashSource']='Pinned admission reports; RGB bytes and dimensions form the identity.'
    elif mode=='crops':
        q.require(all(r['role'] in ('train','development','calibration') for r in rows),'crop_role')
        # Audit the actual loader membership separately from both-profile observations.
        keys={}
        for i,row in enumerate(rows):
            image=checked_image(row,root)
            keys[row['id']]=(image.width,image.height,hashlib.sha256(image.tobytes()).hexdigest())
            if i%100==0:q.save(OUT.parent/'progress.json',dict(step='Check repeated crop pixels',completed=i,total=len(rows)),replace=True)
        report=groups_report(rows,lambda r:keys[r['id']],crop=True)
        report['hcfOnly']=groups_report([r for r in rows if r['profile']=='hcf'],lambda r:keys[r['id']],crop=True)
    elif mode=='vision':
        selected,pairs=vision_pairs(rows)
        for row in selected:checked_image(row,root)
        binary=q.local_path(q.ROOT,cfg['binary']['path'])
        q.require(q.digest(binary)==cfg['binary']['sha256'],'changed_probe')
        request=dict(version=1,root=str(root),featureRevision=2,featureCrop='scaleFit',
            frames=[{k:r[k] for k in ('id','path','sha256')} for r in selected],
            pairs=[{k:p[k] for k in ('id','before','after')} for p in pairs])
        q.save(OUT/'request.json',request)
        with (OUT/'vision.json').open('x') as output,(OUT/'vision.stderr').open('x') as errors:
            result=subprocess.run([str(binary)],input=json.dumps(request),text=True,stdout=output,stderr=errors,timeout=740)
        q.require(result.returncode==0,'vision_failed')
        receipt=q.load(OUT/'vision.json')
        q.require(receipt['revision']==2 and receipt['crop']=='scaleFit','vision_settings')
        report=distance_report(pairs,receipt['pairs'])
        report['independentSceneGroups']=len({r['group'] for r in selected})
        report['limitation']='Three development scenes only. No threshold calibration or final-audit inspection.'
    else:raise ValueError('unknown_mode')
    q.save(OUT/'duplicates.json',dict(version='capture-duplicates374-v1',mode=mode,inputs=refs,
        report=report,removedFiles=0,changedMembership=False,modelAccepted=False))
