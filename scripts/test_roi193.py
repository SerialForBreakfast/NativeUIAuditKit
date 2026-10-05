import copy
import unittest
from types import SimpleNamespace
from unittest.mock import Mock,patch
import roi193 as r


class Tests(unittest.TestCase):
    def test_windows_and_inverse(self):
        for box in ([0,0,10,10],[90,190,100,200],[45,95,55,105]):
            for shift in r.JITTER:
                roi=r.window(100,200,box,shift)
                self.assertEqual(roi[2]-roi[0],50)
                self.assertTrue(0<=roi[0]<roi[2]<=100 and 0<=roi[1]<roi[3]<=200)
                self.assertEqual(r.restore([0,0,50,50],roi),roi)
        with self.assertRaises(Exception):r.restore([0,0,51,50],[0,0,50,50])
        with self.assertRaises(Exception):r.window(100,200,[0,0,10,10],(float('nan'),0))

    def test_all_class_clipping(self):
        im=SimpleNamespace(width=100,height=100,label_path=Mock())
        im.label_path.read_text.return_value='0 .5 .5 1 1\n1 .25 .25 .1 .1\n2 .9 .9 .1 .1\n3 .495 .25 .01 .1\n'
        text,audit=r.labels(im,[0,0,50,50])
        self.assertEqual([a['disposition'] for a in audit],['clipped','retained','outside','excluded_sliver'])
        self.assertEqual(len(text.splitlines()),2)
        self.assertTrue(text.startswith('0 0.500000000 0.500000000 1.000000000 1.000000000'))

    def base(self):
        return dict(status='ok',width=100,height=200,detections=[dict(classID=0,score=.7,xyxyPixels=[40,90,60,110]),dict(classID=1,score=.9,xyxyPixels=[0,0,10,10])])

    def item(self):
        return dict(status='ok',window=[25,75,75,125],detections=[dict(classID=0,score=.8,xyxyPixels=[16,16,34,34])])

    def test_refinement_preserves_scores_and_other_classes(self):
        base=self.base();before=copy.deepcopy(base)
        result=r.refine(base,{0:self.item()},0)
        self.assertEqual(result['detections'][0]['xyxyPixels'],[41,91,59,109])
        self.assertEqual(result['detections'][0]['score'],.7)
        self.assertEqual(result['detections'][1],base['detections'][1])
        self.assertEqual(base,before)

    def test_no_proposal_and_ambiguous_donors(self):
        base=self.base();base['detections']=[];base['status']='empty'
        self.assertEqual(r.refine(base,{},0),base)
        base=self.base();item=self.item();item['detections']*=2
        self.assertEqual(r.refine(base,{0:item},0),base)

    def test_fail_closed(self):
        for field,value in [('status','failed'),('window',[0,0,50,50])]:
            item=self.item();item[field]=value
            with self.assertRaises(Exception):r.refine(self.base(),{0:item},0)
        item=self.item();item['detections'][0]['score']=float('nan')
        with self.assertRaises(Exception):r.refine(self.base(),{0:item},0)
        with self.assertRaises(Exception):r.refine(self.base(),{},0)
        base=self.base();base['status']='failed'
        with self.assertRaises(Exception):r.proposals(base,0)

    def test_shared_replacement_abstains(self):
        base=self.base();base['detections'].append(copy.deepcopy(base['detections'][0]))
        self.assertEqual(r.refine(base,{0:self.item(),2:self.item()},0),base)

    def test_collision_before_inputs(self):
        with patch.object(r,'OUT',r.h.ROOT),patch.object(r.c,'inputs') as inputs:
            with self.assertRaisesRegex(Exception,'output_collision'):r.run()
            inputs.assert_not_called()

    def test_duplicate_labels_must_agree(self):
        seen={'pixels':dict(id='first',labels=('0 .5 .5 .2 .2',))}
        self.assertEqual(r.duplicate(seen,'pixels',('0 .5 .5 .2 .2',)),'first')
        with self.assertRaisesRegex(Exception,'conflicting_labels'):r.duplicate(seen,'pixels',('1 .5 .5 .2 .2',))


if __name__=='__main__':unittest.main()
