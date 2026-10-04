"""Reuse old and newly prepared image derivatives for the approved68/5 comparison."""
import argparse
import focus_candidate_ranker as r


def run(output):
    h=r.d.h;out=h.fresh(output)
    old=h.ROOT/'reports/work/BATCH-79-B/native-ready/inputs.json'
    new=h.ROOT/'reports/work/NATIVE-86/candidates/inputs.json'
    a=r.load_inputs(old);b=r.sealed(new,'calibration-proposals-v1')
    h.require(b['trainingEligible'] is False,'native87_calibration_input')
    frames=[{k:f[k] for k in ('id','image','size','candidates')} for f in a['frames']+b['frames']]
    h.require(len(frames)==131 and len({f['id'] for f in frames})==131,'native87_frame_membership')
    r.validate_frames(frames)
    out.mkdir(parents=True)
    h.write(out/'inputs.json',dict(version='calibration-proposals-v1',**h.FLAGS,
        frames=frames,sources=[h.ref(old),h.ref(new)]),sealed=True)
    r.prepare_derivatives(out/'derivatives',out/'inputs.json',h.ROOT/'.build/batch79-derivatives')
    r.prepare_native(out/'ready',h.ROOT/'reports/work/NATIVE-87/admitted',out/'derivatives/derivatives.json')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True)
    run(p.parse_args().output)
