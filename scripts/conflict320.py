"""Measure training gradients before selecting one matched correction."""
import argparse
from collections import defaultdict
from pathlib import Path
import time
import numpy as np
import authored319 as a

b=a.b;r=a.r;t=a.t
OUT=b.ROOT/'reports/work/FOCUS-320'


def cosine(first,second):
    x=first.double();y=second.double()
    b.require(x.shape==y.shape and t.isfinite(x).all() and t.isfinite(y).all(),'gradient_values')
    norm=x.norm()*y.norm()
    return None if not norm else float(t.dot(x,y)/norm)


def groups(rows,labels):
    result=defaultdict(list)
    for i,(row,label) in enumerate(zip(rows,labels)):
        if row is not None:b.require(row.get('role') in ('train','development-training','development-training-derived',None),'gradient_role')
        group='retained-replay' if row is None else row.get('group','training-derived')
        result[f'{group}:label-{int(label)}'].append(i)
    return dict(result)


def gradient(net,values,details,labels,weights,indices,denominator):
    parameters=[p for p in net.parameters() if p.requires_grad]
    total=t.zeros(sum(p.numel() for p in parameters));loss=0.
    for start in range(0,len(indices),8):
        ids=indices[start:start+8]
        inputs=t.from_numpy(np.concatenate((values[ids],details[ids]),1))
        logits=net.change(inputs).flatten()
        part=t.nn.functional.binary_cross_entropy_with_logits(logits,t.from_numpy(labels[ids]),
            weight=t.from_numpy(weights[ids]),reduction='sum')/denominator
        vectors=t.autograd.grad(part,parameters)
        total+=t.cat([v.detach().flatten() for v in vectors]);loss+=float(part.detach())
    b.require(t.isfinite(total).all(),'gradient_finite')
    return total,loss


def audit():
    b.require(not OUT.exists(),'output_collision');OUT.mkdir();t.set_num_threads(2);started=time.monotonic()
    corpus=b.read(a.OUT/'corpus.json');review=b.read(a.OUT/'review.json')
    b.require(review['approvedForAuthoredTraining'] and review['corpusSHA256']==b.ref(a.OUT/'corpus.json')['sha256'],'review_required')
    manifest,membership,full,labels,weights,extra,controls,_,reg=r.s.c.prepare()
    added=r.s.previous.prior.mix(full[controls],extra,labels[1660:1740],True)
    values=np.concatenate((full,added,b.reporting.reverse(added)));del full,extra,added
    prior=b.read(r.OUT/'registration.json')
    for key,value in [('training',values),('labels',labels),('weights',weights)]:
        b.require(b.sha(value.tobytes())==prior[key+'SHA256'],'original_'+key)
    rows=r.s.schedule_rows(membership,reg,labels);indices=groups(rows,labels)
    detail,_=r.prepare(values,rows,2)
    b.require(b.sha(detail.tobytes())==b.read(r.OUT/'regions-2/views.json')['sha256'],'original_details')
    authored=np.load(b.checked(corpus['tensor']),allow_pickle=False);ad,_=r.prepare(authored,corpus['rows'],2)
    ay=np.array([x['changed'] for x in corpus['rows']],np.float32)
    exposure=np.zeros(len(ay),np.float32);np.add.at(exposure,a.schedule(labels,corpus['rows']),weights)
    auxiliary={name:[i for i,x in enumerate(corpus['rows']) if x['condition']==name]
               for name in sorted({x['condition'] for x in corpus['rows']})}
    pins={'FOCUS313':b.ref(r.OUT/'regions-2/last.pt'),'FOCUS319':b.ref(a.OUT/'run/last.pt')}
    registration=dict(version='conflict320-v1',corpus=b.ref(a.OUT/'corpus.json'),review=b.ref(a.OUT/'review.json'),
        initializer=prior['initializer'],checkpoints=pins,runner=b.ref(Path(__file__)),
        originalHashes={key:prior[key] for key in ('trainingSHA256','labelsSHA256','weightsSHA256')},
        detailSHA256=b.sha(detail.tobytes()),trainingGroups=indices,auxiliaryIndices=auxiliary,
        diagnosisOnly=True,evaluationUsedForGradients=False,outputCapBytes=2*1024**3)
    b.write(OUT/'registration.json',registration);results={}
    for name in ('initial','FOCUS313','FOCUS319'):
        t.manual_seed(42)
        net=r.extend(r.s.c.model.load_candidate(b.checked(prior['initializer'])),2) if name=='initial' else r.load_candidate(b.checked(pins[name]))
        for key,p in net.named_parameters():p.requires_grad_(key.startswith(('change.detail.','change.correction.')))
        net.eval();vectors={};stats={}
        for key,ids in indices.items():
            vectors[key],loss=gradient(net,values,detail,labels,weights,ids,len(labels))
            stats[key]=dict(count=len(ids),weightedLoss=loss,norm=float(vectors[key].norm()))
        original=sum(vectors.values());av={};pairs=[]
        for key,ids in auxiliary.items():
            av[key],loss=gradient(net,authored,ad,ay,exposure,ids,len(labels))
            stats['authored:'+key]=dict(count=len(ids),weightedLoss=loss,norm=float(av[key].norm()))
            pairs.append(dict(original='all-original',auxiliary=key,cosine=cosine(original,av[key])))
            pairs += [dict(original=g,auxiliary=key,cosine=cosine(v,av[key])) for g,v in vectors.items()]
        total=sum(av.values())
        results[name]=dict(groups=stats,pairs=pairs,aggregateCosine=cosine(original,total),
            originalNorm=float(original.norm()),auxiliaryNorm=float(total.norm()),
            mixedNorm=float((original+.25*total).norm()))
        print(name,'aggregate cosine',results[name]['aggregateCosine'],flush=True)
    justified=any(x['cosine'] is not None and x['cosine']<-.1 for v in results.values() for x in v['pairs'] if x['original']=='all-original')
    b.write(OUT/'diagnostic.json',dict(registration=b.ref(OUT/'registration.json'),results=results,
        projectionJustified=justified,seconds=time.monotonic()-started,
        limitations=['Training-only weighted gradients at 3 checkpoints.',
                    'A raw gradient projection does not guarantee an Adam update or an unseen decision.']))


def train():
    diagnostic=b.read(OUT/'diagnostic.json');b.checked(diagnostic['registration'])
    b.require(diagnostic['projectionJustified'],'correction_not_justified')
    a.execute(out=OUT,auxiliary_projection=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=['audit','train']);args=parser.parse_args()
    audit() if args.mode=='audit' else train()
