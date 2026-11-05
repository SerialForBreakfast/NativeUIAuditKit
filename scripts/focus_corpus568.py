"""Prepare source-verified native focus crops with the production Swift helper."""
import base64
import hashlib
from collections import Counter
from pathlib import Path
from PIL import Image
import research_queue as q
from template_inputs398 import checked,pin
from focus_dataset_contract import digest,pixel_digest
OUT=None


def replay_members(protocol):
    content=dict(protocol);seal=content.pop('protocolSHA256',None)
    q.require(seal==digest(content),'replay_protocol_seal')
    selected=[r for r in protocol['samples'] if r['role']=='train']
    protected=[r for r in protocol['samples'] if r['role']!='train']
    q.require(len(selected)==96 and len(protected)==16 and len(protocol['replay'])==56,'replay_membership')
    q.require(not {r['group'] for r in selected} & {r['group'] for r in protected},'reserved_group_overlap')
    legacy_manifest=checked(protocol['replayManifest']);pairs={r['pair_id']:r for r in q.load(legacy_manifest)['pairs']}
    for row in protocol['replay']:
        pair=pairs.get(row['pairID']);q.require(pair and pair['split']=='train','legacy_replay_role')
        name='focused_crop' if row['label']==1 else 'unfocused_crop'
        q.require((legacy_manifest.parent/pair[name]).resolve()==checked(row['crop']),'legacy_replay_identity')
    rows=[]
    for source,records in (('native-replay',selected),('legacy-replay',protocol['replay'])):
        for row in records:
            path=checked(row['crop'])
            with Image.open(path) as im:
                q.require(im.size==(256,256),'replay_crop_size')
                q.require(pixel_digest(q.ROOT,row['crop'])==row['pixelSHA256'],'replay_pixels')
            rows.append(dict(id=source+'-'+row['id'],image=row['crop'],label=row['label'],group=row.get('group',row.get('pairID',row['id'])),source=source,role='train'))
    q.require(Counter(r['label'] for r in rows)=={0:76,1:76},'replay_class_support')
    return rows


def validate_native(row,metadata,root):
    from harvest_sidecar_v2 import validate
    from fixture_rendered_body import validate as body
    paths={role:root/row['metadata'][role+'Path'] for role in ('focused','unfocused')}
    hashes={role:q.digest(path) for role,path in paths.items()}
    q.require(hashes['focused']==row['sha256'],'native_manifest_image')
    with Image.open(paths['focused']) as image:size=image.size
    validate(metadata,row,size,hashes)
    result=[]
    for role,scene,label in [('focused',metadata['focused_scene'],1),('unfocused',metadata['baseline_scene'],0)]:
        target=next(e for e in scene['elements'] if e['element_id']==row['expectedFocus'])
        bounds=body(target.get('rendered_body_geometry'),size,row['expectedFocus'],scene['focus_observation']['generation'])
        q.require(bounds is not None,'native_body_unavailable')
        result.append(dict(id=row['id']+'-'+role,image=pin(paths[role]),bounds=bounds,label=label,
            group=row['metadata']['recipeHash'],source='focus556-native',metadata=pin(root/row['metadata']['metadataPath'])))
    return result


def assert_isolation(rows,protected):
    labels={};roles={}
    for row in rows:
        key=row['pixelSHA256']
        q.require(key not in protected,'protected_crop_overlap')
        q.require(labels.setdefault(key,row['label'])==row['label'],'contradictory_crop_labels')
        q.require(roles.setdefault(key,row['role'])==row['role'],'cross_partition_crop')


def quarantine_native(replay,native,protected):
    labels={}
    for row in replay+native:labels.setdefault(row['pixelSHA256'],set()).add(row['label'])
    bad={r['id'].rsplit('-',1)[0] for r in native if len(labels[r['pixelSHA256']])>1 or r['pixelSHA256'] in protected}
    excluded=[dict(id=r['id'],reason='protected_or_contradictory_pixels',image=r['image'],label=r['label']) for r in native if r['id'].rsplit('-',1)[0] in bad]
    return [r for r in native if r['id'].rsplit('-',1)[0] not in bad],excluded


def partitions(rows):
    # Connect recipe groups through duplicate crop pixels before assigning partitions.
    parent={r['group']:r['group'] for r in rows}
    def find(key):
        while parent[key]!=key:
            parent[key]=parent[parent[key]];key=parent[key]
        return key
    pixels={}
    for row in rows:
        group=row['group'];prior=pixels.setdefault(row['pixelSHA256'],group)
        a,b=find(group),find(prior)
        if a!=b:parent[max(a,b)]=min(a,b)
    components=sorted({find(r['group']) for r in rows})
    q.require(len(components)>=2,'insufficient_validation_components')
    validation=set(components[:max(1,round(len(components)*.2))])
    for row in rows:
        row['splitGroup']=find(row['group'])
        row['role']='validation' if row['splitGroup'] in validation else 'train'
    return rows


def prepare():
    import focus_runtime as runtime
    spec=q.load(OUT.parents[2]/'spec.json');request=q.load(checked(spec['inputs'][0]))
    q.require(request['version']=='native-focus-corpus568-v1','corpus_request')
    q.require(runtime.identity()==request['runtime'],'production_runtime_changed')
    source=checked(request['manifest']);root=source.parent
    receipt=q.load(checked(request['approval']))
    q.require(receipt['manifestSHA256']==request['manifest']['sha256'] and receipt['dataRole']=='focus-training','native_training_authority')
    protocol=q.load(checked(request['replayProtocol']));replay=replay_members(protocol)
    protected=set()
    for ref in request['protectedImages']:
        checked(ref);protected.add(pixel_digest(q.ROOT,ref))
    for row in replay:row['pixelSHA256']=pixel_digest(q.ROOT,row['image'])
    raw=[]
    for row in q.load(source):raw.extend(validate_native(row,q.load(root/row['metadata']['metadataPath']),root))
    q.require(len(raw)==184 and len({r['id'] for r in raw})==184,'native_membership')
    (OUT/'crops').mkdir()
    lookup={r['id']:r for r in raw};cropped=[]
    items=[dict(id=r['id'],path=str(checked(r['image'])),sha256=r['image']['sha256'],bounds=r['bounds']) for r in raw]
    for part in runtime.bounded_batches(items):
        reply=runtime.invoke(part)
        for produced in reply['results']:
            row=dict(lookup[produced['id']]);path=OUT/'crops'/(row['id']+'.png')
            path.write_bytes(base64.b64decode(produced['png'],validate=True))
            with Image.open(path) as image:q.require(image.size==(256,256),'native_crop_size')
            row['frame']=row.pop('image');row['image']=pin(path);row['pixelSHA256']=pixel_digest(q.ROOT,row['image'])
            cropped.append(row)
    # Source images stay separate from protected real-app and evaluation frames.
    protected_files={r['sha256'] for r in request['protectedImages']}
    q.require(not protected_files & {r['image']['sha256'] for r in raw},'protected_frame_overlap')
    for row in replay:row['role']='train'
    assert_isolation(replay,protected)
    cropped,excluded=quarantine_native(replay,cropped,protected)
    cropped=partitions(cropped)
    rows=replay+cropped;assert_isolation(rows,protected)
    q.require(not {r['group'] for r in rows if r['role']=='train'} & {r['group'] for r in rows if r['role']=='validation'},'corpus_group_leak')
    result=dict(version='native-focus-corpus568-v1',rows=rows,runtime=request['runtime'],sourceManifest=request['manifest'],
        replayProtocol=request['replayProtocol'],referenceScope='approved-native-training',trainingAdmitted=True,
        reservedReplayExcluded=16,quarantined=excluded,originalNativePairs=92,roles=dict(Counter(r['role'] for r in rows)),metricsStatus='provisional',modelAccepted=False)
    q.save(OUT/'corpus.json',result)
    q.save(OUT/'benchmark_summary.json',dict(nativePairs=len(cropped)//2,originalNativePairs=92,quarantinedPairs=len(excluded)//2,replayCrops=len(replay),reservedExcluded=16,
        roles=result['roles'],protectedImages=len(request['protectedImages']),productionCrops=True,metricsStatus='provisional',modelAccepted=False))
    receipt_files(['corpus.json','benchmark_summary.json'])


def receipt_files(names):
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path=n,sha256=q.digest(OUT/n)) for n in names]))
