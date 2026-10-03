import unittest
from unittest.mock import patch
from types import SimpleNamespace
from local_diagnostics38 import decision, ios_metrics


class SelectionTests(unittest.TestCase):
    controls=[dict(bounds=[10,10,20,20],state='focused')]

    def test_correct(self):
        self.assertEqual(decision([[10,10,20,20]],[.9],self.controls)['outcome'],'correct')

    def test_missing(self):
        self.assertEqual(decision([[50,50,20,20]],[.9],self.controls)['outcome'],'target_missing')

    def test_low(self):
        self.assertEqual(decision([[10,10,20,20]],[.8],self.controls)['outcome'],'below_threshold')

    def test_distractor(self):
        r=decision([[10,10,20,20],[50,50,20,20]],[.9,.95],self.controls)
        self.assertEqual(r['outcome'],'distractor_wins');self.assertEqual(r['targetBest'],.9)

    def test_tie(self):
        self.assertEqual(decision([[10,10,20,20],[50,50,20,20]],[.9,.9],self.controls)['outcome'],'tied')

    def test_invalid(self):
        for probabilities in ([float('nan')],[],[2]):
            with self.assertRaises(ValueError):decision([[10,10,20,20]],probabilities,self.controls)

    def test_nonunique_truth(self):
        with self.assertRaises(ValueError):decision([[10,10,20,20]],[.9],[])

    def test_ios_geometry_is_not_class_accuracy(self):
        members=[dict(imageID='a',label={},width=100,height=100)]
        rows=[dict(imageID='a',imgsz=640,detections=[dict(classID=1,score=.9,xyxyPixels=[40,40,60,60])])]
        with patch('local_diagnostics38.h.taxonomy',return_value=['pageControl','other']),patch(
                'local_diagnostics38.h.checked',return_value=SimpleNamespace(read_text=lambda:'0 .5 .5 .2 .2')):
            r=ios_metrics(members,rows)
        self.assertEqual(r['geometry0.5'],1);self.assertEqual(r['typed0.5'],0)

    def test_ios_rejects_missing_predictions(self):
        with self.assertRaises(ValueError):ios_metrics([dict(imageID='a')],[])


if __name__=='__main__':unittest.main()
