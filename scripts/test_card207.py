import copy
import unittest
import card207 as c


class Tests(unittest.TestCase):
    def row(self):
        return dict(imageID='a',width=100,height=200,status='ok',detections=[dict(classID=1,score=.9,xyxyPixels=[20,30,50,60])])

    def test_selection_no_labels_and_dedup(self):
        row=self.row();row['detections']*=2
        plans=c.select(row,1);self.assertEqual(len(plans),1);self.assertEqual(len(plans[0]['parents']),2)
        self.assertEqual(c.select(row,0),[])
        with self.assertRaises(ValueError):c.select(dict(row,status='failed'),1)

    def test_restore_dedup_parent_and_other_class_preservation(self):
        row=self.row();plan=dict(c.select(row,1)[0],id='crop');x,y=plan['window'][:2]
        d=dict(classID=0,score=.8,xyxyPixels=[20-x,30-y,50-x,60-y])
        crop=dict(status='ok',width=50,height=50,detections=[d,dict(d,score=.7)])
        result=c.merge(row,[plan],{'crop':crop},0)
        self.assertEqual(result['detections'][0],row['detections'][0]);self.assertEqual(len(result['detections']),2)
        self.assertEqual(result['detections'][1]['xyxyPixels'],[20,30,50,60])
        self.assertEqual(row,self.row())

    def test_failed_or_mismatched_crop_rejected(self):
        row=self.row();plan=dict(c.select(row,1)[0],id='crop')
        for crop in [dict(status='failed',width=50,height=50),dict(status='empty',width=51,height=50,detections=[])]:
            with self.assertRaises(ValueError):c.merge(row,[plan],{'crop':crop},0)
        with self.assertRaises(KeyError):c.merge(row,[plan],{},0)

    def test_outside_parent_and_low_confidence_do_not_add(self):
        row=self.row();plan=dict(c.select(row,1)[0],id='crop')
        crop=dict(status='ok',width=50,height=50,detections=[dict(classID=0,score=.9,xyxyPixels=[0,0,2,2]),dict(classID=0,score=.1,xyxyPixels=[10,10,40,40])])
        self.assertEqual(c.merge(row,[plan],{'crop':crop},0),row)

    def test_empty_proposal_retains_existing_predictions(self):
        row=self.row();self.assertEqual(c.merge(row,[],{},0),row)


if __name__=='__main__':unittest.main()
