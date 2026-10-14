"""Test omitted optional IDs without changing native focus evidence."""
import copy
import unittest
import native343 as adapter


class NullTests(unittest.TestCase):
    def value(self):
        return dict(device=dict(simulator_udid='s',fixture_instance_id='i',fixture_run_id='r'),startedAt=1,finishedAt=1,
            scene=dict(recipe={},is_settled=True,focus_observation=dict(generation=1,verified=True,source='uikit_focus_system',plannedFocusIDs=[]),
                observation_generation=1,observation_diagnostics=dict(sampledGeneration=1,sampleAgeMilliseconds=1,stableMilliseconds=200,
                    nativeFocusResolved=True,reason='ready',nativeProbe=dict(referenceFocused=True)),timestamp=1,scene_width=3840,scene_height=2160,elements=[]))

    def test_omitted_and_explicit_null_are_equal(self):
        value=self.value();explicit=copy.deepcopy(value)
        explicit['scene']['focused_element_id']=None;explicit['scene']['focus_observation']['observedID']=None
        self.assertEqual(adapter.signature(value,value,None),adapter.signature(explicit,explicit,None))
        self.assertNotIn('observedID',value['scene']['focus_observation'])

    def test_unknown_and_conflicting_states_fail(self):
        value=self.value();value['scene']['observation_diagnostics']['nativeFocusResolved']=False
        with self.assertRaisesRegex(ValueError,'unfocused_reference_unverified'):adapter.signature(value,value,None)
        value=self.value();value['scene']['focus_observation']['observedID']='control'
        with self.assertRaisesRegex(ValueError,'wrong_focus'):adapter.signature(value,value,None)
        value=self.value();value['scene']['focus_observation']['verified']=False
        with self.assertRaisesRegex(ValueError,'unverified_focus'):adapter.signature(value,value,None)


if __name__=='__main__':unittest.main()
