"""Group reviewed stills and spatial counterpart proposals for human identity review."""
import argparse
from collections import defaultdict
import human_annotation_review as h
import native_focus_transfer as t
import focus_recorded_readiness as r
import focus_runtime as runtime


def iou(a,b):
    x,y,w,v=a;X,Y,W,V=b
    intersection=max(0,min(x+w,X+W)-max(x,X))*max(0,min(y+v,Y+V)-max(y,Y))
    return intersection/(w*v+W*V-intersection)


def candidates(truth):
    proposals=[]
    for sha,f in sorted(truth.items()):
        for c in f['controls']:
            if c['state']!='focused':continue
            for other,g in sorted(truth.items()):
                if sha==other or f['screen']!=g['screen']:continue
                matches=[(iou(c['bounds'],d['bounds']),d) for d in g['controls']
                         if d['state']=='unfocused' and d.get('class')==c.get('class')]
                matches.sort(key=lambda x:(-x[0],x[1]['id']))
                if not matches or matches[0][0]<.5:continue
                # Ambiguous spatial overlap is retained as a reason, never a label.
                score,d=matches[0]
                proposals.append(dict(screen=f['screen'],focusedImage=sha,referenceImage=other,
                    focusedControl=c['id'],referenceControl=d['id'],iou=score,
                    ambiguous=len(matches)>1 and matches[1][0]>=.5,
                    identity='unverified',nativeEffect='unverified',profile='unknown'))
    return sorted(proposals,key=lambda p:(p['ambiguous'],-p['iou'],p['focusedImage'],p['referenceImage']))


def run(output):
    refs=h.read(t.READINESS)['inputs']
    args=[t.checked(refs[k]) for k in ('batch','baseline','pending','revision','completeness')]
    truth=r.reviewed_frames(r.baseline_reader.baseline(args[1]),*args[2:])
    sizes={sha:h.image(h.ROOT,f['image']) for sha,f in truth.items()}
    proposed=[p for p in candidates(truth) if sizes[p['focusedImage']]==sizes[p['referenceImage']]]
    groups=defaultdict(list)
    for sha,f in sorted(truth.items()):groups[f['screen']].append(dict(sha256=sha,**f))
    # One best candidate per focused frame, then round-robin screen families.
    queues=defaultdict(list);seen=set()
    for p in proposed:
        # Already-scored Home variants add no new identity review value.
        if p['screen']=='home':continue
        if p['focusedImage'] in seen:continue
        seen.add(p['focusedImage']);queues[p['screen']].append(p)
    selected=[]
    while len(selected)<8 and any(queues.values()):
        for key in sorted(queues):
            if queues[key] and len(selected)<8:selected.append(queues[key].pop(0))
    out=h.fresh(output);out.mkdir(parents=True)
    identity=runtime.identity()
    lines=['# Grouped reference identity review','',
        'Existing boxes and focus labels are preserved. Check whether each pair shows the SAME control/content and viewport. Spatial overlap alone is not identity. Profile/native-effect applicability is unknown. Related frames are not independent evaluation data.',
        '',f'{len(truth)} unique reviewed images; {len(groups)} screen labels; {len(proposed)} spatial proposals; {len(selected)} shown together.','']
    for i,p in enumerate(selected,1):
        lines += [f"## {i}. {p['screen']}",'',f"Spatial IoU {p['iou']:.3f}; identity confirmation required.",
                  f"Focused control: `{p['focusedControl']}`; reference: `{p['referenceControl']}`.",'']
        for role in ('focusedImage','referenceImage'):
            frame=truth[p[role]];path=t.checked(frame['image'])
            control=p['focusedControl' if role=='focusedImage' else 'referenceControl']
            target=next(c for c in frame['controls'] if c['id']==control)
            preview=t.crop(dict(id=role,path=str(path),sha256=frame['image']['sha256'],
                                bounds=target['bounds']),h.ROOT)
            dest=out/f'{i:02d}-{role}.png';preview.save(dest)
            p[role+'Preview']=h.ref(dest)
            lines += [f'![{role} — identity preview]({dest})',f'[Full screenshot]({path})','']
    h.require(runtime.identity()==identity,'runtime_changed')
    h.write(out/'inventory.json',dict(version='real-reference-inventory-v1',**h.FLAGS,
        readiness=h.ref(t.READINESS),implementation=h.ref(__file__),inputs=refs,runtime=identity,
        frames=len(truth),screens=len(groups),groups=dict(groups),proposals=proposed,selected=selected,
        previewMeaning='Per-state reviewed bounds for identity review only; not FDR036 common-window inputs'),sealed=True)
    (out/'review.md').write_text('\n'.join(lines)+'\n')
    print(dict(frames=len(truth),screens=len(groups),proposals=len(proposed),selected=len(selected)))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True)
    run(p.parse_args().output)
