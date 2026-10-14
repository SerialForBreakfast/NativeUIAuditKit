"""Check aligned inputs, initial parity, gradients, and saved model contracts."""
import unittest
import copy
import tempfile
import context309 as m

torch = m.torch


class ContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(2)

    def model(self, local=True):
        return m.extend(m.c.model.extend(m.base.worker.make_model(torch, paired_context=True)), local)

    def test_identical_fallback(self):
        a = torch.rand(2, 3, 128, 192); x = torch.cat((a, a), 1)
        self.assertTrue(torch.equal(x, m.aligned_view(x)))

    def test_alignment_reversal_and_edges(self):
        for y, x in [(0, 0), (0, 189), (125, 0), (125, 189), (64, 96)]:
            value = torch.zeros(1, 6, 128, 192)
            value[:, 3:, y:y+3, x:x+3] = 1
            crop = m.aligned_view(value)
            reverse = m.aligned_view(torch.cat((value[:, 3:], value[:, :3]), 1))
            self.assertTrue(torch.equal(crop, torch.cat((reverse[:, 3:], reverse[:, :3]), 1)))
            self.assertGreater(float(crop[:, 3:].sum()), float(value[:, 3:].sum()))
            self.assertEqual(float(crop[:, :3].sum()), 0)
            self.assertEqual(crop.shape, value.shape)

    def test_wrong_shape(self):
        with self.assertRaises(ValueError): m.aligned_view(torch.zeros(1, 6, 32, 32))

    def test_initial_parity_and_capacity(self):
        original = m.c.model.extend(m.base.worker.make_model(torch, paired_context=True))
        values = torch.rand(2, 6, 128, 192)
        expected = original.change(original.change_inputs(values))
        models = [m.extend(copy.deepcopy(original), local) for local in (False, True)]
        for net in models:
            self.assertTrue(torch.equal(expected, net.change(net.change_inputs(values))))
        self.assertEqual(sum(p.numel() for p in models[0].parameters()), sum(p.numel() for p in models[1].parameters()))

    def test_existing_trainer_and_frozen_geometry(self):
        net = self.model(); x = torch.rand(2, 6, 128, 192); y = torch.tensor([0., 1.])
        before = {k: v.clone() for k, v in net.state_dict().items() if not k.startswith('change.')}
        net, history = m.base.trainer.fit(net, x, y, dict(epochs=1, batch=2, lr=.0001, seed=42, threads=2))
        self.assertEqual(len(history), 1)
        self.assertTrue(all(torch.equal(v, net.state_dict()[k]) for k, v in before.items()))
        self.assertGreater(float(net.change.correction.weight.detach().abs().sum()), 0)

    def test_checkpoint_and_real_scorer(self):
        for local in (True, False):
            net = self.model(local).eval()
            values = torch.rand(3, 6, 128, 192).numpy()
            with tempfile.TemporaryDirectory(dir=m.base.ROOT/'.build') as folder:
                path = m.base.Path(folder)/'model.pt'
                torch.save(dict(state=net.state_dict(), representation=m.VERSION, local=local), path)
                loaded = m.load_candidate(path)
                self.assertTrue((m.base.worker.score(net, values) == m.base.worker.score(loaded, values)).all())
                torch.save(dict(state=net.state_dict(), representation='unknown', local=local), path)
                with self.assertRaises(ValueError): m.load_candidate(path)

    def test_metrics_keep_abstentions_separate(self):
        from report_context309 import metrics
        result = metrics([.01, .5, .99], [1, 1, 0])
        self.assertEqual(result['missedChanges'], 1)
        self.assertEqual(result['changeAbstentions'], 1)
        self.assertEqual(result['falseChanges'], 1)
        for labels in ([0.4], [float('nan')], [2]):
            with self.assertRaises(ValueError): metrics([.5], labels)


if __name__ == '__main__': unittest.main()
