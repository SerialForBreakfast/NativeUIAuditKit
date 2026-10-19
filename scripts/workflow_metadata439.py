"""Read bounded graph metadata. No worker imports or execution authority."""
import copy
import hashlib
import json
import math
import re


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()


def enrich(snapshot, queue):
    result=copy.deepcopy(snapshot)
    jobs=result.get('jobs',[])
    if not isinstance(jobs,list) or len(jobs)>10000:raise ValueError('metadata_job_limit')
    histories={};keys={}
    for row in jobs:
        try:
            ident=row['job']
            if not isinstance(ident,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}',ident):raise ValueError('metadata_identity')
            path=queue/'jobs'/ident/'spec.json'
            if path.is_symlink() or path.resolve()!=path.absolute() or path.stat().st_size>1_000_000:raise ValueError('metadata_path')
            spec=json.loads(path.read_text())
            if spec['id']!=ident or digest(spec)!=row.get('specSHA256'):raise ValueError('metadata_spec_changed')
            for key in ('owner','conditions','nextActionByOutcome'):
                row[key]=spec.get(key, [] if key=='conditions' else None)
            row['metadataVerified']=True
            template=spec.get('template',{})
            # Exact execution and input identities only. No estimates from budget ceilings.
            key=digest(dict(adapter=spec.get('adapter'),inputs=spec.get('inputs'),template=template,
                            training=spec.get('training'),capture=spec.get('capture'),stage=spec.get('stage'),
                            dependencies=spec.get('dependencies')))
            keys[ident]=key
            seconds=row.get('wallSeconds')
            if row.get('state')=='complete' and isinstance(seconds,(int,float)) and not isinstance(seconds,bool) and math.isfinite(seconds) and seconds>0:
                histories.setdefault(key,[]).append((ident,seconds))
        except (OSError,ValueError,KeyError,TypeError):
            row['metadataVerified']=False
            row['metadataIssue']='Specification unavailable or different from this snapshot.'
    for row in jobs:
        samples=[seconds for ident,seconds in histories.get(keys.get(row.get('job')),[]) if ident!=row.get('job')]
        row['workflowDuration']=dict(low=min(samples),high=max(samples),samples=len(samples),
                                    basis='completed records with identical execution and inputs') if samples else None
    return result
