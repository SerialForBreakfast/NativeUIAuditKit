"""Exercise real checkpoint intake without fitting a model."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import numpy as np
import torch
import transition249_worker as w
from transition249_result_checks import review

ROOT=Path(__file__).resolve().parents[1]


class IntakeTests(unittest.TestCase):
    def setUp(self):
        (ROOT/'.build').mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=ROOT/'.build',prefix='intake249-')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.package=self.root/'package';self.package.mkdir()
        self.returned=self.root/'returned';self.returned.mkdir();self.output=self.root/'review.json'
        torch.set_num_threads(2);torch.manual_seed(123)
        self.net=w.make_model(torch,paired_context=True);self.net.eval()
        torch.save({'state':self.net.state_dict()},self.package/'initializer.pt')
        x=np.zeros((2,6,16,24),dtype=np.float32);x[1,3:]=.5
        names=['native.npy','replay.npy','reverse_native.npy','reverse_replay.npy','global8.npy','left8.npy','center8.npy']
        for name in names:np.save(self.package/name,x)
        self.write(self.package/'membership.json',{'rows':[
            {'changed':0,'role':'train','conditions':[]},
            {'changed':1,'role':'reserved','conditions':[]}],'replayLabels':[0,1],
            'provenanceNotes':['fixture-only']*11000})
        runs=[{'id':name,'configuration':{'epochs':120,'seed':42}} for name in ['DTM068','DTM069','DTM070']]
        files={p.name:{'bytes':p.stat().st_size,'sha256':w.digest(p)} for p in self.package.iterdir()}
        self.write(self.package/'manifest.json',{'version':'transition249-v1','files':files,'evaluation':names,'runs':runs})
        self.pin=w.digest(self.package/'manifest.json')
        probs=w.score(self.net,x).tolist()
        for run in runs:
            folder=self.returned/run['id'];folder.mkdir()
            torch.save({'state':self.net.state_dict(),'manifestSHA256':self.pin,'run':run},folder/'last.pt')
            self.write(folder/'result.json',{'id':run['id'],'manifestSHA256':self.pin,'backend':'cpu',
                'history':[{'epoch':i,'loss':.1} for i in range(1,121)],
                'predictions':{name:probs for name in names},'checkpointSHA256':w.digest(folder/'last.pt')})
        self.write(self.returned/'complete.json',{'manifestSHA256':self.pin,'runs':[r['id'] for r in runs]})

    def write(self,path,value):path.write_text(json.dumps(value))

    def mutate_result(self,change):
        path=self.returned/'DTM068/result.json';doc=json.loads(path.read_text());change(doc);self.write(path,doc)

    def mutate_weights(self,change):
        path=self.returned/'DTM068/last.pt';doc=torch.load(path,weights_only=True);change(doc['state']);torch.save(doc,path)
        self.mutate_result(lambda r:r.update(checkpointSHA256=w.digest(path)))

    def reject(self,reason):
        with self.assertRaisesRegex(ValueError,reason):review(self.package,self.returned,self.output)
        self.assertFalse(self.output.exists())

    def test_real_cli_and_collision(self):
        args=[sys.executable,str(ROOT/'scripts/transition249_result_checks.py'),str(self.package),str(self.returned),str(self.output)]
        result=subprocess.run(args,capture_output=True,text=True,timeout=60)
        self.assertEqual(result.returncode,0,result.stderr)
        doc=json.loads(self.output.read_text());self.assertTrue(doc['localReplayVerified']);self.assertFalse(doc['productionEligible'])
        self.assertEqual(len(doc['results']),3)
        before=self.output.read_bytes()
        with self.assertRaisesRegex(ValueError,'output_collision'):review(self.package,self.returned,self.output)
        self.assertEqual(self.output.read_bytes(),before)

    def test_missing_epoch(self):
        self.mutate_result(lambda r:r['history'].pop());self.reject('incomplete_training')

    def test_altered_prediction(self):
        self.mutate_result(lambda r:r['predictions']['native.npy'].__setitem__(0,.99));self.reject('prediction_parity')

    def test_geometry_change(self):
        self.mutate_weights(lambda state:state['encoder.0.bias'].add_(1));self.reject('geometry_changed')

    def test_nonfinite_change_weights(self):
        self.mutate_weights(lambda state:state['change.0.bias'].fill_(float('nan')));self.reject('nonfinite_weights')

    def test_wrong_checkpoint_hash(self):
        self.mutate_result(lambda r:r.update(checkpointSHA256='0'*64));self.reject('checkpoint_hash')

    def test_partial_completion(self):
        path=self.returned/'complete.json';doc=json.loads(path.read_text());doc['runs'].pop();self.write(path,doc)
        self.reject('completion_identity')

    def test_changed_input(self):
        with (self.package/'native.npy').open('ab') as f:f.write(b'changed')
        self.reject('member_hash')


if __name__=='__main__':unittest.main()
