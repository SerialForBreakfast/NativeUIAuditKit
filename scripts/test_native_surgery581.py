"""Test recovered ancestry with generated software evidence, not quality measurements."""
import copy
import tempfile
import unittest
from pathlib import Path
import torch
import research_queue as q
from template_inputs398 import pin
import weight_surgery_queue as w


class RecoveredAncestryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='ancestry581-');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.job=self.root/'source';self.folder=self.job/'attempts/1/out';self.folder.mkdir(parents=True)
        state=dict(model_name='mobilenetv4_conv_small',state_dict={'sample':torch.ones(1)},epoch=30,loss=1.)
        self.base=self.root/'base.pt';torch.save(state,self.base);self.base_ref=pin(self.base)
        self.donor=self.folder/'final.pt';torch.save(dict(state,state_dict={'sample':torch.zeros(1)}),self.donor)
        self.spec=dict(authority='training',adapter=dict(steps=['focus_replay568.train']),training=dict(initialization=self.base_ref,epochs=30))
        q.save(self.job/'spec.json',self.spec)
        self.fit=dict(version='native-focus-fit568-v1',initialization=self.base_ref,epochs=30,validationCropsRead=0)
        q.save(self.folder/'fit.json',self.fit);q.save(self.folder/'history.json',[dict(epoch=i,loss=1.) for i in range(1,31)])
        outputs,_=q.inventory(self.folder,100000000)
        result=dict(status='failed',reason='training_history_loss_invalid',returnCode=0,specSHA256=q.text_digest(self.spec),outputs=outputs)
        self.result=self.folder.parent/'result.json';q.save(self.result,result)
        self.normalized=self.root/'normalized.json';q.save(self.normalized,self.fit)
        self.proof=dict(ancestryVerified=True,method='strict-checkpoint-training-initialization',additionalTraining=False,
            ancestry=dict(base=self.base_ref),originalFailedResult=pin(self.result),training=pin(self.folder/'fit.json'),normalizedTraining=pin(self.normalized))
        self.p=self.root/'proof.json';self.c=self.root/'model.json';self.write()
    def write(self):
        q.save(self.p,self.proof,replace=self.p.exists())
        self.model=dict(version='weight-surgery-model-v1',checkpoint=pin(self.donor),edit=pin(self.p),threshold=.85)
        q.save(self.c,self.model,replace=self.c.exists())
    def run_ancestry(self):return w.ancestry(self.base_ref,pin(self.donor),pin(self.p),pin(self.c))
    def test_verified_record_is_supported(self):
        self.assertTrue(self.run_ancestry()['verified'])
    def test_wrong_parent_unverified_and_extra_training_fail(self):
        old=copy.deepcopy(self.proof)
        for change in [dict(ancestryVerified=False),dict(additionalTraining=True),dict(ancestry=dict(base={'path':'other','sha256':'0'*64}))]:
            self.proof=dict(old,**change);self.write()
            with self.assertRaises(ValueError):self.run_ancestry()
    def test_recovered_native_checkpoint_needs_its_run_identity(self):
        state=torch.load(self.donor,map_location='cpu',weights_only=True)
        state.pop('model_name');state['run_name']='focus568-native'
        self.fit['arm']='native';q.save(self.folder/'fit.json',self.fit,replace=True)
        q.save(self.normalized,self.fit,replace=True);torch.save(state,self.donor)
        result=q.load(self.result);result['outputs']=q.inventory(self.folder,100000000)[0]
        q.save(self.result,result,replace=True)
        self.proof.update(originalFailedResult=pin(self.result),training=pin(self.folder/'fit.json'),normalizedTraining=pin(self.normalized));self.write()
        self.assertTrue(self.run_ancestry()['verified'])
        state['run_name']='unrelated';torch.save(state,self.donor)
        result['outputs']=q.inventory(self.folder,100000000)[0];q.save(self.result,result,replace=True)
        self.proof['originalFailedResult']=pin(self.result);self.write()
        with self.assertRaisesRegex(ValueError,'model_name_or_nonfinite'):self.run_ancestry()

    def test_changed_output_and_incomplete_history_fail(self):
        p=self.folder/'history.json';q.save(p,[dict(epoch=i,loss=1.) for i in range(1,30)],replace=True)
        with self.assertRaisesRegex(ValueError,'outputs'):self.run_ancestry()
    def test_failed_process_cannot_be_recovered_as_ancestry(self):
        d=q.load(self.result);d['returnCode']=1;q.save(self.result,d,replace=True)
        self.proof['originalFailedResult']=pin(self.result);self.write()
        with self.assertRaisesRegex(ValueError,'failure'):self.run_ancestry()
    def test_two_recipe_descriptions_use_the_actual_queue(self):
        import hcf_templates395 as templates
        import experiment_batch402 as batches
        import research_approval as approval
        from focus_ring_backbone import mobilenetv4_conv_small
        torch.manual_seed(581);model=mobilenetv4_conv_small()
        base_state=model.state_dict();donor_state={k:v.clone() for k,v in base_state.items()}
        for key in donor_state:
            if key.startswith(('classifier.','conv_head.')) and donor_state[key].is_floating_point():donor_state[key]+=.01
        torch.save(dict(model_name='mobilenetv4_conv_small',state_dict=base_state),self.base);self.base_ref=pin(self.base)
        torch.save(dict(model_name='mobilenetv4_conv_small',state_dict=donor_state,epoch=30,loss=1.),self.donor)
        self.spec['training']['initialization']=self.base_ref;q.save(self.job/'spec.json',self.spec,replace=True)
        self.fit['initialization']=self.base_ref;q.save(self.folder/'fit.json',self.fit,replace=True);q.save(self.normalized,self.fit,replace=True)
        result=q.load(self.result);result.update(specSHA256=q.text_digest(self.spec),outputs=q.inventory(self.folder,100000000)[0]);q.save(self.result,result,replace=True)
        self.proof.update(ancestry=dict(base=self.base_ref),originalFailedResult=pin(self.result),training=pin(self.folder/'fit.json'),normalizedTraining=pin(self.normalized));self.write()
        jobs=[]
        for arm in ('classifier','head','donor-base-bn'):
            path=self.root/(arm+'.json');q.save(path,dict(version='weight-surgery-recipe-v1',arm=arm))
            jobs.append(dict(version='hcf-template-description-v1',id='ancestry581-'+arm,owner='test-NUIAK',template='T94',
                question='Does the actual adapter verify recovered ancestry before a restricted parameter edit?',
                decision='Generated software records only. Verify immutable tensors and exact candidate roundtrip.',
                inputs=dict(base=self.base_ref,donor=pin(self.donor),preflight=pin(self.p),completion=pin(self.c),recipe=pin(path)),parameters={},dependencies=[]))
        queue=self.root/'queue';batch=dict(version='experiment-batch-v1',jobs=jobs)
        docs=batches.compile_batch(batch,queue)
        for doc in docs:
            templates.register(doc,queue);approval.approve(queue,doc['id'],'test','Generated software-only ancestry and recipe qualification.')
        result=q.run(queue,max_jobs=3,lock=self.root/'worker.lock')
        self.assertEqual({state for _,state in result},{'complete'});self.assertEqual(len(result),3)
        for doc in docs:
            out=queue/'jobs'/doc['id']/'attempts/1/out';edit=q.load(out/'edit.json')
            self.assertTrue(edit['ancestryVerified']);self.assertFalse(edit['modelAccepted'])
            if edit['arm']=='donor-base-bn':
                actual=torch.load(out/'candidate.pt',map_location='cpu',weights_only=True)['state_dict']
                for k,_ in model.named_parameters():self.assertTrue(torch.equal(actual[k],donor_state[k]))
                for k,_ in model.named_buffers():self.assertTrue(torch.equal(actual[k],base_state[k]))
            else:
                self.assertTrue(all(k.split('.')[0] in ('classifier','conv_head') for k in edit['changedParameters']))

    def test_model_pointer_and_threshold_cannot_change(self):
        for key,value in [('threshold',.01),('checkpoint',self.base_ref)]:
            changed=dict(self.model,**{key:value});q.save(self.c,changed,replace=True)
            with self.assertRaisesRegex(ValueError,'binding'):self.run_ancestry()

if __name__=='__main__':unittest.main()
