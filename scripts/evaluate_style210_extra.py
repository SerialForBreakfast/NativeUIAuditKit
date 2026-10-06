"""Replay frozen ROI197 proposals for either completed style210 candidate."""
import argparse
import time
import roi197_compare as comparison
import train_style210 as training

h,p,e=comparison.h,comparison.p,comparison.e
FROZEN=comparison.OUT/'protocol.json'


def run(arm):
    training.configure(arm)
    checkpoint,_=training.previous.runner.ready()
    out=training.BASE/arm/'extra-proposal'
    h.require(not out.exists(),'output_collision')
    old=p.sealed(FROZEN)
    for ref in old['sources']+[old['screen']]:h.checked(h.ROOT,ref,256*1024**2)
    requests={kind:h.checked(h.ROOT,plan['manifest']) for kind,plan in old['plans'].items()}
    for path in requests.values():e.load_request(path,41)
    out.mkdir();start=time.monotonic()
    for kind,path in requests.items():
        e.export_predictions(path,checkpoint,out/(kind+'-predictions.json'),'mps',discard_degenerate=True)
    doc=dict(old,checkpoint=h.ref(checkpoint),fitPredictions=h.ref(out/'fit-predictions.json'),
             sources=old['sources']+[h.ref(__file__),h.ref(FROZEN)],
             currentCandidateNegativeScreenPassed=False,
             historicalScreenOnly=True,arm=arm)
    doc.pop('seal',None);h.write(out/'protocol.json',doc,sealed=True)
    saved=comparison.OUT
    try:
        comparison.OUT=out;comparison.report()
    finally:comparison.OUT=saved
    h.write(out/'execution.json',dict(seconds=time.monotonic()-start,checkpoint=h.ref(checkpoint),
        protocol=h.ref(out/'protocol.json'),modelGatePassed=False),sealed=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('arm',choices=list(training.RUNS));run(parser.parse_args().arm)
