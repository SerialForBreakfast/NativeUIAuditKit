import unittest
import research_queue as q
from experiment_templates import pin
from sdk_temporal508 import rows

class NativeTemporalTests(unittest.TestCase):
    def test_absence_is_a_real_endpoint_not_missing_telemetry(self):
        ref=pin(q.ROOT/'reports/work/FOCUS-329/run/last.pt')
        request=dict(version='sdk-temporal-request-v1',pairs=[pin(q.ROOT/f'reports/work/SDK507/extracted/pair-{i}/manifest.json') for i in range(6)],models={n:ref for n in ('baseline','seed42','seed44')})
        result=rows(request)
        self.assertEqual([r['changed'] for r in result],[0,1,1,0,0,1])
        self.assertEqual(result[0]['endpoints'],dict(before=None,after=None))
        self.assertTrue(all(r['role']=='review_only' and r['split']=='test' for r in result))
        request['pairs']*=2
        with self.assertRaisesRegex(ValueError,'sdk_temporal_scope'):rows(request)


class PairIdentityTests(unittest.TestCase):
    def test_identical_export_names_keep_manifest_and_group_identity(self):
        from unittest.mock import patch
        model=pin(q.ROOT/'reports/work/FOCUS-329/run/last.pt')
        refs=[dict(path='one/manifest.json',sha256='a'*64),dict(path='two/manifest.json',sha256='b'*64)]
        def fake(ref):
            return dict(id='pair',expected='move',observed='move',issues=[],temporalEligible=True,frames=[
                dict(group='group-'+ref['sha256'][0],split='validation',focusID='a',image=model),
                dict(group='group-'+ref['sha256'][0],split='validation',focusID='b',image=model)])
        request=dict(version='sdk-temporal-request-v1',pairs=refs,models={n:model for n in ('baseline','seed42','seed44')})
        with patch('sdk_temporal508.pair',side_effect=fake):
            with self.assertRaisesRegex(ValueError,'duplicate_pair_id'):rows(request)
            request['identityPolicy']='manifest-sha256'
            result=rows(request)
            self.assertEqual(len({r['id'] for r in result}),2)
            self.assertTrue(all(r['producerID']=='pair' and r['role']=='review_only' for r in result))
            request['identityPolicy']='guess'
            with self.assertRaisesRegex(ValueError,'identity_policy'):rows(request)
