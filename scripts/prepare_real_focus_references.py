"""Prepare explicit reviewed still-image reference candidates, without model execution."""
import argparse
import json
from PIL import Image
import human_annotation_review as h
import native_focus_transfer as transfer
import native_focus_spike as native26
import focus_recorded_readiness as readiness
import focus_runtime as runtime


def intersections(window, controls, target):
    """Any neighboring body in the input window is explicit; no tolerance inferred."""
    return [dict(id=c['id'], state=c['state'], area=area,
                 windowFraction=area/(window[2]*window[3]))
            for c in controls if c['id'] != target
            for area in [native26.overlap(window, c['bounds'])] if area > 0]


def prepare(request_path, output):
    request_path=h.local(request_path);request=h.read(request_path)
    h.require(request.get('version')=='real-reference-candidates-v1','candidate_version')
    h.require(0<len(request['pairs'])<=16,'candidate_limit')
    source=transfer.checked(request['readiness']);refs=h.read(source)['inputs']
    args=[transfer.checked(refs[k]) for k in ('batch','baseline','pending','revision','completeness')]
    truth=readiness.reviewed_frames(readiness.baseline_reader.baseline(args[1]),*args[2:])
    out=h.fresh(output);out.mkdir(parents=True);rows=[];identity=runtime.identity()
    lines=['# Reviewed Home reference candidates','',
        'Existing approved boxes and focus labels are reused unchanged. These are retrospective still-image candidates, not action-linked transitions.',
        'Pair-role/identity confirmation remains pending. Neighbor overlap prevents clean-context qualification.', '']
    h.require(len({p['id'] for p in request['pairs']})==len(request['pairs']),'duplicate_pair')
    for p in request['pairs']:
        h.identifier(p['id']);frames=[];targets=[]
        for role,state in [('reference','unfocused'),('focused','focused')]:
            spec=p[role];f=truth[spec['imageSHA256']];cs={c['id']:c for c in f['controls']}
            c=cs[spec['controlID']];h.require(c['state']==state,'wrong_reviewed_state')
            frames.append(f);targets.append(c)
        sizes=[h.image(h.ROOT,f['image']) for f in frames]
        h.require(sizes[0]==sizes[1] and frames[0]['screen']==frames[1]['screen'],'candidate_context_mismatch')
        window=transfer.geometry(targets[0]['bounds'],sizes[0])
        overlaps=[intersections(window,f['controls'],c['id']) for f,c in zip(frames,targets)]
        paths=[]
        for i,f in enumerate(frames):
            crop=transfer.crop(dict(id=str(i),path=str(h.checked(h.ROOT,f['image'])),sha256=f['image']['sha256'],
                bounds=native26.common_window(targets[0]['bounds'])),h.ROOT)
            path=out/f"{p['id']}-{i}.png";crop.save(path);paths.append(path)
        rows.append(dict(id=p['id'],frames=[dict(image=f['image'],source=f['source'],target=c) for f,c in zip(frames,targets)],
            referenceWindow=window,neighborOverlaps=overlaps,crops=[h.ref(path) for path in paths],
            cleanContext=not any(overlaps),pairIdentity='agent_proposed_human_pending',
            dataRole='pending_development_diagnostic',actionLinked=False,profileVerification='not_available'))
        lines += [f"## {p['id']}",'',f"Neighbor overlaps (reference / focused): {overlaps}",
            'Unfocused reference crop:',f'![Reference]({paths[0]})','Focused crop:',f'![Focused]({paths[1]})','']
    h.require(identity==runtime.identity(),'crop_runtime_changed')
    result=dict(version='real-reference-review-v1',**h.FLAGS,request=h.ref(request_path),runtime=identity,
        implementation=h.ref(h.ROOT/'scripts/prepare_real_focus_references.py'),pairs=rows,
        eligibleCleanPairs=sum(p['cleanContext'] for p in rows),admittedPairs=0,modelExecuted=False)
    h.write(out/'review.json',result,sealed=True);(out/'review.md').write_text('\n'.join(lines)+'\n')
    print(dict(candidates=len(rows),eligibleCleanPairs=result['eligibleCleanPairs'],admittedPairs=0))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--request',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();prepare(a.request,a.output)
