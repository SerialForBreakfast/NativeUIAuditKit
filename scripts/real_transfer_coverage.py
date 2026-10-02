"""Read-only pinned corpus metadata coverage audit; no image inference or admission."""
import argparse
from collections import Counter
import human_annotation_review as h
import native_focus_transfer as t


def aspect(bounds):
    h.require(len(bounds)==4 and bounds[2]>0 and bounds[3]>0,'invalid_body_bounds')
    return bounds[2]/bounds[3]


def run(output):
    p=h.read(t.PROTOCOL);rows=[]
    for ref in p['sourceEvidence']:
        document=h.read(t.checked(ref))
        if ref['path'].endswith('/accepted.json'):rows.extend(document['rows'])
    expected={s['caseID'] for s in p['samples']}
    h.require(len(rows)==len(expected) and {r['caseID'] for r in rows}==expected,'corpus_membership')
    train=[r for r in rows if r['role']=='train']
    lo=min(aspect(r['frames'][0]['bounds']) for r in train)
    hi=max(aspect(r['frames'][0]['bounds']) for r in train)
    result_path=h.ROOT/'reports/work/REAL-TRANSFER-DIAGNOSIS-32/scored-clipping-aware/result.json'
    result=h.sealed(result_path,'real-transfer-diagnosis-v1')
    h.require(h.ref(t.PROTOCOL)==result['model']['protocol'],'protocol_changed')
    real=[dict(id=r['id'],aspect=aspect(r['referenceBounds']),
               outsideTrainingAspect=not lo-1e-6<=aspect(r['referenceBounds'])<=hi+1e-6,
               clipped=r['clippedContext'],retainedWindowFraction=r['retainedWindowFraction']) for r in result['rows']]
    data=dict(version='real-transfer-coverage-v1',**h.FLAGS,protocol=h.ref(t.PROTOCOL),
              implementation=h.ref(__file__),result=h.ref(result_path),sourceEvidence=p['sourceEvidence'],
              trainingPairs=len(train),allPairs=len(rows),trainingAspectRange=[lo,hi],
              trainingFamilies=dict(Counter(r['layoutFamily'] for r in train)),
              trainingArtworkFamilies=dict(Counter(r['artworkFamily'] for r in train)),
              trainingGrowthRange=[[min(r['growth'][i] for r in train),max(r['growth'][i] for r in train)] for i in (0,1)],
              real=real,interpretation='Metadata coverage mismatch is not causal proof; native control rendering and appearance also differ.')
    out=h.fresh(output);out.mkdir(parents=True);h.write(out/'coverage.json',data,sealed=True)
    lines=['# Training coverage versus reviewed controls','',
           f"Verified {len(rows)} source pairs, including {len(train)} training pairs.",
           f"Training body width/height range: {lo:.3f}–{hi:.3f}.",
           f"Layout names: {data['trainingFamilies']}. A layout named row is not a Settings listRow control.",
           '', '| Real pair | Width/height | Outside training range | Context clipped |',
           '| --- | --- | --- | --- |']
    for r in real:lines.append(f"| {r['id']} | {r['aspect']:.3f} | {r['outsideTrainingAspect']} | {r['clipped']} |")
    lines+=['',data['interpretation']]
    (out/'coverage.md').write_text('\n'.join(lines)+'\n');print('\n'.join(lines))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True)
    run(p.parse_args().output)
