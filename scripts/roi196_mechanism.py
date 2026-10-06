"""Separate paired geometry gains from conservative base-detector fallbacks."""
import collections
import roi196 as r
import roi195 as g
h,p,e=r.h,r.p,r.e


def reason_group(reason):
    return 'new_refinement' if reason=='replaced' else 'base_fallback'


def run():
    r.configure();destination=r.OUT/'mechanism.json';h.require(not destination.exists(),'output_collision')
    old_path=h.ROOT/'reports/work/IOS-ROI-194/artifacts/attempt02/diagnosis.json'
    new_path=r.runner.OUT/'diagnosis.json';old=p.sealed(old_path);new=p.sealed(new_path)
    prior={(v['kind'],v['cropID']):v for v in old['rows']};parent=r.r.c.inputs();cid=e.load_names().index('pageControl')
    requests={k:e.load_request(h.checked(h.ROOT,ref),41) for k,ref in parent['manifests'].items()}
    images={k:{im.image_id:im for im in req.images} for k,req in requests.items()}
    families={(v['kind'],v['imageID']):v['family'] for v in p.sealed(g.OUT/'diagnosis.json')['images']}
    rows=[]
    h.require(set(prior)=={(v['kind'],v['cropID']) for v in new['rows']},'proposal_membership')
    for v in new['rows']:
        before=prior[(v['kind'],v['cropID'])];h.require(before['before']==v['before'],'base_changed')
        truth=r.r.c.g.r.f.d.prior.truth(images[v['kind']][v['imageID']],cid)
        overlaps=[e.iou_xyxy(v['before']['xyxyPixels'],t) for t in truth]
        target=[truth[max(range(len(truth)),key=overlaps.__getitem__)]] if overlaps and max(overlaps)>0 else []
        rows.append(dict(kind=v['kind'],family=families[(v['kind'],v['imageID'])],cropID=v['cropID'],
            mechanism=reason_group(v['reason']),reason=v['reason'],**g.compare_row(before['after'],v['after'],target)))
    summary={}
    for k in requests:
        summary[k]={}
        for family in sorted({v['family'] for v in rows if v['kind']==k}):
            summary[k][family]={}
            for mechanism in ('new_refinement','base_fallback'):
                subset=[v for v in rows if v['kind']==k and v['family']==family and v['mechanism']==mechanism]
                summary[k][family][mechanism]=dict(total=len(subset),changed=sum(v['changed'] for v in subset),
                    dispositions=dict(collections.Counter(v['disposition'] for v in subset)))
    h.write(destination,dict(summary=summary,rows=rows,sources=[h.ref(old_path),h.ref(new_path),h.ref(__file__)],
        interpretation='Paired IoU diagnostic anchored to original base-box truth association, not an AP decomposition or causal data-only ablation.'),sealed=True)
    print(summary)


if __name__=='__main__':run()
