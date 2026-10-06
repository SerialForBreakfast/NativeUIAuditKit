"""Account for fixed-rule fallbacks without threshold search or new inference."""
import collections
import roi194 as x


def run():
    h,p,e=x.h,x.p,x.e;cp,proposal=x.ready();parent=x.r.c.inputs();cid=e.load_names().index('pageControl');summary={};rows=[]
    for kind,plan in proposal['evaluation'].items():
        base=h.read(h.checked(h.ROOT,parent['reused']['022'][kind],256*1024**2),256*1024**2)
        crop=h.read(x.OUT/(kind+'-predictions.json'),256*1024**2)
        req=e.load_request(h.checked(h.ROOT,parent['manifests'][kind]),41)
        e.validated_artifact(base,req,parent['checkpoints']['022']['sha256'],expected_settings=x.r.c.SETTINGS)
        crop_req=e.load_request(h.checked(h.ROOT,plan['manifest']),41)
        e.validated_artifact(crop,crop_req,h.sha(cp),expected_settings=x.r.c.SETTINGS)
        derived=x.merge(base['results'],plan['records'],crop['results'],cid)
        originals={v['imageID']:v for v in base['results']};predicted={v['imageID']:v for v in crop['results']};merged={v['imageID']:v for v in derived['results']}
        reasons=collections.Counter()
        for record in plan['records']:
            if not record['proposals']:reasons['no_base_proposal']+=1
            for item in record['proposals']:
                before=originals[record['imageID']]['detections'][item['proposalIndex']]
                donors=[d for d in predicted[item['id']]['detections'] if d['classID']==cid and d['score']>=.25]
                matching=[d for d in donors if e.iou_xyxy(x.r.restore(d['xyxyPixels'],item['window']),before['xyxyPixels'])>=.25]
                after=merged[record['imageID']]['detections'][item['proposalIndex']]
                reason=('no_crop_detection' if not donors else 'no_overlap_match' if not matching else 'ambiguous_donors' if len(matching)>1 else
                        'unchanged_or_shared_match' if before==after else 'replaced')
                reasons[reason]+=1;rows.append(dict(kind=kind,imageID=record['imageID'],cropID=item['id'],reason=reason,
                    donors=len(donors),matching=len(matching),before=before,after=after))
        summary[kind]=dict(reasons)
    h.write(x.OUT/'diagnosis.json',dict(summary=summary,rows=rows,source=h.ref(__file__),checkpoint=h.ref(cp),
        scope='Frozen association only; no threshold search, new labels or causal architecture claim.'),sealed=True)
    print(summary)


if __name__=='__main__':run()
