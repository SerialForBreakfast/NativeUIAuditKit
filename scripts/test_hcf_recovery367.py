import copy
import unittest
import tempfile
from pathlib import Path
from contextlib import nullcontext
from unittest.mock import patch, MagicMock
import research_queue as q
import qualify_hcf362 as runtime
from hcf_recovery367 import valid_result


class RecoveryTests(unittest.TestCase):
    def good(self):
        return dict(complete=True,route=dict(hcf=dict(status='completed',desiredVerified=True,
            original='standard',observed='standard',restoration='verified')),
            disconnect=dict(state='closed'),postflight=dict(can_run=True,ownership=[dict(state='clear')]))

    def test_verified_recovery(self):valid_result(self.good())

    def restoration(self):
        d=self.good();d['recoveryMode']='standard-restoration-v1'
        d['route']['hcf'].update(mode='ensure',requested='standard',original='hcf',
                                 restoration='explicit_persistent_change')
        d['standardPreparation']=copy.deepcopy(d['route'])
        return d

    def test_restoration_only(self):valid_result(self.restoration())

    def test_restoration_rejects_wrong_mode_or_missing_evidence(self):
        for field,value in [('observed','hcf'),('mode','roundtrip'),('requested','hcf'),
                            ('restoration','required_unverified')]:
            d=self.restoration();d['route']['hcf'][field]=value
            with self.assertRaises(ValueError):valid_result(d)
        d=self.restoration();del d['standardPreparation']
        with self.assertRaises(ValueError):valid_result(d)

    def test_runtime_restores_without_roundtrip(self):
        client=MagicMock()
        ready=dict(can_run=True,ownership=[dict(state='clear')])
        route=self.restoration()['route']
        route['hcf']['inputsAttempted']=7
        def call(name,*args):
            if name in ('readiness','postflight'):return ready
            if name=='ensure-standard':return route
            raise AssertionError('Unexpected operation: '+name)
        client.call.side_effect=call
        client.remote.return_value={'operationID':'owned'}
        client.terminal.return_value={'state':'closed'}
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build') as folder, \
                patch('hcf_settings368.Client',return_value=client), \
                patch.object(runtime,'lock',nullcontext), \
                patch.object(runtime.d,'Fixture') as fixture, \
                patch.object(runtime.d,'run',return_value='fixture'):
            fixture.return_value.snapshot.return_value={'device':{'simulator_udid':runtime.TARGET}}
            report=runtime.run(Path(folder)/'out',normalize=True,ensure_standard=True,restore_only=True)
            valid_result(report)
            self.assertEqual([c.args[0] for c in client.call.call_args_list],
                             ['readiness','ensure-standard','postflight'])

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
