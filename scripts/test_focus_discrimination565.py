import copy
import tempfile
import unittest
from pathlib import Path
from PIL import Image
import focus_discrimination565 as f
import research_queue as q
from focus_dataset_contract import digest

class DiscriminationTests(unittest.TestCase):
    def test_grayscale_preserves_dimensions_and_positions(self):
        image=Image.new('RGB',(256,256),'red');image.paste((0,255,0),(128,0,256,256))
        result=f.neutralize_chroma(image)
        self.assertEqual(result.size,image.size)
        self.assertEqual(result.getpixel((127,20)),(76,76,76))
        self.assertEqual(result.getpixel((128,20)),(150,150,150))
        self.assertEqual(image.getpixel((127,20)),(255,0,0))

    def report(self):
        return dict(model=dict(path='same.pt'),threshold=.85,suiteSHA256='old',legacyLabels=[1],legacyProbabilities=[.9],
            development=dict(negatives=2,falseHigh=2),outcomes=[dict(id='a',correct=False,wrong=False)])

    def test_compare_preserves_successes_and_source_identity(self):
        a=self.report();b=copy.deepcopy(a);b['suiteSHA256']='new';b['development']['falseHigh']=1;b['outcomes'][0]['correct']=True
        suite=dict(intervention='Pillow-grayscale-RGB-replicated-v1',sourceSuite=dict(sha256='old'))
        self.assertEqual(f.compare_reports(a,b,suite,dict(sha256='new'),dict(version='anchor-preservation565-v1',complete=True,model=a['model'],sourceSuiteSHA256='old',candidateSuiteSHA256='new',lost=[]))['outcome'],'supported')
        b['legacyProbabilities']=[.2]
        self.assertEqual(f.compare_reports(a,b,suite,dict(sha256='new'),dict(version='anchor-preservation565-v1',complete=True,model=a['model'],sourceSuiteSHA256='old',candidateSuiteSHA256='new',lost=[]))['outcome'],'contradicted')
        b['model']=dict(path='different.pt')
        with self.assertRaisesRegex(ValueError,'model_or_threshold'):f.compare_reports(a,b,suite,dict(sha256='new'),dict(version='anchor-preservation565-v1',complete=True,model=a['model'],sourceSuiteSHA256='old',candidateSuiteSHA256='new',lost=[]))

    def protocol(self):
        rows=[dict(id=str(i),label=i%2,split='train',screenID='settings/root',group='train') for i in range(74)]
        rows += [dict(id='v'+str(i),label=i%2,split='validation',screenID='settings/accessibility',group='validation') for i in range(18)]
        doc=dict(version='focus-learning-protocol-v1',scope='development-only-same-app-screen-groups',samples=rows)
        return dict(doc,protocolSHA256=digest(doc))

    def test_feature_probe_uses_training_only(self):
        protocol=self.protocol();rows=f.training_rows(protocol)
        self.assertEqual(len(rows),74);self.assertTrue(all(r['split']=='train' for r in rows))
        protocol['samples'][0]['group']='validation';protocol.pop('protocolSHA256');protocol['protocolSHA256']=digest(protocol)
        with self.assertRaisesRegex(ValueError,'training_group_leak'):f.training_rows(protocol)

    def test_actual_queue_comparison(self):
        import hcf_templates395 as templates,research_approval as approval
        from template_inputs398 import pin
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='discrimination565-') as temp:
            root=Path(temp);suite=dict(intervention='Pillow-grayscale-RGB-replicated-v1',sourceSuite=dict(sha256='old'))
            q.save(root/'suite.json',suite);a=self.report();b=copy.deepcopy(a);b['suiteSHA256']=pin(root/'suite.json')['sha256']
            q.save(root/'a.json',a);q.save(root/'b.json',b)
            q.save(root/'retention.json',dict(version='anchor-preservation565-v1',complete=True,model=a['model'],sourceSuiteSHA256='old',candidateSuiteSHA256=b['suiteSHA256'],lost=[]))
            doc=dict(version='hcf-template-description-v1',id='gray-fixture',owner='test-NUIAK',template='T102',
                question='Does unchanged model comparison enforce the declared crop intervention?',
                decision='Reject regressions and keep all results provisional for user review.',
                inputs=dict(baseline=pin(root/'a.json'),candidate=pin(root/'b.json'),suite=pin(root/'suite.json'),retention=pin(root/'retention.json')),parameters={},dependencies=[])
            queue=root/'queue';templates.register(doc,queue);approval.approve(queue,doc['id'],'test','Synthetic comparison only.')
            self.assertEqual(q.run(queue,max_jobs=1,lock=root/'lock',job_ids=[doc['id']]),[(doc['id'],'complete')])
            self.assertEqual(q.load(queue/'jobs'/doc['id']/'attempts/1/out/benchmark_summary.json')['metricsStatus'],'provisional')

    def test_prepare_uses_real_pixels_and_preserves_labels(self):
        from unittest.mock import patch
        from template_inputs398 import pin
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='gray565-') as temp:
            root=Path(temp);out=root/'job/attempts/1/out';out.mkdir(parents=True)
            image=root/'rgb.png';Image.new('RGB',(256,256),'red').save(image);ref=pin(image)
            source=dict(version='weight-surgery-suite-v1',threshold=.85,frames=[dict(id='case')],crops={'case|truth':ref},
                legacy=[dict(image=ref,label=1)],ancillary=dict(reserved=[dict(image=ref,label=0)],calibration=[]))
            q.save(root/'suite.json',source)
            q.save(out.parents[2]/'spec.json',dict(template=dict(inputs=dict(suite=pin(root/'suite.json')))))
            before=image.read_bytes()
            with patch.object(f,'OUT',out):f.prepare()
            result=q.load(out/'suite.json')
            self.assertEqual(result['frames'],source['frames']);self.assertEqual(result['legacy'][0]['label'],1)
            self.assertEqual(image.read_bytes(),before)
            with Image.open(q.ROOT/result['crops']['case|truth']['path']) as transformed:
                self.assertEqual(transformed.getpixel((0,0)),(76,76,76))

    def test_ancillary_gate_finds_losses_hidden_by_equal_accuracy(self):
        from unittest.mock import patch
        from template_inputs398 import pin
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='anchors565-') as temp:
            root=Path(temp);out=root/'job/attempts/1/out';out.mkdir(parents=True)
            crop=root/'crop.png';Image.new('RGB',(256,256),'red').save(crop)
            source=dict(ancillary={group:[dict(image=pin(crop),label=0) for _ in range(n)] for group,n in [('reserved',16),('calibration',8)]})
            q.save(root/'source.json',source);candidate=dict(source,sourceSuite=pin(root/'source.json'));q.save(root/'candidate.json',candidate)
            model=root/'model.pt';model.write_bytes(b'test placeholder');q.save(root/'model.json',dict(checkpoint=pin(model)))
            q.save(out.parents[2]/'spec.json',dict(template=dict(inputs=dict(source=pin(root/'source.json'),candidate=pin(root/'candidate.json'),model=pin(root/'model.json')))))
            with patch.object(f,'OUT',out),patch('eval_focus_ring_detector.predict_torch',side_effect=[[.9]+[.2]*15,[.2,.9]+[.2]*14,[.2]*8,[.2]*8]):f.anchors()
            result=q.load(out/'retention.json');self.assertEqual(result['lost'],['reserved-1'])
            self.assertEqual(len(result['rows']),24)


    def test_training_crop_checks_metadata_and_pixels(self):
        from template_inputs398 import pin
        from focus_dataset_contract import pixel_digest
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='training565-') as temp:
            path=Path(temp)/'crop.png';Image.new('RGB',(256,256),'red').save(path)
            ref=pin(path);ref['pixelSHA256']=pixel_digest(q.ROOT,ref)
            row=dict(crops={'stretch':ref,'aspect-fit':ref})
            for policy in ('stretch','aspect-fit'):self.assertEqual(f.training_crop(row,policy),path)
            with self.assertRaisesRegex(ValueError,'training_crop_policy'):f.training_crop(row,'invalid')
            ref['pixelSHA256']='0'*64
            with self.assertRaisesRegex(ValueError,'training_crop_pixels'):f.training_crop(row,'stretch')

    def test_feature_policy_description(self):
        import hcf_templates395 as templates
        from template_inputs398 import pin
        ref=pin(q.ROOT/'reports/work/FOCUS-EXP-01/corpus-01/protocol.json')
        doc=dict(version='hcf-template-description-v1',id='policy-test',owner='test-NUIAK',template='T103',
            question='Does crop policy change training feature contributions?',decision='Keep weights and labels unchanged.',
            inputs=dict(protocol=ref,model=ref),parameters=dict(cropPolicy='aspect-fit'),dependencies=[])
        self.assertEqual(templates.build(doc)['template']['parameters']['cropPolicy'],'aspect-fit')
        doc['parameters']['cropPolicy']='invalid'
        with self.assertRaisesRegex(ValueError,'training_crop_policy'):templates.build(doc)

if __name__=='__main__':unittest.main()
