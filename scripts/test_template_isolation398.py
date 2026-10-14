"""Keep authoring changes separate from executable input checks."""
from pathlib import Path
import tempfile
import unittest
import research_queue as q
import research_approval as approval
import hcf_templates395 as templates
from template_inputs398 import pin


class IsolationTests(unittest.TestCase):
    def test_dependency_membership_is_explicit(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='membership398-') as folder:
            source=Path(folder)/'membership.json';q.save(source,dict(rows=[dict(id='one')]))
            ref=pin(source)
            inputs={}
            for key in ('catalog','retained','model','tool'):
                path=Path(folder)/(key+'.json');q.save(path,dict(rows=[]));inputs[key]=pin(path)
            inputs['rules']=dict(job='producer',output='comparison.json')
            doc=dict(version='hcf-template-description-v1',id='membership-test',owner='test-NUIAK',template='T18',
                question='Does dependent scoring require exact membership?',decision='Reject an inferred catalog count.',
                inputs=inputs,parameters={},dependencies=[dict(job='producer',specSHA256='a'*64,outputs=['comparison.json'])])
            with self.assertRaisesRegex(ValueError,'dependency_membership_required'):templates.build(doc)
            inputs['membership']=ref
            self.assertEqual(templates.build(doc)['evidence']['membershipCount'],1)

    def test_authoring_is_not_runtime_input(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='isolation398-') as folder:
            root=Path(folder);source=root/'source.json'
            q.save(source,dict(rows=[dict(id='one',group='g',family='f',role='development',profile='hcf')]))
            description=dict(version='hcf-template-description-v1',id='isolation-test',owner='test-NUIAK',template='T01',
                question='Does inventory require only execution inputs?',decision='Keep authoring provenance without runtime coupling.',
                inputs=dict(catalog=pin(source)),parameters={},dependencies=[])
            spec=templates.build(description)
            self.assertEqual(spec['template']['compiler'],pin(Path(templates.__file__)))
            runtime={p['path'] for p in spec['inputs']}|{p['path'] for p in approval.code_pins(spec,q.MODULES)}
            for name in ('hcf_templates395.py','experiment_templates.py','template_analysis397.py'):
                self.assertNotIn('scripts/'+name,runtime)
            self.assertIn('scripts/template_inputs398.py',runtime)
            self.assertIn('scripts/template_adapters395.py',runtime)
            queue=root/'queue';templates.register(description,queue)
            approval.approve(queue,'isolation-test','test','Isolated template input checks.')
            self.assertEqual(q.run(queue,max_jobs=1,lock=root/'lock',job_ids=['isolation-test']),[('isolation-test','complete')])


if __name__=='__main__':unittest.main()
