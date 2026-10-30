"""Qualify complete native RTLMirror rows without changing historical annotations."""
import hashlib
from pathlib import Path
from PIL import Image
import research_queue as q
from experiment_templates import checked, pin
from detector_native_inputs import bounds


def controls(side, width, height, names):
    expected = dict(navigationBar='navigationBar', textField_0='textField', primaryButton_0='primaryButton')
    expected.update({f'label_row_{i}':'label' for i in range(4)})
    expected.update({f'listRow_{i}':'listRow' for i in range(4)})
    for i in range(2):
        expected.update({f'label_toggle_{i}':'label', f'listRow_toggle_{i}':'listRow', f'toggle_{i}':'toggle'})
    elements = side['elements']
    q.require(len(elements) == len(expected) and {e['id']:e['elementType'] for e in elements} == expected,
              'row545_annotation_coverage')
    result = []
    for e in elements:
        q.require(not e.get('excluded') and not e.get('knownIssues') and not e.get('occluded'), 'row545_uncertain_label')
        q.require(e['elementType'] in names, 'row545_class')
        b = e['boundsPixels']
        result.append(dict(id=e['id'], **{'class':e['elementType']},
                           bounds=bounds([b[k] for k in ('x','y','width','height')],width,height)))
    by = {r['id']:r['bounds'] for r in result}
    def contains(a,b):
        return a[0]<=b[0] and a[1]<=b[1] and a[0]+a[2]>=b[0]+b[2] and a[1]+a[3]>=b[1]+b[3]
    for i in range(4):
        row,label=by[f'listRow_{i}'],by[f'label_row_{i}']
        q.require(row != label and contains(row,label), 'row545_row_contains_label')
    footer=by['primaryButton_0']
    for key,b in by.items():
        if key.startswith(('listRow','label_','toggle_','textField')):
            overlap=min(b[0]+b[2],footer[0]+footer[2])>max(b[0],footer[0]) and min(b[1]+b[3],footer[1]+footer[3])>max(b[1],footer[1])
            q.require(not overlap,'row545_footer_occlusion')
    return result


def prepare(sources, exclusion, names, role, reserved_groups=()):
    q.require(role in ('training','development'),'row545_role')
    inv=q.load(checked(exclusion))
    q.require(inv.get('integrityPassed') and not inv.get('errors'),'row545_exclusion_integrity')
    reserved=set(reserved_groups)|{r['family']+':'+str(r['seed']) for r in inv['members']}
    pixels={r['pixelSHA256'] for r in inv['members']}; encoded={r['imageSHA256'] for r in inv['members']}
    rows=[];seen=set();lineage=[]
    for source in sources:
        mp=checked(source['manifest']);sp=checked(source['summary']);doc=q.load(mp);summary=q.load(sp)
        q.require(doc['version']=='ios-native-capture-manifest-v1' and summary['sourcesMatchBuild'],'row545_source')
        q.require(not summary['bodyChecks']['failingFamilies'],'row545_body_gate')
        recipe=q.load(checked(doc['recipe']))
        q.require(recipe['families']==['RTLMirror'] and recipe['roles']=={'RTLMirror':role},'row545_recipe_role')
        q.require(len(doc['rows'])==recipe['maxFrames'] and summary['frames']==len(doc['rows']),'row545_frame_count')
        for r in doc['rows']:
            q.require(r['family']=='RTLMirror' and r['device']=='iPhone 17 Pro' and r['role']==role,'row545_frame_role')
            q.require(r['status']=='eligible' and not r['reasons'] and not r['rejectedLabels'] and r['appearanceVerified']=='paired-rendered','row545_frame_rejected')
            q.require(r['group'] not in reserved,'row545_reserved_group')
            paths={k:q.local_path(mp.parent,r[k]['path']) for k in ('image','sidecar')}
            q.require(all(q.digest(paths[k])==r[k]['sha256'] for k in paths),'row545_payload_changed')
            side=q.load(paths['sidecar']);q.require(side['imageSHA256']==r['image']['sha256'],'row545_image_binding')
            with Image.open(paths['image']) as im:
                w,h=im.size;pixel=hashlib.sha256(str(im.size).encode()+im.convert('RGBA').tobytes()).hexdigest()
            q.require(pixel not in pixels and r['image']['sha256'] not in encoded,'row545_reserved_pixels')
            q.require(pixel not in seen,'row545_duplicate_pixels');seen.add(pixel)
            cc=controls(side,w,h,names)
            q.require(len(cc)==r['labels'],'row545_label_count')
            rows.append(dict(id=r['id'],group=r['group'],role='train' if role=='training' else 'development',
                trainingEligible=role=='training',labelsComplete=True,image=pin(paths['image']),width=w,height=h,controls=cc))
            lineage.append(dict(id=r['id'],manifest=source['manifest'],sidecar=pin(paths['sidecar']),originalRole=role,decodedPixelSHA256=pixel))
    q.require(rows and len({r['id'] for r in rows})==len(rows),'row545_identity')
    return dict(version='detector-training-membership-v2',trainingAdmitted=role=='training',
        calibrationPolicy='none-fixed-last-training-diagnostics',names=names,rows=rows,lineage=lineage,
        exclusion=exclusion,modelAccepted=False,limitation='Native generated source labels, restricted Pro layout. Not independent real-app accuracy.')


def validate_partitions(training, development):
    """Reject related groups or duplicate pixels across training and development."""
    q.require(training['trainingAdmitted'] and not development['trainingAdmitted'], 'row545_partition_roles')
    q.require(all(r['role']=='train' for r in training['rows']) and
              all(r['role']=='development' for r in development['rows']), 'row545_partition_roles')
    groups = [{r['group'] for r in doc['rows']} for doc in (training,development)]
    encoded = [{r['image']['sha256'] for r in doc['rows']} for doc in (training,development)]
    decoded = []
    for doc in (training,development):
        rows = {r['id'] for r in doc['rows']}
        lineage = {r['id']:r['decodedPixelSHA256'] for r in doc['lineage']}
        q.require(rows == set(lineage), 'row545_partition_lineage')
        decoded.append(set(lineage.values()))
    q.require(not groups[0] & groups[1], 'row545_partition_groups')
    q.require(not encoded[0] & encoded[1] and not decoded[0] & decoded[1], 'row545_partition_pixels')
    return dict(trainingFrames=len(training['rows']),developmentFrames=len(development['rows']),
                trainingGroups=len(groups[0]),developmentGroups=len(groups[1]),overlap=False)
