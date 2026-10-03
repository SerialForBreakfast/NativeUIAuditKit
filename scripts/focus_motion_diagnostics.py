"""Explain reference motion conflicts using native truth strictly for scoring."""
import argparse
from collections import Counter
import numpy as np
from PIL import Image
import human_annotation_review as h
import focus_corrected_transition_audit as audit
import focus_transition_verifier as visual


def mixed_motion_count(rows):
    return sum(int(r.get('nearStationary',0)>=6 and r.get('nearNativeMotion',0)>=6 and
                   np.linalg.norm(r['nativeCenterDisplacement'])>1) for r in rows)


def run(report,root,output):
    source=h.local(report);doc=h.sealed(source,'reference-transition-audit-v1')
    h.require(doc.get('tracker')=='feature-consensus-v1','diagnostic_tracker_required')
    root=h.local(root);out=h.fresh(output);rows=[]
    for pair in doc['pairs']:
        selected=[r for r in pair.get('controls',[]) if r['expected'] in ('arrival','departure')]
        if not selected:continue
        evidence=h.checked(h.ROOT,pair['inputs'][2]);campaign=h.read(h.checked(h.ROOT,pair['inputs'][3]))
        case=next(c for c in campaign['cases'] if c['case_id']==pair['id'])
        _,before,after=audit.validate_case(root,evidence,case)
        images=[]
        for frame in (before,after):
            with Image.open(h.checked(h.ROOT,frame['image'])) as im:images.append(im.convert('RGB'))
        for control in selected:
            bounds=next(c['bounds'] for c in before['controls'] if c['id']==control['id'])
            h.require(visual.track(*images,bounds,common=True,tracker='feature-consensus-v1')==
                      control['prediction']['tracking'],'diagnostic_tracking_parity')
            match,error=visual.feature_matches(*images,bounds)
            row=dict(case=pair['id'],control=control['id'],expected=control['expected'],
                     tracking=control['prediction']['tracking']);rows.append(row)
            if error:row['reason']=error['reason'];continue
            a,b,scale=match;delta=b-a
            # Native geometry enters this diagnostic only after pixel matches are frozen.
            target=next(c['bounds'] for c in after['controls'] if c['id']==control['afterControl'])
            expected=np.array([target[0]+target[2]/2-bounds[0]-bounds[2]/2,
                               target[1]+target[3]/2-bounds[1]-bounds[3]/2])*scale
            tolerance=max(visual.FEATURE_POLICY['residual'],visual.FEATURE_POLICY['heightResidual']*bounds[3]*scale)
            zero=np.linalg.norm(delta,axis=1)<=tolerance
            moving=np.linalg.norm(delta-expected,axis=1)<=tolerance
            histogram=Counter(tuple(int(v) for v in np.round(d/3)) for d in delta)
            row.update(matches=len(delta),nearStationary=int(zero.sum()),nearNativeMotion=int(moving.sum()),
                nativeCenterDisplacement=(expected/scale).tolist(),workingScale=scale,
                motionModes=[dict(workingDisplacement=[x*3,y*3],count=count)
                             for (x,y),count in histogram.most_common(5)])
    h.require(len(rows)<=512,'diagnostic_budget')
    result=dict(version='focus-motion-diagnostic-v1',**h.FLAGS,source=h.ref(source),
        pixelPolicy=visual.FEATURE_POLICY,controls=rows,
        mixedMotionControls=mixed_motion_count(rows),
        limitation='Native displacement is scoring-only; diagnostic does not resolve runtime identity or admit data.',
        implementation=[h.ref(h.ROOT/'scripts'/name) for name in ('focus_motion_diagnostics.py','focus_transition_verifier.py')])
    h.write(out,result,sealed=True);print('mixed motion controls',result['mixedMotionControls'],'of',len(rows))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('report','root','output'):p.add_argument('--'+k,required=True)
    a=p.parse_args();run(a.report,a.root,a.output)
