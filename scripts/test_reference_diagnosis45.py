import os
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import human_annotation_review as h
from diagnose_reference45 import associations
from reference_coverage45 import native_manifest, membership, check_response
from reference_benchmark45 import prepare_environment
from harvest_sidecar_v2 import recipe_hash


class DiagnosisTests(unittest.TestCase):
    def controls(self):
        return [dict(id='f',bounds=[0,0,10,20],state='focused'),dict(id='u',bounds=[20,0,10,20],state='unfocused')]

    def test_partial_body_candidate_does_not_hide_wrong_ranking(self):
        r=associations(self.controls(),[dict(box=[1,1,9,9],score=.2),dict(box=[21,1,29,9],score=.8)])
        self.assertTrue(r['anyContainedFocus']);self.assertTrue(r['unfocusedOutranksFocus'])
        self.assertFalse(r['focusAboveOperating'])

    def test_ambiguous_overlap_and_crossing_candidates_excluded(self):
        c=self.controls();c.append(dict(id='overlay',bounds=[0,0,10,20],state='unfocused'))
        r=associations(c,[dict(box=[1,1,9,9],score=.9),dict(box=[0,0,30,20],score=.8)])
        self.assertFalse(r['anyContainedFocus'])

    def test_threshold_inclusive_and_zero_area_rejected(self):
        r=associations(self.controls(),[dict(box=[1,1,9,9],score=.25)])
        self.assertTrue(r['focusAboveOperating']);self.assertFalse(r['unfocusedOutranksFocus'])
        with self.assertRaisesRegex(ValueError,'invalid_candidate'):
            associations(self.controls(),[dict(box=[0,0,0,0],score=1)])

    def test_calibration_manifest_exact_membership_and_recipe_hashes(self):
        m=native_manifest({'simulator_udid':'test','fixture_url':'http://127.0.0.1:8080'})
        self.assertEqual(len(m['cases']),6)
        self.assertEqual(sum(len(c['target_element_ids']) for c in m['cases']),30)
        for c in m['cases']:
            self.assertEqual(c['split_group'],'validation')
            self.assertEqual(c['recipe']['recipe_hash'],recipe_hash(c['recipe']))
            self.assertEqual(len(set(c['target_element_ids'])),c['recipe']['element_count'])

    def test_ids_follow_producer_not_visual_columns(self):
        m=native_manifest({})
        rows=next(c for c in m['cases'] if 'settings_rows' in c['case_id'])
        self.assertEqual(rows['recipe']['appearance']['canvas']['columns'],1)
        self.assertEqual(rows['target_element_ids'],['grid_cell_0_0','grid_cell_0_1','grid_cell_1_0'])

    def test_membership_defaults_to_calibration_and_groups_duplicates(self):
        f=dict(id='a',disposition='imported',sourceRole='calibration',pixelSHA256='p',
               image={'path':'a','sha256':'a'},evidenceKind='appearance',
               recipe={'appearance':{'referencePack':{'screen':'catalog'}}},
               proposals=[dict(sourceElementID='x',bounds=[0,0,10,10],state='focused',**{'class':'primaryButton'})])
        other=dict(f,id='b')
        m=membership({'frames':[f,other]})
        self.assertEqual(m['recommended']['training'],[])
        self.assertEqual(m['familyGroups']['catalog'][0]['aliases'],['a','b'])
        self.assertEqual(m['alternative']['candidateTrainingPixels'],['p'])
        self.assertEqual(m['alternative']['independentEvaluation'],[])

    def test_cache_parents_exist_before_library_import(self):
        root=h.ROOT/'.build/debug-output';root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as folder, patch.object(h,'ROOT',Path(folder)), patch.dict(os.environ):
            prepare_environment()
            for key in ('YOLO_CONFIG_DIR','MPLCONFIGDIR','TORCH_HOME'):
                self.assertTrue(Path(os.environ[key]).is_dir())
                self.assertTrue(Path(os.environ[key]).is_relative_to(folder))
            self.assertTrue((Path(os.environ['YOLO_CONFIG_DIR'])/'Ultralytics').is_dir())

    def test_native_response_exact_binding_and_no_execution(self):
        m=native_manifest({})
        s=dict(state='validated',total_accepted_pairs=0,total_cases=6,
               cases=[dict(case_id=c['case_id'],state='unattempted') for c in m['cases']],
               input_manifest_sha256=hashlib.sha256(json.dumps(m).encode()).hexdigest())
        r=dict(success=True,data={'campaign':{'_0':s}})
        self.assertEqual(check_response('native',r,m),6)
        s['input_manifest_sha256']='changed'
        with self.assertRaisesRegex(ValueError,'planner_exact_input'):check_response('native',r,m)
        s['total_accepted_pairs']=1
        with self.assertRaisesRegex(ValueError,'planner_execution_state'):check_response('native',r,m)

    def test_grid_response_capacity_is_not_assumed(self):
        p=dict(layouts=['a','b'],seeds=[1],scenarios=['a','b','c','d'],background_groups=['dark'])
        s=dict(state='validated',total_accepted_pairs=0,total_cases=8,cases=[],coverage_plan={'attainable_pairs':8})
        r=dict(success=True,data={'campaign':{'_0':s}})
        self.assertEqual(check_response('grid',r,p),8)
        s['coverage_plan']['attainable_pairs']=7
        with self.assertRaisesRegex(ValueError,'grid_plan_counts'):check_response('grid',r,p)


if __name__=='__main__':unittest.main()
