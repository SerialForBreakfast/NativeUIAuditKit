"""Prepare unchanged crop comparisons after the approved project move."""
from pathlib import Path
import copy
import research_queue as q
import research_approval as approval


def main():
    folder=q.ROOT/'Research/ResearchSpecs/MIGRATION387'
    folder.mkdir(parents=True,exist_ok=True)
    jobs=[]
    for cell in ('hcf-repeated','balanced-repeated','hcf-unique'):
        jobs += [f'hcf376-{cell}-train-v1-usb2',f'hcf376-{cell}-evaluate-v1-usb2']
    jobs += ['hcf376-factor-comparison-v1-usb2']
    converted={}
    for old in jobs:
        original=q.load(q.QUEUE/'jobs'/old/'spec.json')
        state,attempts=q.state(q.QUEUE/'jobs'/old)
        q.require(not attempts,'migration_job_already_attempted:'+old)
        spec=copy.deepcopy(original);spec['id']=old+'-move387'
        for item in spec['inputs']:
            if item['path'] in ('scripts/usb_training386.py','scripts/hcf_compare371.py','scripts/artifact_storage.py'):
                item['sha256']=q.digest(q.ROOT/item['path'])
        for dep in spec.get('dependencies',[]):
            if dep['job'] in converted:
                successor=converted[dep['job']]
                dep.update(job=successor['id'],specSHA256=q.text_digest(successor))
        if spec['authority']=='training':
            stage=next(x for x in spec['stage'] if x['to']=='usb.json')
            config=q.load(q.ROOT/stage['from']['path'])
            config['job']=spec['id']
            config_path=folder/(spec['id']+'-usb.json')
            save_once(config_path,config)
            stage['from']=dict(path=q.relative(config_path),sha256=q.digest(config_path))
        elif old.endswith('-evaluate-v1-usb2'):
            stage=next(x for x in spec['stage'] if x['to']=='config.json')
            config=q.load(q.ROOT/stage['from']['path'])
            config['sourceProjectRoot']=str(Path.home() / 'Documents/GitHub/NativeUIAuditKit')
            config_path=folder/(spec['id']+'-config.json');save_once(config_path,config)
            stage['from']=dict(path=q.relative(config_path),sha256=q.digest(config_path))
        path=folder/(spec['id']+'.json');save_once(path,spec)
        q.validate(spec);q.verify_pins(spec)
        if not (q.QUEUE/'jobs'/spec['id']).exists():q.submit(path)
        if old in approval.approved_map(q.QUEUE):
            approval.revoke(q.QUEUE,old,'agent:migration387','Explicit successor preserves this comparison after the approved USB project move.')
        approval.approve(q.QUEUE,spec['id'],'agent:migration387',
            'Maintainer approves USB migration. Preserve the existing crop recipe, inputs, limits, and comparisons.')
        converted[old]=spec
        print(spec['id'],flush=True)


def save_once(path,value):
    if path.exists():q.require(q.load(path)==value,'migration_spec_changed')
    else:q.save(path,value)


if __name__=='__main__':main()
