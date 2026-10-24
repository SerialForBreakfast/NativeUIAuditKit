"""Exercise actual SDK pair intake and negative evidence contracts."""
import copy
import unittest
from unittest.mock import patch
import research_queue as q
import sdk_campaign508 as s
from experiment_templates import pin

class CampaignTests(unittest.TestCase):
    root=q.ROOT/'reports/work/SDK507/extracted'

    def test_all_native_pairs_preserve_roles_and_labels(self):
        pairs=[s.pair(pin(self.root/f'pair-{i}/manifest.json')) for i in range(6)]
        self.assertEqual([p['observed'] for p in pairs],['no_focus','arrival','move','unchanged','unchanged','departure'])
        frames=[f for p in pairs for f in p['frames']]
        self.assertEqual(sum(f['truth'] is None for f in frames),4)
        self.assertEqual({f['split'] for f in frames},{'test'})
        self.assertEqual({f['profile'] for f in frames},{'unknown'})
        self.assertEqual(sum(len(f['controls']) for f in frames),16)
        self.assertTrue(all(not f['controls'] for f in frames if f['truth'] is None))
        self.assertEqual(pairs[4]['issues'],['content_motion_not_independently_verified'])

    def test_action_failure_order_and_label_conflict_fail(self):
        path=self.root/'pair-1/manifest.json';original=q.load
        for failure,reason in [('delivery','sdk508_action_not_delivered'),('identity','sdk508_action_identity'),('order','sdk508_action_order'),('label','sdk508_observed_mismatch')]:
            d=original(path)
            if failure=='delivery':d['action']['receipt']['state']='unknown'
            elif failure=='identity':d['action']['receipt']['sequence']+=1
            elif failure=='order':d['action']['timing']['actionStartedNS']=0
            else:d['observed']='no_focus'
            with self.subTest(failure=failure),patch.object(q,'load',side_effect=lambda p:copy.deepcopy(d) if p==path else original(p)),self.assertRaisesRegex(ValueError,reason):
                s.pair(pin(path))

    def test_fallback_preserves_unique_primary_and_abstention(self):
        self.assertEqual(s.fallback([.9,.1],[.1,.9]),[.9,.1])
        self.assertEqual(s.fallback([.2,.1],[.1,.9]),[.1,.9])
        self.assertEqual(s.fallback([.9,.9],[.9,.9]),[.9,.9])
        self.assertEqual(s.fallback([],[]),[])

    def test_no_focus_false_selection_is_regression(self):
        row=dict(id='none',truth=None,arms={arm:dict(models={m:dict(outcome=value) for m in ('hcf','mixed','fallback')}) for arm,value in [('scoped','correct-abstention'),('union','false-selection')]})
        results=s.compare([row]);self.assertTrue(all(r['loss'] and r['newWrong'] for r in results))
