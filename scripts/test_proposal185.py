import unittest
from unittest.mock import patch
import proposal185 as p


class Tests(unittest.TestCase):
    def test_missing_predictions_are_unavailable(self):
        result=p.summary([dict(geometry=None)])
        self.assertEqual(result['geometrySupport'],0)
        self.assertTrue(all(x is None for x in result['medianGeometry'].values()))

    def test_one_parameter_only(self):
        original=dict(box=7.5,epochs=10,batch=8,cls=.5,seed=42)
        actual=p.config(original)
        self.assertEqual({k for k in actual if actual[k]!=original[k]},{'box'})
        self.assertEqual(original['box'],7.5)
        for key in ('box','epochs','batch'):
            with self.subTest(key=key),self.assertRaisesRegex(Exception,'control_configuration'):p.config(dict(original,**{key:99}))

    def test_output_collision(self):
        with patch.object(p.d,'OUT',p.h.ROOT/'reports/work/IOS-DIAG-185/artifacts'),patch.object(p.p,'sealed') as read,patch.object(p.Path,'exists',return_value=True):
            with self.assertRaisesRegex(Exception,'output_collision'):p.run()
            read.assert_not_called()


if __name__=='__main__':unittest.main()
