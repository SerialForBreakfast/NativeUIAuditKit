"""Materialize the maintainer-approved exact full-scene admission, no training."""
import human_annotation_review as h

def main():
    base=h.ROOT/'reports/work/FULLSCREEN-EXPERIMENT-41';base.mkdir(parents=True,exist_ok=True)
    old=h.ROOT/'reports/work/FULLSCREEN-READTHROUGH-40/run-draft-v2.json'
    doc=h.read(old);frames=doc['frames']
    h.require(len(frames)==2500 and sum(f['split']=='train' for f in frames)==2000 and
        sum(f['split']=='evaluation' for f in frames)==500,'unexpected_membership')
    admission=dict(version='fullscreen-focus-admission-v1',approved=True,
        purpose='full-screen-focus-training',approvedBy='Maintainer: Great i approve that tranche, after FULLSCREEN-READTHROUGH-40',
        membershipSHA256=h.digest(frames),sourcePreparation=h.ref(old),
        scope='FSF001: exact full scenes, original groups, one bounded run; no promotion.')
    h.write(base/'admission.json',admission);doc['admission']=h.ref(base/'admission.json')
    h.write(base/'run.json',doc)
    print(base/'run.json')

if __name__=='__main__':main()
