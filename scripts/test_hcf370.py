"""Check that each new capture changes only its intended factor."""
import unittest
import research_queue as q
from register_hcf370 import variant


class VariantTests(unittest.TestCase):
    def setUp(self):
        self.base = q.load(q.ROOT/'Research/ResearchSpecs/HCF368/small-dark-plan.json')

    def test_other_corners_keep_recipe(self):
        plan = variant(self.base, 'opposite-corners')
        self.assertEqual(plan['recipe'], self.base['recipe'])
        self.assertEqual(plan['targets'], ['item-1', 'item-2'])

    def test_artwork_keeps_geometry_and_effect(self):
        plan = variant(self.base, 'artwork-exchange')
        a = plan['recipe']['appearance']['composition']
        b = self.base['recipe']['appearance']['composition']
        for field in ('styles', 'regions', 'definitions', 'background'):
            self.assertEqual(a[field], b[field])
        self.assertNotEqual(a['contents'], b['contents'])

    def test_center_keeps_artwork_and_role(self):
        plan = variant(self.base, 'center')
        a = plan['recipe']['appearance']['composition']
        b = self.base['recipe']['appearance']['composition']
        self.assertEqual(a['contents'], b['contents'])
        self.assertEqual(plan['group'], self.base['group'])
        self.assertFalse(plan['trainingEligible'])
        self.assertEqual(plan['role'], 'development')
        for region in a['regions']:
            x,y,w,h = region['frame']
            self.assertLessEqual(x+w, 1920)
            self.assertLessEqual(y+h, 1080)


if __name__ == '__main__':
    unittest.main()
