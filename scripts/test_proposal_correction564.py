import copy
import unittest
from pathlib import Path
from proposal_correction564 import replace_candidates,compare_reports

class CorrectionTests(unittest.TestCase):
    def report(self):
        return dict(model=dict(path='same.pt',sha256='a'),threshold=.85,legacyLabels=[1],legacyProbabilities=[.9],
          scores={'case|truth':.2},development=dict(D1=0,D2=1,D3=0),outcomes=[dict(id='case',correct=False,wrong=False)])
    def test_matched_weights_and_references(self):
        left=self.report();right=copy.deepcopy(left);right['outcomes'][0]['correct']=True
        self.assertEqual(compare_reports(left,right)['recovered'],['case'])
        right['scores']['case|truth']=.3
        with self.assertRaisesRegex(ValueError,'reference_crop'):compare_reports(left,right)
    def test_regressions_reject(self):
        left=self.report();right=copy.deepcopy(left);right['outcomes'][0]['wrong']=True
        self.assertEqual(compare_reports(left,right)['outcome'],'contradicted')
    def test_proposals_do_not_replace_reference_labels(self):
        plan=dict(frames=[dict(image=dict(path='image.png'),label=dict(path='human.json'),candidates=[])])
        result=replace_candidates(plan,{'image.png':[dict(cls='button',box=[1,2,3,4]),dict(cls='text',box=[5,6,7,8])]})
        self.assertEqual(result['frames'][0]['label'],plan['frames'][0]['label'])
        self.assertEqual(len(result['frames'][0]['candidates']),1)
        self.assertEqual(plan['frames'][0]['candidates'],[])

    def test_comparison_through_actual_queue(self):
        import tempfile
        import research_queue as q
        import hcf_templates395 as templates
        import research_approval as approval
        from template_inputs398 import pin
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='proposal564-') as temp:
            root=Path(temp);q.save(root/'base.json',self.report());q.save(root/'candidate.json',self.report())
            doc=dict(version='hcf-template-description-v1',id='proposal-fixture',owner='test-NUIAK',template='T100',
              question='Does matched proposal comparison preserve the unchanged focus model identity?',
              decision='Reject changed models, reference scores, thresholds, or legacy outputs.',
              inputs=dict(baseline=pin(root/'base.json'),candidate=pin(root/'candidate.json')),parameters={},dependencies=[])
            queue=root/'queue';templates.register(doc,queue);approval.approve(queue,doc['id'],'test','Cached synthetic comparison only.')
            self.assertEqual(q.run(queue,max_jobs=1,lock=root/'lock',job_ids=[doc['id']]),[(doc['id'],'complete')])
            result=q.load(queue/'jobs'/doc['id']/'attempts/1/out/benchmark_summary.json')
            self.assertEqual(result['metricsStatus'],'provisional');self.assertFalse(result['modelAccepted'])

    def test_producer_preserves_raw_predictions_and_clips_visible_geometry(self):
        import tempfile
        from unittest.mock import patch
        from PIL import Image
        import research_queue as q
        import proposal_correction564 as module
        import roles559_evaluate as evaluator
        from template_inputs398 import pin
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='proposal564-geometry-') as temp:
            root=Path(temp);out=root/'job/attempts/1/out';out.mkdir(parents=True)
            image=root/'image.png';Image.new('RGB',(20,20)).save(image)
            model=root/'model.pt';model.write_bytes(b'synthetic model placeholder')
            q.save(root/'label.json',dict(focus=dict(box=[0,1,2,4])))
            frame=dict(id='case',image=pin(image),label=pin(root/'label.json'),candidates=[])
            q.save(root/'plan.json',dict(frames=[frame]))
            q.save(out.parents[2]/'spec.json',dict(template=dict(inputs=dict(plan=pin(root/'plan.json'),model=pin(model)))))
            raw={image:[dict(cls='button',box=[-2,1,4,4],score=.9),dict(cls='button',box=[50,50,4,4],score=.8)]}
            with patch.object(module,'OUT',out),patch.object(evaluator,'predict',return_value=raw):module.proposals()
            result=q.load(out/'plan.json');receipt=q.load(out/'proposals.json')
            self.assertEqual(result['frames'][0]['candidates'][0]['bounds'],[0.,1,2.,4])
            self.assertEqual(len(receipt['rejectedProposals']),1)
            self.assertEqual(receipt['predictions'][q.relative(image)][0]['box'],[-2,1,4,4])

if __name__=='__main__':unittest.main()
