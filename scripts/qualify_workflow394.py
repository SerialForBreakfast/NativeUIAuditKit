"""Check real workflow outputs and isolated DVC failures. Never accept a model."""
import argparse
import copy
import json
from pathlib import Path
import shutil
import subprocess

import research_queue as q
import experiment_templates as templates
import workflow394 as workflow


def qualify(root):
    queue = root/'queue-v2'
    comparisons = []
    for index in range(3):
        normal = queue/f'jobs/workflow394-q{index}-report/attempts/1/out/report.json'
        alternative = queue/f'jobs/workflow394-d{index}/attempts/1/out/pipeline/report/report.json'
        q.require(q.load(normal) == q.load(alternative), 'arm_outputs_differ')
        timing = q.load(alternative.parents[2]/'dvc-result.json')
        comparisons.append(dict(repetition=index, identical=True, reportSHA256=q.digest(normal), timing=timing))

    folder = root/'failure-tests'
    folder.mkdir(exist_ok=False)
    original = q.load(queue/'jobs/workflow394-d0/spec.json')['templateConfig']
    manifest = copy.deepcopy(q.load(templates.checked(original['manifest'])))
    for index,row in enumerate(manifest['rows']):
        target=folder/f'image-{index}.png'
        shutil.copyfile(templates.checked(row['image']),target)
        row['image']=templates.pin(target)
    q.save(folder/'membership.json',manifest)
    config=dict(original,manifest=templates.pin(folder/'membership.json'))
    workflow.dvc_pipeline(config,folder)
    workspace=folder/'pipeline'
    dvc=str(q.ROOT/'.venv-workflow394/bin/dvc')
    env=workflow.environment(folder)
    outcomes=[]

    def invoke(name,expected,arguments=('repro',)):
        result=subprocess.run([dvc,*arguments],cwd=workspace,env=env,capture_output=True,text=True,timeout=180)
        q.save(folder/(name+'.json'),dict(returnCode=result.returncode,stdout=result.stdout[-8000:],stderr=result.stderr[-8000:]))
        q.require((result.returncode==0)==expected,'unexpected_test_outcome:'+name)
        outcomes.append(dict(test=name,expectedSuccess=expected,matched=True,modelAccepted=False))
        return result

    image=templates.checked(manifest['rows'][0]['image'])
    saved=image.read_bytes()
    image.rename(folder/'hidden-image.png')
    try: invoke('missing-input',False)
    finally: (folder/'hidden-image.png').rename(image)

    # Mutate a test copy only. The declared input hash remains unchanged.
    with image.open('ab') as stream: stream.write(b'test mutation')
    try:
        result=invoke('changed-input',False)
        q.require('input_changed' in result.stderr,'changed_input_not_named')
    finally:
        with image.open('wb') as stream: stream.write(saved)

    invoke('restored-input',True)
    prepared=workspace/'prepare/tensors.npy'
    before=(q.digest(prepared),prepared.stat().st_mtime_ns)
    # Remove only downstream test outputs. DVC must recover them without changing preparation.
    (workspace/'score/predictions.json').unlink()
    (workspace/'report/report.json').unlink()
    invoke('downstream-recovery',True)
    q.require(before==(q.digest(prepared),prepared.stat().st_mtime_ns),'recovery_changed_preparation')
    invoke('duplicate-repro',True)

    bad=folder/'invalid-model.pt'
    bad.write_bytes(b'Invalid model for a deliberate scoring failure.')
    badconfig=dict(config,model=templates.pin(bad))
    badfolder=folder/'bad-score'; badfolder.mkdir()
    try: workflow.dvc_pipeline(badconfig,badfolder)
    except ValueError as error:
        q.require(str(error)=='dvc_command_failed:first-run','unexpected_failure')
    else: raise ValueError('invalid_model_succeeded')
    q.require(not (badfolder/'pipeline/report/report.json').exists(),'failed_score_created_report')
    outcomes.append(dict(test='invalid-model',expectedSuccess=False,matched=True,modelAccepted=False))
    result=dict(version=1,comparisons=comparisons,failureTests=outcomes,modelAccepted=False,
        limits=['This tests recovery of missing downstream outputs, not a killed training process.',
                'The small known-box sample does not measure deployment accuracy.'])
    q.save(root/'qualification.json',result)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root',type=Path)
    args=parser.parse_args()
    print(json.dumps(qualify(args.root.absolute()),indent=2))
