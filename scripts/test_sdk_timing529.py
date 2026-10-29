import unittest
from sdk_timing529 import compare

class TimingTests(unittest.TestCase):
    def episode(self):
        return dict(id='a',group='group-a',scenario='moving-background',eligibility=dict(temporalReview=True),events=[],reasons=[],frames=[
            dict(producerIntervalNS=[t*1000000,t*1000000+1000],frameReviewable=stable,bytes=10,focusID='cell',frameFocusState='focused' if stable else 'unknown')
            for t,stable in [(0,False),(100,False),(300,True)]])
    def test_unstable_fixed_endpoint_and_stable_geometry(self):
        r=compare(self.episode(),100,500)
        self.assertFalse(r['arms']['fixed-delay']['sample']['stable'])
        self.assertTrue(r['arms']['observed-stability']['sample']['stable'])
        self.assertFalse(r['policyAccepted'] if 'policyAccepted' in r else r['liveLatencyMeasured'])
    def test_timeout_is_explicit_without_waiting_for_video(self):
        e=self.episode()
        r=compare(e,100,200)
        self.assertEqual(r['arms']['observed-stability']['state'],'no_observed_sample')
    def test_missing_history_is_not_success(self):
        e=self.episode();e['eligibility']['temporalReview']=False;e['reasons']=['episode_event_gap']
        self.assertEqual(compare(e,100,500)['state'],'unavailable')
    def test_invalid_budget_rejected(self):
        with self.assertRaisesRegex(ValueError,'policy_budget'):compare(self.episode(),500,100)

if __name__=='__main__':unittest.main()
