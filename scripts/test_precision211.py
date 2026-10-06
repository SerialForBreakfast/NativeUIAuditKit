import copy
import unittest
from unittest.mock import patch
import precision211 as p


class AliasTests(unittest.TestCase):
    def row(self,scores=(.8,.7),boxes=None):
        boxes=boxes or [[0,0,10,10]]*len(scores)
        return dict(imageID='a',width=100,height=200,status='ok',detections=[
            dict(classID=18,score=s,xyxyPixels=b) for s,b in zip(scores,boxes)])

    def test_unique_donors_elect_highest_original_score(self):
        row=self.row((.4,.8));before=copy.deepcopy(row)
        out,counts=p.resolve(row,{0:[1,1,11,11],1:[1,1,11,11]},18)
        self.assertEqual(row,before);self.assertEqual(counts,{'refined':1,'suppressed':1})
        self.assertEqual(out['detections'][0]['score'],.8)

    def test_tie_is_stable_and_uncorroborated_unchanged(self):
        row=self.row((.8,.8,.9));out,counts=p.resolve(row,{0:[1,1,11,11],1:[1,1,11,11]},18)
        self.assertEqual([v['score'] for v in out['detections']],[.8,.9])
        self.assertEqual(out['detections'][1],row['detections'][2])

    def test_nearby_controls_and_chain_do_not_collapse(self):
        row=self.row((.9,.8,.7));out,counts=p.resolve(row,{0:[0,0,10,10],1:[3,0,13,10],2:[6,0,16,10]},18)
        self.assertEqual(counts['suppressed'],1);self.assertEqual(len(out['detections']),2)
        _,counts=p.resolve(row,{0:[0,0,10,10],1:[11,0,21,10]},18)
        self.assertEqual(counts['suppressed'],0)

    def test_invalid_indices_and_bounds(self):
        for donors in ({2:[0,0,10,10]},{0:[0,0,0,10]},{0:[0,0,101,10]},{0:[float('nan'),0,10,10]}):
            with self.assertRaises(Exception):p.resolve(self.row(),donors,18)

    def test_merge_actual_crop_contract(self):
        row=self.row((.8,.7),[[9,10,21,20],[10,10,20,20]])
        records=[dict(imageID='a',proposals=[dict(id=str(i),proposalIndex=i,
            window=p.r.window(100,200,d['xyxyPixels'])) for i,d in enumerate(row['detections'])])]
        crops=[dict(imageID=str(i),status='ok',width=50,height=50,detections=[
            dict(classID=18,score=.9,xyxyPixels=[10,10,20,20])]) for i in range(2)]
        out,counts=p.merge([row],records,crops,18)
        self.assertEqual(len(out['results'][0]['detections']),1);self.assertEqual(counts['suppressed'],1)
        crops[0]['status']='failed'
        with self.assertRaises(Exception):p.merge([row],records,crops,18)

    def test_no_unique_donor_does_not_delete(self):
        row=self.row();out,counts=p.resolve(row,{},18)
        self.assertEqual(row,out);self.assertEqual(counts['suppressed'],0)

    def test_report_requires_passing_fit_same_protocol(self):
        with patch('pathlib.Path.exists',return_value=False), \
             patch.object(p.p,'sealed',side_effect=[{'rule':p.RULE,'inputs':[{}, {}, {}]},{'protocol':{},'fitPassed':False}]), \
             patch.object(p.c,'collect',return_value=({}, {}, [])),patch.object(p.h,'ref',return_value={}), \
             patch.object(p.h,'checked'),patch.object(p.e,'score') as score:
            with self.assertRaisesRegex(Exception,'fit_screen_failed'):p.report()
            score.assert_not_called()


if __name__=='__main__':unittest.main()
