import unittest
import dataset351 as d
import compare351 as c
from pathlib import Path
from unittest.mock import patch


class RecipeTests(unittest.TestCase):
    def test_factors_and_original(self):
        source = {'recipe_hash':'old','appearance':{'family_id':'old','composition':{
            'version':5,'regions':[{'frame':[x,100,200,200]} for x in (100,500,1000,1500)],
            'styles':{'image':{'focus':{'version':1,'kind':'native_image'}}}}}}
        cases=d.recipes(source)
        self.assertEqual(len(cases),8)
        self.assertEqual(source['recipe_hash'],'old')
        self.assertEqual(source['appearance']['composition']['regions'][0]['frame'][0],100)
        for case in cases:
            self.assertNotIn('recipe_hash',case['recipe'])
            focus=case['recipe']['appearance']['composition']['styles']['image']['focus']
            if case['effect']=='growth':
                self.assertEqual(focus['custom']['borderWidth'],0)
                self.assertEqual(focus['custom']['scale'],1.08)
            if case['effect']=='border':self.assertEqual(focus['custom']['scale'],1)

    def test_reject_wrong_version(self):
        with self.assertRaises(ValueError):
            d.recipes({'appearance':{'composition':{'version':4,'regions':[]}}})

    def capture(self):
        frames=[dict(id=str(i),path=str(i)+'.png',sha256='a'*64,
            before={'finishedAt':1},start=2,end=3,after={'startedAt':4},
            verifiedInterval=True,observedFocusID=str(i%2)) for i in range(40)]
        return dict(version='controlled-fixture351-v1',complete=True,cleanup=True,
            trainingEligible=False,role='development',frames=frames,
            pairs=[dict(before='0',after='1',changed=True) for _ in range(24)])

    @patch('compare351.q.digest',return_value='a'*64)
    def test_capture_validation(self,_):
        self.assertEqual(len(c.validate_capture(self.capture(),Path('/example'))),40)

    @patch('compare351.q.digest',return_value='a'*64)
    def test_reject_partial_cleanup_labels_and_times(self,_):
        for field in ('complete','cleanup'):
            doc=self.capture();doc[field]=False
            with self.assertRaises(ValueError):c.validate_capture(doc,Path('/example'))
        doc=self.capture();doc['pairs'][0]['changed']=False
        with self.assertRaises(ValueError):c.validate_capture(doc,Path('/example'))
        doc=self.capture();doc['frames'][0]['start']=5
        with self.assertRaises(ValueError):c.validate_capture(doc,Path('/example'))

    @patch('compare351.q.digest',return_value='b'*64)
    def test_reject_changed_pixels(self,_):
        with self.assertRaises(ValueError):c.validate_capture(self.capture(),Path('/example'))
