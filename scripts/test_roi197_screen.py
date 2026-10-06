import unittest
import roi197_screen as s
import roi197_compare as comparison


class Tests(unittest.TestCase):
    def detection(self,box,score=.5):return dict(classID=2,score=score,xyxyPixels=box)
    def base(self):return dict(status='ok',width=200,height=400,detections=[self.detection([20,20,40,40],.1)])
    def crop(self,detections):return dict(status='ok',width=100,height=100,detections=detections)
    def test_unique_donor_and_empty_abstention(self):
        d=self.detection([20,20,40,40]);result,reason=s.admit(self.base(),self.crop([d]),2)
        self.assertEqual(reason,'added');self.assertEqual(result,d)
        self.assertEqual(s.admit(self.base(),self.crop([]),2),(None,'no_unique_donor'))
    def test_ambiguous_donors_abstain(self):
        self.assertEqual(s.admit(self.base(),self.crop([self.detection([20,20,40,40])]*2),2),(None,'no_unique_donor'))
    def test_score_and_overlap_are_both_required(self):
        for d in [self.detection([20,20,40,40],.249),self.detection([80,80,90,90])]:
            self.assertEqual(s.admit(self.base(),self.crop([d]),2)[1],'no_unique_donor')
    def test_failed_or_wrong_geometry_not_empty(self):
        for change in [dict(status='error'),dict(width=99)]:
            with self.assertRaises(Exception):s.admit(self.base(),dict(self.crop([]),**change),2)
    def test_operating_duplicate_rejected(self):
        base=self.base();base['detections'].append(self.detection([30,20,50,40],.8))
        self.assertEqual(s.admit(base,self.crop([self.detection([30,20,50,40])]),2),(None,'duplicate_operating'))

    def test_merge_preserves_no_candidate_and_original_detections(self):
        base=dict(self.base(),imageID='a');empty=dict(status='empty',imageID='b',width=200,height=400,detections=[])
        crop=dict(self.crop([self.detection([20,20,40,40])]),imageID='c')
        records=[dict(imageID='a',reason='selected',cropID='c'),dict(imageID='b',reason='absent',cropID=None)]
        result,decisions=comparison.merge([base,empty],records,[crop],2)
        self.assertEqual(result['results'][1],empty)
        self.assertEqual(result['results'][0]['detections'][:-1],base['detections'])
        self.assertEqual(len(base['detections']),1)
        self.assertEqual([v['added'] for v in decisions],[True,False])
        with self.assertRaisesRegex(Exception,'crop_membership'):comparison.merge([base,empty],records,[],2)


if __name__=='__main__':unittest.main()
