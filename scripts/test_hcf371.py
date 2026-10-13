"""Check native study isolation and rule behavior without starting capture or training."""
import copy
import unittest
from unittest.mock import patch
import numpy as np
from PIL import Image, ImageDraw
import research_queue as q
import hcf_study371 as study
from hcf_compare371 import outline_rule, summarize
from register_hcf371 import make_cases
from types import SimpleNamespace
import hcf_capture362


class StudyTests(unittest.TestCase):
    def test_screenshot_copy_verified_before_cleanup(self):
        import tempfile
        from pathlib import Path
        root=q.ROOT/'.build/debug-output';root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as directory:
            target=Path(directory)/'copy.png'
            data=b'\x89PNG\r\n\x1a\n'+b'test'
            def capture(args,**kwargs):Path(args[-1]).write_bytes(data)
            with patch.object(hcf_capture362.d,'run',side_effect=capture) as run:
                hcf_capture362.save_native_screenshot(target)
            self.assertEqual(target.read_bytes(),data)
            self.assertFalse(Path(run.call_args.args[0][-1]).exists())

    def setUp(self):
        self.base=q.load(q.ROOT/'Research/ResearchSpecs/HCF368/small-dark-plan.json')
        self.cases=make_cases(self.base['recipe'])

    def test_frozen_counts_and_ancestry(self):
        self.assertEqual(len(self.cases),340)
        self.assertEqual({role:sum(c['role']==role for c in self.cases)*4 for role in study.ROLES},
            dict(train=1000,development=120,calibration=120,audit=120))
        study.validate_groups(self.cases)
        self.assertEqual(len({s for c in self.cases for s in c['artworkSeeds']}),1360)

    def test_cross_role_family_and_artwork_rejected(self):
        for field in ('family','group','artworkSeeds'):
            cases=copy.deepcopy(self.cases)
            cases[-1][field]=cases[0][field]
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'cross_role'):
                study.validate_groups(cases)

    def test_native_capture_plan_and_budget(self):
        plan=copy.deepcopy(self.base)
        plan.update(version='native-hcf371-v1',role='study-pending',cases=self.cases[:10],
                    repeats=1,expectedFrames=80,captureBudgetBytes=2*1024**3)
        study.validate_capture_plan(plan)
        for key,value in [('role','train'),('expectedFrames',81),('repeats',2),('captureBudgetBytes',10**12)]:
            altered=copy.deepcopy(plan);altered[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):study.validate_capture_plan(altered)
        altered=copy.deepcopy(plan)
        altered['cases'][0]['recipe']['appearance']['composition']['styles']['image']['focus']['kind']='custom'
        with self.assertRaisesRegex(ValueError,'authored'):study.validate_capture_plan(altered)

    def test_all_layouts_fit(self):
        for case in self.cases:
            self.assertEqual(case['recipe']['theme'],'dark')
            self.assertIn(case['theme'],('dark','light'))
            for region in case['recipe']['appearance']['composition']['regions']:
                x,y,w,h=region['frame']
                self.assertLessEqual(x+w,1920);self.assertLessEqual(y+h,1080)


class RuleTests(unittest.TestCase):
    def test_one_outline(self):
        image=Image.new('RGB',(400,300),'black');d=ImageDraw.Draw(image)
        d.rounded_rectangle((50,50,180,180),radius=12,outline='white',width=5)
        self.assertEqual(outline_rule(image)['decision'],'select')

    def test_filled_white_and_no_outline(self):
        for color in ('black','white'):
            self.assertEqual(outline_rule(Image.new('RGB',(400,300),color))['decision'],'abstain')

    def test_two_outlines_abstain(self):
        image=Image.new('RGB',(500,300),'black');d=ImageDraw.Draw(image)
        for x in (30,280):d.rectangle((x,50,x+130,180),outline='white',width=5)
        self.assertEqual(outline_rule(image)['decision'],'abstain')

    def test_counts_distinguish_wrong_and_missed(self):
        row=dict(id='a',boxes={'focus':[0,0,50,50]},focus='focus',profile='hcf',role='development',
                 family='family',group='group',sha256='a'*64)
        for prediction,outcome in [(None,'miss'),([100,100,50,50],'wrong'),([0,0,50,50],'correct')]:
            result=summarize([row],[dict(id='a',box=prediction)])
            self.assertEqual(result['rows'][0]['outcome'],outcome)
            self.assertFalse(result['modelAccepted'])

    def test_missing_prediction_fails(self):
        with self.assertRaisesRegex(ValueError,'membership'):summarize([dict(id='a')],[])


if __name__=='__main__':unittest.main()
