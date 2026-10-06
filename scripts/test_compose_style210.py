import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import compose_style210 as c


class Composition(unittest.TestCase):
    def detection(self,box=(0,0,10,10),score=.8,cid=18):
        return dict(classID=cid,score=score,xyxyPixels=list(box))

    def inputs(self):
        base=dict(imageID='one',width=100,height=100,status='ok',detections=[self.detection(),self.detection(cid=2)])
        refined=copy.deepcopy(base);refined['detections'][0]=self.detection((1,1,11,11))
        extra=copy.deepcopy(base);extra['detections'].append(self.detection((50,50,60,60)))
        return [base],[refined],[extra],[dict(imageID='one',added=True)]

    def test_add_preserve_and_no_mutation(self):
        args=self.inputs();before=copy.deepcopy(args)
        result,counts=c.compose(*args,18)
        self.assertEqual(args,before);self.assertEqual(counts,{'added':1})
        self.assertEqual(result['results'][0]['detections'][:2],args[1][0]['detections'])

    def test_overlap_suppressed_at_operating_threshold(self):
        args=self.inputs();args[2][0]['detections'][-1]=self.detection((1,1,11,11))
        _,counts=c.compose(*args,18);self.assertEqual(counts,{'suppressed':1})
        args[1][0]['detections'][0]['score']=.249
        _,counts=c.compose(*args,18);self.assertEqual(counts,{'added':1})

    def test_membership_order_and_duplicates(self):
        for index in (1,2,3):
            args=self.inputs();args[index][0]['imageID']='changed'
            with self.assertRaisesRegex(Exception,'membership'):c.compose(*args,18)
        args=self.inputs();args[0].append(copy.deepcopy(args[0][0]))
        with self.assertRaisesRegex(Exception,'duplicate_base'):c.compose(*args,18)

    def test_failed_empty_geometry_and_mutated_extra(self):
        for field,value in [('status','failed'),('status','empty'),('width',99)]:
            args=self.inputs();args[1][0][field]=value
            with self.assertRaises(Exception):c.compose(*args,18)
        args=self.inputs();args[2][0]['detections'][0]['score']=.9
        with self.assertRaisesRegex(Exception,'extra_mutation'):c.compose(*args,18)

    def test_non_page_and_false_donor_rejected(self):
        args=self.inputs();args[1][0]['detections'][1]['score']=.9
        with self.assertRaisesRegex(Exception,'non_page_change'):c.compose(*args,18)
        for field,value in [('classID',2),('score',.24)]:
            args=self.inputs();args[2][0]['detections'][-1][field]=value
            with self.assertRaisesRegex(Exception,'invalid_donor'):c.compose(*args,18)

    def test_no_extra_and_success_empty(self):
        args=self.inputs();args[2][0]['detections'].pop();args[3][0]['added']=False
        result,counts=c.compose(*args,18);self.assertEqual(result['results'],args[1]);self.assertEqual(counts,{'no_extra':1})
        for rows in args[:3]:rows[0].update(status='empty',detections=[])
        result,_=c.compose(*args,18);self.assertEqual(result['results'][0]['status'],'empty')


class Entrypoints(unittest.TestCase):
    def test_prepare_collision_before_reading(self):
        with patch.object(c,'OUT',Path(__file__).parent),patch.object(c,'collect') as read:
            with self.assertRaisesRegex(Exception,'output_collision'):c.prepare()
            read.assert_not_called()

    def test_report_rejects_changed_bytes_and_versions_before_scoring(self):
        with patch('pathlib.Path.exists',return_value=False),patch.object(c.p,'sealed',return_value={'rule':'unknown'}):
            with self.assertRaisesRegex(Exception,'unsupported_rule'):c.report()
        with patch('pathlib.Path.exists',return_value=False), \
             patch.object(c.p,'sealed',return_value={'rule':c.RULE,'inputs':[{}]}), \
             patch.object(c.h,'checked',side_effect=ValueError('hash_changed')),patch.object(c.e,'score') as score:
            with self.assertRaisesRegex(Exception,'hash_changed'):c.report()
            score.assert_not_called()

    def test_prepare_failed_artifact_publishes_nothing(self):
        root=c.h.ROOT/'.build/test-composition';root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as temp,patch.object(c,'OUT',Path(temp)/'output'):
            with patch.object(c,'collect',return_value=({}, {'control':{}}, [])), \
                 patch.object(c,'load_kind',side_effect=ValueError('corrupt_png')):
                with self.assertRaisesRegex(Exception,'corrupt_png'):c.prepare()
                self.assertFalse(c.OUT.exists())


if __name__=='__main__':unittest.main()
