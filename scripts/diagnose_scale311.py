"""Check scaled training examples without another fit or threshold change."""
from collections import defaultdict
from pathlib import Path
import numpy as np
import scale311 as run


def main():
    b=run.base;s=run.s;out=run.OUT
    b.require((out/'completion.json').exists(),'incomplete_run')
    b.require(not (out/'training-diagnostic.json').exists(),'output_collision')
    s.torch.set_num_threads(2)
    audit=b.read(out/'scale-audit.json');groups=defaultdict(dict)
    for row in audit['rows']:
        key='|'.join(sorted(r['sha256'] for r in row['sourceImages']))
        groups[str(row['targetPixels'])].setdefault(key,row)
    selected=[groups[g][k] for g in sorted(groups) for k in sorted(groups[g])[:32]]
    models={'FOCUS310':s.load_candidate(s.OUT/'source-detail/last.pt'),
            'FOCUS311':s.load_candidate(out/'last.pt')}
    results=[]
    for row in selected:
        images=[s.image(r['path'],r['sha256']) for r in row['sourceImages']]
        scaled,_=run.scale_pair(images,row['scale'])
        values={name:s.encoded(*frames,(192,128))[0] for name,frames in [('original',images),('scaled',scaled)]}
        b.require(b.sha(values['scaled'].tobytes())==row['tensorSHA256'],'derived_identity')
        details={name:run.detail(values[name],frames) for name,frames in [('original',images),('scaled',scaled)]}
        b.require(b.sha(details['scaled'].tobytes())==row['detailSHA256'],'detail_identity')
        scores={model:{name:float(b.worker.score(net,np.concatenate((value,details[name]))[None])[0])
                       for name,value in values.items()} for model,net in models.items()}
        results.append(dict(index=row['index'],group=row['group'],targetPixels=row['targetPixels'],
                            changed=row['changed'],scores=scores))
    summaries=[]
    for target in sorted(groups):
        rows=[r for r in results if str(r['targetPixels'])==target]
        for model in models:
            for view in ('original','scaled'):
                scores=np.array([r['scores'][model][view] for r in rows]);labels=np.array([r['changed'] for r in rows])
                summaries.append(dict(target=target,model=model,view=view,
                    summary=b.trainer.w.summary(scores,labels),
                    changed=b.trainer.w.summary(scores[labels==1],labels[labels==1])))
    b.write(out/'training-diagnostic.json',dict(runner=b.ref(Path(__file__)),rows=results,summaries=summaries,
        selection='First 32 unique canonical image pairs per target, ordered by image hashes. Training only.',
        limitation='Diagnostic sample, not independent evaluation. No settings change or new training.'))
    for row in summaries:print(row,flush=True)


if __name__=='__main__':main()
