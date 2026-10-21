import copy
import unittest
from capture_postcheck_review481 import validate


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.plan=dict(cases=[dict(id='a',targets=[None])],profiles=['standard','hcf'],expectedFrames=2)
        self.capture=dict(complete=False,cleanup=True,cleanupErrors=[],error='profile-hcf:None',
            originalProfile='standard',frames=[dict(case='a',profile=p,focus=None,repeat=0,end=2) for p in self.plan['profiles']],
            profileReceipts=[dict(profile=p,time=3,receipt=dict(hcf=dict(status='completed',desiredVerified=True,
                observed=p,original='hcf' if i==2 else 'standard'))) for i,p in enumerate(['standard','hcf','standard'])])
        self.native=dict(data=dict(navigationRoute={'_0':dict(hcf=dict(requested='hcf',status='stopped',
            desiredVerified=False,inputs=0,inputsAttempted=0,reason='HCF evidence budget exhausted'))}))

    def test_zero_input_budget_stop_with_verified_restore(self):
        original=copy.deepcopy(self.capture)
        validate(self.capture,self.plan,self.native)
        self.assertEqual(self.capture,original)

    def test_nonzero_or_unknown_inputs_fail(self):
        for value in (1,None):
            self.native['data']['navigationRoute']['_0']['hcf']['inputsAttempted']=value
            with self.assertRaisesRegex(ValueError,'native_cause'):validate(self.capture,self.plan,self.native)

    def test_unknown_original_profile_fails(self):
        self.capture['profileReceipts'][-1]['receipt']['hcf']['original']='unknown'
        with self.assertRaisesRegex(ValueError,'restore_origin'):validate(self.capture,self.plan,self.native)

    def test_failed_cleanup_fails(self):
        self.capture['cleanup']=False
        with self.assertRaisesRegex(ValueError,'failure_scope'):validate(self.capture,self.plan,self.native)

    def test_missing_frame_fails(self):
        self.capture['frames'].pop()
        with self.assertRaisesRegex(ValueError,'membership'):validate(self.capture,self.plan,self.native)

    def test_unexpected_focus_fails(self):
        self.capture['frames'][0]['focus']='unknown-control'
        with self.assertRaisesRegex(ValueError,'membership'):validate(self.capture,self.plan,self.native)

    def test_unverified_restore_fails(self):
        self.capture['profileReceipts'][-1]['receipt']['hcf']['desiredVerified']=False
        with self.assertRaisesRegex(ValueError,'unverified'):validate(self.capture,self.plan,self.native)


if __name__=='__main__':unittest.main()

