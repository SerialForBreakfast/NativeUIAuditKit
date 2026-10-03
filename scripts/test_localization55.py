"""Loss geometry and closed configuration compatibility, not model qualification."""
import unittest
import focus_direct_transition as d
import evaluate_direct_transition as e


class LocalizationTests(unittest.TestCase):
    def test_identical_and_disjoint_giou_gradients(self):
        torch=d.torch_runtime()
        target=torch.tensor([[.7,.7,.2,.2]])
        self.assertAlmostEqual(float(d.box_loss(target,target,d.LOCALIZATION_CONFIG)),0,places=6)
        prediction=torch.tensor([[.2,.2,.2,.2]],requires_grad=True)
        loss=d.box_loss(prediction,target,d.LOCALIZATION_CONFIG)
        self.assertGreater(float(loss.detach()),1)
        loss.backward();self.assertTrue(bool(torch.isfinite(prediction.grad).all()))
        self.assertLess(float(prediction.grad[0,0]),0)
        self.assertGreater(float(prediction.grad.abs().sum()),0)

    def test_legacy_loss_and_closed_configs(self):
        torch=d.torch_runtime();p=torch.ones((2,8))*.4;t=torch.ones((2,8))*.2
        self.assertAlmostEqual(float(d.box_loss(p,t,d.CONFIG)),.04,places=6)
        for config in (dict(d.LOCALIZATION_CONFIG,epochs=31),dict(d.CONFIG,boxLoss='unknown')):
            self.assertFalse(d.valid_configuration(config))
            with self.assertRaises(ValueError):d.box_loss(p,t,config)

    def test_endpoint_errors_do_not_hide_invalid_predictions(self):
        row=e.localization([[10,20,20,10],None],[[10,20,20,10],[0,0,10,10]],[100,100])
        report=e.endpoint_summary([{'localization':row}])
        self.assertEqual(report['before']['meanIoU'],1)
        self.assertEqual(report['before']['meanCenterError'],[0,0])
        self.assertEqual(report['after']['invalid'],1)
        self.assertEqual(report['after']['localized'],0)
        self.assertIsNone(report['after']['meanCenterError'])


if __name__=='__main__':unittest.main()
