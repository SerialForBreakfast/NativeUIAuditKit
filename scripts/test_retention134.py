import unittest
import numpy as np
import retention134 as r


class RetentionTests(unittest.TestCase):
    def setUp(self):
        self.t = r.a.r.d.torch_runtime()
        self.z = np.zeros((3, 1153), dtype=np.float32)
        self.z[:, 0] = [3, -3, -5]
        self.z[0, 1] = self.z[1, 2] = 1
        self.y = np.array([1, 0, 0], dtype=np.float32)

    def test_zero_and_constraints(self):
        net = r.constrained_model(self.z, self.y)
        tx = self.t.from_numpy(self.z)
        self.t.testing.assert_close(net.change(tx).flatten(), tx[:, 0], rtol=0, atol=0)
        with self.t.no_grad():
            net.change.linear.weight[0, :2] = self.t.tensor([-100., 100.])
        margins = (2*self.t.from_numpy(self.y)-1)*net.change(tx).flatten()
        self.assertTrue(bool((margins >= r.FLOOR).all()))
        self.assertEqual(float(net.change(tx)[2, 0].detach()), -5.)

    def test_actual_trainer_and_materialization(self):
        net = r.constrained_model(self.z, self.y)
        zz = np.concatenate([self.z, self.z.copy()])
        # Opposing diagnostic objectives must not override original retention.
        yy = np.concatenate([self.y, 1-self.y])
        net, history = r.a.r.d.fit_change_features(net, self.t.from_numpy(zz), self.t.from_numpy(yy),
            dict(threads=2, seed=42, epochs=8, lr=.1))
        weights, _ = net.change.effective()
        replay = r.d.model()
        replay.change.linear.weight.data.copy_(weights.detach())
        tx = self.t.from_numpy(self.z)
        self.t.testing.assert_close(net.change(tx), replay.change(tx), rtol=0, atol=0)
        self.assertEqual(len(history), 8)
        self.assertTrue(bool(self.t.isfinite(weights).all()))
        self.assertTrue(bool((((2*self.t.from_numpy(self.y)-1)*net.change(tx).flatten()) >= r.FLOOR).all()))

    def test_invalid_and_uncertain_baseline(self):
        with self.assertRaises(ValueError):r.constrained_model(self.z, np.ones(2))
        self.z[0, 0] = .1
        with self.assertRaises(ValueError):r.constrained_model(self.z, self.y)
        self.z[0, 0] = np.nan
        with self.assertRaises(ValueError):r.constrained_model(self.z, self.y)

    def test_quantization_locality_and_padding(self):
        x = np.full((1, 6, 8, 12), .234, dtype=np.float32)
        mask = np.zeros_like(x, dtype=bool)
        mask[:, :, 2:6, 2:10] = True
        for mode in ('global8', 'left8', 'center8'):
            out = r.localized(x, mask, mode)
            np.testing.assert_array_equal(out[:, :3], x[:, :3])
            np.testing.assert_array_equal(out[~mask], x[~mask])
            changed = out != x
            self.assertTrue(changed.any())
            np.testing.assert_allclose(out[changed]*255, np.rint(out[changed]*255), atol=1e-5)
        out = r.localized(x, mask, 'left8')
        np.testing.assert_array_equal(out[:, 3:, :, 6:], x[:, 3:, :, 6:])
        with self.assertRaises(ValueError):r.localized(x, mask, 'unknown')
        with self.assertRaises(ValueError):r.localized(x, np.zeros_like(mask), 'global8')


if __name__ == '__main__':unittest.main()
