"""Software checks for pinned detector training. These checks do not establish model accuracy."""
import copy
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from PIL import Image
import research_queue as q
import detector_training419 as d
from template_inputs398 import pin


class DetectorTrainingTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='detector419-')
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        rows=[]
        for i,role in enumerate(('train','calibration')):
            image=self.root/(role+'.png'); Image.new('RGB',(32,32),(i*30,0,0)).save(image)
            rows.append(dict(id=role,role=role,group=role,trainingEligible=role=='train',
                image=pin(image),width=32,height=32,labelsComplete=True,
                controls=[{'class':'button','bounds':[2,2,10,10]}]))
        self.data=dict(version=d.VERSION,trainingAdmitted=True,names=['button'],rows=rows)

    def test_prepare(self):
        path,counts=d.prepare(self.data,self.root)
        self.assertTrue(path.is_file())
        self.assertEqual(counts,{'train':1,'calibration':1})
        with self.assertRaisesRegex(ValueError,'detector_training_dataset_exists'): d.prepare(self.data,self.root)

    def test_reject_before_output(self):
        mutations=[('role','audit','detector_training_roles'),
                   ('group','train','detector_training_group_leak'),
                   ('labelsComplete',False,'detector_training_incomplete_labels'),
                   ('width',33,'detector_training_dimensions')]
        for key,value,error in mutations:
            bad=copy.deepcopy(self.data);bad['rows'][1][key]=value
            with self.assertRaisesRegex(ValueError,error): d.prepare(bad,self.root)
            self.assertFalse((self.root/'dataset').exists())

    def test_duplicate_pixels_cannot_cross_roles(self):
        bad=copy.deepcopy(self.data);bad['rows'][1]['image']=bad['rows'][0]['image']
        with self.assertRaisesRegex(ValueError,'detector_training_pixel_conflict'): d.prepare(bad,self.root)

    def test_train_only_policy_is_explicit(self):
        data=copy.deepcopy(self.data)
        data.update(version=d.TRAIN_ONLY_VERSION,rows=[data['rows'][0]])
        with self.assertRaisesRegex(ValueError,'detector_training_calibration_policy'):d.prepare(data,self.root)
        data['calibrationPolicy']='none-fixed-last-training-diagnostics'
        bad=copy.deepcopy(data);bad['rows'][0]['role']='development'
        with self.assertRaisesRegex(ValueError,'detector_training_roles'):d.prepare(bad,self.root)
        path,counts=d.prepare(data,self.root)
        import yaml
        spec=yaml.safe_load(path.read_text())
        self.assertEqual(spec['val'],spec['train'])
        self.assertEqual(counts,{'train':1,'calibration':0})

    def test_checkpoint_review_actual_queue(self):
        import torch
        import hcf_templates395 as t
        import research_approval as approval
        checkpoint=self.root/'state.pt';torch.save(dict(epoch=8,optimizer={}),checkpoint)
        doc=dict(version='hcf-template-description-v1',id='checkpoint-review',owner='test-NUIAK',template='T90',
            question='Does incomplete checkpoint state reject restoration without rerunning training?',
            decision='Require scheduler and random state plus separate parity qualification before resume.',
            inputs=dict(checkpoint=pin(checkpoint)),parameters={},dependencies=[])
        queue=self.root/'queue';t.register(doc,queue)
        approval.approve(queue,doc['id'],'test','Software checkpoint review only.')
        self.assertEqual(q.run(queue,max_jobs=1,lock=self.root/'lock',job_ids=[doc['id']]),[(doc['id'],'complete')])
        report=q.load(queue/'jobs/checkpoint-review/attempts/1/out/benchmark_summary.json')
        self.assertFalse(report['resumeQualified'])
        self.assertEqual(report['missing'],['scheduler','random_state'])

    def test_training_wrapper_calls_resident_trainer(self):
        # This test qualifies the caller contract, not training or model quality.
        out=self.root/'jobs/train/attempts/1/out';out.mkdir(parents=True)
        init=self.root/'init.pt';init.write_bytes(b'test-only')
        membership=self.root/'membership.json';q.save(membership,self.data)
        config=self.root/'configuration.json'
        q.save(config,dict(initialization=pin(init),selection='fixed-last',patience=0))
        refs=dict(configuration=pin(config),initialization=pin(init),membership=pin(membership))
        q.save(out.parents[2]/'spec.json',dict(template=dict(inputs=refs)))
        def train(dataset,initialization,output,progress,weights,patience):
            self.assertEqual(weights,'last');self.assertEqual(patience,0)
            self.assertEqual(initialization,init)
            folder=output/'detector';folder.mkdir()
            (folder/'results.csv').write_text('epoch,train/box_loss,train/cls_loss,train/dfl_loss\n'+
                ''.join(f'{i},1,1,1\n' for i in range(1,31)))
            model=folder/'last.pt';model.write_bytes(b'software-fixture-not-a-model')
            return model
        with patch.object(d,'OUT',out),patch('train_yolo.train_native_hcf',side_effect=train): d.run()
        self.assertEqual(q.load(out/'fit.json')['epochs'],30)
        self.assertFalse(q.load(out/'fit.json')['modelAccepted'])


if __name__=='__main__':unittest.main()
