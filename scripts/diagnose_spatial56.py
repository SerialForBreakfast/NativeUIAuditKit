"""Training-subset spatial loss decomposition; diagnostic labels never enter prediction."""
import argparse
import numpy as np
import focus_direct_transition as d
import focus_spatial_transition as s
from focus_recorded_transition_eval import iou


def run(output):
    out=d.h.fresh(output)
    result_path=d.h.ROOT/'NativeUITrainer/focus_ring_runs/spatial56-dtm003/result.json'
    result=d.h.read(result_path);protocol=d.h.read(d.h.checked(d.h.ROOT,result['protocol']))
    d.h.require(protocol['pins']==d.pins() and protocol['configuration']==d.SPATIAL_DIAGNOSTIC,'diagnostic_binding')
    corpus=d.collect(protocol['sources']);rows=d.admitted(corpus,d.h.read(d.h.checked(d.h.ROOT,protocol['admission'])))
    rows=d.training_rows([r for r in rows if r['split']=='train'],d.SPATIAL_DIAGNOSTIC)
    d.h.require([r['id'] for r in rows]==result['trainingIDs'],'fit_membership_changed')
    t=d.torch_runtime();t.set_num_threads(2)
    state=t.load(d.h.checked(d.h.ROOT,result['model']),map_location='cpu',weights_only=True)
    net=d.model(state['configuration']);net.load_state_dict(state['state']);net.eval();details=[]
    for row in rows:
        frames=[d.pixels(v) for v in row['images']]
        x=t.from_numpy(d.encode(*frames)).unsqueeze(0)
        y=t.tensor([
            [v for b in row['boxes'] for v in d.target_box(b,row['size'])]])
        indices,truth=s.targets(t,y)
        with t.inference_mode():
            cells,geometry,change=net.fields(x)
            values=geometry.flatten(3).gather(3,indices[:,:,None,None].expand(-1,-1,4,1)).squeeze(3).sigmoid()
            logits=cells.flatten(2);p=d.infer(net,*frames)
            endpoints=[]
            for k in range(2):
                target=int(indices[0,k]);predicted=int(logits[0,k].argmax());v=values[0,k].tolist()
                oracle=d.image_box([(target%24+v[0])/24,(target//24+v[1])/16,v[2],v[3]],row['size'])
                endpoints.append(dict(endpoint=('before','after')[k],targetCell=target,predictedCell=predicted,
                    targetRank=int((logits[0,k]>logits[0,k,target]).sum())+1,
                    cellCrossEntropy=float(t.nn.functional.cross_entropy(logits[:,k],indices[:,k])),
                    targetCellGeometry=v,expectedCellGeometry=truth[0,k].tolist(),
                    geometryL1=float((values[0,k]-truth[0,k]).abs().mean()),
                    scoringOnlyGroundTruthCellIoU=iou(oracle,row['boxes'][k]) if oracle else 0,
                    actualIoU=iou(p['boxes'][k],row['boxes'][k]) if p['boxes'][k] else 0))
            details.append(dict(id=row['id'],endpoints=endpoints,
                rawChangeCorrect=(p['changeProbability']>=.5)==row['changed'],
                changeBCE=float(t.nn.functional.binary_cross_entropy_with_logits(change[:,0],t.tensor([float(row['changed'])])))))
    endpoints=[e for r in details for e in r['endpoints']]
    report=dict(version='spatial56-fit-diagnosis-v1',model=result['model'],source=d.h.ref(result_path),
        fittedPairs=len(rows),bothBoxesCorrect=sum(all(e['actualIoU']>=.5 for e in r['endpoints']) for r in details),
        rawChangeCorrect=sum(r['rawChangeCorrect'] for r in details),correctCells=sum(e['targetCell']==e['predictedCell'] for e in endpoints),
        meanCellCrossEntropy=float(np.mean([e['cellCrossEntropy'] for e in endpoints])),
        meanGeometryL1=float(np.mean([e['geometryL1'] for e in endpoints])),
        meanChangeBCE=float(np.mean([r['changeBCE'] for r in details])),details=details,
        limitation='Ground-truth-cell IoU is a scoring-only oracle decomposition, never a prediction or quality gate.',
        architectureObservation='Local cell/geometry heads have a 15x15 input-pixel receptive field; change head has full-frame context. This is a structural limitation, not proven causal attribution.')
    d.h.write(out,report,sealed=True);print({k:v for k,v in report.items() if k not in ('details','source','model')})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);run(p.parse_args().output)
