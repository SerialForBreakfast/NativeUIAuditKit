import copy
import unittest
from unittest.mock import patch
import weight_surgery_queue as w


class QueueTests(unittest.TestCase):
    def test_independent_reference_required(self):
        label = dict(review=dict(blinded=True, status='accepted', reviewer='Joe'),
                     focus=dict(state='focused', box=[0, 0, 20, 10]), objects=[])
        w.validate_reference(label)
        for change in (dict(review=dict(blinded=False, status='accepted', reviewer='Joe')),
                       dict(review=dict(blinded=True, status='accepted', reviewer='Maximum-mini-NUIAK')),
                       dict(objects=[dict(provenance='candidate_prediction')]),
                       dict(focus=dict(state='unknown', box=None))):
            with self.assertRaises(ValueError):
                w.validate_reference(dict(label, **change))

    def test_prediction_membership_and_values(self):
        w.validate_scores({'a': .5}, ['a'])
        for scores in ({}, {'b': .5}, {'a': float('nan')}, {'a': 1.1}):
            with self.assertRaises(ValueError): w.validate_scores(scores, ['a'])

    def report(self):
        return dict(suiteSHA256='a', threshold=.85, outcomes=[dict(id='a', correct=True, wrong=False)],
                    legacyLabels=[1] * 270, legacyProbabilities=[.9] * 270,
                    development=dict(D1=12, D2=8, D3=5), ancillary=dict(reserved=dict(tp=14,tn=0),calibration=dict(tp=3,tn=0)), retention=dict(tp=270, tn=0), unmeasuredGates=['R2', 'R3'])

    def test_missing_gates_cannot_pass(self):
        reports = {key: self.report() for key in w.ARMS}
        result = w.compare_reports(reports)
        self.assertFalse(result['modelAccepted'])
        self.assertTrue(all(r['outcome'] == 'inconclusive' for r in result['arms']))
        reports['head']['outcomes'][0].update(correct=False, wrong=True)
        result = w.compare_reports(reports)
        row = next(r for r in result['arms'] if r['arm'] == 'head')
        self.assertEqual(row['lost'], ['a']); self.assertEqual(row['newWrong'], ['a'])
        self.assertEqual(row['outcome'], 'contradicted')
        reports['head']['suiteSHA256'] = 'b'
        with self.assertRaisesRegex(ValueError, 'comparison_membership'): w.compare_reports(reports)

    def test_ancestry_rejects_scratch_and_wrong_parent(self):
        base = dict(path='base.pt', sha256='a'); donor = dict(path='donor.pt', sha256='b')
        p = dict(arm='warm-stretch', launchEligible=True, protocolSHA256='c', warmCheckpoint=base,
                 configuration=dict(model='mobilenetv4_conv_small', augmentation='none'),
                 support=dict(train={'0':37,'1':37}, validation={'0':9,'1':9}))
        c = dict(arm='warm-stretch', status='completed', protocolSHA256='c', bestSHA256='b', experimentID='FDR-006')
        with patch.object(w, 'document', side_effect=lambda ref: p if ref == 'p' else c), \
             patch.object(w, 'checked', return_value='unused'), \
             patch.object(w.torch, 'load', return_value=dict(model_name='mobilenetv4_conv_small')):
            self.assertTrue(w.ancestry(base, donor, 'p', 'c')['verified'])
            c['arm'] = 'scratch-stretch'
            with self.assertRaisesRegex(ValueError, 'ancestry_arm'): w.ancestry(base, donor, 'p', 'c')
            c['arm'] = 'warm-stretch'; p['warmCheckpoint'] = dict(base, sha256='wrong')
            with self.assertRaisesRegex(ValueError, 'ancestry_parent'): w.ancestry(base, donor, 'p', 'c')

    def test_another_comparison_reuses_same_code(self):
        reports = {key: self.report() for key in w.ARMS}
        for r in reports.values(): r['outcomes'][0]['id'] = 'second-campaign'
        self.assertEqual(len(w.compare_reports(reports)['arms']), 4)


    def test_actual_queue_produces_immutable_candidate(self):
        import tempfile
        import torch
        import research_queue as q
        import hcf_templates395 as templates
        import research_approval as approval
        from pathlib import Path
        from template_inputs398 import pin
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build', prefix='surgery562-test-') as tmp:
            root = Path(tmp)
            model = w.mobilenetv4_conv_small()
            for name in ('base', 'donor'):
                torch.save(dict(model_name='mobilenetv4_conv_small', state_dict=model.state_dict()), root/(name+'.pt'))
            base, donor = pin(root/'base.pt'), pin(root/'donor.pt')
            q.save(root/'preflight.json', dict(arm='warm-stretch', launchEligible=True, protocolSHA256='a'*64,
                warmCheckpoint=base, configuration=dict(model='mobilenetv4_conv_small', augmentation='none'),
                support=dict(train={'0':37,'1':37}, validation={'0':9,'1':9})))
            q.save(root/'completion.json', dict(arm='warm-stretch',status='completed',protocolSHA256='a'*64,
                bestSHA256=donor['sha256'],experimentID='FDR-006'))
            q.save(root/'recipe.json',dict(version='weight-surgery-recipe-v1',arm='baseline'))
            doc=dict(version='hcf-template-description-v1',id='surgery-fixture',owner='test-NUIAK',template='T94',
                question='Does the actual queue preserve an unchanged model through serialization?',
                decision='Require exact state roundtrip and immutable output before any scoring.',
                inputs=dict(base=base,donor=donor,preflight=pin(root/'preflight.json'),
                    completion=pin(root/'completion.json'),recipe=pin(root/'recipe.json')), parameters={},dependencies=[])
            queue=root/'queue';templates.register(doc,queue)
            approval.approve(queue,doc['id'],'test','Synthetic software integration only.')
            self.assertEqual(q.run(queue,max_jobs=1,lock=root/'lock',job_ids=[doc['id']]),[(doc['id'],'complete')])
            out=queue/'jobs'/doc['id']/'attempts/1/out'
            receipt=q.load(out/'edit.json')
            self.assertTrue(receipt['ancestryVerified']);self.assertEqual(receipt['changedParameters'],[])
            self.assertFalse(q.load(out/'model.json')['modelAccepted'])

if __name__ == '__main__': unittest.main()
