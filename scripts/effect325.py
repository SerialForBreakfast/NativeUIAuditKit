"""Compare authored and native effect footprints after fixed training."""
from pathlib import Path
import numpy as np
import pool325 as p
import effect312 as e


def main():
    b=p.b;p.t.set_num_threads(2);corpus=b.read(p.OUT/'corpus.json');records=[]
    for row in corpus['rows']:
        if row['condition']!='movement' or row['reverse']:continue
        images=[p.r.s.image(v['path'],v['sha256']) for v in row['images']]
        value=p.r.s.encoded(*images,(192,128))[0]
        records.append(dict(id=row['id'],domain='authored',role='train',size=row['sizePixels'],
            separation=row['separationPixels'],metrics=e.metrics(value,[])))
    tiny,rows,pin=p.r.s.tiny_rows()
    for i,row in enumerate(rows):
        if row['condition']!='forward':continue
        records.append(dict(id=f'tiny-{i}',domain='native',role='development',size=None,separation=None,
            metrics=e.metrics(tiny[i],[])))
    groups={}
    for domain,size in [('authored',3),('authored',6),('authored',12),('native',None)]:
        selected=[v for v in records if v['domain']==domain and v['size']==size]
        groups[f'{domain}:{size}']=dict(count=len(selected),ranges={key:np.percentile([v['metrics'][key] for v in selected],[0,50,100]).tolist()
            for key in ('areaAbove1','areaAbove8','maximum','windowEnergyFraction')})
    b.write(p.OUT/'effect-audit.json',dict(source=b.ref(Path(__file__)),metricSource=b.ref(Path(e.__file__)),
        corpus=b.ref(p.OUT/'corpus.json'),tiny=pin,records=records,groups=groups,
        use='Post-training diagnosis only. No membership, weight, or threshold changes.',
        limitation='Image differences include all visible changes. They do not establish semantic focus labels.'))
    print(groups,flush=True)


if __name__=='__main__':main()
