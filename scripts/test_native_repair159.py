import copy
import unittest
import native_repair159 as n
from test_page_regeneration41 import PageRepairTests


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.doc=dict(version='native-page-repair-v1',target=n.TARGET,split='train',
            members=[dict(id=f'img_{i:06}',family='UIKitControls' if i<700 else 'KitchenSink') for i in range(900)])

    def test_membership(self):self.assertEqual(len(n.members(self.doc)),900)
    def test_wrong_target(self):
        self.doc['target']='booted'
        with self.assertRaisesRegex(ValueError,'catalog_identity'):n.members(self.doc)
    def test_evaluation_rejected(self):
        self.doc['split']='test'
        with self.assertRaisesRegex(ValueError,'catalog_identity'):n.members(self.doc)
    def test_duplicate_rejected(self):
        self.doc['members'][-1]['id']=self.doc['members'][0]['id']
        with self.assertRaisesRegex(ValueError,'catalog_membership'):n.members(self.doc)
    def test_family_mismatch(self):
        self.doc['members'][0]['family']='MediaCardGrid'
        with self.assertRaisesRegex(ValueError,'catalog_membership'):n.members(self.doc)
    def test_partial_rejected(self):
        self.doc['members'].pop()
        with self.assertRaisesRegex(ValueError,'catalog_membership'):n.members(self.doc)


class NativeAnnotationTests(PageRepairTests):
    def test_independent_decoded_edge_tolerance(self):
        self.assertEqual(n.check_measurement([157,406.5,61.5,9],[156.5,406.5,62,9],2),[1,0,0,0])
        with self.assertRaisesRegex(ValueError,'measurement_mismatch'):
            n.check_measurement([158,406.5,61.5,9],[156.5,406.5,62,9],2)
        with self.assertRaisesRegex(ValueError,'measurement_shape'):
            n.check_measurement([157,406.5,float('nan'),9],[156.5,406.5,62,9],2)

    def test_measured_native_bounds(self):
        self.check()
        from page_regeneration41 import checked_annotation
        checked_annotation(self.recipe,self.image,self.ann,native_body=[20,10,25,10])
        with self.assertRaisesRegex(ValueError,'native_body_mismatch'):
            checked_annotation(self.recipe,self.image,self.ann,native_body=[20,10,24,10])
        with self.assertRaisesRegex(ValueError,'native_body_mismatch'):
            checked_annotation(self.recipe,self.image,self.ann,native_body=[20,10,float('nan'),10])


if __name__=='__main__':unittest.main()
