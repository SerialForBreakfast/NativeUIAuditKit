"""Check fixed labels and deterministic alternation without new data roles."""
import copy
import unittest
import numpy as np
import layout290 as run
import coverage290
import native_inspection290
import matched_states290

torch=run.torch


class LayoutTests(unittest.TestCase):
    def test_matched_states_keep_recipe_and_role(self):
        states=[dict(role='train',settled=True,recipeHash='recipe',runID='run',group='group',
                     focusID=str(i),image={'sha256':str(i)},metadata={'path':str(i)}) for i in range(4)]
        rows=matched_states290.make_pairs(states)
        self.assertEqual(len(rows),10)
        self.assertEqual(sum(r['changed'] for r in rows),6)
        states[0]['role']='validation'
        with self.assertRaisesRegex(ValueError,'state_role_or_focus'):matched_states290.make_pairs(states)

    def test_producer_agreement_keeps_uncertainty_separate(self):
        result=native_inspection290.agreement([.1,.5,.9],[0,1,0])
        self.assertEqual(result,dict(count=3,agreesWithProducer=1,disagreesWithProducer=1,uncertain=1))
        with self.assertRaises(ValueError):native_inspection290.agreement([float('nan')],[0])

    def test_visible_cell_and_invalid_bounds(self):
        self.assertEqual(coverage290.cell([90,0,10,10],(100,100)),(2,0))
        self.assertEqual(coverage290.cell([40,80,20,20],(100,100)),(1,2))
        for box in ([95,0,10,10],[-1,0,5,5],[0,0,0,5],[0,0,float('nan'),5]):
            with self.assertRaises(ValueError):coverage290.cell(box,(100,100))

    def test_replacement_and_reverse(self):
        x=np.zeros((4,6,128,192),np.float32); y=np.array([1,0,1,0],np.float32)
        value=np.ones((1,6,128,192),np.float32);value[:,:3]=.25
        rows={'rows':[dict(trainingIndex=0,role='train',changed=1)]}
        result=run.replace_rows(x,y,rows,value,2)
        self.assertTrue(np.array_equal(result[0],value[0]))
        self.assertTrue(np.array_equal(result[2,:3],value[0,3:]))
        self.assertFalse(x.any());self.assertFalse(result[1].any())
        rows['rows'][0]['role']='validation'
        with self.assertRaisesRegex(ValueError,'replacement_role'):run.replace_rows(x,y,rows,value,2)

    def test_identical_alternate_preserves_weights(self):
        torch.manual_seed(42);torch.set_num_threads(2)
        net=run.model.extend(run.base.worker.make_model(torch,paired_context=True))
        x=torch.rand(2,6,128,192);y=torch.tensor([0.,1.])
        config=dict(epochs=2,batch=2,lr=.0001,seed=42,threads=2)
        a,_=run.base.trainer.fit(copy.deepcopy(net),x,y,config)
        b,_=run.base.trainer.fit(copy.deepcopy(net),x,y,config,alternate_inputs=x.clone())
        self.assertTrue(all(torch.equal(v,b.state_dict()[k]) for k,v in a.state_dict().items()))
        with self.assertRaisesRegex(ValueError,'alternate_inputs'):
            run.base.trainer.fit(net,x,y,config,alternate_inputs=x[:1])

    def test_alternate_used_after_first_epoch(self):
        torch.manual_seed(42);torch.set_num_threads(2)
        net=run.model.extend(run.base.worker.make_model(torch,paired_context=True))
        x=torch.rand(2,6,128,192);y=torch.tensor([0.,1.])
        config=dict(epochs=1,batch=2,lr=.0001,seed=42,threads=2)
        a,_=run.base.trainer.fit(copy.deepcopy(net),x,y,config)
        b,_=run.base.trainer.fit(copy.deepcopy(net),x,y,config,alternate_inputs=torch.zeros_like(x))
        self.assertTrue(all(torch.equal(v,b.state_dict()[k]) for k,v in a.state_dict().items()))
        config['epochs']=2
        a,_=run.base.trainer.fit(copy.deepcopy(net),x,y,config)
        b,_=run.base.trainer.fit(copy.deepcopy(net),x,y,config,alternate_inputs=torch.zeros_like(x))
        self.assertTrue(any(not torch.equal(v,b.state_dict()[k]) for k,v in a.state_dict().items()))


if __name__=='__main__':unittest.main()
