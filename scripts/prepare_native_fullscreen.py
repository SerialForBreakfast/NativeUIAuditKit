"""Read-only native26 corpus validation and project-local full-screen draft export.

Preserves producer calibration and consumer train/evaluation roles. No admission,
model imports, image copies, external writes or model execution.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import time

from PIL import Image
import human_annotation_review as h
import native_focus_spike as n
from harvest_bundle_validation import validate_bundle
from fixture_rendered_body import validate as body_validate
from harvest_sidecar_v2 import recipe_hash

BASE=h.ROOT/'reports/work/NATIVE-FOCUS-EFFECT-SPIKE-26'


def annotate(scene,size):
    h.require(scene.get('is_settled') is True,'unsettled_scene')
    elements=scene['elements']
    h.require(len(elements)==3 and {e['element_id'] for e in elements}=={'item-0','item-1','item-2'},'incomplete_native_membership')
    h.require(all(type(e.get('is_focused')) is bool for e in elements),'unknown_focus')
    h.require(sum(e['is_focused'] for e in elements)==1,'nonunique_focus')
    controls=[]
    for e in elements:
        h.require(e.get('is_hidden') is False,'hidden_control')
        b=body_validate(e.get('rendered_body_geometry'),size,e['element_id'],scene['observation_generation'])
        h.require(b is not None,'unmeasured_body')
        controls.append(dict(id=e['element_id'],bounds=b,state='focused' if e['is_focused'] else 'unfocused'))
    return controls


def check_group(groups,group,role):
    h.require(role in ('train','evaluation'),'invalid_source_role')
    h.require(groups.setdefault(str(group),role)==role,'cross_split_configuration')


def run(output):
    n.mounted();out=h.fresh(output);out.mkdir(parents=True)
    planpath=BASE/'plan-storage-v2.json';plan=h.read(planpath);members={r['caseID']:r for r in plan['members']}
    h.require(len(members)==1250,'unexpected_plan_membership')
    receipts=[];accepted=[]
    for chunk in range(50):
        p=BASE/f'batch/chunk-{chunk:03d}/accepted.json';doc=h.read(p);accepted+=doc['rows'];receipts.append(h.ref(p))
    h.require(len(accepted)==1250 and {r['caseID'] for r in accepted}==set(members),'incomplete_accepted_membership')
    h.write(out/'protocol.json',dict(version='native-fullscreen-preparation-v1',**h.FLAGS,
        plan=h.ref(planpath),accepted=receipts,sources=[h.ref(Path(__file__)),h.ref(h.ROOT/'scripts/harvest_bundle_validation.py'),
        h.ref(h.ROOT/'scripts/fixture_rendered_body.py')],imageRoot=str(n.USB),expectedFrames=2500))
    started=time.monotonic();frames=[];groups={};pixels={};bytes_total=0
    for index,a in enumerate(accepted):
        m=members[a['caseID']];h.require(all(a[k]==v for k,v in m.items()),'changed_frozen_membership')
        check_group(groups,m['configurationGroup'],m['role'])
        bundle=Path(a['frames'][0]['path']).parent
        h.require(bundle.resolve()==bundle and bundle.is_relative_to(n.USB),'unsafe_bundle')
        contract=validate_bundle(bundle)
        h.require(contract['acceptedRowCount']==1 and len(contract['usableRows'])==1,'invalid_pair_count')
        row=contract['usableRows'][0]
        h.require(recipe_hash(row['recipe'])==m['recipeSHA256'] and row['split']==a['sourceRole']==plan['sourceRole'],'changed_recipe_or_source_role')
        metadata=bundle/'synth-0_metadata.json';metadata_ref=dict(path=str(metadata),sha256=n.sha(metadata))
        for ordinal,(scene_key,path_key,hash_key) in enumerate((('baselineScene','unfocusedPath','unfocusedSHA256'),('focusedScene','focusedPath','focusedSHA256'))):
            source=bundle/row[path_key];old=a['frames'][ordinal]
            h.require(str(source)==old['path'] and row[hash_key]==old['sha256'],'changed_frame_binding')
            with Image.open(source) as im:
                im.load();size=list(im.size);pixel=hashlib.sha256(str(im.size).encode()+b'\0'+im.convert('RGB').tobytes()).hexdigest()
            h.require(size==old['size'],'changed_dimensions')
            controls=annotate(row['observationBinding'][scene_key],size)
            h.require({c['id']:c['bounds'] for c in controls}==old['allBounds'],'changed_body_geometry')
            target=next(c for c in controls if c['id']==m['target'])
            h.require((target['state']=='focused')==bool(ordinal),'changed_target_state')
            h.require(pixels.setdefault(pixel,m['role'])==m['role'],'cross_split_pixels')
            image_ref=dict(path=str(source),sha256=row[hash_key]);frame_id=f"{m['caseID']}-{ordinal}"
            annotation=dict(version='fullscreen-focus-annotation-v1',image=image_ref,completeFocus=True,
                completenessBasis='validated three-control native26 recipe and observed scene',profile='ordinary',controls=controls,
                sourceMetadata=metadata_ref,observationGeneration=old['generation'])
            annpath=out/'annotations'/f'{frame_id}.json';annpath.parent.mkdir(exist_ok=True);h.write(annpath,annotation)
            frames.append(dict(id=frame_id,split=m['role'],group=f"native26-configuration-{m['configurationGroup']}",
                image=image_ref,annotation=h.ref(annpath),pixelSHA256=pixel,recipeSHA256=m['recipeSHA256'],
                targetID=m['target'],sourceRole=a['sourceRole']))
            bytes_total+=source.stat().st_size
        if (index+1)%125==0:print(f'Validated {index+1}/1250 pairs',flush=True)
    # The prior target-crop admission is evidence, not a new full-screen approval.
    result=dict(version='native-fullscreen-draft-v1',**h.FLAGS,frames=frames,
        counts=dict(frames=len(frames),controls=3*len(frames),focused=len(frames),
                    splits=dict(Counter(f['split'] for f in frames)),groups=len(groups)),
        originalImageBytes=bytes_total,validationSeconds=time.monotonic()-started,duplicateFrames=len(frames)-len(pixels),
        dataIntegrityPassed=True,trainingReady=False,
        blockers=['Exact full-screen membership needs its own admission binding; existing execution admitted nominated target crops.',
                  'Runner v1 accepts project-local images and train/development only; these originals are USB and retain evaluation role.',
                  'Copy-staging all originals exceeds the 2GiB experiment output envelope; use an explicitly scoped read-through loader or revised storage budget.'],
        suggestedExecution='Keep all source roles. Implement USB read-through and terminal-only evaluation; compare focused-body prediction on original full scenes.')
    h.write(out/'draft.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='frames'},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();run(a.output)
