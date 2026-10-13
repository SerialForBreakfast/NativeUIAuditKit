import copy
import unittest
from unittest.mock import patch
from native343 import signature


class NativeTests(unittest.TestCase):
    def sample(self):
        return dict(startedAt=10,finishedAt=11,device=dict(simulator_udid='a',fixture_instance_id='b',fixture_run_id='c'),
            scene=dict(recipe={'v':5},is_settled=True,focused_element_id='x',timestamp=10.5,
                focus_observation=dict(verified=True,source='uikit_focus_system',observedID='x',generation=1,plannedFocusIDs=['x']),
                observation_generation=1,observation_diagnostics=dict(sampledGeneration=1,sampleAgeMilliseconds=50,stableMilliseconds=200),
                scene_width=3840,scene_height=2160,elements=[dict(element_id='x',is_focused=True,rendered_body_geometry={})]))

    @patch('native343.body.validate',return_value=[1,2,3,4])
    def test_valid_and_changes(self,_):
        original=self.sample();signature(original,original,'x')
        for field,value in [('recipe',{}),('timestamp',1),('is_settled',False),('focused_element_id','y')]:
            sample=copy.deepcopy(original);sample['scene'][field]=value
            with self.assertRaises(ValueError):signature(sample,original,'x')
        sample=copy.deepcopy(original);sample['scene']['observation_diagnostics']['sampleAgeMilliseconds']=201
        with self.assertRaises(ValueError):signature(sample,original,'x')

    @patch('native343.body.validate',return_value=None)
    def test_missing_body(self,_):
        sample=self.sample()
        with self.assertRaisesRegex(ValueError,'missing_body'):signature(sample,sample,'x')


if __name__=='__main__':unittest.main()
