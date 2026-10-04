"""Software-only export graph tests; no CoreML conversion or new model artifact."""
import unittest
from unittest.mock import patch
import focus_identity_residual as r
import adapt_reflow117 as a
from transition_shadow_export import residual_wrapper


class ResidualGraphTests(unittest.TestCase):
    def setUp(self):
        self.t=r.d.torch_runtime();self.t.set_num_threads(2);self.t.manual_seed(42)
        self.net=r.model(r.d.model(r.d.PAIRED_TEMPORAL_CONFIG))
        with self.t.no_grad():self.net.change.linear.weight.normal_(0,.1)
        self.state=dict(version=r.VERSION,configuration=a.CONFIG,state=self.net.state_dict())

    def test_export_graph_matches_runtime_and_identity(self):
        wrapper=residual_wrapper(self.state)
        with self.t.no_grad():
            x=self.t.rand(1,6,128,192)
            self.assertTrue(self.t.equal(wrapper(x),r.c.score_change(self.net,x,a.CONFIG)))
            x[:,3:]=x[:,:3]
            expected=self.net.base_readout(self.net.encoder(self.t.cat((self.t.zeros_like(x[:,:3]),x),1))).sigmoid().flatten()
            self.assertTrue(self.t.equal(wrapper(x),expected))

    def test_wrong_version_config_and_incomplete_state(self):
        for state in (dict(self.state,version='unknown'),dict(self.state,configuration={}),dict(self.state,state={})):
            with self.assertRaises((ValueError,RuntimeError)):residual_wrapper(state)

    def test_orchestration_rejects_missing_compiled_model_before_writes(self):
        import transition_shadow118 as p
        with patch.object(p,'BASE',r.h.ROOT/'.build/missing-shadow118-test'),patch.object(p.v,'tree') as tree:
            with self.assertRaisesRegex(ValueError,'compiled_model_missing'):p.prepare()
            tree.assert_not_called()


if __name__=='__main__':unittest.main()
