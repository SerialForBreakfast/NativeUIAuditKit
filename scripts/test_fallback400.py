"""Check precedence, Standard preservation, and failures through the queue."""
import copy
from pathlib import Path
import tempfile
import unittest
import research_queue as q
import research_approval as approval
import hcf_templates395 as templates
from template_inputs398 import pin
from fallback400 import combine


class FallbackTests(unittest.TestCase):
    def inputs(self):
        row=dict(id='one',sha256='a'*64,group='g',role='development',profile='hcf',family='card',outcome='miss',
                 prediction=dict(decision='abstain',box=None))
        other=copy.deepcopy(row);other.update(outcome='correct',prediction=dict(decision='select',box=[1,2,3,4]))
        return dict(rows=[row]),dict(rows=[other])

    def test_precedence_and_disabled(self):
        primary,fallback=self.inputs()
        self.assertEqual(combine(primary,fallback,True)['rows'],fallback['rows'])
        self.assertEqual(combine(primary,fallback,False)['rows'],primary['rows'])
        primary['rows'][0]['profile']=fallback['rows'][0]['profile']='standard'
        self.assertEqual(combine(primary,fallback,True)['rows'],primary['rows'])
        primary['rows'][0]['profile']=fallback['rows'][0]['profile']='hcf'
        primary['rows'][0]['prediction']=dict(decision='select',box=[9,9,9,9])
        primary['rows'][0]['outcome']='wrong'
        self.assertEqual(combine(primary,fallback,True)['rows'],primary['rows'])

    def test_queue_success_and_failure(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='fallback400-') as folder:
            root=Path(folder);queue=root/'queue'
            for ident,bad in [('positive',False),('negative',True)]:
                primary,fallback=self.inputs()
                if bad:fallback['rows'][0]['sha256']='b'*64
                inputs={}
                for key,value in [('primary',primary),('fallback',fallback)]:
                    path=root/(ident+'-'+key+'.json');q.save(path,value);inputs[key]=pin(path)
                doc=dict(version='hcf-template-description-v1',id=ident,owner='test-NUIAK',template='T30',
                    question='Does the fallback preserve input identity?',decision='Reject changed identities.',
                    inputs=inputs,parameters=dict(enabled=True),dependencies=[])
                templates.register(doc,queue);approval.approve(queue,ident,'test','Isolated fallback validation.')
                self.assertEqual(q.run(queue,max_jobs=1,lock=root/'lock',job_ids=[ident]),[(ident,'failed' if bad else 'complete')])


if __name__=='__main__':unittest.main()
