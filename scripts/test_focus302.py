"""Check the fixed recipe matrix without a native runtime."""
import copy
import unittest
from unittest.mock import patch
import focus302 as f


class RecipeTests(unittest.TestCase):
    def test_fixed_matrix_and_preserved_source(self):
        source=dict(seed=1,appearance=dict(composition=dict(definitions=dict(poster=dict(width=260,height=360)),regions=[])))
        before=copy.deepcopy(source)
        rows=f.recipes(source)
        self.assertEqual(source,before)
        self.assertEqual([r['requestedSizePoints'] for r in rows],[40,80])
        self.assertEqual(len({r['recipe']['seed'] for r in rows}),2)
        for row in rows:
            self.assertEqual(row['role'],'training')
            self.assertEqual(row['group'],'portrait-grid-training')
            regions=row['recipe']['appearance']['composition']['regions']
            self.assertEqual(len(regions),4)
            self.assertEqual(len({r['items'][0]['id'] for r in regions}),4)

    def test_plan_collision_stops_before_runtime(self):
        with patch.object(f,'OUT',f.ROOT):
            with self.assertRaisesRegex(ValueError,'output_collision'):
                f.plan()

    def test_capture_requires_new_attempt(self):
        with patch.object(f.Path,'exists',return_value=True):
            with self.assertRaisesRegex(ValueError,'existing_attempt_requires_review'):
                f.capture()

    def test_resume_requires_prior_attempt(self):
        with patch.object(f.Path,'exists',return_value=False):
            with self.assertRaisesRegex(ValueError,'existing_attempt_requires_review'):
                f.capture(True)


if __name__=='__main__':unittest.main()
