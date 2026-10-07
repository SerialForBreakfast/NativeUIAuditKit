"""Check the matched recipe design and regression decision without capture."""
import copy
import unittest
from unittest.mock import patch
import transition243 as t


class CampaignTests(unittest.TestCase):
    def test_partial_intake_cannot_archive(self):
        with patch.object(t,'capture_tool') as tool, patch.object(t.h,'read',return_value={
                'review':{'reviewed':31,'expected':32}}):
            with self.assertRaisesRegex(ValueError,'partial_intake'):
                t.archive_current()
            tool.return_value.prior.cli.assert_not_called()

    def test_matrix_changes_only_artwork_and_background(self):
        c=dict(asset_pack=dict(assets=[dict(sha256='a'),dict(sha256='b')]),
               contents={'one':dict(asset=dict(sha256='a')),'two':dict(asset=dict(sha256='b'))},
               background=dict(colors=[1,2]),regions=[dict(id='native-control')])
        entry=dict(recipe=dict(seed=7,appearance=dict(composition=c)))
        source=dict(recipes=[entry,copy.deepcopy(entry)])
        before=copy.deepcopy(source)
        rows=t.matrix(source)
        self.assertEqual(source,before)
        self.assertEqual(len(rows),8)
        self.assertEqual(len({r['id'] for r in rows}),8)
        self.assertEqual({r['role'] for r in rows},{'training'})
        self.assertEqual({r['recipe']['seed'] for r in rows},{7})
        for r in rows:
            composition=r['recipe']['appearance']['composition']
            self.assertEqual(composition['regions'],c['regions'])
            self.assertEqual(composition['asset_pack'],c['asset_pack'])

    def test_distraction_regression_vetoes_native_gain(self):
        before=dict(reserved=dict(correct=52),development=dict(correct=44),artwork_0=dict(correct=0),original_capture=dict(correct=49))
        after=dict(reserved=dict(correct=52),development=dict(correct=48),artwork_0=dict(correct=4),original_capture=dict(correct=72))
        baseline=dict(left=dict(summary=dict(correct=226)))
        stress=dict(left=dict(correct=226,previousCorrectLost=0))
        self.assertTrue(t.gate(before,after,baseline,stress,0))
        stress['left']['previousCorrectLost']=1
        self.assertFalse(t.gate(before,after,baseline,stress,0))
        stress['left']=dict(correct=174,previousCorrectLost=52)
        self.assertFalse(t.gate(before,after,baseline,stress,0))

    def test_replay_and_reserved_regressions_veto(self):
        before=dict(reserved=dict(correct=52),development=dict(correct=44),artwork_0=dict(correct=0),original_capture=dict(correct=49))
        after=dict(reserved=dict(correct=52),development=dict(correct=48),artwork_0=dict(correct=4),original_capture=dict(correct=72))
        self.assertFalse(t.gate(before,after,{}, {},1))
        after['reserved']['correct']=51
        self.assertFalse(t.gate(before,after,{}, {},0))


if __name__=='__main__':unittest.main()
