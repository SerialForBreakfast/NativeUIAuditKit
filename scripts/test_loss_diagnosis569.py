import unittest
from loss_diagnosis569 import classify,ios_rows

class LossTests(unittest.TestCase):
    def test_confidence_class_localization_and_assignment(self):
        truth=dict(cls='button',box=[0,0,10,10])
        for prediction,expected in [([], 'proposal-missing'),([dict(cls='button',box=[0,0,10,10],score=.4)],'confidence-below-fixed-threshold'),([dict(cls='text',box=[0,0,10,10],score=.9)],'class-or-assignment'),([dict(cls='button',box=[4,0,10,10],score=.9)],'localization'),([dict(cls='button',box=[0,0,10,10],score=.9)],'assignment-ambiguity')]:
            self.assertEqual(classify(truth,prediction),expected)

    def test_class_agnostic_baseline_change_is_not_a_class_recovery(self):
        original=dict(reports=[dict(condition='set',comparison='Run013',lostPriorSuccesses=['x'])])
        row=dict(id='x',labelClass='label',baseline=dict(status='missed'),candidate=dict(status='detected'))
        rows=ios_rows(original,[dict(condition='set',cases=dict(rows=[row]))])
        self.assertEqual(rows[0]['diagnosis'],'baseline-assignment-changed')
        row['baseline']['status']='detected'
        self.assertEqual(ios_rows(original,[dict(condition='set',cases=dict(rows=[row]))])[0]['diagnosis'],'class-or-assignment')

    def test_ios_summary_actual_queue(self):
        import tempfile
        from pathlib import Path
        import research_queue as q
        import research_approval as a
        from template_inputs398 import pin
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='loss569-') as temp:
            root=Path(temp)
            docs=dict(request=dict(pairs=[dict(condition='set',key='cases1')]),reference=dict(reports=[dict(condition='set',comparison='Run013',lostPriorSuccesses=['x'])]),cases1=dict(rows=[dict(id='x',labelClass='label',baseline=dict(status='detected'),candidate=dict(status='mislocalized',iou=.4))]))
            refs={}
            for name,value in docs.items():
                path=root/(name+'.json');q.save(path,value);refs[name]=pin(path)
            spec=dict(version='research-spec-v2',id='loss569-test',task='DIAG569',owner='test-NUIAK',kind='screen',authority='diagnostic',jobKind='artifact',
                question='Does cached iOS diagnosis use the declared template input container?',hypothesis='The report preserves known geometry losses without inference.',controlledComparison='Synthetic cached case only. No model execution or acceptance.',decisionRule='Reject missing references and report unchanged losses.',nextActionByOutcome=dict(supported='Keep provisional report for review.',contradicted='Fix the exact caller mismatch.'),inputs=[pin(q.MODULES/'loss_diagnosis569.py')]+list(refs.values()),dependencies=[],template=dict(inputs=refs,parameters={}),adapter=dict(type='python-callable',steps=['loss_diagnosis569.ios'],outputAttributes=['loss_diagnosis569.OUT']),evidence=dict(reads=[v['path'] for v in refs.values()],artifactReceipt='artifact-receipt.json'),limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1))
            path=root/'spec.json';q.save(path,spec);queue=root/'queue';q.submit(path,queue);a.approve(queue,spec['id'],'test','Synthetic cached aggregation only.')
            self.assertEqual(q.run(queue,max_jobs=1,lock=root/'lock',job_ids=[spec['id']]),[(spec['id'],'complete')])
            report=q.load(queue/'jobs'/spec['id']/'attempts/1/out/benchmark_summary.json')
            self.assertEqual(report['counts'],{'mislocalized':1});self.assertFalse(report['trainingOrInferenceRepeated'])
