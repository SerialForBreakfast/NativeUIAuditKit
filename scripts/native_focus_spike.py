"""Native26 serial campaign plan, verified receipt and observed-body intake.

Capture is explicit. Importing/planning never controls a target. No automatic retries,
deletion, training, model downloads or annotation overrides.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import time
import uuid

from fixture_composition import resolve
from fixture_rendered_body import validate as body_validate
from harvest_bundle_validation import validate_bundle
from harvest_sidecar_v2 import recipe_hash

ROOT = Path(__file__).resolve().parents[1]
USB = Path('/Volumes/training-drive/data/NUIAK/NATIVE-FOCUS-EFFECT-SPIKE-26')
EVIDENCE = Path('/Users/josephmccraw/Library/Containers/com.showblender.TVTestRig/Data/.tvtr/Evidence')
VERSION = 'native-focus-spike-26-v1'
TERMINAL={'completed','completed_with_failures','failed','cancelled','budget_exhausted',
          'budget_exceeded','stopped'}


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''):
            h.update(b)
    return h.hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as f:
        json.dump(value, f, indent=2, allow_nan=False)


def mounted():
    require(Path('/Volumes/training-drive').is_mount(), 'external_volume_not_mounted')
    require(USB.is_dir() and USB.resolve() == USB, 'external_root_missing_or_symlink')


def plan(base, helper, output):
    """Freeze 1,250 pairs, with complete layout families separated before capture."""
    require(not output.exists(), 'plan_exists')
    base = json.loads(Path(base).read_text())
    chunks = []
    members = []
    for group in range(10):
        role = 'train' if group < 8 else 'evaluation'
        axis = 'row' if role == 'train' else 'column'
        width = 220 + (group % 4)*30 if axis == 'row' else 260 + (group-8)*40
        height = 260 + (group//4)*30 if axis == 'row' else 240
        for block in range(5):
            manifest = copy.deepcopy(base)
            manifest['campaign_id'] = str(uuid.uuid4())
            manifest['title'] = f'Native26 {role} group {group} block {block}'
            manifest['budget'] = dict(max_cases=25, max_targets_per_case=1,
                max_wall_clock_seconds=600, max_retained_bytes=1073741824,
                minimum_free_disk_bytes=10737418240)
            manifest['cases'] = []
            for j in range(block*25, (block+1)*25):
                case = copy.deepcopy(base['cases'][0])
                seed = 2600000 + group*10000 + j*10
                case_id = f'n26-g{group:02d}-v{j:03d}'
                recipe = case['recipe']; recipe['seed'] = seed
                c = recipe['appearance']['composition']
                recipe['appearance'].pop('family_id', None)
                c['definitions']['target'].update(width=width, height=height)
                region = c['regions'][0]
                region.update(axis=axis, gap=90 if axis == 'row' else 60,
                    frame=[180, 180+group*28, 1560, 580] if axis == 'row'
                    else [450+(group-8)*500, 70, 600, 940])
                light = j % 2 == 1
                colors = [0xd0d0d0, 0xf0f0f0] if light else [0x070b10, 0x202731]
                c['background'].update(colors=colors, direction=('horizontal','vertical','diagonal')[j%3])
                target = j % 3
                for k in range(3):
                    content = c['contents'][f'item-{k}']
                    content.update(seed=seed+k, title=f'Artwork {seed+k}')
                    content.pop('design', None)
                    content['preset'] = 'artwork' if k == target else 'bright_unfocused'
                    if k == target:
                        content['design'] = ('city','orbit','collage')[(j//3)%3] if role == 'train' else 'checkerboard'
                _, suffix = resolve(c, recipe, require)
                recipe['appearance']['family_id'] = 'appearance-v1.artwork.standard.' + suffix
                recipe['recipe_hash'] = recipe_hash(recipe)
                case.update(case_id=case_id, priority=j-block*25,
                    target_element_ids=[f'item-{target}'])
                manifest['cases'].append(case)
                members.append(dict(caseID=case_id, role=role, configurationGroup=group,
                    layoutFamily=axis, artworkFamily=c['contents'][f'item-{target}']['design'],
                    target=f'item-{target}', seed=seed, background='light' if light else 'dark',
                    recipeSHA256=recipe['recipe_hash']))
            chunks.append(manifest)
    require(len(members)==1250 and len({r['recipeSHA256'] for r in members})==1250,
            'planned_membership')
    doc = dict(version=VERSION, helper=str(helper), helperSHA256=sha(helper),
        members=members, chunks=chunks, expected=dict(train=1000,evaluation=250),
        evaluationScope='withheld vertical configuration and artwork family; shared native renderer',
        sourceRole='calibration', consumerRoleAuthority='maintainer-approved Native26 experiment')
    write(output, doc)
    return doc


def call(helper, args, output):
    start = time.monotonic()
    result = subprocess.run([str(helper),'--json',*args], capture_output=True, text=True, timeout=45)
    write(output, dict(seconds=time.monotonic()-start, returncode=result.returncode,
        reply=json.loads(result.stdout), stderr=result.stderr))
    reply = json.loads(result.stdout)
    require(result.returncode==0 and reply.get('success') is True, 'ttr_command_failed:'+str(output))
    return next(iter(reply['data'].values()))['_0']


def receive(source, dest, receipt):
    mounted()
    source = Path(source)
    require(source.parent==EVIDENCE and source.name.startswith('nuiak-native26-') and
            source.resolve()==source, 'unsupported_export_source')
    require(dest.parent==USB and not dest.exists(), 'unsafe_or_existing_destination')
    files=[]
    for p in sorted(source.rglob('*')):
        mode=p.lstat().st_mode
        require(not p.is_symlink() and (stat.S_ISREG(mode) or stat.S_ISDIR(mode)), 'export_special_file')
        if p.is_file(): files.append(p)
    size=sum(p.stat().st_size for p in files)
    require(0<len(files)<=4096 and size<=2*1024**3, 'export_size_limit')
    require(shutil.disk_usage(USB).free>size+10*1024**3, 'usb_capacity')
    rows=[]; start=time.monotonic();dest.mkdir()
    for p in files:
        rel=p.relative_to(source); q=dest/rel; q.parent.mkdir(parents=True,exist_ok=True)
        digest=sha(p)
        with p.open('rb') as src, q.open('xb') as out: shutil.copyfileobj(src,out,1024*1024)
        require(sha(q)==digest and sha(p)==digest, 'transfer_hash_mismatch')
        rows.append(dict(path=str(rel),bytes=q.stat().st_size,sha256=digest))
    result=dict(source=str(source),destination=str(dest),files=rows,bytes=size,
        seconds=time.monotonic()-start,verified=True,sourcePreserved=True)
    write(receipt,result)
    return result


def inspect(bundle, member):
    """Reuse full byte/bracket validation; derive labels only from observed scenes."""
    from PIL import Image
    contract=validate_bundle(bundle)
    require(contract['acceptedRowCount']==1 and len(contract['usableRows'])==1,'pair_count')
    row=contract['usableRows'][0]
    require(recipe_hash(row['recipe'])==member['recipeSHA256'],'recipe_membership')
    binding=row['observationBinding']; target=member['target']; frames=[]
    for scene_key,path_key,hash_key,label in (
        ('baselineScene','unfocusedPath','unfocusedSHA256',0),
        ('focusedScene','focusedPath','focusedSHA256',1)):
        scene=binding[scene_key]; p=bundle/row[path_key]
        require(len(scene['elements'])==3 and
            {e['element_id'] for e in scene['elements']}=={'item-0','item-1','item-2'},
            'native_control_membership')
        with Image.open(p) as im: im.load();size=list(im.size)
        boxes={}
        for element in scene['elements']:
            eid=element['element_id']
            bounds=body_validate(element.get('rendered_body_geometry'),size,eid,scene['observation_generation'])
            require(bounds is not None,'unmeasured_body')
            boxes[eid]=bounds
        item=next(e for e in scene['elements'] if e['element_id']==target)
        require(item['is_focused'] is bool(label) and scene['is_settled'] is True,'observed_focus')
        require(sum(e['is_focused'] for e in scene['elements'])==1,'ambiguous_focus')
        frames.append(dict(path=str(p),sha256=row[hash_key],label=label,bounds=boxes[target],
            allBounds=boxes,size=size,generation=scene['observation_generation']))
    require(frames[0]['size']==frames[1]['size'],'viewport_changed')
    return dict(**member,frames=frames,sourceRole=row['split'],
        growth=[frames[1]['bounds'][i]/frames[0]['bounds'][i] for i in (2,3)],
        observedPairValid=True)


def common_window(before):
    """Virtual box gives 20% context through makeCrop's fixed 16% expansion."""
    x,y,w,h=before
    factor=1.40/1.32
    return [x-(factor-1)*w/2,y-(factor-1)*h/2,w*factor,h*factor]


def overlap(a,b):
    return max(0,min(a[0]+a[2],b[0]+b[2])-max(a[0],b[0]))*max(
        0,min(a[1]+a[3],b[1]+b[3])-max(a[1],b[1]))


def render(rows, output):
    import base64
    import io
    from PIL import Image
    import focus_runtime as native
    mounted();require(output.parent==USB and not output.exists(),'crop_output_collision')
    output.mkdir();items=[];record={};exceptions=[];started=time.monotonic()
    for row in rows:
        anchor=common_window(row['frames'][0]['bounds'])
        x,y,w,h=anchor; actual=[x-.16*w,y-.16*h,w*1.32,h*1.32]
        for frame in row['frames']:
            W,H=frame['size']; reasons=[]
            if actual[0]<0 or actual[1]<0 or actual[0]+actual[2]>W or actual[1]+actual[3]>H:
                reasons.append('context_clipped')
            if any(overlap(actual,b)>0 for eid,b in frame['allBounds'].items() if eid!=row['target']):
                reasons.append('neighbor_body_in_context')
            if reasons:exceptions.append(dict(caseID=row['caseID'],label=frame['label'],reasons=reasons))
            for arm,bounds in [('normalized',frame['bounds']),('common',anchor)]:
                require(bounds[0]>=0 and bounds[1]>=0 and bounds[0]+bounds[2]<=W and
                        bounds[1]+bounds[3]<=H,'virtual_crop_outside_image')
                sid=f"{row['caseID']}-{frame['label']}-{arm}"
                items.append(dict(id=sid,path=frame['path'],sha256=frame['sha256'],bounds=bounds))
                record[sid]=dict(caseID=row['caseID'],role=row['role'],label=frame['label'],
                    arm=arm,sourceSHA256=frame['sha256'],bounds=bounds,reasons=reasons,
                    background=row['background'],configurationGroup=row['configurationGroup'])
    for batch in native.bounded_batches(items):
        reply=native.invoke(batch,image_root=USB)
        for r in reply['results']:
            raw=base64.b64decode(r['png'],validate=True)
            with Image.open(io.BytesIO(raw)) as im:
                im.load();require(im.size==(256,256),'crop_shape')
            p=output/(r['id']+'.png')
            with p.open('xb') as f:f.write(raw)
            record[r['id']].update(path=str(p),sha256=sha(p),cropMilliseconds=r['cropMilliseconds'])
    result=dict(version=VERSION,runtime=native.identity(),records=record,
        exceptions=exceptions,seconds=time.monotonic()-started)
    write(output/'crops.json',result)
    return result


def capture(doc, output, limit, reconcile_active=False):
    mounted();helper=Path(doc['helper'])
    require(sha(helper)==doc['helperSHA256'],'helper_changed')
    require(doc['version']==VERSION,'plan_version')
    members={r['caseID']:r for r in doc['members']}
    for index,manifest in enumerate(doc['chunks'][:limit]):
        folder=output/f'chunk-{index:03d}'
        if (folder/'accepted.json').exists():
            accepted=json.loads((folder/'accepted.json').read_text())
            require(accepted['campaignID']==manifest['campaign_id'],'resume_campaign_mismatch')
            for receipt_name in accepted.get('receipts',['receipt.json']):
                receipt=json.loads((folder/receipt_name).read_text())
                for item in receipt['files']:
                    require(sha(Path(receipt['destination'])/item['path'])==item['sha256'],'changed_received_file')
            continue
        start=time.monotonic()
        existing=folder.exists()
        require(not existing or reconcile_active,'incomplete_chunk_reconcile_before_resume')
        require(shutil.disk_usage(ROOT).free>manifest['budget']['minimum_free_disk_bytes']+1024**3,
                'internal_staging_reserve')
        token=str(uuid.uuid4())[:8]
        if existing:
            require((folder/'start.json').is_file(),'missing_start_receipt')
            status=call(helper,['campaign','status',manifest['campaign_id']],folder/f'reconcile-{token}.json')
        else:
            folder.mkdir(parents=True)
            payload=json.dumps(manifest,separators=(',',':'))
            call(helper,['campaign','validate','--manifest-json',payload],folder/'validate.json')
            status=call(helper,['campaign','start','--manifest-json',payload],folder/'start.json')
        poll=0
        while status['state'] not in TERMINAL:
            require(time.monotonic()-start<660,'campaign_poll_deadline_reconcile_required')
            time.sleep(5);poll+=1
            status=call(helper,['campaign','status',manifest['campaign_id']],folder/f'poll-{token}-{poll:03d}.json')
        require(status['total_accepted_pairs']==25 and status['total_rejected_pairs']==0 and
                status['completed_cases']==25,'campaign_incomplete')
        source=EVIDENCE/f"nuiak-native26-{manifest['campaign_id']}"
        call(helper,['campaign','export',manifest['campaign_id'],'--output-dir',str(source)],folder/'export.json')
        dest=USB/f"corpus-{manifest['campaign_id']}"
        receipt=receive(source,dest,folder/'receipt.json')
        validation_start=time.monotonic(); rows=[]
        for case in manifest['cases']:
            rows.append(inspect(dest/'splits'/case['split_group']/case['case_id'],members[case['case_id']]))
        write(folder/'accepted.json',dict(campaignID=manifest['campaign_id'],rows=rows,
            totalSeconds=time.monotonic()-start,validationSeconds=time.monotonic()-validation_start,
            captureSeconds=status['elapsed_seconds'],transferSeconds=receipt['seconds']))
        print(json.dumps(dict(chunk=index,pairs=25,totalPairs=(index+1)*25,
            seconds=time.monotonic()-start,internalFreeGiB=shutil.disk_usage(ROOT).free/1024**3)),flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='action',required=True)
    a=s.add_parser('plan');a.add_argument('--base',required=True);a.add_argument('--helper',required=True)
    a.add_argument('--output',required=True)
    a=s.add_parser('capture');a.add_argument('--plan',required=True);a.add_argument('--output',required=True)
    a.add_argument('--chunks',type=int,default=50)
    a.add_argument('--reconcile-active',action='store_true',help='Read an existing active/completed campaign; never retries failed cases')
    a=s.add_parser('render');a.add_argument('--accepted',required=True);a.add_argument('--name',required=True)
    args=p.parse_args()
    if args.action=='render':
        require(Path(args.name).name==args.name and args.name not in ('.','..'),'crop_name')
        rows=json.loads(Path(args.accepted).read_text())['rows']
        result=render(rows,USB/args.name)
        print(json.dumps(dict(crops=len(result['records']),exceptions=len(result['exceptions']),seconds=result['seconds'])))
        return
    out=Path(args.output).resolve();require(out.is_relative_to(ROOT),'metadata_outside_project')
    if args.action=='plan':
        doc=plan(args.base,Path(args.helper),out);print(json.dumps(doc['expected']))
    else:
        require(1<=args.chunks<=50,'chunk_limit')
        capture(json.loads(Path(args.plan).read_text()),out,args.chunks,args.reconcile_active)


if __name__=='__main__': main()
