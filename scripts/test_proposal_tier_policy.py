"""Check preservation, unsafe no-focus recovery, and invalid comparison inputs."""
import copy
import unittest
from proposal_tier_policy import compare


def report(score=.9, outcome='correct', no_focus=False):
    value=dict(scores=[score],aboveThreshold=int(score>=.85),outcome=outcome)
    arm=dict(candidates=[dict(box=[0,0,10,10])],models={m:copy.deepcopy(value) for m in ('baseline','candidate')})
    return dict(version='detector-focus-pilot-v1',threshold=.85,matchingIoU=.5,duplicateIoU=.5,
        inputs=dict(model='fixed',scorecard='card'),rows=[dict(id='frame',sha256='hash',group='scene',profile='standard',
        noFocus=no_focus,arms={'known-box':{},'detector':copy.deepcopy(arm),'detector-plus-ring':copy.deepcopy(arm)})])


class TierTests(unittest.TestCase):
    def test_preserves_single_decision(self):
        r=compare(report(),report(.1,'miss'),'high-first')
        self.assertFalse(r['lostPriorSuccesses'])
        self.assertTrue(all(x['source']=='high' for x in r['rows']))

    def test_recovers_abstention(self):
        r=compare(report(.1,'miss'),report(),'high-first')
        self.assertEqual(len(r['gains']),4)
        self.assertFalse(r['modelAccepted'])

    def test_does_not_use_truth_to_fix_wrong_selection(self):
        r=compare(report(.9,'wrong'),report(),'high-first')
        self.assertFalse(r['gains'])

    def test_no_focus_failure_remains_visible(self):
        r=compare(report(.1,'correct-abstention',True),report(.9,'false-selection',True),'high-first')
        self.assertEqual(len(r['lostPriorSuccesses']),4)
        self.assertEqual(len(r['newWrongSelections']),4)

    def test_replay_and_invalid_identity(self):
        a=report(.1,'miss');b=report()
        self.assertFalse(compare(a,b,'unchanged')['gains'])
        for field in ('sha256','group','id'):
            altered=copy.deepcopy(b);altered['rows'][0][field]='different'
            with self.assertRaises(ValueError):compare(a,altered,'high-first')
        b['inputs']['model']='different'
        with self.assertRaisesRegex(ValueError,'tier_inputs'):compare(a,b,'high-first')

    def test_invalid_scores_and_outcomes(self):
        a=report();b=report(float('nan'),'correct')
        with self.assertRaisesRegex(ValueError,'tier_scores'):compare(a,b,'high-first')
        with self.assertRaisesRegex(ValueError,'tier_focus'):compare(a,report(.1,'correct'),'high-first')


if __name__=='__main__':unittest.main()
