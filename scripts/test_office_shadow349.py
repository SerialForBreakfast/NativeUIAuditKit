import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import office_shadow349 as s


class ShadowTests(unittest.TestCase):
    def test_fixed_decision_boundaries(self):
        self.assertEqual([s.decision(v) for v in [0, .15, .16, .84, .85, 1]],
                         ['stable', 'stable', 'abstain', 'abstain', 'changed', 'changed'])

    def test_scores_do_not_become_labels(self):
        with tempfile.TemporaryDirectory(dir=s.q.ROOT/'.build') as tmp:
            output=Path(tmp)
            config=dict(models={'a':{'path':'unused-a'},'b':{'path':'unused-b'}},
                        rows=[dict(id='pair', group='one-session', actionLinked=False)], inputs=[])
            s.q.save(output/'config.json',config)
            with patch.object(s,'OUT',output), patch.object(s.m,'check_inputs'), \
                 patch.object(s.m.a.e,'load_candidate'), \
                 patch.object(s.scoring,'score_rows',side_effect=[np.array([.1]),np.array([.9])]):
                s.run()
            result=s.q.load(output/'shadow.json')
            self.assertIsNone(result['accuracy'])
            self.assertFalse(result['trainingEligible'])
            self.assertFalse(result['productionEligible'])
            row=result['rows'][0]
            self.assertTrue(row['disagreement'])
            self.assertIsNone(row['focusChanged'])
            self.assertFalse(row['actionLinked'])
            self.assertEqual(row['group'],'one-session')


if __name__=='__main__':unittest.main()
