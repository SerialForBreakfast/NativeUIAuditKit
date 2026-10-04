"""Paired fixed-checkpoint sensitivity comparison; incompatible inputs fail closed."""
import argparse
import human_annotation_review as h


def load(path):
    doc=h.read(path)
    h.require(doc.get('version')=='transfer-sensitivity-v1' and
        doc.get('seal')==h.digest({k:v for k,v in doc.items() if k!='seal'}) and
        doc.get('trainingEligible') is False and doc.get('modelGatePassed') is False,
        'invalid_sensitivity_seal_or_scope')
    return doc


def compare(before,after):
    h.require(before['version']==after['version']=='transfer-sensitivity-v1' and
        before['corpusSHA256']==after['corpusSHA256'] and before['conditions']==after['conditions'] and
        before['rejected']==after['rejected'],'sensitivity_incompatible')
    def indexed(report):
        rows=report['results'];keys=[(r['id'],r['split'],r['condition']) for r in rows]
        h.require(len(keys)==len(set(keys)),'duplicate_sensitivity_row')
        return dict(zip(keys,rows))
    a,b=indexed(before),indexed(after);h.require(set(a)==set(b),'sensitivity_membership')
    h.require(all(a[k]['expectedChange']==b[k]['expectedChange'] for k in a),'sensitivity_labels')
    result=[]
    for split in ('train','development'):
        for condition in before['conditions']:
            keys=[k for k in a if k[1:]==(split,condition)]
            result.append(dict(split=split,condition=condition,pairs=len(keys),
                beforePaired=sum(a[k]['bothBoxesCorrect'] for k in keys),
                afterPaired=sum(b[k]['bothBoxesCorrect'] for k in keys),
                gained=sum(not a[k]['bothBoxesCorrect'] and b[k]['bothBoxesCorrect'] for k in keys),
                lost=sum(a[k]['bothBoxesCorrect'] and not b[k]['bothBoxesCorrect'] for k in keys)))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('before','after','output'):p.add_argument('--'+k,required=True)
    args=p.parse_args();paths=[h.local(args.before),h.local(args.after)];out=h.fresh(args.output)
    docs=[load(path) for path in paths]
    report=dict(version='robustness-comparison-v1',inputs=[h.ref(p) for p in paths],
        comparison=compare(*docs),releaseEligible=False,
        limitation='Exposed diagnostic transforms; not independent generalization or production qualification.')
    h.write(out,report,sealed=True);print(report['comparison'])
