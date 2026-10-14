import copy
import unittest
from hcf_recovery367 import valid_result


class RecoveryTests(unittest.TestCase):
    def good(self):
        return dict(complete=True,route=dict(hcf=dict(status='completed',desiredVerified=True,
            original='standard',observed='standard',restoration='verified')),
            disconnect=dict(state='closed'),postflight=dict(can_run=True,ownership=[dict(state='clear')]))

    def test_verified_recovery(self):valid_result(self.good())

    def test_wrong_profile(self):
        d=self.good();d['route']['hcf']['observed']='hcf'
        with self.assertRaisesRegex(ValueError,'standard_restoration'):valid_result(d)

    def test_incomplete(self):
        d=self.good();d['complete']=False
        with self.assertRaisesRegex(ValueError,'recovery_incomplete'):valid_result(d)

    def test_open_session(self):
        d=self.good();d['disconnect']['state']='ready'
        with self.assertRaisesRegex(ValueError,'session_not_closed'):valid_result(d)

    def test_missing_ownership(self):
        d=self.good();d['postflight']['ownership']=[]
        with self.assertRaisesRegex(ValueError,'ownership_not_clear'):valid_result(d)


if __name__=='__main__':unittest.main()
