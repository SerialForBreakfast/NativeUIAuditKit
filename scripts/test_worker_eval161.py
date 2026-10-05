import copy
import unittest
import torch
import worker_eval161 as e


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.net=torch.nn.Linear(2,1)
        c=dict(run_id='DTM050',seed=42,kind='augmented',rows=928,optimizer_updates=69600,batch=8,
            optimizer='Adam',lr=.001,loss='BCEWithLogitsLoss unweighted mean',device='cuda:0',dtype='float32',
            amp=False,tf32=False,compile=False,selection='fixed-last',thresholds=[.15,.85],deterministic=True,
            pool_adapter='fixed8x8-equivalent-v1',maximum_seconds=28800)
        self.saved=dict(version='robust153-checkpoint-v1',pins=dict(configuration=c),
            cursor=dict(epoch=600,next_batch=0,steps=69600),model=copy.deepcopy(self.net.state_dict()))
    def test_valid(self):self.assertIs(e.checked(torch,self.net,self.saved,'DTM050'),self.net)
    def test_incomplete(self):
        self.saved['cursor']['steps']-=1
        with self.assertRaisesRegex(ValueError,'completion_config'):e.checked(torch,self.net,self.saved,'DTM050')
    def test_threshold_tuning_rejected(self):
        self.saved['pins']['configuration']['thresholds']=[.2,.8]
        with self.assertRaisesRegex(ValueError,'completion_config'):e.checked(torch,self.net,self.saved,'DTM050')
    def test_nonfinite(self):
        self.saved['model']['weight'][0,0]=float('nan')
        with self.assertRaisesRegex(ValueError,'state_tensor'):e.checked(torch,self.net,self.saved,'DTM050')
    def test_unexpected_state(self):
        self.saved['model']['extra']=torch.zeros(1)
        with self.assertRaisesRegex(ValueError,'state_keys'):e.checked(torch,self.net,self.saved,'DTM050')


if __name__=='__main__':unittest.main()
