"""Check original native records without capture, inference, or admission."""
import math
from PIL import Image
import research_queue as q

OUT=None


def scene_record(scene, size):
    q.require(scene['schema_version']==1,'scene_version')
    q.require(scene.get('is_settled') is True and scene.get('isSettled') is True,'unsettled')
    observation=scene['focus_observation'];ident=observation['observedID']
    q.require(ident and observation['verified'] is True,'unverified_focus')
    q.require(scene['focused_element_id']==ident==scene['activeFocusId'],'focus_conflict')
    q.require(observation['generation']==scene['observation_generation'],'observation_generation')
    selected=[e for e in scene['elements'] if e.get('is_focused') is True]
    q.require(len(selected)==1 and selected[0]['id']==ident,'selected_focus')
    body=selected[0]['rendered_body_geometry']
    q.require(body['version']==1 and body['availability']=='measured' and body['role']=='rendered_control_body','body_contract')
    q.require(body['element_id']==ident and body['generation']==scene['observation_generation'],'body_generation')
    q.require(body['coordinate_space']=='image_top_left_pixels','body_coordinates')
    q.require(list(size)==[scene['scene_width'],scene['scene_height']],'image_size')
    x,y,w,h=body['visible_pixel_bounds']
    q.require(all(type(v) in (int,float) and math.isfinite(v) for v in (x,y,w,h)) and
              x>=0 and y>=0 and w>0 and h>0 and x+w<=size[0]+.01 and y+h<=size[1]+.01,'visible_bounds')
    normalized=[x/size[0],y/size[1],(x+w)/size[0],(y+h)/size[1]]
    q.require(len(body['visible_normalized_bounds'])==4 and
              all(abs(a-b)<1e-6 for a,b in zip(normalized,body['visible_normalized_bounds'])),'normalized_body')
    return dict(focus=ident,generation=scene['observation_generation'],run=scene['fixture_run_id'],
                bounds=body['visible_pixel_bounds'],timestamp=scene['timestamp'])


def run():
    cfg=q.load(OUT/'config.json');root=q.local_path(q.ROOT,cfg['root'])
    index=root/'MEMBERS.json';q.require(q.digest(index)==cfg['membersSHA256'],'member_index_changed')
    manifest=q.load(index);q.require(manifest['version']==1,'member_version')
    for relative,pin in manifest['files'].items():
        path=q.local_path(root,relative)
        q.require(path.stat().st_size==pin['bytes'] and q.digest(path)==pin['sha256'],'member_changed')
    audit=q.load(root/'corrected-native-audit.json');q.require(audit['schema_version']==1,'audit_version')
    q.require(len(audit['cases'])==cfg['cases'],'case_count');rows=[];seen=set()
    for case in audit['cases']:
        ident=case['case_id'];q.require(q.ID.fullmatch(ident) and ident not in seen,'case_id');seen.add(ident)
        image=root/'captures'/(ident+'.png')
        q.require(q.digest(image)==case['screenshot']['sha256'],'image_binding')
        recipe=root/'recipes'/(ident+'.json');q.require(q.digest(recipe)==case['recipe']['sha256'],'recipe_binding')
        with Image.open(image) as pixels:
            q.require(pixels.format=='PNG' and pixels.width*pixels.height<=16_000_000,'image_contract')
            size=pixels.size;pixels.load()
        observations=[]
        for side in ('pre','post'):
            path=root/'captures'/(ident+'-'+side+'-scene.json')
            q.require(q.digest(path)==case['native_brackets'][side]['scene']['sha256'],'scene_binding')
            observations.append(scene_record(q.load(path),size))
        pre,post=observations
        q.require(all(pre[k]==post[k] for k in ('focus','generation','run','bounds')) and post['timestamp']>=pre['timestamp'],'bracket_conflict')
        rows.append(dict(id=ident,focus=pre['focus'],bounds=pre['bounds'],imageSize=size,
                         originalSummaryFocused=case['original_summary'].get('focused'),rawFocused=True))
    q.save(OUT/'summary.json',dict(version='native-receipt373-v1',rows=rows,cases=len(rows),
        rawBracketsVerified=len(rows)*2,summaryDisagreements=sum(r['originalSummaryFocused'] is not True for r in rows),
        dataRole='development',trainingAdmitted=False,modelAccepted=False,hcfEvidence=False,
        captureTimeBuildVerified=False,decision='Use the raw native fields for diagnostic intake. Do not infer no focus from the original summary.',
        nextAction='Compare the consumer decoder with these records. Keep capture-time build uncertainty and native model qualification separate.'))
