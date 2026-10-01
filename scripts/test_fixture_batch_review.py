"""Real offline intake/editor/crop entrypoints with generated native fixtures."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import fixture_batch_review as b
import human_annotation_review as h
import human_intake_audit as audit
import human_regression_review as regression
import human_review_finish as finish
from test_fixture_semantic_inventory import inventory
import test_ttr_sidecar_v2 as fixtures


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.f=fixtures.V2Tests(); self.f.setUp()
        self.root=self.f.root; self.bundle=self.f.bundle
        self.protected=self.root/'protected.json'; self.protected.write_text('{}')

    def tearDown(self): self.f.tearDown()

    def attach(self):
        def walk(value):
            if isinstance(value,dict):
                for child in list(value.values()): walk(child)
                if 'scene_width' in value: value['semantic_inventory']=inventory(value)
            elif isinstance(value,list):
                for child in value: walk(child)
        walk(self.f.meta); self.f.mutate(lambda m:None)

    def prepare(self,**kwargs):
        return b.prepare([self.bundle],self.root/'qa',self.protected,**kwargs)

    def test_real_pipeline_crop_editor_finish_and_source_preservation(self):
        self.attach()
        before={p:h.sha(p) for p in self.bundle.iterdir() if p.is_file()}
        result=self.prepare(count=1)
        self.assertEqual(result['crops'],{'expected':2,'completed':2})
        self.assertEqual(result['pairCount'],1)
        self.assertFalse(result['trainingEligible'])
        queue=self.root/'qa/audit/combined-queue.json'
        work=self.root/'qa/audit/review/batch.json'
        selected=regression.queue_scope(queue,work)
        plan=finish.preview(work,selected)
        self.assertTrue(any(f['ready'] for f in plan['frames']))
        revision=self.root/'revision'
        finish.apply_preview(plan,revision,reviewer='test',attested=True,reviewer_kind='software-test')
        doc=h.read(revision/'revision/revision.json')
        self.assertEqual(doc['reviewer']['kind'],'software-test')
        self.assertNotIn('reviewed',doc['frameCounts'])
        self.assertEqual(before,{p:h.sha(p) for p in before})
        self.assertEqual(h.validate_batch(work)['version'],b.VERSION)
        self.assertTrue((self.root/'qa/review.md').is_file())
        with self.assertRaisesRegex(ValueError,'output_collision'): self.prepare()

    def test_legacy_remains_diagnostic_and_sample_is_deterministic(self):
        self.prepare(count=1,seed=12)
        path=self.root/'qa/native-review/batch.json'
        first=audit.plan(path,count=1,seed=12)
        self.assertEqual(first,audit.plan(path,count=1,seed=12))
        self.assertIn('legacy_semantics_unavailable',first['frames'][0]['findings'])

    def test_reject_protected_before_any_image_decode(self):
        self.protected.write_text(json.dumps({'sha256':h.sha(self.bundle/'f.png')}))
        with patch('harvest_bundle_validation._png_size',side_effect=AssertionError('decoded protected pixels')):
            result=self.prepare()
        self.assertEqual(result['counts'],{'rejected':1})
        self.assertIn('protected_reference',result['bundles'][0]['reasons'])
        self.assertFalse((self.root/'qa/native-review').exists())

    def test_partial_and_changed_hash_are_accounted_not_admitted(self):
        receipt=self.bundle/'harvest-receipt.json'
        doc=h.read(receipt); doc.update(outcome='aborted',acceptedRowCount=0,failure={'cause':'native_failure'})
        receipt.write_text(json.dumps(doc))
        result=self.prepare()
        self.assertEqual(result['counts'],{'rejected':1})
        self.assertEqual(result['bundles'][0]['producerReportedReceipt']['failure']['cause'],'native_failure')
        self.assertEqual(result['pairCount'],0)

    def test_tampered_projection_rejected_even_if_resealed(self):
        self.attach(); self.prepare()
        path=self.root/'qa/native-review/batch.json'; doc=h.read(path)
        doc['frames'][0]['proposals'][0]['state']='focused'
        doc.pop('seal'); doc['seal']=h.digest(doc); path.write_text(json.dumps(doc))
        with self.assertRaisesRegex(ValueError,'projection_changed'): h.validate_batch(path)

    def test_unknown_focusability_and_children_accounted(self):
        source,contract=b.source_record(self.bundle,set())
        for key in ('baselineScene','focusedScene'):
            scene=contract['usableRows'][0]['observationBinding'][key]
            inv=inventory(scene); inv['elements'][0]['focusable']=None
            child=copy.deepcopy(inv['elements'][0]); child.update(id='child',role='label_view',input_focused=False)
            inv['elements'].append(child); scene['semantic_inventory']=inv
        result=b.project([source],[contract])
        self.assertEqual(len(result['records']),4)
        self.assertTrue(all(f['disposition']=='blocked' for f in result['frames']))
        self.assertEqual(result['pairs'],[])

    def test_selected_parent_not_promoted_to_focus(self):
        from test_ttr_competitor import competitor_meta
        self.f.meta=competitor_meta(self.f.meta); self.attach()
        source,contract=b.source_record(self.bundle,set())
        for key in ('baselineScene','focusedScene'):
            inv=contract['usableRows'][0]['observationBinding'][key]['semantic_inventory']
            inv['elements'][1]['selected']=True
        result=b.project([source],[contract]); target=result['frames'][1]
        self.assertEqual(target['proposals'][1]['state'],'unfocused')
        self.assertTrue(target['proposals'][1]['selected'])
        self.assertEqual(len(result['pairs']),2)

    def test_exact_duplicates_and_conflicts_keep_accounting(self):
        source,contract=b.source_record(self.bundle,set())
        second=copy.deepcopy(contract['usableRows'][0]); second['id']='pair-2'
        contract['usableRows'].append(second)
        result=b.project([source],[contract])
        self.assertEqual(len(result['frames']),4)
        self.assertTrue(all(f['duplicateOf'] for f in result['frames'][2:]))
        second['observationBinding']['focusedScene']['elements'][0]['is_focused']=False
        result=b.project([source],[contract])
        self.assertIn('same_pixels_conflicting_native_proposals',result['frames'][1]['reviewFindings'])

    def test_held_out_rejected_before_decode(self):
        rows=h.read(self.bundle/'manifest.json'); rows[0]['split']='held-out'
        (self.bundle/'manifest.json').write_text(json.dumps(rows))
        with patch('harvest_bundle_validation._png_size',side_effect=AssertionError('decoded')):
            result=self.prepare()
        self.assertIn('protected_or_unsupported_split',result['bundles'][0]['reasons'])

    def test_changed_source_invalidates_batch(self):
        self.attach(); self.prepare()
        path=self.bundle/'m.json'; path.write_text(path.read_text()+' ')
        with self.assertRaises(ValueError): h.validate_batch(self.root/'qa/native-review/batch.json')

    def test_crop_failure_leaves_intake_accounting(self):
        with patch.object(h,'crop_qa',side_effect=ValueError('test crop failure')):
            with self.assertRaisesRegex(ValueError,'test crop failure'): self.prepare()
        self.assertTrue((self.root/'qa/intake.json').exists())
        self.assertFalse((self.root/'qa/report.json').exists())
        self.assertEqual(h.read(self.root/'qa/failure.json')['stage'],'production_crop_QA')


if __name__=='__main__': unittest.main()
