"""Test input suppression, cached-score checks, and paired reports."""
import unittest
from unittest.mock import patch
import numpy as np
import input_use289 as r
import input_route289 as routes


class InputUseTests(unittest.TestCase):
    def test_only_added_channels_change(self):
        x = r.base.torch.rand(2,6,16,24)
        before = x.clone()
        normal = r.model.change_inputs(None,x)
        suppressed = r.without_residual(None,x)
        self.assertTrue(r.base.torch.equal(normal[:,:9],suppressed[:,:9]))
        self.assertEqual(float(suppressed[:,9:].sum()),0)
        self.assertTrue(r.base.torch.equal(x,before))

    def test_decision_transitions(self):
        report = r.compare([.99,.01,.5,.99],[.5,.01,.01,.01],[1,0,0,0])
        self.assertEqual(report['decisionChanges'],3)
        self.assertEqual(report['lostCorrect'],1)
        self.assertEqual(report['gainedCorrect'],2)

    def test_empty_and_invalid(self):
        self.assertIsNone(r.compare([],[],[])['meanAbsoluteScoreChange'])
        for a,b,y in [([np.nan],[0],[0]),([2],[0],[0]),([0],[0],[2]),([0],[],[0])]:
            with self.assertRaises(ValueError):r.compare(a,b,y)

    def test_score_pair_checks_cache(self):
        with patch.object(r.base.worker,'score',side_effect=[np.array([.1]),np.array([.2])]):
            a,b=r.score_pair(None,None,None,[.1])
            self.assertEqual(float(b[0]-a[0]),.1)
        with patch.object(r.base.worker,'score',return_value=np.array([.1])):
            with self.assertRaisesRegex(ValueError,'cache_parity'):
                r.score_pair(None,None,None,[.9])

    def test_route_modes_preserve_rgb(self):
        from types import SimpleNamespace
        x = r.base.torch.rand(1,6,16,24)
        normal = r.model.change_inputs(None,x)
        for mode in ('absolute','both'):
            net = routes.suppress(SimpleNamespace(),mode)
            result = net.change_inputs(x)
            self.assertTrue(r.base.torch.equal(result[:,3:9],x))
            self.assertEqual(float(result[:,:3].sum()),0)
            if mode=='both':self.assertEqual(float(result[:,9:].sum()),0)
            else:self.assertTrue(r.base.torch.equal(result[:,9:],normal[:,9:]))
        with self.assertRaisesRegex(ValueError,'mode'):routes.suppress(SimpleNamespace(),'unknown')


if __name__ == '__main__':unittest.main()
