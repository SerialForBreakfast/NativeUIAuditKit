"""Check preparation boundaries without capture, model execution, or data admission."""
import copy
import unittest
import research_queue as q
import native_training587 as n


class NativePreparationTests(unittest.TestCase):
    def setUp(self):
        self.path=q.ROOT/'reports/work/NATIVE587-IOS588/native587-review-preparation.json'
        self.request=q.load(self.path)

    def test_role_and_member_drift_fail(self):
        for mutate in (lambda r:r['captures'].pop(),lambda r:r['captures'].__setitem__(1,copy.deepcopy(r['captures'][0])),lambda r:r['captures'][0].update(split='test')):
            r=copy.deepcopy(self.request);mutate(r)
            with self.assertRaises(ValueError):n.validate(r)

    def test_preparation_stays_diagnostic_with_exact_dependencies(self):
        s=n.build(self.path);q.validate(s)
        self.assertEqual(s['authority'],'diagnostic');self.assertNotIn('training',s)
        self.assertEqual({d['job'] for d in s['dependencies']},{r['job'] for r in self.request['captures']})
        self.assertTrue(all('cleanup.json' in d['outputs'] for d in s['dependencies']))

    def test_no_unreviewed_admission_field_is_accepted(self):
        r=copy.deepcopy(self.request);r['admission']={'reviewer':'agent'}
        with self.assertRaisesRegex(ValueError,'fields'):n.validate(r)

if __name__=='__main__':unittest.main()
