"""Prepare same-recipe state comparisons from approved retained frames."""
import argparse
from collections import defaultdict
from itertools import combinations
from pathlib import Path
import transition270 as base

OUT=base.ROOT/'reports/work/TRANSITION-290/matched-states.json'


def make_pairs(states):
    groups=defaultdict(list)
    for state in states:
        base.require(state['role']=='train' and state['settled'] is True,'state_role_or_focus')
        groups[(state['recipeHash'],state['runID'],state['group'])].append(state)
    rows=[]
    for key,group in sorted(groups.items()):
        ordered=sorted(group,key=lambda s:s['image']['sha256'])
        base.require(len({s['focusID'] for s in ordered})==len(ordered),'duplicate_focus_state')
        for first,second in combinations(ordered,2):
            rows.append(dict(group=key[2],role='train',changed=1,
                images=[first['image'],second['image']],metadata=[first['metadata'],second['metadata']],
                focusIDs=[first['focusID'],second['focusID']],recipeHash=key[0],runID=key[1],
                condition='focus_only_state_comparison'))
        for state in ordered:
            rows.append(dict(group=key[2],role='train',changed=0,
                images=[state['image'],state['image']],metadata=[state['metadata'],state['metadata']],
                focusIDs=[state['focusID'],state['focusID']],recipeHash=key[0],runID=key[1],
                condition='identity_control'))
    for row in rows:
        row['id']='290:'+base.sha(('|'.join(r['sha256'] for r in row['images'])).encode())
    base.require(len({r['id'] for r in rows})==len(rows),'duplicate_pair')
    return rows


def run():
    base.require(not OUT.exists(),'output_collision')
    prior=base.read(base.ROOT/'reports/work/TRANSITION-266/preflight.json')
    replacement=base.read(base.checked(prior['replacements']))
    admission=base.read(base.checked(prior['admission']))
    base.require(admission['approved'] and admission['role']=='development-training'
                 and admission['protectedEndpointOverlap'] is False,'parent_admission')
    base.checked(admission['intake'])
    states={};verified={}
    def checked(reference):
        key=(reference['path'],reference['sha256'])
        if key not in verified:verified[key]=base.checked(reference)
        return verified[key]
    for row in replacement['rows']:
        for image,metadata in zip(row['images'],row['metadata']):
            checked(image);doc=base.read(checked(metadata))
            scenes=[doc[scene] for prefix,scene in [('unfocused','baseline_scene'),('focused','focused_scene')]
                    if doc[prefix+'_sha256']==image['sha256']]
            base.require(bool(scenes),'observed_frame')
            scene=scenes[0]
            state=dict(image=image,metadata=metadata,focusID=scene['focused_element_id'],
                recipeHash=doc['recipe']['recipe_hash'],runID=scene['fixture_run_id'],
                group=row['group'],role=row['role'],settled=scene['is_settled'])
            base.require(state['focusID'] and doc['is_settled'],'observed_focus')
            old=states.get(image['sha256'])
            base.require(old is None or all(old[k]==state[k] for k in state if k!='metadata'),'conflicting_state')
            if old is None:states[image['sha256']]=state
    rows=make_pairs(list(states.values()))
    base.require(len(states)==32 and len(rows)==80 and sum(r['changed'] for r in rows)==48,'expected_membership')
    base.write(OUT,dict(version='matched-states290-v1',rows=rows,states=list(states.values()),
        parentAdmission=prior['admission'],parentReplacements=prior['replacements'],runner=base.ref(Path(__file__)),
        role='development-training-derived',independentEvaluation=False,
        pairing='Same-recipe retained states. Not a recorded remote action or continuous transition.',
        currentCandidateUsesThesePairs=False,
        limitations=['Identity controls do not cover animated backgrounds.',
                     'Frame sorting does not establish action order.',
                     'The 80 pairs use only 32 frames from 2 related training families.',
                     'Keep all parent groups and derivatives outside final evaluation.']))
    print('Prepared 48 focus-only state comparisons and 32 identity controls from 32 existing frames.',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true',required=True)
    parser.parse_args();run()
