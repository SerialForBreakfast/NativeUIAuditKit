"""Check handoff claims without changing models, capture, or the runner."""
import math
import research_queue as q

OUT = None


def receipt_audit(documents):
    rows=[]
    for name, document in documents.items():
        for case in document['cases']:
            geometry=case.get('focused_element_geometry',{})
            rows.append(dict(batch=name,case=case['case_id'],
                settled=case.get('pre_settled') is True and case.get('post_settled') is True,
                identityAgrees=bool(case.get('pre_observed_focus_id')) and
                    case.get('pre_observed_focus_id')==case.get('post_observed_focus_id'),
                selectedElementFocused=geometry.get('focused'),
                bodyPresent=bool(geometry.get('rendered_body_geometry') or geometry.get('body_geometry')),
                screenshot=case.get('screenshot_file'),sha256=case.get('screenshot_sha256')))
    return dict(cases=len(rows),settled=sum(r['settled'] for r in rows),
        matchingFocus=sum(r['identityAgrees'] for r in rows),
        bodyPresent=sum(r['bodyPresent'] for r in rows),
        selectedElementFalse=sum(r['selectedElementFocused'] is False for r in rows),
        rows=rows,trainingAdmitted=False,modelAccepted=False,
        decision='Verify original bracket observations before labels or bounds enter training. Summary consistency is insufficient.')


def receipts():
    cfg=q.load(OUT/'config.json')
    documents={r['path']:q.load(q.ROOT/r['path']) for r in cfg['receipts']}
    q.save(OUT/'summary.json',receipt_audit(documents))


def scalar_normalization():
    rows=[]
    for z in (-10.,-1.,-.1,.1,1.,10.):
        denominator=.05*abs(z)+1e-7
        rows.append(dict(logit=z,normalized=z/denominator,derivative=1e-7/denominator**2))
    q.save(OUT/'summary.json',dict(rows=rows,modelAccuracy=None,modelAccepted=False,
        decision='Reject direct scalar LogitNorm. Positive magnitudes collapse near 20 and gradients shrink. Test retention methods separately.'))


def crop_geometry():
    rows=[]
    for w,h in ((180,48),(216,60),(260,72),(320,88)):
        width,height=w*2,h*2
        margin=max(32,.25*max(width,height))
        rows.append(dict(designPoints=[w,h],exampleRasterScale=2,
            nativePixels=[width,height],requiredWindow=[width+2*margin,height+2*margin],
            fits384=width+2*margin<=384 and height+2*margin<=384))
    q.save(OUT/'summary.json',dict(rows=rows,modelAccuracy=None,modelAccepted=False,
        baseCombinations=4*4,proposedCases=12,
        decision='Use measured raster transforms. Preserve the original crop; compare padding, larger windows, or declared resizing separately.'))
