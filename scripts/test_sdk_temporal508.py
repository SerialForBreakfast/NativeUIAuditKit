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
