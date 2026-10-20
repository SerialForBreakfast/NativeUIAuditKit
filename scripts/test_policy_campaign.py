import copy
import unittest
import policy_campaign as gate
import tempfile
from pathlib import Path
import research_queue as q
import research_approval as approval
from experiment_templates import pin


def report():
    rows = []
    for i in range(4):
        no = i == 3
        rows.append(dict(id=str(i), group='group'+str(i), profile='standard', noFocus=no,
                         baseline='correct-abstention' if no else 'miss',
                         reference='correct-abstention' if no else 'correct',
                         outcome='correct-abstention' if no else 'correct', loss=False, baselineLoss=False))
    return dict(version='cached-focus-policy-v1', policy='abstention-fallback',
                threshold=.85, modelAccepted=False, rows=rows)


class GateTests(unittest.TestCase):
    def test_two_supported_descriptions(self):
        for minimum in (1, 3):
            doc = report()
            expected = [(r['id'], r['group'], r['profile']) for r in doc['rows']]
            self.assertEqual(gate.assess([doc], expected, minimum)['outcome'], 'supported')

    def test_regression_closes_branch(self):
        doc = report(); expected = [(r['id'],r['group'],r['profile']) for r in doc['rows']]
        doc['rows'][0].update(outcome='wrong', loss=True)
        result = gate.assess([doc],expected,1)
        self.assertEqual(result['outcome'],'contradicted')
        self.assertEqual(result['newWrong'],['0'])

    def test_missing_support_is_inconclusive(self):
        doc=report();doc['rows'].pop()
        expected=[(r['id'],r['group'],r['profile']) for r in doc['rows']]
        self.assertEqual(gate.assess([doc],expected,1)['outcome'],'inconclusive')

    def test_hcf_cannot_unlock(self):
        doc=report()
        for r in doc['rows']:
            r['baseline']=r['outcome']
        extra=copy.deepcopy(doc['rows'][0]);extra.update(id='optional',profile='hcf',baseline='miss')
        doc['rows'].append(extra)
        expected=[(r['id'],r['group'],r['profile']) for r in doc['rows']]
        self.assertEqual(gate.assess([doc],expected,1)['outcome'],'inconclusive')

    def test_changed_membership_and_forged_counts(self):
        doc=report();expected=[(r['id'],r['group'],r['profile']) for r in doc['rows']]
        with self.assertRaisesRegex(ValueError,'policy_gate_membership'):
            gate.assess([doc],expected[:-1],1)
        doc['rows'][0]['loss']=True
        with self.assertRaisesRegex(ValueError,'policy_gate_counts'):
            gate.assess([doc],expected,1)

    def test_queue_conditions_and_restart(self):
        """Synthetic receipts test execution control, not model quality."""
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='policy-gate-') as folder:
            root=Path(folder); queue=root/'queue'
            model=root/'model.json';q.save(model,dict(synthetic=True))
            for label, negative in [('positive',False),('regression',True)]:
                doc=report()
                if negative:
                    doc['rows'][0].update(outcome='wrong',loss=True)
                raw=root/(label+'-raw')
                (raw/'out').mkdir(parents=True)
                source=dict(rows=[dict(id=r['id']) for r in doc['rows']],
                            inputs={k:pin(model) for k in ('baseline','candidate','tool','mapping')})
                q.save(raw/'out/source.json',source)
                q.save(raw/'result.json',dict(status='complete',outputs=[
                    dict(path='source.json',sha256=q.digest(raw/'out/source.json'))]))
                doc['inputs']=dict(report=pin(raw/'out/source.json'),receipt=pin(raw/'result.json'))
                parent=queue/'jobs'/('source-'+label);out=parent/'attempts/1/out';out.mkdir(parents=True)
                original=dict(id=parent.name,dependencies=[])
                q.save(parent/'spec.json',original);q.save(out/'benchmark_summary.json',doc)
                q.save(out.parent/'result.json',dict(status='complete',specSHA256=q.text_digest(original),
                    outputs=[dict(path='benchmark_summary.json',sha256=q.digest(out/'benchmark_summary.json'))]))
                membership=root/(label+'-members.json')
                q.save(membership,[(r['id'],r['group'],r['profile']) for r in doc['rows']])
                spec=dict(version='research-spec-v2',id='gate-'+label,task='test-policy',owner='Maximum-mini-NUIAK',
                    kind='screen',authority='diagnostic',jobKind='artifact',
                    question='Does the synthetic condition select the correct branch?',
                    hypothesis='Synthetic regression closes the branch.',
                    controlledComparison='Change one recorded synthetic outcome.',
                    decisionRule='Reject losses. No model acceptance.',
                    nextActionByOutcome=dict(supported='Check branch execution.',contradicted='Check closed branch.'),
                    inputs=[pin(membership),pin(q.MODULES/'policy_campaign.py')],
                    expectedMembership=pin(membership),minimumGain=1,retainedFailures=[],
                    dependencies=[dict(job=parent.name,specSHA256=q.text_digest(original),outputs=['benchmark_summary.json'])],
                    adapter=dict(type='python-callable',steps=['policy_campaign.run'],outputAttributes=['policy_campaign.OUT']),
                    evidence=dict(reads=[q.relative(membership)],artifactReceipt='artifact-receipt.json'),
                    limits=dict(timeoutSeconds=60,maxOutputBytes=1_000_000,maxAttempts=1))
                child=copy.deepcopy(spec);child['id']='child-'+label
                child['dependencies']=[dict(job=spec['id'],specSHA256=q.text_digest(spec),outputs=['decision.json','gate.json'])]
                child['conditions']=[dict(job=spec['id'],output='gate.json',outcome='supported')]
                for s in (spec,child):
                    path=root/(s['id']+'.json');q.save(path,s);q.submit(path,queue)
                    approval.approve(queue,s['id'],'test','Synthetic conditional execution test.')
                ids=[spec['id'],child['id']]
                q.run(queue,max_jobs=2,job_ids=ids,lock=root/'lock')
                q.run(queue,max_jobs=2,job_ids=ids,lock=root/'lock')
                self.assertEqual(q.state(queue/'jobs'/spec['id'])[0],'complete')
                self.assertEqual(q.state(queue/'jobs'/child['id'])[0],'blocked' if negative else 'complete')
                before=[len(q.attempts_of(queue/'jobs'/i)) for i in ids]
                q.run(queue,max_jobs=2,job_ids=ids,lock=root/'lock')
                self.assertEqual(before,[len(q.attempts_of(queue/'jobs'/i)) for i in ids])


if __name__ == '__main__':
    unittest.main()
