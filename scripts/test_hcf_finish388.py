"""Test fixed training settings and fail-closed reports without model execution."""
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch
import train_yolo
import hcf_factor_train376 as factor
import hcf_finish388 as finish


class FinishTests(unittest.TestCase):
    def test_fixed_epochs_disable_early_stop(self):
        with tempfile.TemporaryDirectory(dir=finish.q.ROOT/'.build/debug-output') as name:
            root=Path(name); initial=root/'weights.pt'; initial.write_bytes(b'test')
            model=MagicMock()
            with patch.dict(sys.modules, {'ultralytics': SimpleNamespace(YOLO=MagicMock(return_value=model))}):
                train_yolo.train_native_hcf(root/'dataset.yaml',initial,root,patience=0)
            self.assertEqual(model.train.call_args.kwargs['patience'],0)
            self.assertEqual(model.train.call_args.kwargs['epochs'],30)
            self.assertEqual(model.train.call_args.kwargs['seed'],371)

    def test_invalid_patience_fails_before_import(self):
        for value in (-1, True, 30):
            with self.assertRaisesRegex(ValueError,'hcf_patience_choice'):
                train_yolo.train_native_hcf(None,None,None,patience=value)

    def test_seed_scope(self):
        for seed in (371,372,373):
            factor.validate_config(dict(profile='balanced',deduplicate=True,seed=seed))
        with self.assertRaisesRegex(ValueError,'seed_changed'):
            factor.validate_config(dict(profile='balanced',deduplicate=True,seed=374))

    def test_missing_reports_fail(self):
        with patch.object(finish,'inputs',return_value=({},[])):
            with self.assertRaisesRegex(ValueError,'finish_reports_missing'):finish.finish()

    def test_loss_drives_next_action_without_acceptance(self):
        methods={k:dict(losses=['retained-1'] if k=='full-screen-candidate' else []) for k in
            ('bright-closed-stroke-v1','crop-baseline','crop-candidate','full-screen-candidate')}
        docs={'hcf388-method-decision':dict(comparisons=methods),
              'hcf388-seed-review':dict(previousSuccessesPreserved=False)}
        with tempfile.TemporaryDirectory(dir=finish.q.ROOT/'.build/debug-output') as name:
            with patch.object(finish,'OUT',Path(name)),patch.object(finish,'inputs',return_value=(docs,[])):
                finish.finish()
                result=finish.q.load(Path(name)/'hcf-study-report.json')
                self.assertFalse(result['modelAccepted'])
                self.assertIn('Diagnose detector losses before more training.',result['nextActions'])


if __name__=='__main__':unittest.main()
