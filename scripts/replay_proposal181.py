"""Train-only replacement proposal; no model launch or evaluation-based sampling."""
import collections
import diagnose181 as d
r=d.r;h=d.h;p=d.p


def select(candidates,kept,labels,count=80,family_by_id=None):
    support=collections.Counter();families=collections.Counter()
    family_by_id=family_by_id or {}
    def family(row):
        value=row.get('family') or family_by_id.get(row['id'])
        h.require(bool(value),'family_provenance_missing');return value
    for row in kept:support.update(labels[row['id']]);families[family(row)]+=1
    pool={row['id']:row for row in candidates};pixels={row['pixelSHA256'] for row in kept};chosen=[]
    while len(chosen)<count:
        eligible=[row for row in pool.values() if row['pixelSHA256'] not in pixels and labels[row['id']]]
        h.require(bool(eligible),'insufficient_unique_positives')
        best=min(eligible,key=lambda row:(-sum(1/(1+support[c]) for c in sorted(labels[row['id']])),families[family(row)],row['id']))
        chosen.append(best);pixels.add(best['pixelSHA256']);support.update(labels[best['id']]);families[family(best)]+=1;del pool[best['id']]
    return chosen


def run():
    out=d.OUT/'proposal.json';h.require(not out.exists(),'output_collision')
    doc=r.inputs();diagnosis=p.sealed(d.OUT/'diagnosis.json')
    membership=p.sealed(h.checked(h.ROOT,doc['membership']));labels={}
    for row in membership['rows']:
        if row['split']=='train':
            labels[row['id']]={int(line.split()[0]) for line in h.checked(h.ROOT,row['label']).read_text().splitlines() if line.strip()}
    fit=doc['rows'][:216];positive=[x for x in doc['rows'][216:] if labels[x['id']]]
    removed=[x['id'] for x in doc['rows'][216:] if not labels[x['id']]]
    h.require(len(positive)==136 and len(removed)==80,'original_balance')
    oldids={x['id'] for x in doc['rows']};oldpixels={x['pixelSHA256'] for x in doc['rows']}
    evalpixels={x['pixelSHA256'] for x in membership['rows'] if x['split']!='train'}
    pool=[x for x in membership['rows'] if x['split']=='train' and x['id'] not in oldids and x['pixelSHA256'] not in oldpixels|evalpixels]
    # Native added rows keep family in the source catalog metadata, not the row.
    catalog=r.f.d.inputs()['metadata'];families={k:v['family'] for k,v in catalog.items()}
    added=select(pool,fit+positive,labels,family_by_id=families);rows=fit+positive+added
    # Reuse ancestry and split-role check against authoritative membership.
    r.choose(dict(fitIDs=[x['id'] for x in fit],replayRows=positive+added),membership['rows'],doc['metadata'])
    for row in rows:
        for key in ('image','label','annotation'):h.checked(h.ROOT,row[key])
    h.write(out,dict(version='replay181-proposal-v1',rows=rows,removedIDs=removed,
        addedIDs=[x['id'] for x in added],membership=doc['membership'],referenceProtocol=h.ref(r.OUT/'protocol.json'),
        diagnosis=h.ref(d.OUT/'diagnosis.json'),sources=[h.ref(__file__),h.ref(d.__file__)],
        selection='inverse-current-class-image-support, selected-family-support, imageID; train labels only',
        config=dict(doc['args']),schedule=doc['schedule'],initializer=doc['initializer'],
        addedFamilies=dict(collections.Counter(x.get('family') or families[x['id']] for x in added)),
        dataRole='existing train only',launchEligible=False,
        remainingPreflight=['new isolated staged dataset/output', 'parse complete labels/images', 'bind final config/source and log next run before launch'],
        hypothesis='labeled replay context versus empty fillers at unchanged batch/epoch budget',
        trainingLaunched=False,productionEligible=False),sealed=True)
    print('Frozen80replacements;432training-only members; no training launch',flush=True)


if __name__=='__main__':run()
