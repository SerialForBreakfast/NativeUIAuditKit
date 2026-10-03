"""Direct paired-image software tests; synthetic optimization is not model evidence."""
import copy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from PIL import Image
import focus_direct_transition as d


class DirectTests(unittest.TestCase):
    def setUp(self):
        base=d.h.ROOT/'.build/debug-output/direct53-tests';base.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=base);self.root=Path(self.temp.name)

    def tearDown(self):self.temp.cleanup()

    def write(self,name,obj):
        path=self.root/name;d.h.write(path,obj);return path

    def image(self,name,color):
        path=self.root/name;Image.new('RGB',(96,64),color).save(path);return d.h.ref(path)

    def corpus(self):
        rows=[]
        for group in ('a','b'):
            for n in (0,1):
                rows.append(dict(id=group+str(n),group=group,changed=bool(n),images=[{'sha256':group+str(n)}],
                                 decodedPixelHashes=[group+str(n)],sourceRole='calibration'))
        return dict(corpusSHA256='fixture',records=rows)

    def admission(self,corpus):
        return dict(version='focus-direct-admission-v1',approved=True,reviewer='unit-test',
            decisionReference='software-fixture-not-real-permission',corpusSHA256=corpus['corpusSHA256'],
            assignments={r['id']:'train' if r['group']=='a' else 'development' for r in corpus['records']})

    def protocol(self,corpus,admission=None):
        p=dict(version=d.VERSION,configuration=d.CONFIG,sources={},corpusSHA256=corpus['corpusSHA256'],
               admission=admission,implementation=d.h.ref(Path(d.__file__)),pins=d.pins())
        p['protocolSHA256']=d.digest(p);return self.write('protocol.json',p)

    def test_geometry_roundtrip_and_order(self):
        for size in ((1920,1080),(800,1200),(96,64)):
            box=[10,20,min(100,size[0]-20),min(100,size[1]-30)];np.testing.assert_allclose(d.image_box(d.target_box(box,size),size),box,atol=1e-6)
        a=Image.new('RGB',(800,1200),'red');b=Image.new('RGB',a.size,'blue')
        x=d.encode(a,b);y=d.encode(b,a);self.assertEqual(x.shape,(6,64,96))
        np.testing.assert_array_equal(x[:3],y[3:]);self.assertFalse(np.array_equal(x,y))
        with self.assertRaises(ValueError):d.encode(a,b.resize((100,100)))
        with self.assertRaises(ValueError):d.target_box([-1,0,10,10],(100,100))
        self.assertIsNone(d.image_box([0,0,1,1],(1920,1080)))

    def test_admission_and_group_pixel_leakage(self):
        c=self.corpus();a=self.admission(c);self.assertEqual(len(d.admitted(c,a)),4)
        for kind in ('group','pixel','omitted','authority','hash'):
            bad=copy.deepcopy(c);ad=copy.deepcopy(a)
            if kind=='group':ad['assignments']['a1']='development'
            if kind=='pixel':bad['records'][2]['decodedPixelHashes']=['a0']
            if kind=='omitted':ad['assignments'].pop('a0')
            if kind=='authority':ad['approved']=False
            if kind=='hash':ad['corpusSHA256']='changed'
            with self.assertRaises(ValueError):d.admitted(bad,ad)

    def test_preflight_never_imports_model_or_implicitly_admits(self):
        c=self.corpus();p=self.protocol(c)
        with patch.object(d,'collect',return_value=c),patch.object(d,'model',side_effect=AssertionError('model accessed')):
            report,rows=d.load_protocol(p,d.ARM,'direct53-unit')
        self.assertFalse(report['launchEligible']);self.assertEqual(rows,[])
        self.assertIn('missing_exact_data_role_admission',report['blockers'])

    def test_positive_preflight_requires_separate_execution_and_both_states(self):
        c=self.corpus();ad=self.write('admission.json',self.admission(c));p=self.protocol(c,d.h.ref(ad))
        doc=d.h.read(p);approval=self.write('approval.json',dict(version='focus-direct-approval-v1',approved=True,
            protocolSHA256=doc['protocolSHA256'],arm=d.ARM,runName='direct53-unit',decisionReference='software-only'))
        with patch.object(d,'collect',return_value=c):
            report,_=d.load_protocol(p,d.ARM,'direct53-unit',approval)
            self.assertTrue(report['launchEligible']);self.assertFalse(report['executionAuthorized'])
            c['records'][1]['changed']=False
            report,_=d.load_protocol(p,d.ARM,'direct53-unit',approval)
            self.assertIn('train_missing_change_states',report['blockers'])

    def test_metrics_do_not_hide_abstentions_or_box_failures(self):
        rows=[dict(prediction={'decision':'unknown'},baseline=None,rawChangeCorrect=True,
                   bothBoxesCorrect=True,expectedChange=True)]
        result=d.summarize(rows)['all'];self.assertEqual(result['jointCorrect'],0)
        self.assertEqual(result['abstained'],1);self.assertEqual(result['baselineDecided'],0)

    def test_configuration_pin_and_output_collision(self):
        c=self.corpus();p=self.protocol(c);doc=d.h.read(p);doc['implementation']['sha256']='bad'
        doc['protocolSHA256']=d.digest({k:v for k,v in doc.items() if k!='protocolSHA256'})
        bad=self.write('bad.json',doc)
        with self.assertRaisesRegex(ValueError,'implementation_changed'):d.load_protocol(bad,d.ARM,'direct53-unit')
        with patch.object(d,'collect',return_value=c):
            with self.assertRaises(ValueError):d.load_protocol(p,d.ARM,'../../bad')
            with patch.object(d.old,'fresh_run',side_effect=ValueError('output_collision')):
                with self.assertRaisesRegex(ValueError,'output_collision'):d.load_protocol(p,d.ARM,'direct53-unit')

    def test_prediction_rejects_labels_and_unverified_context(self):
        request=dict(version='focus-direct-request-v1',before={},after={},context=dict(sameScene=True,settled=True,fresh=False))
        with patch.object(d,'torch_runtime',side_effect=AssertionError('torch accessed')):
            self.assertEqual(d.predict(request,'missing')['decision'],'unavailable')
            with self.assertRaisesRegex(ValueError,'request_fields'):d.predict(dict(request,afterBounds=[1,2,3,4]),'missing')

    def test_model_training_serialization_and_real_prediction_cli(self):
        refs=[self.image('a.png','red'),self.image('b.png','blue')]
        rows=[dict(images=refs if n else list(reversed(refs)),size=[96,64],
                   boxes=[[10,10,20,20],[40 if n else 10,10,20,20]],changed=bool(n)) for n in (0,1)]
        net,history=d.fit(rows);self.assertEqual(len(history),30)
        self.assertTrue(all(np.isfinite(r['trainingLoss']) for r in history))
        torch=d.torch_runtime();path=self.root/'test-only.pt'
        torch.save(dict(version=d.VERSION,configuration=d.CONFIG,state=net.state_dict()),path)
        request=self.write('request.json',dict(version='focus-direct-request-v1',before=refs[0],after=refs[1],
            context=dict(sameScene=True,settled=True,fresh=True)))
        output=self.root/'prediction.json';env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
        proc=subprocess.run([str(d.h.ROOT/'.venv-yolo/bin/python'),'scripts/focus_direct_transition.py',
            '--request',str(request),'--model',str(path),'--output',str(output)],cwd=d.h.ROOT,env=env,capture_output=True,text=True,timeout=60)
        self.assertEqual(proc.returncode,0,proc.stderr);result=d.h.read(output)
        self.assertFalse(result['releaseEligible']);self.assertEqual(len(result['boxes']),2)

    def test_record_missing_labels_and_corrupt_pixels(self):
        ref=self.image('a.png','black');frame=dict(image=ref,controls=[])
        with self.assertRaisesRegex(ValueError,'unique_known_focus'):d.record('a','g','calibration',frame,frame,True,[],None)
        bad=self.root/'bad.png';bad.write_bytes(b'not png')
        with self.assertRaises(OSError):d.pixels(d.h.ref(bad))


if __name__=='__main__':unittest.main()
