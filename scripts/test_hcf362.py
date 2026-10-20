"""Check native profile admission without sending Simulator input."""
import copy
import unittest
from unittest.mock import patch
import hcf_capture362 as h
import test_generation352


class NativeProfileTests(unittest.TestCase):
    def value(self):
        return {'hcf': dict(status='completed', desiredVerified=True, requested='hcf', observed='hcf',
            original='standard', mode='ensure', policy='hcf-setting-en-us-23L470-v1')}

    def test_verified_os_profile(self):
        self.assertEqual(h.verified_profile(self.value(), 'hcf')['original'], 'standard')

    def test_v2_retains_all_profile_checks(self):
        value=self.value();value['hcf']['policy']='hcf-setting-en-us-23L470-v2'
        self.assertEqual(h.verified_profile(value,'hcf')['observed'],'hcf')
        value['hcf']['desiredVerified']=False
        with self.assertRaisesRegex(ValueError,'os_profile_unverified'):h.verified_profile(value,'hcf')

    def test_missing_stale_wrong_and_unverified_profile(self):
        for field, value in [('status','stopped'), ('desiredVerified',False), ('observed','standard'),
                             ('original',None), ('mode','roundtrip'), ('policy','other')]:
            row = self.value(); row['hcf'][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                h.verified_profile(row, 'hcf')
        with self.assertRaises(ValueError):
            h.verified_profile({'artworkTheme':'highContrast'}, 'hcf')

    def plan(self):
        return dict(version='native-hcf362-v1', binding=dict(simulatorUDID=h.n.TARGET,
            endpoint='http://127.0.0.1:8080'), role='development', trainingEligible=False,
            profiles=['standard','hcf'], targets=['a','b'], expectedFrames=8,
            recipe={'appearance': {'composition': {'styles': {'image': {'focus': {'kind':'native_image'}}}}}},
            qualification=dict(complete=True, restoration='verified'))

    def test_native_plan(self):
        h.validate_plan(self.plan())

    def test_authored_cues_never_native_hcf(self):
        value = self.plan()
        value['recipe']['appearance']['composition']['styles']['image']['focus']['kind'] = 'custom'
        with self.assertRaisesRegex(ValueError, 'authored_focus'):
            h.validate_plan(value)

    def test_roles_targets_and_cleanup(self):
        for key,value in [('role','train'), ('trainingEligible',True), ('expectedFrames',16),
                          ('profiles',['hcf']), ('targets',['a','a']),
                          ('qualification',dict(complete=True, restoration='unknown'))]:
            plan = self.plan(); plan[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): h.validate_plan(plan)


class DispatchTests(test_generation352.CaptureTests):
    def test_new_dispatch_preserves_old_adapter(self):
        import generation352 as g
        import research_queue as q
        plan = q.load(self.plan); plan['version'] = 'native-hcf362-v1'
        q.save(self.plan, plan, replace=True)
        sp = self.root/'job/spec.json'; spec=q.load(sp)
        spec['capture']['plan']['sha256']=q.digest(self.plan); q.save(sp,spec,replace=True)
        with patch.object(h,'capture',side_effect=lambda *a: self.receipt(True)) as new, patch.object(g.capture,'run') as old:
            g.run()
        new.assert_called_once(); old.assert_not_called()
        self.assertFalse(self.marker.exists())
