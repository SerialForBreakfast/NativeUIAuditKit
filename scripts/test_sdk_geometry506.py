"""Check geometry comparisons without model execution."""
import unittest
from sdk_geometry506 import matches

class GeometryTests(unittest.TestCase):
    def element(self, **changes):
        return dict(identity={'id':'control'},geometryAvailable=True,observedVisibleEnabled=True,pixelBounds=[10,20,30,40],**changes)

    def test_native_consumer_rows(self):
        import research_queue as q
        from sdk_geometry506 import prepare
        _,frames=prepare(q.load(q.ROOT/'reports/work/SDK506/request.json'))
        rows=matches(frames[0]['elements'],[])
        self.assertEqual(len(rows),4)
        self.assertTrue(all(r['id'] and not r['covered'] for r in rows))

    def test_exact_missing_and_ambiguous_proposals(self):
        e=self.element();p=dict(boundingBoxPixels=dict(x=10,y=20,width=30,height=40))
        self.assertEqual(matches([e],[p])[0]['bestIoU'],1)
        self.assertFalse(matches([e],[])[0]['covered'])
        self.assertEqual(matches([e],[p,p])[0]['candidates'],2)

    def test_nonvisible_elements_are_not_scored(self):
        e=self.element();e['observedVisibleEnabled']=False
        self.assertEqual(matches([e],[]),[])

    def test_invalid_predictions_fail(self):
        for width in [-1,float('nan')]:
            with self.assertRaisesRegex(ValueError,'sdk_prediction_geometry'):
                matches([self.element()],[dict(boundingBoxPixels=dict(x=0,y=0,width=width,height=2))])
