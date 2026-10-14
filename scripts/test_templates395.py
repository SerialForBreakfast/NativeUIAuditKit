"""Software contract tests. Stubbed native operations do not qualify captures or models."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import research_queue as q
import research_approval as approval
import template_adapters395 as a
import hcf_templates395 as t
from experiment_templates import pin


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='template395-')
        self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.out=self.root/'out';self.out.mkdir()

    def doc(self,name,value):
        path=self.root/name;q.save(path,value);return pin(path)

    def text(self,name,text='test-only'):
        path=self.root/name;path.write_text(text);return pin(path)

    def catalog(self):
        row=dict(id='one',group='g',family='f',role='development',profile='hcf',focus='c',sha256='a'*64)
        return dict(rows=[row],cases=[dict(group='g',family='f',role='development',artworkSeeds=[1])])

    def export_doc(self):
        for name in ('model.mlpackage','model.mlmodelc'):
            folder=self.root/name;folder.mkdir();(folder/'data').write_bytes(b'software-test-not-a-model')
        return self.doc('export.json',dict(version='template-export-v1',modelAccepted=False,
            compiled=q.relative(self.root/'model.mlmodelc'),package=q.relative(self.root/'model.mlpackage'),
            files=[pin(self.root/name/'data') for name in ('model.mlpackage','model.mlmodelc')]))

    def test_inventory_positive_and_duplicate_failure(self):
        doc=self.catalog();ref=self.doc('catalog.json',doc)
        a.inventory({'catalog':ref},{},self.out)
        self.assertEqual(q.load(self.out/'inventory.json')['frames'],1)
        doc['rows']*=2;ref=self.doc('bad.json',doc)
        with self.assertRaisesRegex(ValueError,'duplicate'):a.inventory({'catalog':ref},{},self.out)

    def test_groups_positive_and_role_failure(self):
        ref=self.doc('catalog.json',self.catalog());policy=self.doc('policy.json',dict(version='frozen-roles-v1',groups={'g':'development'}))
        a.dataset(dict(catalog=ref,policy=policy),{},self.out)
        bad=self.doc('bad.json',dict(version='frozen-roles-v1',groups={'g':'audit'}))
        with self.assertRaisesRegex(ValueError,'role_change'):a.dataset(dict(catalog=ref,policy=bad),{},self.out)

    def test_candidate_positive_and_losses(self):
        checkpoint=self.text('weights.pt')
        method=dict(losses=[],gains=['x'],counts=dict(frames=1,correct=1,wrong=0,misses=0))
        doc=dict(methods={k:copy.deepcopy(method) for k in ('bright-closed-stroke-v1','crop-baseline','crop-candidate','full-screen-candidate')},
                 cropSeeds=dict(previousSuccessesPreserved=True),models={'crop-candidate':checkpoint})
        ref=self.doc('review.json',doc)
        a.candidate(dict(review=ref,checkpoint=checkpoint),dict(method='crop-candidate'),self.out)
        doc['methods']['crop-candidate']['losses']=['lost'];ref=self.doc('bad.json',doc)
        with self.assertRaisesRegex(ValueError,'regression'):a.candidate(dict(review=ref,checkpoint=checkpoint),dict(method='crop-candidate'),self.out)

    def test_export_rejects_unqualified_candidate(self):
        candidate=self.doc('candidate.json',dict(version='template-candidate-v1',eligibleForExport=False))
        environment=self.doc('environment.json',{})
        with self.assertRaisesRegex(ValueError,'not_eligible'):a.export(dict(candidate=candidate,environment=environment),{},self.out)

    def test_changed_package_fails(self):
        ref=self.export_doc();a.verified_export(ref)
        (self.root/'model.mlmodelc/data').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'input_changed'):a.verified_export(ref)

    def test_runtime_rejects_failed_parity(self):
        export=self.export_doc();parity=self.doc('parity.json',dict(export=export,comparison=dict(passed=False)))
        membership=self.doc('items.json',dict(version='focus-runtime-items-v1',rows=[]))
        with patch.object(a,'runtime_items',return_value=([],[])):
            with self.assertRaisesRegex(ValueError,'parity_required'):
                a.runtime(dict(export=export,parity=parity,membership=membership),dict(repetitions=3),self.out)

    def test_package_and_consumer_positive_and_mismatch(self):
        export=self.export_doc();parity=self.doc('parity.json',dict(export=export,comparison=dict(passed=True)))
        runtime=self.doc('runtime.json',dict(export=export));license=self.text('LICENSE')
        a.package(dict(export=export,parity=parity,runtime=runtime,license=license),{},self.out)
        bundle=pin(self.out/'bundle.json');expected=self.doc('expected.json',dict(results=[dict(id='one',score=.9)]))
        receipt=dict(version='ttr-model-inference-v1',bundleSHA256=bundle['sha256'],backend='Vision',navigationAuthority=False,
                     results=[dict(id='one',score=.9)])
        ref=self.doc('receipt.json',receipt)
        a.consumer(dict(bundle=bundle,expected=expected,receipt=ref),{},self.out)
        receipt['results'][0]['score']=.8;ref=self.doc('bad.json',receipt)
        with self.assertRaisesRegex(ValueError,'consumer_parity'):a.consumer(dict(bundle=bundle,expected=expected,receipt=ref),{},self.out)

    def test_actual_queue_artifact_positive_and_failed_successor(self):
        queue=self.root/'queue';catalog=self.doc('catalog.json',self.catalog())
        doc=dict(version='hcf-template-description-v1',id='inventory-test',owner='test-NUIAK',template='T01',
                 question='Can the adapter inventory these software test records?',decision='Require exact counts and explicit failures.',
                 inputs=dict(catalog=catalog),parameters={},dependencies=[])
        t.register(doc,queue);t.register(doc,queue)
        approval.approve(queue,doc['id'],'test','Isolated software qualification. No model acceptance.')
        self.assertEqual(q.run(queue,max_jobs=1,lock=self.root/'lock',job_ids=[doc['id']]),[(doc['id'],'complete')])
        bad=self.catalog();bad['rows']*=2
        doc=dict(doc,id='inventory-failure',inputs=dict(catalog=self.doc('bad.json',bad)))
        t.register(doc,queue);approval.approve(queue,doc['id'],'test','Expected software validation failure, not model evidence.')
        self.assertEqual(q.run(queue,max_jobs=1,lock=self.root/'lock',job_ids=[doc['id']]),[(doc['id'],'failed')])
        self.assertEqual(q.load(queue/'jobs/inventory-failure/attempts/1/out/template-result.json')['execution'],'failed')

    def test_description_rejects_unknown_inputs_commands_versions(self):
        ref=self.doc('catalog.json',self.catalog())
        doc=dict(version='hcf-template-description-v1',id='test',owner='test-NUIAK',template='T01',
                 question='Check actual input requirements.',decision='Fail unknown operations and fields.',inputs=dict(catalog=ref),parameters={},dependencies=[])
        for changes in ({'version':'wrong'},{'template':'T99'},{'command':'anything'},{'parameters':{'shell':'anything'}}):
            with self.subTest(changes=changes),self.assertRaises(ValueError):t.build(dict(doc,**changes))

    def test_export_authority_rejects_arbitrary_adapter(self):
        ref=self.doc('catalog.json',self.catalog())
        doc=dict(version='hcf-template-description-v1',id='test',owner='test-NUIAK',template='T01',question='Check export authority boundaries.',
                 decision='Reject an unrelated export operation.',inputs=dict(catalog=ref),parameters={},dependencies=[])
        spec=t.build(doc);spec['authority']='export'
        with self.assertRaisesRegex(ValueError,'export_template'):q.validate(spec)


if __name__=='__main__':unittest.main()
