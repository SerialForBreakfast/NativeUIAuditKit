import unittest
import numpy as np
from unittest.mock import patch
import transition248 as t


class SamplingTests(unittest.TestCase):
    def test_equal_mass(self):
        w=t.weights(['a','a','b'],2,True)
        self.assertAlmostEqual(w[2:4].sum(),w[4])
        self.assertEqual(w.sum(),8)

    def test_connected_pixels_stay_together(self):
        rows=[dict(group=g,pixelHashes=p,role='train') for g,p in [('a',['x']),('b',['x']),('c',['y'])]]
        selected,held,names=t.partition(rows)
        self.assertEqual(names['a'],names['b'])
        self.assertEqual(0 in held,1 in held)
        self.assertFalse(set(selected)&set(held))

    def test_protected_roles_excluded(self):
        rows=[dict(group=g,pixelHashes=[g],role=r) for g,r in [('a','train'),('b','train'),('c','reserved')]]
        selected,held,_=t.partition(rows)
        self.assertNotIn(2,selected+held)

    def test_transitive_pixels_share_component(self):
        rows=[dict(group=g,pixelHashes=p,role='train') for g,p in
              [('a',['x']),('b',['x','y']),('c',['y']),('d',['z'])]]
        _,_,names=t.partition(rows)
        self.assertEqual(len({names[g] for g in ['a','b','c']}),1)

    def test_one_component_cannot_form_holdout(self):
        rows=[dict(group='a',pixelHashes=['x'],role='train')]
        with self.assertRaisesRegex(ValueError,'insufficient_components'):t.partition(rows)

    def test_weights_preserve_replay_and_reversal(self):
        w=t.weights(['a','a','b'],2,True)
        np.testing.assert_array_equal(w[:2],np.ones(2))
        np.testing.assert_array_equal(w[2:5],w[5:])

    def test_collision(self):
        with patch.object(t,'OUT') as p,patch.object(t.t,'prepare') as prepare:
            p.exists.return_value=True
            with self.assertRaises(ValueError):t.run()
            prepare.assert_not_called()


if __name__=='__main__':unittest.main()
