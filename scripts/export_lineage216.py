"""Bind worker evaluation ROI IDs to frozen original-frame lineage."""
import argparse
from pathlib import Path
import operating215 as prior
import fullframe_replay_audit as pool
import evaluate_artwork213 as worker
import compose_style210 as composition
from artwork200_campaign import sha,write
from shared_transfer import require


def check_window(window,parent,crop):
    require(len(window)==4 and all(type(v)is int for v in window),'window_type')
    x,y,right,bottom=window
    require(0<=x<right<=parent.width and 0<=y<bottom<=parent.height and
            (right-x,bottom-y)==(crop.width,crop.height),'window_geometry')


def export(out):
    out=worker.fresh(out)
    require(sha(prior.MAPPING)==prior.PINS[1] and sha(pool.MEMBERSHIP)==pool.PIN,'mapping_changed')
    mapping=worker.evaluation.read(prior.MAPPING)
    membership=pool.source.p.sealed(pool.MEMBERSHIP)['rows']
    byhash={}
    for row in membership:byhash.setdefault(row['image']['sha256'],[]).append(row)
    parent=composition.r.c.inputs()
    requests=worker.checked_requests(worker.ROOT/'reports/work/ARTWORK-204/artifacts/evaluation213-input01')
    plans={}
    for kind in ('fit','page','combined'):
        full=worker.evaluation.load_request(composition.h.checked(worker.ROOT,parent['manifests'][kind]),41)
        originals={i.image_id:i for i in full.images}
        records={r['cropID']:r for r in mapping['plans'][kind]['records'] if r['cropID'] is not None}
        require(set(records)=={i.image_id for i in requests[kind].images},'roi_membership')
        rows=[]
        for image in requests[kind].images:
            record=records[image.image_id];original=originals[record['imageID']]
            check_window(record['window'],original,image)
            ancestry=byhash.get(original.image_sha256,[])
            groups={r.get('group',Path(r['id']).stem) for r in ancestry}
            require(len(groups)<=1,'ambiguous_parent_group')
            rows.append(dict(imageID=image.image_id,imageSHA256=image.image_sha256,labelSHA256=image.label_sha256,
                parentImageID=original.image_id,parentImageSHA256=original.image_sha256,
                parentDimensions=[original.width,original.height],window=record['window'],
                group=next(iter(groups)) if groups else None,
                groupEvidence='sealed173sameImageHash' if groups else 'not_in173; parent identity known, higher ancestry unavailable',
                role='training-derived fit diagnostic' if kind=='fit' else 'retained development evaluation'))
        plans[kind]=dict(contentSHA256=requests[kind].content_sha256,rows=rows)
    report=dict(schemaVersion='worker216-evaluation-lineage-v1',sourceMappingSHA256=prior.PINS[1],
        sourceMembershipSHA256=pool.PIN,sourceSHA256=sha(Path(__file__)),plans=plans,
        trainingEligible=False,coordinateSpace='top-left original pixels; crop window xyxy')
    write(out,report)
    return {k:dict(count=len(v['rows']),unknownGroups=sum(r['group'] is None for r in v['rows'])) for k,v in plans.items()}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('out',type=Path)
    print(export(parser.parse_args().out))
