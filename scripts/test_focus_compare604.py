"""Tests for RESET604 Stage 2 proposal-vs-supplied FocusRing comparison."""
import tempfile
import unittest
from pathlib import Path

import focus_compare604 as fc
import research_queue as q


class FocusCompare604Tests(unittest.TestCase):
    def test_summarize_tracks_recovered_lost_and_no_focus(self):
        manifest = dict(
            classes=['cell', 'button'],
            apps=[dict(id='AppA', sealed=False)],
            cases=[
                dict(id='f1', app='AppA', flow='fl', status='captured', width=100, height=100,
                     image=dict(path='a.png', sha256='0' * 64), labels=dict(path='a.json')),
                dict(id='f2', app='AppA', flow='fl', status='captured', width=100, height=100,
                     image=dict(path='b.png', sha256='1' * 64), labels=dict(path='b.json')),
                dict(id='nf', app='AppA', flow='fl', status='captured', width=100, height=100,
                     image=dict(path='c.png', sha256='2' * 64), labels=dict(path='c.json')),
            ],
        )
        labels = {
            'f1': dict(complete=True, objects=[], focus=dict(state='focused', box=[10, 10, 20, 20])),
            'f2': dict(complete=True, objects=[], focus=dict(state='focused', box=[50, 50, 20, 20])),
            'nf': dict(complete=True, objects=[], focus=dict(state='no_focus', box=None)),
        }
        ctrl = {
            'f1': dict(detections=[dict(cls='cell', box=[10, 10, 20, 20], score=0.9)], focusBox=[10, 10, 20, 20],
                       focusExecution=dict(threshold=0.85, winnerProbability=0.95, candidates=[dict(box=[10, 10, 20, 20], disposition='scored', probability=0.95)])),
            'f2': dict(detections=[dict(cls='cell', box=[50, 50, 20, 20], score=0.9)], focusBox=None,
                       focusExecution=dict(threshold=0.85, winnerProbability=None, candidates=[dict(box=[50, 50, 20, 20], disposition='scored', probability=0.40)])),
            'nf': dict(detections=[], focusBox=[0, 0, 10, 10], focusExecution=dict(threshold=0.85, candidates=[dict(box=[0, 0, 10, 10], disposition='scored', probability=0.99)])),
        }
        cand = {
            'f1': dict(detections=[], focusBox=None, focusExecution=dict(threshold=0.85, candidates=[])),
            'f2': dict(detections=[dict(cls='cell', box=[50, 50, 20, 20], score=0.9)], focusBox=[50, 50, 20, 20],
                       focusExecution=dict(threshold=0.85, winnerProbability=0.92, candidates=[dict(box=[50, 50, 20, 20], disposition='scored', probability=0.92)])),
            'nf': dict(detections=[], focusBox=None, focusExecution=dict(threshold=0.85, candidates=[])),
        }
        s_ctrl = fc.summarize_focus_condition('ctrl', manifest, ctrl, labels)
        s_cand = fc.summarize_focus_condition('cand', manifest, cand, labels, control_outcomes=s_ctrl['outcomesById'])
        self.assertEqual(s_ctrl['overall']['correctFocused'], 1)
        self.assertEqual(s_ctrl['overall']['noFocusFalseSelections'], 1)
        self.assertEqual(s_cand['recoveredVsControl'], ['f2', 'nf'])
        self.assertEqual(s_cand['lostPreviousSuccessesVsControl'], ['f1'])


if __name__ == '__main__':
    unittest.main()
