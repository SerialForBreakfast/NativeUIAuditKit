import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from focus_dataset_contract import ROOT
import focus_offline_diagnosis as o
import focus_matched_trial as trial
from focus_duplicate_sensitivity import sensitivity
from harvest_sidecar_v2 import recipe_hash
from harvest_artwork import artwork_identity
from test_ttr_competitor import competitor_meta
from test_ttr_sidecar_v2 import write_bundle, reindex

PROPOSAL=ROOT/'reports/work/FOCUS-OFFLINE-PREP-03/producer-proposal.json'


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.root=Path(tempfile.mkdtemp(dir=ROOT/'.build/debug-output',prefix='offline-prep-'))

    def tearDown(self): shutil.rmtree(self.root)

    def test_vectors_and_rejections(self):
        doc,density=trial.proposal(PROPOSAL,o.ref(PROPOSAL)['sha256'])
        self.assertEqual((len(doc['cases']),sum(r['competitorMatched'] for r in density)),(8,8))
        for kind in ('hash','role','duplicate','flag'):
            changed=copy.deepcopy(doc)
            if kind=='hash': changed['cases'][0]['recipe']['seed']+=1
            if kind=='role': changed['cases'][0]['split']='held-out'
            if kind=='duplicate': changed['cases'][1]=changed['cases'][0]
            if kind=='flag': changed['cases'][0]['common_target_pairs'][0]['density_comparison_competitor_matched']=False
            path=self.root/(kind+'.json');path.write_text(json.dumps(changed))
            with self.assertRaises(ValueError):trial.proposal(path,o.ref(path)['sha256'])
        with self.assertRaises(ValueError):trial.proposal(PROPOSAL,'0'*64)

    def test_optional_field_semantics(self):
        recipe=copy.deepcopy(o.read(PROPOSAL)['cases'][0]['recipe'])
        recipe['appearance'].pop('family_id');recipe.pop('recipe_hash')
        c=recipe['appearance']['canvas']
        for invalid in (0,1,'false',[]):
            c['fillViewport']=invalid
            with self.assertRaises(ValueError):recipe_hash(recipe)
        c['fillViewport']=False;c['version']=1
        with self.assertRaises(ValueError):recipe_hash(recipe)
        c.pop('fillViewport');old=recipe_hash(recipe);c['fillViewport']=None
        self.assertEqual(old,recipe_hash(recipe))
        art=recipe['appearance']['artwork'];old=artwork_identity(art,o.require)
        art['palette']=None;self.assertEqual(old,artwork_identity(art,o.require))
        art['palette']='bright';self.assertNotEqual(old,artwork_identity(art,o.require))
        art['palette']='dark'
        with self.assertRaises(ValueError):artwork_identity(art,o.require)

    def test_duplicate_scores_and_labels(self):
        rows=[dict(id=str(i),label=0,pixelSHA256='same',family='test',theme='dark',control='collectionItem',hard=False) for i in range(2)]
        pred=[dict(id=str(i),probability=.9) for i in range(2)]
        result=sensitivity(rows,pred)
        self.assertEqual(result['official']['groups']['overall']['fp'],2)
        self.assertEqual(result['unique']['groups']['overall']['fp'],1)
        pred[1]['probability']=.8
        with self.assertRaisesRegex(ValueError,'score_conflict'):sensitivity(rows,pred)
        pred[1]['probability']=.9;rows[1]['label']=1
        with self.assertRaisesRegex(ValueError,'label_conflict'):sensitivity(rows,pred)
        pred[1]['probability']=float('nan')
        with self.assertRaises(ValueError):sensitivity(rows,pred)

    def source_case(self, case_number=0):
        case=o.read(PROPOSAL)['cases'][case_number];ids=case['all_target_ids']
        bundle=self.root/('bundle' if case_number==0 else f'bundle{case_number}');base=competitor_meta(write_bundle(bundle));rows=[]
        for i,target in enumerate(ids):
            m=copy.deepcopy(base);comp=ids[(i+1)%len(ids)]
            def walk(v):
                if isinstance(v,dict):
                    if 'focus_observation' in v:
                        focus=target if v['focused_element_id']=='e' else comp
                        v['recipe']=copy.deepcopy(case['recipe']);v['focused_element_id']=focus
                        v['elements']=[]
                        for j,name in enumerate(ids):
                            x=2+(j%4)*15;y=4+(j//4)*14
                            v['elements'].append(dict(element_id=name,taxonomy_class='collectionItem',is_focused=name==focus,
                                pixel_bounds=[x,y,12,12],normalized_bounds=[x/64,y/48,(x+12)/64,(y+12)/48],
                                artwork_geometry=dict(version=1,source=trial.geometry.ROLE,
                                    presentation_bounds_status=trial.geometry.STATUS,
                                    pixel_bounds=[x+1,y+1,10,10],normalized_bounds=[(x+1)/64,(y+1)/48,(x+11)/64,(y+11)/48])))
                        v['focus_observation'].update(requestedID=focus,observedID=focus,plannedFocusIDs=ids)
                        v['observation_diagnostics'].update(requestedID=focus,observedID=focus,requiredIDs=ids,measuredIDs=ids)
                    for child in v.values():walk(child)
                elif isinstance(v,list):
                    for child in v:walk(child)
            walk(m);m.update(id=f'p{i}',competitor_element_id=comp)
            (bundle/f'm{i}.json').write_text(json.dumps(m))
            row=dict(id=f'p{i}',path='f.png',sha256=o.ref(bundle/'f.png')['sha256'],expectedFocus=target,
                box=[2+(i%4)*15,4+(i//4)*14,12,12],split='calibration',
                metadata=dict(unfocusedPath='u.png',focusedPath='f.png',metadataPath=f'm{i}.json'))
            rows.append(row)
        for name in ('manifest','calibration'):(bundle/(name+'.json')).write_text(json.dumps(rows))
        (bundle/'m.json').unlink()  # Owned fixture prototype; only m0..m3 belong to the bundle.
        (bundle/'harvest-receipt.json').write_text(json.dumps(dict(schemaVersion=1,outcome='completed',acceptedRowCount=len(ids))))
        reindex(bundle)
        spec=dict(version='focus-trial-delivery-v1',cases=[dict(caseID=case['case_id'],index=o.ref(bundle/'dataset-index.json'),receipt=o.ref(bundle/'harvest-receipt.json'))])
        path=self.root/f'delivery{case_number}.json';path.write_text(json.dumps(spec));return path,spec

    def test_all_64_pair_integration(self):
        cases=[]
        for i in range(8):cases.extend(self.source_case(i)[1]['cases'])
        path=self.root/'all.json';path.write_text(json.dumps(dict(version='focus-trial-delivery-v1',cases=cases)))
        result=trial.run(PROPOSAL,o.ref(PROPOSAL)['sha256'],path,self.root/'all-output')
        self.assertTrue(result['allCasesPrepared'],result)
        self.assertEqual(sum(len(c['targets']) for c in result['cases']),64)
        self.assertEqual(sum(r['commonTarget'] for c in result['cases'] for r in c['targets']),32)
        for c in result['cases']:
            for counts in c['geometryCounts'].values():self.assertEqual(counts,dict(rendered=2*c['pairCount'],blocked=0,failed=0))

    def test_actual_cli_intake_crops_sheets_and_partial_accounting(self):
        delivery,spec=self.source_case();before={p:o.ref(p) for p in (self.root/'bundle').iterdir()}
        command=[sys.executable,str(ROOT/'scripts/focus_matched_trial.py'),'--proposal',str(PROPOSAL),
            '--proposal-sha256',o.ref(PROPOSAL)['sha256'],'--delivery',str(delivery),'--output',str(self.root/'out')]
        r=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},timeout=180)
        self.assertEqual(r.returncode,2,r.stderr)
        report=o.read(self.root/'out/review.json')
        self.assertEqual(report['caseCounts'],{'prepared_for_review':1,'missing_delivery':7},report)
        self.assertEqual(len(list((self.root/'out/case-01').glob('*.png'))),4)
        self.assertTrue(all(o.ref(p)==v for p,v in before.items()))
        self.assertFalse(report['trainingAdmission'])
        spec['cases'][0]['index']['sha256']='0'*64;delivery.write_text(json.dumps(spec))
        r=trial.run(PROPOSAL,o.ref(PROPOSAL)['sha256'],delivery,self.root/'bad')
        self.assertEqual(r['caseCounts'],{'failed':1,'missing_delivery':7})
        self.assertIn('changed_hash',r['cases'][0]['error'])


if __name__=='__main__':unittest.main()
