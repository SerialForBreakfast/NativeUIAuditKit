import unittest
import focus_direct_transition as d


class TemporalTests(unittest.TestCase):
    def test_campaign_batches_preserve_groups_without_execution(self):
        from unittest.mock import patch
        import plan_stationary_transitions as p
        doc=dict(version='retained-stationary-coverage-v1',sources=[],stationaryCandidates=0)
        doc['seal']=p.h.digest(doc)
        with patch.object(p.h,'read',return_value=doc),patch.object(p.h,'checked',return_value='unused'):
            plan=p.campaign({'path':'test','sha256':'test'})
        self.assertEqual(len(plan['batches']),6);self.assertFalse(plan['executionEligible'])
        ids=[v for b in plan['batches'] for v in b['caseIDs']]
        self.assertEqual(len(ids),len(set(ids)));self.assertEqual(len(ids),24)
        self.assertTrue(all(len(b['caseIDs'])==4 and b['maxSeconds']==600 for b in plan['batches']))
        for i in range(0,len(plan['cases']),2):
            self.assertEqual(plan['cases'][i]['condition'],'interior_switch')

    def test_geometry_initialization_and_legacy_prediction(self):
        t=d.torch_runtime();t.manual_seed(42);old=d.model(d.EXPOSURE_CONFIG)
        t.manual_seed(42);new=d.model(d.TEMPORAL_CONFIG)
        for name,value in old.state_dict().items():
            if not name.startswith('change.'):self.assertTrue(t.equal(value,new.state_dict()[name]),name)
        x=t.rand(2,6,64,96)
        self.assertTrue(t.equal(old(x)[:,:8],new(x)[:,:8]))
        clone=d.model(d.EXPOSURE_CONFIG);clone.load_state_dict(old.state_dict(),strict=True)
        self.assertTrue(t.equal(clone(x),old(x)))
        self.assertLess(sum(p.numel() for p in new.parameters()),sum(p.numel() for p in old.parameters()))

    def test_null_and_reversal_properties_not_semantic_labels(self):
        t=d.torch_runtime();t.manual_seed(42);net=d.model(d.TEMPORAL_CONFIG)
        a,b=t.rand(2,3,64,96),t.rand(2,3,64,96)
        x=t.cat((a,b),1);reverse=t.cat((b,a),1)
        self.assertTrue(t.equal(net.fields(x)[2],net.fields(reverse)[2]))
        same=t.cat((a,a),1);other=t.cat((b,b),1)
        self.assertTrue(t.equal(net.fields(same)[2],net.fields(other)[2]))
        self.assertEqual(net(x).shape,(2,9));self.assertTrue(t.isfinite(net(x)).all())
        net.zero_grad();net.fields(x)[2].sum().backward()
        self.assertTrue(all(p.grad is None for p in net.encoder.parameters()))
        self.assertTrue(any(p.grad is not None for p in net.change.parameters()))


if __name__=='__main__':unittest.main()
