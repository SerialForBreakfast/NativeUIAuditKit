"""Count-based operating-point ceiling; diagnostic truth never selects crops."""
import roi194 as x


def run():
    h,p,e=x.h,x.p,x.e;parent=x.r.c.inputs();cid=e.load_names().index('pageControl');rows=[]
    for kind,ref in parent['manifests'].items():
        req=e.load_request(h.checked(h.ROOT,ref),41)
        base=e.validated_artifact(h.read(h.checked(h.ROOT,parent['reused']['022'][kind],256*1024**2),256*1024**2),req,parent['checkpoints']['022']['sha256'],expected_settings=x.r.c.SETTINGS)
        indexed={row['imageID']:row for row in base['results']};cases=[]
        for im in req.images:
            truths=sum(int(line.split()[0])==cid for line in im.label_path.read_text().splitlines() if line.strip())
            proposals=len(x.r.proposals(indexed[im.image_id],cid))
            cases.append(dict(imageID=im.image_id,truths=truths,proposals=proposals,maxTP=min(truths,proposals)))
        rows.append(dict(kind=kind,maxTP=sum(v['maxTP'] for v in cases),minimumFP=sum(v['proposals']-v['maxTP'] for v in cases),
            targetSupport=sum(v['truths'] for v in cases),cases=cases))
    control=p.sealed(x.r.c.g.CONTROL/'evaluation.json')
    immutable={k:v for k,v in control['assessment']['gates'].items() if k.startswith(('sheet','cancelAction','mapView','scrollIndicator'))}
    h.write(x.OUT/'ceiling.json',dict(rows=rows,immutableNonPageGates=immutable,
        interpretation='Optimistic count-only ceiling permits arbitrary geometry, not achievable model accuracy. Fixed base scores/counts limit recall and false-positive reductions. Truth used for diagnosis only.'),sealed=True)
    print([{k:v for k,v in row.items() if k!='cases'} for row in rows]);print(immutable)


if __name__=='__main__':run()
