"""Validate deconfounded acquisition metadata; never confer training eligibility."""
import argparse
from collections import Counter
import re
import human_annotation_review as h


def validate(doc):
    h.require(doc.get('version')=='transition-intake-coverage-v1','intake_version')
    ids=set();groups={};pixels={};counts=Counter()
    for row in doc['records']:
        h.require(isinstance(row.get('id'),str) and row['id'] and row['id'] not in ids,'duplicate_or_missing_pair')
        ids.add(row['id'])
        h.require(row.get('partition') in ('train','development','evaluation'),'partition')
        h.require(isinstance(row.get('journeyGroup'),str) and row['journeyGroup'],'journey_group')
        group=row['journeyGroup'];partition=row['partition']
        h.require(groups.setdefault(group,partition)==partition,'journey_leakage')
        for field in ('focusChanged','scrolled'):
            h.require(type(row.get(field)) is bool,'observed_'+field+'_required')
        h.require(row.get('labelSource') in ('fixture-observed','human-reviewed'),'label_source')
        for field in ('beforeObservation','afterObservation','actionReceipt','cleanupReceipt'):
            ref=row.get(field)
            h.require(isinstance(ref,dict) and set(ref)=={'path','sha256'} and
                isinstance(ref['path'],str) and ref['path'] and
                isinstance(ref['sha256'],str) and re.fullmatch('[0-9a-f]{64}',ref['sha256']), 'evidence_reference')
            # Validate the actual referenced bytes, not just a caller's assertion.
            h.checked(h.ROOT,ref)
        hashes=row.get('decodedFrameHashes')
        h.require(isinstance(hashes,list) and len(hashes)==2 and
            all(isinstance(v,str) and re.fullmatch('[0-9a-f]{64}',v) for v in hashes),'frame_hashes')
        for value in hashes:
            h.require(pixels.setdefault(value,partition)==partition,'pixel_leakage')
        counts[(partition,row['scrolled'],row['focusChanged'])]+=1
    cells=[dict(partition=p,scrolled=s,focusChanged=f,count=counts[p,s,f])
        for p in ('train','development','evaluation') for s in (False,True) for f in (False,True)]
    return dict(version='transition-intake-coverage-report-v1',pairs=len(ids),cells=cells,
        gaps=[c for c in cells if not c['count']],trainingEligible=False,
        limitation='Metadata/reference validation only. Observation semantics, pixel hashes, boxes and independent evaluation reservation require source intake; displacement is not scrolling truth.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();out=h.fresh(a.output);h.write(out,validate(h.read(h.local(a.input))),sealed=True)
