"""Keep grouped reports separate from frame counts."""
import unittest
import numpy as np
from report_additive341 import grouped_comparison


class ReportTests(unittest.TestCase):
    def test_groups_keep_gains_and_losses(self):
        rows=[dict(group='a',changed=0),dict(group='a',changed=1),dict(group='b',changed=1)]
        report=grouped_comparison(rows,np.array([.9,.9,.1]),np.array([.1,.1,.9]))
        self.assertEqual(report['a']['count'],2)
        self.assertEqual(report['a']['gainedCorrect'],1)
        self.assertEqual(report['a']['lostCorrect'],1)
        self.assertEqual(report['b']['gainedCorrect'],1)

    def test_empty_support_stays_empty(self):
        self.assertEqual(grouped_comparison([],np.array([]),np.array([])),{})

    def test_mismatched_predictions_fail(self):
        with self.assertRaises(ValueError):
            grouped_comparison([dict(group='a',changed=0)],np.array([]),np.array([.1]))


if __name__=='__main__':unittest.main()
