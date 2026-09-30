"""Optional geometry-only proposal filtering. Never infers labels or focus."""
import argparse
import json
from pathlib import Path
from PIL import Image
from compare_annotation_proposals import match, validate_boxes, overlay, sha
from perception_benchmark import _iou
from focus_dataset_contract import ROOT, local


def select(boxes, width, height, policy='deduplicate'):
    validate_boxes(boxes, width, height)
    if policy not in ('deduplicate', 'compact'): raise ValueError('unknown_filter_policy')
    kept=[]; removed=[]
    # Stable first occurrence, no truth/confidence-based ranking.
    for i, box in enumerate(boxes):
        duplicate=next((j for j in kept if _iou(box, boxes[j]) >= .8), None)
        reason='near_duplicate' if duplicate is not None else None
        if policy=='compact' and box[2]*box[3] < width*height*.001:
            reason='small_region'
        if reason: removed.append(dict(index=i, reason=reason, duplicateOf=duplicate))
        else: kept.append(i)
    return kept, removed


def run(comparison, expected, protocol, protocol_sha, output):
    comparison,protocol,output=map(local,(comparison,protocol,output))
    if output.exists(): raise ValueError('output_collision')
    if sha(comparison)!=expected or sha(protocol)!=protocol_sha: raise ValueError('changed_input')
    source=json.loads(comparison.read_text()); frozen=json.loads(protocol.read_text())
    if source.get('version')!=1 or frozen.get('version')!=1: raise ValueError('unsupported_protocol')
    for ref in frozen['inputs']:
        if sha(local(ROOT/ref['path']))!=ref['sha256']: raise ValueError('changed_source')
    revision=json.loads(local(ROOT/frozen['inputs'][0]['path']).read_text())
    if revision.get('partition')!='development': raise ValueError('development_only')
    truth={f['id']:f for f in revision['frames']}
    ids=[f['id'] for f in source['frames']]
    if len(set(ids))!=len(ids) or set(ids)!=set(truth): raise ValueError('changed_membership')
    result=dict(version='annotation-filter-v1', sources=[dict(path=str(comparison.relative_to(ROOT)),sha256=expected),
        dict(path=str(protocol.relative_to(ROOT)),sha256=protocol_sha)], frames=[], totals={},
        humanTimeSaved=None, trainingEligible=False, defaultChanged=False)
    result['implementation']={name:sha(ROOT/'scripts'/name) for name in
        ('annotation_proposal_filter.py','compare_annotation_proposals.py','perception_benchmark.py')}
    output.mkdir(parents=True)
    for frame in source['frames']:
        reviewed=truth[frame['id']]
        if frame['image']!=reviewed['image']: raise ValueError('changed_image_binding')
        boxes=[c['bounds'] for c in reviewed['controls']]
        with Image.open(local(ROOT/frame['image']['path'])) as im:
            im.load(); panels=[]; methods={}
            for name, proposals in [('raster',frame['heuristic']),('vision',frame['vision'])]:
                for policy in ('raw','deduplicate','compact'):
                    key=name+'-'+policy
                    indices,removed=(list(range(len(proposals))),[]) if policy=='raw' else select(proposals,*im.size,policy)
                    selected=[proposals[i] for i in indices]
                    metrics={str(t):match(selected,boxes,t) for t in (.5,.75)}
                    methods[key]=dict(indices=indices,removed=removed,metrics=metrics)
                    totals=result['totals'].setdefault(key,{})
                    for t,m in metrics.items():
                        dst=totals.setdefault(t,{})
                        for k in ('matches','reviewed','proposals','missedReviewed','unmatchedProposals'):
                            dst[k]=dst.get(k,0)+m[k]
                    if name=='vision': panels.append(overlay(im,selected,key+': '+str(len(selected)),'#00d8ae'))
            page=Image.new('RGB',(1920,392))
            for i,panel in enumerate(panels):page.paste(panel,(i*640,0))
            page.save(output/(frame['id']+'.png'))
        result['frames'].append(dict(id=frame['id'],screen=frame['screen'],methods=methods))
    for ref in frozen['inputs']:
        if sha(local(ROOT/ref['path']))!=ref['sha256']: raise ValueError('changed_source')
    if sha(comparison)!=expected or sha(protocol)!=protocol_sha:raise ValueError('changed_input')
    (output/'report.json').write_text(json.dumps(result,indent=2,allow_nan=False))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('comparison','protocol','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--sha256',required=True);p.add_argument('--protocol-sha256',required=True)
    a=p.parse_args();print(json.dumps(run(a.comparison,a.sha256,a.protocol,a.protocol_sha256,a.output)['totals']))
