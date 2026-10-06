import unittest
import roi196 as r
import roi196_recall as recall
import roi196_admission as admission
import roi196_mechanism as mechanism


class Tests(unittest.TestCase):
    def test_fallback_is_not_a_new_refinement(self):
        self.assertEqual(mechanism.reason_group('replaced'),'new_refinement')
        for reason in ('ambiguous_donors','unchanged_or_shared_match','no_crop_detection','no_overlap_match'):
            self.assertEqual(mechanism.reason_group(reason),'base_fallback')
    def test_admission_receipt_is_immutable(self):
        if not (r.OUT/'admission.json').exists():self.skipTest('integration receipt not present')
        with self.assertRaisesRegex(Exception,'output_collision'):admission.run()
    def test_real_prepare_refuses_existing_output(self):
        if not r.OUT.exists():self.skipTest('integration output not present')
        with self.assertRaisesRegex(Exception,'output_collision'):r.prepare()
    def test_recall_distinguishes_missing_low_and_duplicates(self):
        def d(box,score):return dict(classID=2,xyxyPixels=box,score=score)
        result=recall.classify([[0,0,10,10],[20,0,30,10],[40,0,50,10]],
            [d([0,0,10,10],.9),d([0,0,10,10],.8),d([20,0,30,10],.1)],2)
        self.assertEqual(result['truePositives'],1)
        self.assertEqual(result['falsePositives'],['duplicate'])
        self.assertEqual([v['reason'] for v in result['misses']],['low_confidence','no_overlapping_exported_proposal'])
    def test_recall_geometry_is_not_absence(self):
        result=recall.classify([[0,0,10,10]],[dict(classID=2,xyxyPixels=[0,0,30,30],score=.8)],2)
        self.assertEqual(result['falsePositives'],['geometry'])
        self.assertEqual(result['misses'][0]['reason'],'geometry')
    def test_ancestry_uses_source_not_filename(self):
        row=dict(id='train/a',split='train',sourceFamily='KitchenSink')
        source=dict(generatorProfile=dict(templateFamily='KitchenSink',seed=7))
        self.assertEqual(r.ancestry(row,source,{'reader-footer'})['seed'],7)
        with self.assertRaisesRegex(Exception,'unknown'):r.ancestry(row,{},set())
        with self.assertRaisesRegex(Exception,'reserved'):r.ancestry(row,source,{'KitchenSink'})
        with self.assertRaisesRegex(Exception,'identity'):r.ancestry(dict(row,sourceFamily='UIKitControls'),source,set())
        with self.assertRaisesRegex(Exception,'role'):r.ancestry(dict(row,split='test'),source,set())


if __name__=='__main__':unittest.main()
