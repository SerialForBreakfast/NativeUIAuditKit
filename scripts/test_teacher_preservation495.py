"""Positive and negative checks for training-only teacher preservation."""
import copy
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
import torch
from teacher_preservation495 import Preservation, validate_anchors


class TrainerIntegrationTests(unittest.TestCase):
    def test_actual_trainer_and_reference_failures(self):
        import research_queue as q
        import train_focus_ring_detector as trainer
        from experiment_templates import pin
        from focus_ring_backbone import mobilenetv4_conv_small
        from PIL import Image
        root = q.ROOT/'.build/teacher495-tests'; root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as folder:
            base = Path(folder); rows = []
            for i in range(2):
                path = base/f'{i}.png'; Image.new('RGB', (256, 256), (i*100, 40, 90)).save(path)
                rows.append(dict(id=str(i), path=str(path), sha256=q.digest(path), role='train',
                                 group='training', profile='standard', label=i))
            checkpoint = base/'initial.pt'
            torch.save(dict(state_dict=mobilenetv4_conv_small(num_classes=1).state_dict()), checkpoint)
            anchors = base/'anchors.json';q.save(anchors, dict(version='teacher-anchors-v1', rows=rows))
            config = dict(model=pin(checkpoint), anchors=pin(anchors), weight=1.0)
            device = torch.device
            class DeviceMeta(type):
                def __instancecheck__(cls, value): return isinstance(value, device)
            class CPUDevice(metaclass=DeviceMeta):
                def __new__(cls, name): return device('cpu' if name == 'mps' else name)
            with patch.object(torch.backends.mps, 'is_available', return_value=True), \
                 patch.object(torch, 'device', CPUDevice), \
                 patch.object(torch.mps, 'get_rng_state', side_effect=torch.get_rng_state):
                out = base/'fit';out.mkdir()
                result = trainer.train_native_hcf(rows, checkpoint, out, profile='balanced',
                    selection='fixed-last', stop_after_epoch=1, teacher_preservation=config)
                self.assertEqual(result['exposure']['optimizerUpdates'], 1)
                report = q.load(out/'teacher-preservation.json')
                self.assertEqual(report['anchorPresentations'], 2)
                self.assertTrue(report['teacherUnchanged'])
                self.assertTrue((out/'final.pt').is_file())
                with self.assertRaisesRegex(ValueError, 'teacher_requires_full_fixed_last_restart'):
                    trainer.train_native_hcf(rows, checkpoint, out, teacher_preservation=config, freeze_encoder=True)
                from teacher_preservation495 import prepare
                changed = dict(config, anchors=dict(config['anchors'], sha256='0'*64))
                with self.assertRaises(ValueError): prepare(changed, rows, lambda r: None, device('cpu'))


class TeacherTests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(2)
        self.rows = [dict(id=str(i), role='train', label=i % 2, sha256=str(i)) for i in range(4)]
        self.x = torch.tensor([[0., 1.], [1., 0.], [1., 1.], [0., 0.]])
        self.teacher = torch.nn.Linear(2, 1)

    def tensors(self, rows):
        return self.x[[int(r['id']) for r in rows]], None

    def test_real_gradients_and_teacher_integrity(self):
        student = copy.deepcopy(self.teacher)
        p = Preservation(self.teacher, self.rows, self.rows, self.tensors)
        self.assertAlmostEqual(p.loss(student(self.x), self.rows).item(), 0, places=6)
        with torch.no_grad(): student.bias.add_(1)
        optimizer = torch.optim.SGD(student.parameters(), lr=.1)
        before = p.loss(student(self.x), self.rows).item()
        for _ in range(5):
            optimizer.zero_grad(); p.loss(student(self.x), self.rows).backward(); optimizer.step()
        self.assertLess(p.loss(student(self.x), self.rows).item(), before)
        self.assertTrue(p.report()['teacherDetached'])
        self.assertTrue(all(t.grad is None for t in self.teacher.parameters()))
        with torch.no_grad(): self.teacher.bias.add_(1)
        with self.assertRaisesRegex(ValueError, 'teacher_state_changed'): p.verify()

    def test_missing_anchors_do_not_change_loss(self):
        p = Preservation(self.teacher, self.rows, self.rows[:2], self.tensors)
        logits = torch.ones(2, requires_grad=True)
        loss = p.loss(logits, self.rows[2:]);loss.backward()
        self.assertEqual(loss.item(), 0)
        self.assertTrue(torch.equal(logits.grad, torch.zeros(2)))

    def test_roles_duplicates_and_changed_rows_fail(self):
        for anchors in [[], self.rows[:1], [self.rows[0], self.rows[0]],
                        [dict(self.rows[0], role='development'), self.rows[1]],
                        [dict(self.rows[0], sha256='changed'), self.rows[1]]]:
            with self.assertRaises(ValueError):validate_anchors(self.rows, anchors)
        for weight in [True, 0, -1, float('nan'), float('inf')]:
            with self.assertRaisesRegex(ValueError, 'teacher_weight'):
                Preservation(self.teacher, self.rows, self.rows, self.tensors, weight=weight)

    def test_real_backbone_has_detached_targets(self):
        from focus_ring_backbone import mobilenetv4_conv_small
        model = mobilenetv4_conv_small(num_classes=1)
        x = torch.rand(2, 3, 256, 256)
        p = Preservation(model, self.rows[:2], self.rows[:2], lambda rows: (x[:len(rows)], None))
        logits = torch.ones(2, requires_grad=True)
        p.loss(logits, self.rows[:2]).backward()
        self.assertTrue(torch.isfinite(logits.grad).all())
        p.verify()


if __name__ == '__main__': unittest.main()
