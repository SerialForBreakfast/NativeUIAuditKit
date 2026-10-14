"""Validate saved HCF proposals through the existing review importer."""
import argparse
import time
from collections import Counter
import accessibility_review as a
import human_annotation_review as h


def run(root):
    root=h.local(root)
    manifest=h.read(root/'manifest.json')
    h.require(manifest.get('schema_version')==1 and manifest.get('kind')=='hcf_review_feedback',
              'unsupported_hcf_inventory')
    h.require(manifest.get('role')=='development_review_only_not_training_admitted','hcf_data_role')
    frames=manifest['frames'];by={f['frame']:f for f in frames}
    h.require(len(by)==len(frames),'duplicate_frame_id')
    for frame in frames:
        path=h.local(root/frame['file'])
        h.require(path.is_relative_to(root),'frame_path_escape')
        h.require(h.sha(path)==frame['sha256'],'changed_hcf_image')
        with a.Image.open(path) as im:
            h.require(im.format=='PNG' and im.size==(frame['width'],frame['height']),'hcf_dimensions')
            im.verify()
    rows=[]
    for pair in manifest['pairs']:
        side=h.local(root/'analysis'/(pair['id']+'.json'))
        h.require(side.is_relative_to(root),'sidecar_path_escape')
        for role in ('before','after'):
            frame=by[pair[role]]
            result=a.perception(dict(perceptionReport=h.ref(side),perceptionFrameRole=role,
                                     perceptionImage=h.ref(root/frame['file'])))
            rules=result['focusRules']
            rows.append(dict(frame=frame['frame'],profile=frame['profile'],
                analysisProfile=result['profile'],sha256=frame['sha256'],sidecar=h.ref(side),
                state=rules['state'],geometryRoles=[c['geometryRole'] for c in rules['candidates']],
                settingsEvidence=result['settingsEvidence'],navigationEligible=False))
    return dict(version='hcf-review-audit-v1',manifest=h.ref(root/'manifest.json'),
        images=len(frames),uniqueImages=len({f['sha256'] for f in frames}),
        ancestry=manifest['ancestry'],dataRole=manifest['role'],rows=rows,
        states=dict(Counter(r['state'] for r in rows)),
        analysisProfileDiffersFromCapture=sum(r['profile']=='Default' for r in rows),
        inferenceExecuted=False,independentAccuracy=None,noFocusSpecificity=None,
        ordinaryBodyIoU=None,decision='retain_optional_rules_no_separate_model_yet')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();start=time.monotonic();result=run(args.input)
    result['elapsedSeconds']=time.monotonic()-start
    h.write(h.local(args.output),result)
    print({k:result[k] for k in ('images','uniqueImages','states','elapsedSeconds')})
