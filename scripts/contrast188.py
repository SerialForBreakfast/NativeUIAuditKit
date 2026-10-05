"""Source-connected transition sensitivity; diagnostic labels stay diagnostic."""
import collections
import numpy as np
import replay_worker180 as b
import verify_consensus180 as c
h,a=b.h,b.a
OUT=h.ROOT/'reports/work/TRANSITION-CONTRAST-188/artifacts'
BROOT=h.ROOT/'reports/work/WORKER-180B/artifacts/worker180b-return-4e85246d86324329a4d880d4d99711bc'


def connected(cases):
    parent={}
    def find(g):
        parent.setdefault(g,g)
        if parent[g]!=g:parent[g]=find(parent[g])
        return parent[g]
    memberships=[]
    for case in cases:
        h.require(case['kind'] in ('original','identity') and case['label'] in (0,1),'case_kind')
        groups=[case['group']] if case['kind']=='original' else sorted({x['group'] for x in case['ancestry']})
        h.require(groups and all(type(g) is str and g for g in groups),'empty_ancestry')
        memberships.append(groups)
        for g in groups:
            left,right=find(groups[0]),find(g);parent[max(left,right)]=min(left,right)
    return [find(groups[0]) for groups in memberships]


def summarize(vectors,cases):
    h.require(vectors.shape==(3,3,len(cases),768),'vector_shape')
    h.require(np.isfinite(vectors).all() and ((vectors>=0)&(vectors<=1)).all(),'vector_values')
    groups=connected(cases);labels=np.array([r['label'] for r in cases]);unique=sorted(set(groups))
    populations={name:[i for i,r in enumerate(cases) if ('identity' if r['kind']=='identity' else ('changed' if r['label'] else 'unchanged'))==name] for name in ('changed','unchanged','identity')}
    h.require(sum(map(len,populations.values()))==len(cases),'population_count')
    summary={};case_priority=np.zeros(len(cases));ranks=[]
    for pi,placement in enumerate(('after','before','both')):
        value=vectors[:,pi];individual=np.where(value<=.15,0,np.where(value>=.85,1,-1))
        consensus=np.where((value<=.15).all(axis=0),0,np.where((value>=.85).all(axis=0),1,-1))
        flip=(consensus>=0)&(consensus!=labels[:,None])
        if pi<2:case_priority+=flip.mean(axis=1)/2
        source=[]
        for group in unique:
            ids=[i for i,g in enumerate(groups) if g==group];source.append(dict(group=group,cases=len(ids),confidentFlipRate=float(flip[ids].mean()),abstentionRate=float((consensus[ids]<0).mean())))
        pop={}
        for name,ids in populations.items():
            if not ids:continue
            pop[name]=dict(cases=len(ids),variants=len(ids)*768,consensus=c.counts(value[:,ids].reshape(3,-1),np.repeat(labels[ids],768)),
                individual=[dict(model=model,confidentFlips=int(((individual[mi,ids]>=0)&(individual[mi,ids]!=labels[ids,None])).sum()),abstentions=int((individual[mi,ids]<0).sum())) for mi,model in enumerate(('DTM050','DTM051','DTM052'))])
        summary[placement]=dict(populations=pop,sources=source,equalSourceFlipRate=float(np.mean([x['confidentFlipRate'] for x in source])))
    for i in sorted(range(len(cases)),key=lambda i:(-case_priority[i],cases[i]['id']))[:10]:
        ranks.append(dict(id=cases[i]['id'],kind=cases[i]['kind'],originalLabel=int(labels[i]),group=groups[i],asymmetricConsensusFlipRate=float(case_priority[i])))
    return dict(summary=summary,topTen=ranks,sourceGroups=len(unique),cases=len(cases),variantCountPerPlacement=len(cases)*768,
        warning='Perturbations may alter focus evidence; these are not verified native errors or new training labels.')


def run():
    h.require(not OUT.exists(),'output_collision')
    pins=h.read(b.OLD/'pins.json');cursor=h.read(b.OLD/'cursor.json');bc=h.read(BROOT/'reports/work/WORKER180/b01/cursor.json')
    for root in (a.BASE/'extracted',BROOT):
        for ref in h.read(root/'inventory.json',2*1024**2):
            path=b.v.w.t.path_under(root,ref.get('file',ref.get('path')));b.v.w.t.verified(path,ref)
    def read(base,ref):
        path=b.v.w.t.path_under(base,ref['file']);b.v.w.t.verified(path,ref);return h.read(path)
    after=a.checked_scores(read(a.BASE/'extracted',row['file']) for row in cursor['chunks'])
    other=b.scores(read(BROOT,row) for row in bc['chunks'])
    value=np.concatenate([after[:,None],other],axis=1).reshape(3,3,286,768)
    report=summarize(value,pins['cases']);report.update(source=h.ref(__file__),oldPins=h.ref(b.OLD/'pins.json'),bCursor=h.ref(BROOT/'reports/work/WORKER180/b01/cursor.json'),productionEligible=False)
    OUT.mkdir(parents=True);h.write(OUT/'evaluation.json',report,sealed=True)
    print('Groups',report['sourceGroups'])
    for name,row in report['summary'].items():print(name,'equal source flips',row['equalSourceFlipRate'], 'populations', {k:v['consensus'] for k,v in row['populations'].items()})


if __name__=='__main__':run()
