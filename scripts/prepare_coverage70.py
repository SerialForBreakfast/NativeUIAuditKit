"""One native intake, two explicitly scoped geometry-coverage experiments."""
from pathlib import Path
import numpy as np
import focus_direct_transition as d
from prepare_data67 import verify_gate as expanded_gate
from prepare_temporal68 import verify_gate as temporal_gate
from prepare_transition_inputs import prepare_many,manifest,load

ARMS=(('broad',d.BROAD_CONFIG,'coverage70-dtm014'),('compressed',d.COMPRESSED_CONFIG,'coverage70-dtm015'))


def verify_gate(reference,corpus,rows):
    d.h.require(reference is not None,'missing_coverage_gate')
    report=d.h.sealed(d.h.checked(d.h.ROOT,reference),'data67-batched-comparison-v1')
    result=d.h.read(d.h.checked(d.h.ROOT,report['candidate']))
    protocol=d.h.read(d.h.checked(d.h.ROOT,result['protocol']))
    d.h.require(protocol['configuration']==d.TEMPORAL_CONFIG and report['models']['DTM013']==result['model'] and
        report['corpusSHA256']==protocol['corpusSHA256']==corpus['corpusSHA256'],'coverage_gate_binding')
    d.h.checked(d.h.ROOT,result['model'])
    expected={r['id'] for r in rows if r['split']=='train'}
    scores=[r for r in report['results'] if r['model']=='DTM013' and r['condition']=='baseline' and r['group']!='development']
    d.h.require(len(scores)==len(expected)==32 and {r['id'] for r in scores}==set(result['trainingIDs'])==expected and
        all(r['bothBoxesCorrect'] and r['rawChangeCorrect'] for r in scores),'coverage_fit_gate')
    return protocol


def prepare():
    base=d.h.fresh(d.h.ROOT/'reports/work/COVERAGE-70/ready');base.mkdir(parents=True)
    source=d.h.ROOT/'reports/work/GENERALIZATION-65/admission'
    destinations={config['augmentation']:d.h.ROOT/f'.build/coverage70-{arm}-bank' for arm,config,_ in ARMS}
    timing=prepare_many(source/'corpus.json',source/'admission.json',destinations)
    prior=d.h.read(d.h.ROOT/'reports/work/TEMPORAL-68/ready/protocol.json');coverage=[]
    for arm,config,name in ARMS:
        prepared=destinations[config['augmentation']]/'manifest.json';inputs,corpus,rows=manifest(prepared)
        expanded_gate(prior['expandedGate'],corpus,rows,inputs['admission'])
        temporal_gate(prior['temporalGate'],corpus,rows)
        gate=d.h.ref(d.h.ROOT/'reports/work/TEMPORAL-68/comparison.json');verify_gate(gate,corpus,rows)
        x,y,options,entries,rejected=load(prepared,[r for r in rows if r['split']=='train'],config['augmentation'])
        boxes=y[:,:8].reshape(-1,4)*[96,64,96,64]
        coverage.append(dict(arm=arm,policy=config['augmentation'],views=len(entries),rejected=rejected,
            centerRange=[boxes[:,:2].min(0).tolist(),boxes[:,:2].max(0).tolist()],
            rightHalfWidthThinRows=int(((boxes[:,0]>65)&(boxes[:,2]>30)&(boxes[:,2]<50)&(boxes[:,3]<6)).sum()),
            rightSideEndpoints=int((boxes[:,0]>65).sum()),optionsPerPair=[len(v) for v in options],
            limitation='Development-driven geometry support counts, not model metrics or native-render evidence.'))
        directory=base/arm;directory.mkdir()
        protocol=dict(version=d.VERSION,sources=corpus['sources'],corpusSHA256=corpus['corpusSHA256'],
            admission=inputs['admission'],configuration=config,implementation=d.h.ref(Path(d.__file__)),pins=d.pins(),
            expandedGate=prior['expandedGate'],temporalGate=prior['temporalGate'],coverageGate=gate,preparedInputs=d.h.ref(prepared))
        protocol['protocolSHA256']=d.digest(protocol);d.h.write(directory/'protocol.json',protocol)
        d.h.write(directory/'approval.json',dict(version='focus-direct-approval-v1',approved=True,
            protocolSHA256=protocol['protocolSHA256'],arm=d.ARM,runName=name,
            decisionReference=f'2026-10-03 active goal and standing experiment envelope: COVERAGE-70 two declared600epoch augmentation arms,{arm};same32/5roles and DTM013architecture,2GiB combined outputs,no wall-time cap; no capture/export/promotion.'))
        print(arm,protocol['protocolSHA256'])
    d.h.write(base.parent/'preparation.json',dict(version='coverage70-preparation-v1',timing=timing,coverage=coverage,
        trainingLaunched=False),sealed=True)


if __name__=='__main__':prepare()
