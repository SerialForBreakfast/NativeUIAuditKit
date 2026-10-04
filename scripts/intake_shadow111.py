"""Region12 retained evidence audit and immutable full-journey replay request.

No capture or automatic training admission. Existing model execution is separate.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
from PIL import Image
from shadow_feedback_contract import require


def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def read(path):
    require(path.stat().st_size<16_000_000,'metadata_bound')
    def unique(pairs):
        d={}
        for k,v in pairs:require(k not in d,'duplicate_json_key');d[k]=v
        return d
    def bad(_):raise ValueError('nonfinite_json')
    return json.loads(path.read_bytes(),object_pairs_hook=unique,parse_constant=bad)


def member(root,name):
    require(type(name) is str and '\\' not in name,'member_name')
    p=PurePosixPath(name)
    require(not p.is_absolute() and p.parts and '..' not in p.parts,'member_path')
    path=root/name
    require(not any(v.is_symlink() for v in (path,*path.parents)) and path.resolve().is_relative_to(root.resolve()),'member_link')
    return path


def audit(root):
    root=root.resolve();manifest=read(root/'manifest.json');survey=read(root/'survey.json')
    require(manifest['schema_version']==1 and survey['schema_version']==1,'version')
    require(manifest['role']=='diagnostic_unassigned' and manifest['training_admission'] is False and
            manifest['split_group']=='tvos-settings-native-layout-family','source_role')
    names=set();count=0
    for item in manifest['files']:
        name=item['path'];require(name.casefold() not in names,'duplicate_member');names.add(name.casefold())
        p=member(root,name)
        require(p.is_file() and p.stat().st_size==item['bytes'] and sha(p)==item['sha256'],'member_integrity')
        count+=1
    actual={p.relative_to(root).as_posix().casefold() for p in root.rglob('*') if p.is_file()}
    require(actual==names|{'manifest.json'},'unlisted_members')
    rows=survey['records'];transitions=survey['transitions'];operation=manifest['operation_id']
    require(len(rows)==manifest['frames'] and len(transitions)==manifest['intervals'],'membership_counts')
    records={};image_hashes=set()
    for r in rows:
        seq=r['sequence'];require(type(seq) is int and seq not in records,'sequence')
        require(r['operation_id']==operation and r['clock_domain']=='runner_monotonic','identity_clock')
        require(r['native_bracket_agrees'] is True and r['pixel_stable'] is True,'unsettled')
        require(r['capture_started_monotonic_ns']<=r['capture_completed_monotonic_ns'],'capture_clock')
        path=member(root,r['image']);require(r['image'].casefold() in names and sha(path)==r['image_sha256'],'image_binding')
        with Image.open(path) as im:
            require(im.format=='PNG' and im.size==(r['image_width'],r['image_height']) and im.width*im.height<=20_000_000,'image_dimensions')
            im.load()
        require(r['native_evidence']['screenID']=='Settings>General>Region','screen_scope')
        records[seq]=r;image_hashes.add(r['image_sha256'])
    require(set(records)==set(range(1,len(rows)+1)) and len(transitions)==len(rows)-1,'journey_coverage')
    pairs=[];hints=[];seen=set()
    for t in transitions:
        b=records[t['from_sequence']];a=records[t['to_sequence']];key=(b['sequence'],a['sequence'])
        require(key not in seen and a['sequence']==b['sequence']+1,'transition_sequence');seen.add(key)
        require(t['single_input_association'] is True and len(t['input'])==1 and t['pixel_stable'] is True,'input_association')
        action=t['input'][0]
        require(type(action['input_index']) is int and action['input_index']==b['sequence'] and
                len(t['endpoints'])==2,'action_membership')
        require(action['clock_domain']=='runner_monotonic' and b['capture_completed_monotonic_ns']<=action['invoked_monotonic_ns']
            <=action['returned_monotonic_ns']<=a['capture_started_monotonic_ns'],'action_clock')
        for endpoint,record in zip(t['endpoints'],(b,a)):
            require(endpoint=={k:record['native_evidence'][k] for k in ('screenID','focusedRowLabel')},'native_endpoint')
        relation=b['native_evidence']['focusedRowLabel']!=a['native_evidence']['focusedRowLabel']
        require(type(t['focus_changed']) is bool and t['focus_changed']==relation,'native_relation')
        identity=f"{operation}:{b['sequence']}:{a['sequence']}"
        pair=dict(id=identity,actionID=f"{operation}:{action['input_index']}",
            beforeObservationID=f"{operation}:{b['sequence']}",afterObservationID=f"{operation}:{a['sequence']}",
            before=dict(path=str(member(root,b['image'])),sha256=b['image_sha256']),
            after=dict(path=str(member(root,a['image'])),sha256=a['image_sha256']))
        pairs.append(pair);hints.append(dict(id=identity,native_focus_changed=relation,source='native_identity_hint_not_visual_truth'))
    old=read(root/'feedback/transition/predictions.json');by_id={p['id']:p for p in pairs}
    require(old['modelID']=='focus-transition-experimental-dtm025-change-v1' and old['failed']==0,'peer_model')
    old_ids=set()
    for p in old['results']:
        require(p['id'] not in old_ids and p['id'] in by_id,'peer_membership');old_ids.add(p['id']);expected=by_id[p['id']]
        for k in ('actionID','beforeObservationID','afterObservationID'):require(p[k]==expected[k],'peer_identity')
        require(p['beforeSHA256']==expected['before']['sha256'] and p['afterSHA256']==expected['after']['sha256'],'peer_image_binding')
    return dict(schemaVersion=1,mode='score',root=str(root),pairs=pairs),dict(
        manifest_sha256=sha(root/'manifest.json'),verified_files=count+1,frames=len(rows),unique_png_hashes=len(image_hashes),
        intervals=len(pairs),peer_predictions_bound=len(old_ids),hints=hints,training_admitted=False,
        independent_evaluation=False,geometry='native_proposals_not_rendered_body',profile='persisted_not_render_verified')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();request,report=audit(args.root)
    output=args.output.resolve();output.relative_to(Path(__file__).resolve().parents[1]);output.mkdir(parents=True,exist_ok=False)
    for name,value in [('request.json',request),('audit.json',report)]:
        (output/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='hints'},indent=2))
