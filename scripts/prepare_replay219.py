"""Freeze a resident-input full-frame replay intervention, without training."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
import prepare_fullframe217 as parent
from artwork200_campaign import sha,write
from generator_asset_plan import inventory_metadata
from shared_transfer import require

ROOT=parent.ROOT
MANIFEST=ROOT/'reports/work/FULLFRAME-217/artifacts/input01/payload/manifest.json'
PIN='335afc6940d9148016cc97744ac74c906cfe2655a2d75914bd93eece3f68dcb0'

def schedule(full,native):
    require(len(full)==len(set(full))==189 and len(native)==len(set(native))==60,'source_counts')
    require(not set(full)&set(native),'source_overlap')
    ordered=sorted(full,key=lambda x:(hashlib.sha256(x.encode()).hexdigest(),x))
    return ordered*8+ordered[:186]+native

def prepare(out):
    out=out.absolute()
    require(out.resolve()==out and out.is_relative_to(ROOT) and not out.exists(),'output_collision_boundary')
    require(sha(MANIFEST)==PIN,'parent_changed')
    doc=inventory_metadata(MANIFEST)
    native_doc=inventory_metadata(parent.replay.PAYLOAD/'manifest.json')
    require(sha(parent.replay.PAYLOAD/'manifest.json')==parent.replay.PIN,'native_changed')
    full=[r['id'] for r in doc['examples']];native=doc['slots']['treatment'][-60:]
    plan=schedule(full,native)
    rows={r['id']:(r,MANIFEST.parent) for r in doc['examples']}
    for r in native_doc['examples']:
        if r['id'] in native:rows[r['id']]=(r,parent.replay.PAYLOAD)
    require(len(rows)==249 and set(plan)==set(rows),'membership')
    labels={};refs=[]
    for identity,(row,base) in rows.items():
        require(row['role']=='train','role')
        for kind in ('image','label'):
            path=base/row[kind]
            file_ref=next(f for f in (doc if identity in full else native_doc)['files'] if f['path']==row[kind])
            require(path.resolve()==path and path.is_file() and path.stat().st_size==file_ref['bytes'] and sha(path)==file_ref['sha256'],'input_changed')
            refs.append(dict(id=identity,kind=kind,sha256=file_ref['sha256']))
        labels[identity]=Counter(int(line.split()[0]) for line in (base/row['label']).read_text().splitlines() if line.strip())
    exposure=Counter()
    for identity in plan:exposure.update(labels[identity])
    require(all(0<=c<41 for c in exposure),'taxonomy')
    out.parent.mkdir(parents=True,exist_ok=True)
    write(out,dict(schemaVersion='worker219-replay-v1',run='035',parentManifestSHA256=PIN,
        nativeManifestSHA256=parent.replay.PIN,initializerSHA256=doc['initializerSHA256'],
        slots=plan,slotSHA256=hashlib.sha256(json.dumps(plan,separators=(',',':')).encode()).hexdigest(),
        uniqueSources=249,configuration=doc['configuration'],epochs=10,batchesPerEpoch=440,optimizerUpdates=275,
        exposure={doc['classNames'][c]:exposure[c] for c in range(41)},sourceReferences=refs,
        evaluationContentSHA256=doc['evaluationContentSHA256'],
        comparison='Stored034 and022; changed context/exposure/repetition, not isolated causality',
        trainingLaunched=False,modelGatePassed=False,sourceSHA256=sha(__file__)))
    return dict(path=str(out.relative_to(ROOT)),bytes=out.stat().st_size,sha256=sha(out))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('out',type=Path)
    print(prepare(p.parse_args().out))
