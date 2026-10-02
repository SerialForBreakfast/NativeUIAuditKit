"""Bounded negative-only inference stress; no training or source image edits."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import time

import native_focus_transfer as f


def main():
    import numpy as np
    from PIL import Image
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
    out=Path(a.output).resolve();f.n.require(out.is_relative_to(f.n.ROOT) and not out.exists(),'output_collision')
    scorer=f.Scorer();rows=[r for r in scorer.protocol['samples'] if r['role']=='evaluation' and r['label']==0]
    f.n.require(len(rows)==250,'negative_membership');started=time.monotonic();results={}
    for gain in (.8,1.2):
        values=[]
        for offset in range(0,len(rows),32):
            images=[]
            for row in rows[offset:offset+32]:
                with Image.open(f.checked(dict(path=row['path'],sha256=row['sha256']))) as im:
                    x=np.asarray(im.convert('RGB'),dtype=np.float32)
                images.append(Image.fromarray(np.clip(np.rint(x*gain),0,255).astype(np.uint8)))
            values+=scorer.score(images)
        results[str(gain)]=dict(n=len(values),falseFocused=sum(v>=.85 for v in values),
            uncertain=sum(.15<v<.85 for v in values),unfocused=sum(v<=.15 for v in values),
            predictions=[dict(id=r['id'],probability=v) for r,v in zip(rows,values)])
    saved=json.loads((f.RUN/'result.json').read_text())['predictions'];prob={r['id']:r['probability'] for r in saved}
    groups=defaultdict(list)
    for row in rows:groups[(row['configurationGroup'],row['background'])].append(row)
    transitions=[]
    for group,rs in sorted(groups.items()):
        rs.sort(key=lambda r:r['id'])
        for left,right in zip(rs,rs[1:]):
            transitions.append(dict(before=left['id'],after=right['id'],
                correctUnfocused=prob[left['id']]<=.15 and prob[right['id']]<=.15))
    result=dict(model=scorer.identity,code=f.metrics.local_ref(Path(__file__)),seconds=time.monotonic()-started,
        illumination=results,contentOnly=dict(constructedPairs=len(transitions),
            correctlyUnfocused=sum(r['correctUnfocused'] for r in transitions),pairs=transitions),
        identicalNoOps=dict(pairs=len(rows),correctlyUnfocused=sum(prob[r['id']]<=.15 for r in rows)),
        interpretation='Synthetic negative-only stress and saved-score pair composition, not genuine action sequences')
    f.n.write(out,result);print(json.dumps({k:{x:y for x,y in v.items() if x!='predictions'} for k,v in results.items()}))


if __name__=='__main__':main()
