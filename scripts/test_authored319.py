"""Check matched authored labels, exposure, and auxiliary detail inputs."""
import unittest
from unittest.mock import patch
import numpy as np
import authored319 as a


class AuthoredTests(unittest.TestCase):
    def test_frame_rejects_wrong_version_and_focus(self):
        base=dict(schemaVersion='contract-v1-headless-focus',canvasWidth=1920,canvasHeight=1080,
                  nodes=[dict(id='a',isFocused=True)],focusedNodeID='a')
        for doc in (dict(base,schemaVersion='unknown'),dict(base,focusedNodeID='b'),dict(base,canvasWidth=1)):
            with patch.object(a.b,'read',return_value=doc):
                with self.assertRaises(ValueError):a.frame(a.OUT,'grid','a')

    def test_pair_conditions(self):
        rows=a.pair_rows([['a','b'],['c','d']],'group','grid')
        self.assertEqual(len(rows),12)
        self.assertEqual(sum(x['changed'] for x in rows),4)
        self.assertTrue(all((x['images'][0]==x['images'][1])==(x['condition']=='identical') for x in rows))
        self.assertEqual({x['role'] for x in rows},{'train'})
        self.assertEqual({tuple(x['images']) for x in rows if x['condition']=='artwork-only'},
                         {('a','c'),('c','a'),('b','d'),('d','b')})

    def test_label_matched_schedule(self):
        rows=a.pair_rows([['a','b'],['c','d']],'group','grid')
        labels=np.array([0,1,0,1]*10)
        ids=a.schedule(labels,rows)
        np.testing.assert_array_equal(labels,[rows[i]['changed'] for i in ids])
        np.testing.assert_array_equal(ids,a.schedule(labels,rows))
        with self.assertRaises(ValueError):a.schedule(labels,[dict(changed=0)])

    def test_twelve_channel_auxiliary_fit(self):
        t=a.t;t.set_num_threads(2);t.manual_seed(42)
        net=a.r.extend(a.r.s.c.model.extend(a.b.worker.make_model(t,paired_context=True)),2)
        x=t.rand(2,6,128,192);details=a.r.encoded_details(x,2)
        config=dict(epochs=1,lr=.0001,batch=2,seed=42,threads=2,detailOnly=True)
        _,history=a.b.trainer.fit(net,x,t.tensor([0.,1.]),config,detail_inputs=details,
            auxiliary_inputs=x,auxiliary_detail=details,auxiliary_weight=.25)
        self.assertEqual(history[0]['updates'],1)
        with self.assertRaisesRegex(ValueError,'auxiliary_shape'):
            a.b.trainer.fit(net,x,t.tensor([0.,1.]),config,detail_inputs=details,
                auxiliary_inputs=x,auxiliary_detail=x,auxiliary_weight=.25)


if __name__=='__main__':unittest.main()
