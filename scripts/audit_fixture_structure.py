"""Verify a delivered structural source checkpoint, never admit its planned corpus."""
import argparse
from collections import Counter
import hashlib
import itertools
from pathlib import Path

import human_annotation_review as h
from fixture_composition import resolve
from harvest_sidecar_v2 import require, recipe_hash


def member(root, name):
    require(isinstance(name,str) and name and not Path(name).is_absolute() and
            all(p not in ('..','.') for p in name.split('/')),'checkpoint_member_path')
    path=root/name
    require(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(root.resolve()),'checkpoint_member_file')
    require(path.stat().st_size<=4*1024*1024,'checkpoint_member_size')
    return path


def audit(root):
    root=h.local(root)
    manifest=h.read(root/'manifest.json')
    require(type(manifest.get('schema_version')) is int and manifest['schema_version']==1,'checkpoint_version')
    members=manifest.get('members')
    require(isinstance(members,dict) and 0<len(members)<=256,'checkpoint_members')
    for name,record in members.items():
        p=member(root,name)
        require(isinstance(record,dict) and type(record.get('bytes')) is int and
                p.stat().st_size==record['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==record.get('sha256'),
                'checkpoint_member_integrity:'+name)
    def read(name):
        require(name in members,'checkpoint_unmanifested_input:'+name)
        return h.read(member(root,name))
    matrix=read('recipes/matrix.json'); transitions=read('transitions.json')
    require(matrix.get('version')==1 and transitions.get('version')==1,'checkpoint_matrix_version')
    appearances=matrix.get('appearance_pairs'); pairs=transitions.get('pairs')
    require(isinstance(appearances,list) and len(appearances)==48 and isinstance(pairs,list) and len(pairs)==16,'checkpoint_matrix_count')
    families=('composite_card','ranked_row','home_icon','hero')
    conditions=('boundary_unchanged','content_only','scroll_unchanged','scroll_moved')
    require({(p['family'],p['artwork_luminance'],p['background'],p['position']) for p in appearances}==
            set(itertools.product(families,('dark','light'),('dark','light'),range(3))),'checkpoint_appearance_coverage')
    require({(p['condition'],p['background'],p['seed']) for p in pairs}==
            set(itertools.product(conditions,('dark','light'),(71,83))),'checkpoint_transition_coverage')
    rows=[]; identities=set(); treatments=Counter()
    for lane,entries in [('appearance',appearances),('transition',pairs)]:
        for entry in entries:
            require(isinstance(entry.get('id'),str) and entry['id'] not in identities,'checkpoint_duplicate_id')
            identities.add(entry['id'])
            name='recipes/'+entry['recipe']; r=read(name)
            require(members[name]['sha256']==entry['sha256' if lane=='appearance' else 'recipe_sha256'],'checkpoint_recipe_integrity')
            items,digest=resolve(r['appearance']['composition'],r,require)
            controls={i['id']:i for i in items if i['focusable']}
            target=entry['target' if lane=='appearance' else 'initial_focus']
            require(target in controls,'checkpoint_target')
            if lane=='appearance':
                require(entry.get('competitor') in controls and entry['competitor']!=target and
                        controls[target]['kind']==entry['family'],'checkpoint_family_competitor')
                treatments[controls[target]['style']['focus']['kind']]+=1
            else:
                require(entry['expected_focus_relation'] in ('same','different'),'checkpoint_transition_intent')
            rows.append(dict(id=entry['id'],lane=lane,recipe=entry['recipe'],recipeHash=recipe_hash(r),
                             compositionDigest=digest,targetKind=controls[target]['kind']))
    return dict(version=1,manifest=h.ref(root/'manifest.json'),verifiedMembers=len(members),
                appearanceRecipes=len(appearances),transitionRecipes=len(pairs),
                families=list(families),appearanceFocusTreatments=dict(treatments),recipes=rows,
                softwareRecipeCompatibility=True,liveQualified=False,trainingEligible=False,
                capturedPairs=0,sourceReportedCapturedPairs=manifest.get('new_captured_pairs'),
                caveats=['Plan membership is not captured data or measured luminance.',
                         'Transition expected relation is intent, not an observed label.',
                         'Swift canonical digest parity awaits producer vectors.',
                         'Whole-body geometry and clipped scroll membership await four live family proofs.'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkpoint',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args()
    try:
        result=audit(args.checkpoint)
        h.write(h.fresh(args.output),result)
        print({k:v for k,v in result.items() if k not in ('recipes','manifest')})
        return 0
    except (ValueError,KeyError,TypeError,OSError) as error:
        print(str(error));return 2


if __name__=='__main__':raise SystemExit(main())
