"""Offline retry/geometry integration; generated data, no historical report dependency."""
import copy
import json
import shutil
import unittest
from unittest.mock import patch

import fixture_offline_pipeline as p
import human_annotation_review as h
import test_fixture_batch_review as fixtures


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.f=fixtures.ReviewTests();self.f.setUp();self.f.attach()
        self.root=self.f.root;self.output=self.root/'pipeline';self.plan=self.root/'plan.json'
        self.doc=dict(version=p.VERSION,protectedMetadata=str(self.f.protected),
            bundles=[dict(id='one',path=str(self.f.bundle))],sampleCount=1,exceptionLimit=0)
        h.write(self.plan,self.doc)

    def tearDown(self):self.f.tearDown()
    def run_plan(self):return p.run(self.plan,self.output)

    def test_real_pipeline_resume_preserves_human_edit(self):
        before={str(x):h.sha(x) for x in self.f.bundle.iterdir()}
        result=self.run_plan();self.assertEqual(result['counts'],{'review_ready':1})
        attempt=self.output/'one/attempt-001'
        editor=next((attempt/'audit/review/editor').glob('*.json'))
        doc=h.read(editor);doc['description']='human edit retained';editor.write_text(json.dumps(doc))
        edited=h.sha(editor)
        with patch.object(p.batch,'prepare',side_effect=AssertionError('repeated completed intake')):
            self.assertEqual(self.run_plan(),result)
        self.assertEqual(h.sha(editor),edited)
        self.assertEqual(before,{str(x):h.sha(x) for x in self.f.bundle.iterdir()})
        geometry=h.read(attempt/'geometry/geometry.json')
        self.assertFalse(geometry['automatedGeometryAcceptance'])
        self.assertTrue(all(f['visualAlignment']=='human_verification_required' for f in geometry['frames']))
        self.assertIn('Blue:',(attempt/'geometry/review.md').read_text())

    def test_failed_attempt_resumes_without_repeating_other_bundle(self):
        second=self.root/'second';shutil.copytree(self.f.bundle,second)
        self.doc['bundles'].append(dict(id='two',path=str(second)));self.plan.write_text(json.dumps(self.doc))
        real=p.batch.prepare
        def fail_second(roots,*args,**kwargs):
            if roots==[str(second)]:raise ValueError('interrupted crop')
            return real(roots,*args,**kwargs)
        with patch.object(p.batch,'prepare',side_effect=fail_second):
            self.assertEqual(self.run_plan()['counts'],{'review_ready':1,'failed':1})
        def only_second(roots,*args,**kwargs):
            self.assertEqual(roots,[str(second)]);return real(roots,*args,**kwargs)
        with patch.object(p.batch,'prepare',side_effect=only_second):
            self.assertEqual(self.run_plan()['counts'],{'review_ready':2})
        self.assertTrue((self.output/'two/attempt-001/orchestration-failure.json').exists())
        self.assertTrue((self.output/'two/attempt-002/report.json').exists())

    def test_completed_output_tamper_fails_closed(self):
        self.run_plan();path=self.output/'one/attempt-001/geometry/review.md'
        path.write_text('changed')
        with self.assertRaises(ValueError):self.run_plan()

    def test_changed_source_or_plan_cannot_resume(self):
        self.run_plan();self.doc['sampleCount']=2;self.plan.write_text(json.dumps(self.doc))
        with self.assertRaisesRegex(ValueError,'changed_plan'):self.run_plan()

    def test_changed_source_cannot_resume(self):
        self.run_plan();path=self.f.bundle/'m.json';path.write_text(path.read_text()+' ')
        with self.assertRaisesRegex(ValueError,'changed_plan'):self.run_plan()

    def test_lock_and_low_space_do_not_dispatch(self):
        self.output.mkdir();(self.output/'active.lock').write_text('other owner')
        with patch.object(p.batch,'prepare',side_effect=AssertionError('dispatch')):
            with self.assertRaisesRegex(ValueError,'locked'):self.run_plan()
        (self.output/'active.lock').unlink()
        with patch.object(p.shutil,'disk_usage',return_value=shutil._ntuple_diskusage(10,9,1)):
            with self.assertRaisesRegex(ValueError,'insufficient_space'):self.run_plan()

    def test_rejection_record_reused_and_no_geometry_pass(self):
        receipt=self.f.bundle/'harvest-receipt.json';doc=h.read(receipt);doc['outcome']='aborted';receipt.write_text(json.dumps(doc))
        result=self.run_plan();self.assertEqual(result['counts'],{'rejected':1})
        self.assertFalse(result['trainingEligible'])
        with patch.object(p.batch,'prepare',side_effect=AssertionError('repeat rejected')):self.run_plan()

    def test_duplicate_and_overlapping_plan_rejected(self):
        self.doc['bundles']*=2;self.plan.write_text(json.dumps(self.doc))
        with self.assertRaisesRegex(ValueError,'duplicate_bundle'):self.run_plan()
        self.doc['bundles']=self.doc['bundles'][:1];self.plan.write_text(json.dumps(self.doc))
        with self.assertRaisesRegex(ValueError,'overlap'):p.run(self.plan,self.f.bundle/'output')

    def test_protected_before_decode(self):
        self.f.protected.write_text(json.dumps({'sha256':h.sha(self.f.bundle/'f.png')}))
        with patch('harvest_bundle_validation._png_size',side_effect=AssertionError('decode')):
            self.assertEqual(self.run_plan()['counts'],{'rejected':1})

    def test_interrupted_attempt_kept_and_fresh_retry(self):
        def interrupt(roots,output,*args,**kwargs):
            output.mkdir();(output/'partial.txt').write_text('retained interruption')
            raise KeyboardInterrupt()
        with patch.object(p.batch,'prepare',side_effect=interrupt):
            with self.assertRaises(KeyboardInterrupt):self.run_plan()
        self.assertFalse((self.output/'active.lock').exists())
        self.assertEqual(self.run_plan()['counts'],{'review_ready':1})
        self.assertEqual((self.output/'one/attempt-001/partial.txt').read_text(),'retained interruption')
        self.assertTrue((self.output/'one/attempt-002/report.json').exists())

    def test_catalog_groups_themes_without_reserving(self):
        from fixture_recipe_coverage import STRUCTURES
        from focus_corpus_planner import slots
        catalog=self.root/'catalog';catalog.mkdir()
        recipes=[]
        for theme in ('dark','light'):
            path=catalog/(theme+'.json');recipe=dict(theme=theme,seed=1,element_count=4,
                appearance={'canvas':{'columns':2,'backgroundRGB':0 if theme=='dark' else 999}})
            path.write_text(json.dumps(recipe))
            recipes.append(dict(path=path.name,sha256=h.sha(path),recipe=recipe,
                split_membership='unreserved',shared_source_group=theme))
        structures={v:k for k,v in STRUCTURES.items()}
        doc=dict(version=1,purpose='source_review_catalog_not_capture_manifest',recipes=recipes,sources=[],
            totals=dict(slots=60,requested_pairs=480,bound=0),slots=[dict(id=s['id'],family=s['family'],
                structure=structures[s['requestedVariation']],requested_role=s['intendedRole'],
                requested_appearance=s['theme'],candidate_recipe='dark.json',candidate_sha256=recipes[0]['sha256'],
                requested_pairs=8,binding='unbound',support='candidate',remaining=['pending']) for s in slots()])
        path=catalog/'catalog.json';path.write_text(json.dumps(doc))
        result=p.catalog_review(path,catalog)
        self.assertEqual(len(result['groups']),1);self.assertEqual(len(result['structures']),1)
        self.assertIsNone(result['groups'][0]['roleReserved'])
        self.assertEqual(result['independentValidationGroupsEstablished'],0)
        (catalog/'light.json').write_text('{}')
        with self.assertRaisesRegex(ValueError,'changed_catalog'):p.catalog_review(path,catalog)


if __name__=='__main__':unittest.main()
