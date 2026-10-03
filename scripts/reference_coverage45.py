"""Build calibration-only native coverage candidates and call read-only TTR planners."""
import argparse
import copy
import json
import math
import hashlib
import subprocess
from pathlib import Path
import human_annotation_review as h
from harvest_sidecar_v2 import recipe_hash
from reference_benchmark45 import select_frames


def membership(batch):
    frames=select_frames(batch)
    groups={family:[dict(pixelSHA256=f['pixelSHA256'],image=f['image'],aliases=f['aliases'])
                    for f in frames if f['family']==family] for family in sorted({f['family'] for f in frames})}
    return dict(**h.FLAGS,version='reference-membership-options-v1',currentRole='calibration',
        rendererAncestry='fixture_procedural_renderer_v1',familyGroups=groups,
        recommended=dict(role='retain_calibration_challenge',training=[],
                         diagnosticPixels=[f['pixelSHA256'] for f in frames]),
        alternative=dict(role='train_all_after_explicit_assignment',
                         candidateTrainingPixels=[f['pixelSHA256'] for f in frames],
                         independentEvaluation=[],requires='human review, role assignment, fresh held-out families'),
        rationale='Keep pairs, duplicates, seeds and appearance variants together. Both families share a renderer; splitting these 61 images randomly cannot establish independent transfer. Current diagnostics have already informed development.')


def native_manifest(target):
    cases=[]
    for name,count,columns in [('buttons',9,3),('settings_rows',3,1),('tabs',3,3)]:
        for backdrop,rgb in [('dark',0x202020),('light',0xDDDDDD)]:
            canvas=dict(version=2,columns=columns,spacing=40,inset=120,backgroundRGB=rgb,
                        showLabels=True,pairing='competitor_v1',presentation=name,fillViewport=True)
            if name=='tabs':canvas['selectedIndex']=1
            recipe=dict(schema_version=1,archetype='grid_matrix',element_count=count,
                        theme='dark',density='regular',seed=145,step_index=0,
                        appearance=dict(version=1,preset='artwork',layout='standard',canvas=canvas,
                                        focus=dict(version=1,kind='native_button')))
            recipe['recipe_hash']=recipe_hash(recipe)
            # Producer IDs use ceil(sqrt(count)), NOT canvas columns.
            id_cols=min(8,max(2,math.ceil(math.sqrt(count))))
            cases.append(dict(case_id=f'native45-{name}-{backdrop}',recipe=recipe,
                              target_element_ids=[f'grid_cell_{i//id_cols}_{i%id_cols}' for i in range(count)],
                              split_group='validation',priority=0,independence_group='fixture_procedural_renderer_v1'))
    return dict(schema_version=1,campaign_id='0C34D662-758A-4B30-A66A-001045000001',
                title='Native UIButton spatial coverage calibration candidate',target=copy.deepcopy(target),
                stop_on_case_failure=True,budget=dict(max_cases=6,max_targets_per_case=9,
                max_wall_clock_seconds=1800,max_retained_bytes=1073741824,minimum_free_disk_bytes=2147483648),cases=cases)


def check_response(name, response, payload):
    h.require(response.get('success') is True,'planner_failed')
    state=response['data']['campaign']['_0']
    h.require(state['state']=='validated' and state['total_accepted_pairs']==0 and
              all(c['state']=='unattempted' for c in state['cases']),'planner_execution_state')
    if name=='native':
        h.require(state['total_cases']==len(payload['cases']) and
                  {c['case_id'] for c in state['cases']}=={c['case_id'] for c in payload['cases']},'planner_cases')
        expected=hashlib.sha256(json.dumps(payload).encode()).hexdigest()
        h.require(state['input_manifest_sha256']==expected,'planner_exact_input')
    else:
        plan=state['coverage_plan']
        expected=len(payload['layouts'])*len(payload['seeds'])*len(payload['scenarios'])*len(payload['background_groups'])
        h.require(plan['attainable_pairs']==expected and state['total_cases']==expected,'grid_plan_counts')
    return state['total_cases']


def run(output, target, grid_example, helper=None):
    output=h.fresh(output);output.mkdir(parents=True)
    manifest=native_manifest(target);h.write(output/'native-manifest.json',manifest)
    grid=json.loads(Path(grid_example).read_text());grid['target']=copy.deepcopy(target)
    grid['request_id']='0C34D662-758A-4B30-A66A-001045000002'
    h.require(grid['renderer_contract']=='grid-density-v1' and grid['source_role']=='calibration','grid_source')
    h.write(output/'grid-request.json',grid)
    results={}
    if helper:
        # Only plan and validate are available here; never start/capture.
        for name,verb,flag,payload in [('native','validate','--manifest-json',manifest),('grid','plan','--request-json',grid)]:
            proc=subprocess.run([str(helper),'--json','campaign',verb,flag,json.dumps(payload)],
                                text=True,capture_output=True,timeout=60)
            (output/f'{name}-response.json').write_text(proc.stdout)
            (output/f'{name}.stderr').write_text(proc.stderr)
            h.require(proc.returncode==0,'planner_process_failed')
            count=check_response(name,json.loads(proc.stdout),payload)
            results[name]=dict(exitCode=proc.returncode,success=True,cases=count)
    h.write(output/'qualification.json',dict(**h.FLAGS,results=results,
        nativeTargetPairs=sum(len(c['target_element_ids']) for c in manifest['cases']),
        claim='Recipe/planner validation only; proposed positions need measured rendered geometry.',
        gaps=['Rows and tabs are styled UIButton, not native Settings list or UITabBar.',
              'Grid-density compiler targets one interior control per case; does not cover every position.',
              'Fresh capture/export, review and data-use assignment remain separate.']))
    print(results)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True);p.add_argument('--target-from',required=True)
    p.add_argument('--grid-example',required=True);p.add_argument('--helper')
    a=p.parse_args();prior=h.read(h.local(a.target_from))
    target=prior['data']['campaign']['_0']['coverage_plan']['manifest']['target']
    run(h.local(a.output),target,a.grid_example,a.helper)
