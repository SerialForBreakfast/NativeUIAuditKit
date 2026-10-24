"""Check the OCR connection and its actual queue failure paths without native capture."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from PIL import Image
import research_queue as q
import research_approval
from experiment_templates import pin
import ocr_class_comparison493 as adapter


def rows():
    return [dict(sha256=str(i),group='g'+str(i),controls=[dict(id='c',**{'class':'label'},bounds=[0,0,10,10])]) for i in range(4)]


class OCRTests(unittest.TestCase):
    def test_disjoint_rule_and_retained_success(self):
        frames=rows(); regions={f['sha256']:[dict(text='Hello',confidence=.99,xyxy=[0,0,10,10])] for f in frames}
        preds={f['sha256']:[('button',.9,[0,0,10,10])] for f in frames}
        result=adapter.compare(frames,preds,regions,.5)
        self.assertEqual(len(result['gains']),2)
        self.assertFalse(set(result['fitGroups'])&set(result['evaluationGroups']))
        self.assertFalse(result['lostPreviousSuccesses'])
        self.assertEqual(preds['0'][0][0],'button')
    def test_ambiguous_and_no_text(self):
        r=dict(text='Hello',confidence=.99,xyxy=[0,0,10,10])
        self.assertIsNone(adapter.text_for([0,0,10,10],[r,r]))
        self.assertIsNone(adapter.text_for([0,0,10,10],[]))
    def test_conflicting_fit_classes_keep_baseline(self):
        frames=rows(); fit=adapter.split(frames)
        next(f for f in frames if f['group'] in fit)['controls'][0]['class']='button'
        regions={f['sha256']:[dict(text='Hello',confidence=.99,xyxy=[0,0,10,10])] for f in frames}
        result=adapter.compare(frames,{f['sha256']:[('button',.9,[0,0,10,10])] for f in frames},regions,.5)
        self.assertEqual(result['rule'],{})
        self.assertEqual(result['changes'],[])
    def test_same_text_different_evaluation_role_reports_losses(self):
        frames=rows(); fit=adapter.split(frames)
        for f in frames:
            if f['group'] not in fit: f['controls'][0]['class']='listRow'
        regions={f['sha256']:[dict(text='Hello',confidence=.99,xyxy=[0,0,10,10])] for f in frames}
        result=adapter.compare(frames,{f['sha256']:[('listRow',.9,[0,0,10,10])] for f in frames},regions,.5)
        self.assertEqual(len(result['lostPreviousSuccesses']),2)
        self.assertEqual(len(result['newWrongClasses']),2)
        self.assertEqual(result['gains'],[])
    def test_geometry_and_dimension_failures(self):
        frame=dict(width=10,height=10)
        doc=dict(version='vision-ocr-regions-v1',coordinates='top-left-pixel-xyxy',width=10,height=10,regions=[])
        self.assertEqual(adapter.validate_ocr(doc,frame),[])
        for change,error in [(dict(width=11),'ocr_dimensions'),(dict(regions=[dict(text='x',confidence=.9,xyxy=[0,0,float('nan'),10])]),'ocr_geometry')]:
            with self.assertRaisesRegex(ValueError,error): adapter.validate_ocr(dict(doc,**change),frame)
    def test_geometry_rejects_different_control_shape(self):
        frames=rows(); fit=adapter.split(frames)
        regions={f['sha256']:[dict(text='Hello',confidence=.99,xyxy=[0,0,10,10])] for f in frames}
        preds={}
        for f in frames:
            evaluation=f['group'] not in fit
            if evaluation: f['controls'][0].update(bounds=[0,0,30,10],**{'class':'listRow'})
            preds[f['sha256']]=[('listRow',.9,[0,0,30 if evaluation else 10,10])]
        result=adapter.compare(frames,preds,regions,.5,'geometry-envelope')
        self.assertEqual(result['geometryRejectedChanges'],2)
        self.assertEqual(result['lostPreviousSuccesses'],[])
        self.assertEqual(result['changes'],[])
        # Evaluation labels cannot change the fitted envelope or prediction changes.
        for f in frames:
            if f['group'] not in fit: f['controls'][0]['class']='button'
        other=adapter.compare(frames,preds,regions,.5,'geometry-envelope')
        self.assertEqual(result['geometryEnvelopes'],other['geometryEnvelopes'])
        self.assertEqual(result['changes'],other['changes'])
    def test_geometry_allows_supported_shape(self):
        frames=rows()
        regions={f['sha256']:[dict(text='Hello',confidence=.99,xyxy=[0,0,10,10])] for f in frames}
        result=adapter.compare(frames,{f['sha256']:[('button',.9,[0,0,10,10])] for f in frames},regions,.5,'geometry-envelope')
        self.assertEqual(len(result['gains']),2)
    def test_sparse_groups(self):
        with self.assertRaisesRegex(ValueError,'ocr_group_support'): adapter.split(rows()[:2])
    def test_actual_queue_success_and_invalid_request(self):
        parent=q.ROOT/'.build/ocr493-tests';parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as temp:
            root=Path(temp); queue=root/'queue'; frames=[]; raw=[]
            helper=root/'helper'; doc=dict(version='vision-ocr-regions-v1',coordinates='top-left-pixel-xyxy',width=10,height=10,
                regions=[dict(text='Hello',confidence=.99,xyxy=[0,0,10,10])])
            helper.write_text('#!'+sys.executable+'\nprint('+repr(json.dumps(doc))+')\n');helper.chmod(0o700)
            identity=dict(engine='fixture')
            for i in range(4):
                image=root/f'{i}.png';Image.new('RGB',(10,10),(i,0,0)).save(image);ref=pin(image)
                frames.append(dict(sha256=ref['sha256'],image=ref,group='g'+str(i),width=10,height=10,
                    controls=[dict(id='c',**{'class':'label'},bounds=[0,0,10,10])]))
                path=root/f'raw-{i}.json';q.save(path,dict(inputSHA256=ref['sha256'],coordinates='boundingBoxPixels: pixels top-left',
                    runtime=dict(detector=identity,result=dict(elements=[dict(elementType='button',confidence=.9,
                        boundingBoxPixels=dict(x=0,y=0,width=10,height=10))]))));raw.append(pin(path))
            labels=root/'labels.json';q.save(labels,dict(version='detector-native-inputs-v1',role='development',trainingEligible=False,
                platform='iOS',frames=frames,labelReview='software-fixture',labelsComplete=True))
            card=root/'card.json';q.save(card,dict(inputs=pin(labels),partition='development',frames=[f['sha256'] for f in frames],
                rawPredictions=raw,identity=dict(detector=identity),settings=dict(confidence=.5)))
            for ident,version,status in [('ocr-pass',adapter.VERSION,'complete'),('ocr-fail','invalid','failed')]:
                request=root/(ident+'-request.json');q.save(request,dict(version=version,labels=pin(labels),scorecard=pin(card),helper=pin(helper)))
                spec=adapter.build(request,ident); path=root/(ident+'.json');q.save(path,spec);q.submit(path,queue)
                research_approval.approve(queue,ident,'test','Software qualification only')
                outcome=q.run(queue,max_jobs=1,lock=root/'lock',job_ids=[ident])
                attempt=queue/'jobs'/ident/'attempts/1'
                self.assertEqual(outcome,[(ident,status)],str(q.load(attempt/'result.json')))
                if status=='complete':
                    result=q.load(attempt/'out/comparison.json');self.assertEqual(len(result['gains']),2)
                else:
                    self.assertIn('ocr_request_version',(attempt/'stderr.log').read_text())
            # Reuse a failed attempt with no OCR outputs. It must retain the same input identities.
            request=root/'resume-request.json'
            q.save(request,dict(version=adapter.VERSION,labels=pin(labels),scorecard=pin(card),helper=pin(helper),
                reuseAttempt=pin(queue/'jobs/ocr-fail/attempts/1/result.json')))
            spec=adapter.build(request,'ocr-resume');path=root/'resume-spec.json';q.save(path,spec);q.submit(path,queue)
            research_approval.approve(queue,'ocr-resume','test','Software continuation qualification only')
            self.assertEqual(q.run(queue,max_jobs=1,lock=root/'lock',job_ids=['ocr-resume']),[('ocr-resume','complete')])
            self.assertEqual(q.load(queue/'jobs/ocr-resume/attempts/1/out/comparison.json')['reusedOCRFrames'],0)
            for ident,source,status in [('ocr-geometry','ocr-pass','complete'),('ocr-cache-fail','ocr-fail','failed')]:
                request=root/(ident+'-request.json')
                q.save(request,dict(version=adapter.VERSION,labels=pin(labels),scorecard=pin(card),helper=pin(helper),
                    ruleMode='geometry-envelope',retainedAttempt=pin(queue/'jobs'/source/'attempts/1/result.json')))
                path=root/(ident+'.json');q.save(path,adapter.build(request,ident));q.submit(path,queue)
                research_approval.approve(queue,ident,'test','Retained-output software qualification')
                self.assertEqual(q.run(queue,max_jobs=1,lock=root/'lock',job_ids=[ident]),[(ident,status)])
                if status=='complete':
                    self.assertEqual(q.load(queue/'jobs'/ident/'attempts/1/out/comparison.json')['reusedOCRFrames'],4)


if __name__=='__main__': unittest.main()
