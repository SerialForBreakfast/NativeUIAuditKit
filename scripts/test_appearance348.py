import unittest
from unittest.mock import patch
import appearance348 as m
import numpy as np


class AppearanceTests(unittest.TestCase):
    def test_comparison_keeps_losses_separate(self):
        rows=[dict(id=str(i),changed=y,sourceDomain='test',condition='case',group='one')
              for i,y in enumerate([0,1,1])]
        result=m.report(rows,dict(control=[.1,.9,.5],gamma=[.9,.9,.9]),[.1,.9,.1])
        counts=result['gammaAgainstControl']['test/case/one']
        self.assertEqual(counts['lost'],1)
        self.assertEqual(counts['gained'],1)
        self.assertEqual(counts['falseChange'],1)

    def test_changed_inputs_fail(self):
        with patch.object(m.q,'digest',return_value='changed'):
            with self.assertRaisesRegex(ValueError,'input_changed'):
                m.check_inputs(dict(inputs=[dict(path='a',sha256='original')]))

    def test_counts_reject_missing_predictions(self):
        with self.assertRaisesRegex(ValueError,'count_mismatch'):
            m.report([dict(changed=0)],dict(control=[],gamma=[]),[])

    def test_training_preserves_inputs_and_frozen_layers(self):
        m.t.set_num_threads(2);m.t.manual_seed(42)
        net=m.a.e.load_candidate(m.a.e.OUT/'run/last.pt')
        x=m.t.rand(2,6,128,192);d=m.t.rand(2,12,128,192);y=m.t.tensor([0.,1.])
        before=x.clone();detail=d.clone();state={k:v.clone() for k,v in net.state_dict().items()}
        reference=m.raw_logits(net,x.numpy(),d.numpy())
        settings=dict(epochs=1,lr=.0001,batch=2,seed=42,threads=2,detailOnly=True)
        net,_=m.a.b.trainer.fit(net,x,y,settings,detail_inputs=d,auxiliary_inputs=x.clone(),
            auxiliary_detail=d.clone(),auxiliary_weight=.25,preservation_logits=reference,
            auxiliary_preservation_logits=reference,preservation_weight=1.)
        self.assertTrue(m.t.equal(x,before));self.assertTrue(m.t.equal(d,detail))
        changes=[key for key,value in net.state_dict().items() if not m.t.equal(value,state[key])]
        self.assertTrue(changes)
        self.assertTrue(all(key.startswith(('change.detail.','change.correction.')) for key in changes))


if __name__=='__main__':unittest.main()
