"""Scene aggregation tests; inputs generated here, no retained report dependency."""
import copy
import unittest
from focus_scene_transition import corroborate


def request(*decisions):
    return dict(version=1, context=dict(sameScene=True, settled=True, fresh=True, completeCoverage=True),
                controls=[dict(id=str(i), decision=d, identityVerified=True) for i, d in enumerate(decisions)])


class SceneTests(unittest.TestCase):
    def test_disabled(self):
        self.assertEqual(corroborate(None)['status'], 'disabled')

    def test_switch_and_unknown_background(self):
        x=request('arrival', 'departure', 'unknown')
        r=corroborate(x, True)
        self.assertEqual((r['decision'], r['gained'], r['lost']), ('switch', '0', '1'))
        self.assertFalse(r['releaseEligible']); self.assertFalse(r['controlIssued'])
        self.assertEqual(corroborate(x, True, require_resolved=True)['decision'], 'unavailable')

    def test_isolated_content_changes_rejected(self):
        for direction in ('arrival', 'departure'):
            self.assertEqual(corroborate(request(direction, 'unchanged'), True)['decision'], 'unknown')

    def test_paired_content_is_indistinguishable(self):
        # This intentionally records the limitation, not a claimed focus truth.
        self.assertEqual(corroborate(request('arrival', 'departure'), True)['decision'], 'switch')

    def test_multiple_or_missing_changes(self):
        for ds in [('arrival','arrival','departure'), ('departure','departure','arrival'), ('unknown',)]:
            self.assertEqual(corroborate(request(*ds), True)['decision'], 'unknown')

    def test_unchanged(self):
        self.assertEqual(corroborate(request('unchanged','unchanged'), True)['decision'], 'unchanged')

    def test_unavailable(self):
        self.assertEqual(corroborate(request('arrival','departure','unavailable'), True)['decision'], 'unavailable')

    def test_context_and_identity(self):
        for key in request('arrival')['context']:
            x=request('arrival','departure'); x['context'][key]=False
            self.assertEqual(corroborate(x,True)['decision'],'unavailable')
        x=request('arrival','departure'); x['controls'][0]['identityVerified']=False
        self.assertEqual(corroborate(x,True)['decision'],'unavailable')

    def test_reject_malformed(self):
        base=request('arrival','departure')
        mutations=[lambda x:x.update(version=True), lambda x:x.update(extra=True),
                   lambda x:x['context'].update(fresh=1), lambda x:x['controls'][1].update(id='0'),
                   lambda x:x['controls'][0].update(decision='focused'),
                   lambda x:x['controls'][0].update(identityVerified=1),
                   lambda x:x.update(controls=[]), lambda x:x.update(controls=[x['controls'][0]]*257),
                   lambda x:x['controls'][0].update(truth=True)]
        for mutate in mutations:
            x=copy.deepcopy(base); mutate(x)
            with self.assertRaises(ValueError):corroborate(x,True)


if __name__ == '__main__':unittest.main()
