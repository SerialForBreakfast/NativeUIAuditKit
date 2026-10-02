"""Explicit OS/disposition selection and read-only retirement advice (ADR-0017).

Catalogs and manifests are content sealed. No deletion, migration, OS-version
discovery, training, or change to historical splits is performed.
"""
import argparse
import json
from pathlib import Path

from corpus_retention import digest, new_local, sha256, require

ROOT=Path(__file__).resolve().parents[1]
STATES={'active-training','evaluation-only','historical-reference','retired'}


def seal(doc):
    frozen=json.loads(json.dumps(doc,allow_nan=False))
    return dict(frozen,sha256=digest(frozen))


def unseal(doc,version):
    require(isinstance(doc,dict) and doc.get('version')==version,'unsupported_lifecycle_version')
    require(doc.get('sha256')==digest({k:v for k,v in doc.items() if k!='sha256'}),'changed_lifecycle_document')
    return doc


def root_path(value,mount=None):
    root=Path(value).absolute()
    require(root.resolve()==root and root.is_dir(),'unsafe_or_missing_root')
    if not root.is_relative_to(ROOT):
        require(mount is not None,'external_mount_required')
        mounted=Path(mount).absolute()
        require(mounted.is_mount() and mounted.resolve()==mounted and root.is_relative_to(mounted),
                'external_mount_unavailable')
    return root


def member(root,row):
    name=row.get('path');require(isinstance(name,str) and bool(name),'invalid_path')
    p=Path(name)
    require(not p.is_absolute() and '..' not in p.parts and str(p)==name,'unsafe_path')
    path=root/p
    require(path.resolve()==path and path.is_file(),'missing_or_linked_member')
    require(path.stat().st_size==row.get('bytes') and sha256(path)==row.get('sha256'),'changed_member')
    return path


def catalog_check(catalog,root,verify_bytes=True):
    unseal(catalog,'corpus-lifecycle-catalog-v1')
    rows=catalog['members'];require(isinstance(rows,list) and bool(rows),'empty_catalog')
    require(all(isinstance(r.get('id'),str) and bool(r['id']) for r in rows),'invalid_member_id')
    require(len({r['id'] for r in rows})==len(rows),'duplicate_member_id')
    require(len({r['path'] for r in rows})==len(rows),'duplicate_member_path')
    ids={r['id'] for r in rows};groups={}
    for row in rows:
        require(row['split'] in ('train','evaluation','reference'),'invalid_split')
        require(isinstance(row.get('sourceGroup'),str) and row['sourceGroup'],'missing_source_group')
        prior=groups.setdefault(row['sourceGroup'],row['split'])
        require(prior==row['split'],'cross_split_source_group')
        require(row.get('sourceKind') in ('synthetic','real-device','metadata','derived'),'unknown_source_kind')
        require(type(row.get('humanCorrected')) is bool,'human_correction_status_required')
        for field in ('dependencies','recreationInputs'):
            refs=row.get(field)
            require(isinstance(refs,list) and len(set(refs))==len(refs) and set(refs)<=ids and
                    row['id'] not in refs,'invalid_dependency')
        if verify_bytes:member(root,row)
    return {r['id']:r for r in rows}


def provenance_reasons(row):
    p=row.get('provenance',{});reasons=[]
    keys=['platform','osVersion','runtimeIdentity','annotationVersion','generatorRevision','uiFamily']
    if row['sourceKind']=='synthetic':keys+=['recipeSHA256','seed','assetLicenseIdentity']
    for k in keys:
        if p.get(k) in (None,'','unknown'):reasons.append('missing_provenance:'+k)
    return reasons


def select(catalog,policy,root):
    return _select(catalog,policy,root,True)


def _select(catalog,policy,root,verify_bytes):
    rows=catalog_check(catalog,root,verify_bytes)
    require(policy.get('version')=='corpus-lifecycle-policy-v1','unsupported_policy')
    states=policy['dispositions'];supported=policy['supportedOS']
    require(set(states)==set(rows) and all(s in STATES for s in states.values()),'explicit_dispositions_required')
    require(isinstance(supported,dict) and all(isinstance(v,list) and all(isinstance(x,str) for x in v)
                                            for v in supported.values()),'invalid_os_policy')
    selected=[];excluded=[]
    for ident,row in rows.items():
        state=states[ident];reasons=provenance_reasons(row)
        if state not in ('active-training','evaluation-only'):reasons.append(state)
        elif state=='active-training' and row['split']!='train':reasons.append('cannot_promote_split')
        elif state=='evaluation-only' and row['split']!='evaluation':reasons.append('cannot_change_split')
        p=row.get('provenance',{})
        if p.get('osVersion') not in supported.get(p.get('platform'),[]):reasons.append('unsupported_os')
        if reasons:excluded.append(dict(id=ident,reasons=reasons))
        else:selected.append(dict(row,disposition=state))
    return seal(dict(version='corpus-lifecycle-manifest-v1',catalogSHA256=catalog['sha256'],
        policy=policy,selected=selected,excluded=excluded,originalSplitsPreserved=True))


def replay(manifest,catalog,root):
    unseal(manifest,'corpus-lifecycle-manifest-v1')
    require(manifest['catalogSHA256']==catalog['sha256'],'historical_catalog_changed')
    # Only selected bytes are required for replay; retired files may have been
    # separately removed. Catalog consistency remains checked in full.
    rows=catalog_check(catalog,root,verify_bytes=False)
    expected=_select(catalog,manifest['policy'],root,False)
    require(manifest==expected,'historical_membership_changed')
    for r in manifest['selected']:member(root,rows[r['id']])
    return dict(replayVerified=True,members=len(manifest['selected']),manifestSHA256=manifest['sha256'])


def cleanup_report(catalog,policy,root):
    require(policy.get('version')=='corpus-lifecycle-policy-v1','unsupported_policy')
    rows=catalog_check(catalog,root);states=policy['dispositions']
    require(set(states)==set(rows) and all(s in STATES for s in states.values()),'explicit_dispositions_required')
    protected={i for i,r in rows.items() if states[i]!='retired' or r['sourceKind'] in ('real-device','metadata')
               or r['humanCorrected'] or r['split']=='reference'}
    referenced=set();todo=list(protected)
    while todo:
        ident=todo.pop()
        for dep in rows[ident]['dependencies']+rows[ident]['recreationInputs']:
            if dep not in referenced:referenced.add(dep);todo.append(dep)
    result=[]
    for ident,row in rows.items():
        reasons=[]
        if states[ident]!='retired':reasons.append('not_retired')
        if row['sourceKind']=='real-device':reasons.append('private_real_capture')
        if row['humanCorrected']:reasons.append('human_correction')
        if row['sourceKind']=='metadata' or row['split']=='reference':reasons.append('retained_reference_or_metadata')
        if ident in referenced:reasons.append('retained_dependency')
        rebuild=row['recreationInputs']
        if not rebuild or not set(rebuild)<=protected|referenced:reasons.append('recreation_inputs_not_retained')
        result.append(dict(id=ident,path=row['path'],bytes=row['bytes'],candidate=not reasons,reasons=reasons))
    return seal(dict(version='corpus-lifecycle-cleanup-v1',catalogSHA256=catalog['sha256'],
        rows=result,candidateBytes=sum(r['bytes'] for r in result if r['candidate']),
        deletionAuthorized=False,action='read-only recommendation'))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['select','replay','cleanup'])
    p.add_argument('--catalog',required=True);p.add_argument('--root',required=True);p.add_argument('--mount')
    p.add_argument('--policy');p.add_argument('--manifest');p.add_argument('--output',required=True)
    a=p.parse_args();root=root_path(a.root,a.mount);catalog=json.loads(Path(a.catalog).read_text())
    out=new_local(a.output)
    if a.action=='replay':result=replay(json.loads(Path(a.manifest).read_text()),catalog,root)
    else:
        policy=json.loads(Path(a.policy).read_text())
        result=(select if a.action=='select' else cleanup_report)(catalog,policy,root)
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x') as f:json.dump(result,f,indent=2)
    print(json.dumps(dict(action=a.action,output=str(out))))


if __name__=='__main__':main()
