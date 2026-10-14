"""Positive and negative geometry cases through the existing queue."""
import copy
from pathlib import Path
import tempfile
import unittest
import research_queue as q
import research_approval as approval
import hcf_templates395 as templates
from template_inputs398 import pin
from geometry399 import audit,flip


class GeometryTests(unittest.TestCase):
    def data(self):
        frame=dict(id='one',sha256='a'*64,group='g',role='development',profile='hcf',
                   width=600,height=400,boxes=[[40,30,120,80]],focus=0)
        proposal=dict(frame,prediction=dict(candidates=[[44,34,112,72]]))
        selected=dict(frame,outcome='correct')
        return [frame],dict(rows=[proposal]),dict(rows=[selected])

    def test_axes_and_insets(self):
        frames,proposals,selection=self.data()
        result=audit(frames,proposals,selection,'insets')
        self.assertEqual(result['summary']['hcf']['medianInsetsPixels'],[4,4,4,4])
        self.assertGreater(result['rows'][0]['directIoU'],.8)
        self.assertEqual(result['rows'][0]['invertedIoU'],0)
        self.assertEqual(flip(flip([1,2,3,4],400),400),[1,2,3,4])

    def test_reject_changed_identity_and_audit(self):
        for field,value in [('sha256','b'*64),('role','audit')]:
            frames,proposals,selection=self.data();frames[0][field]=value
            with self.assertRaises(ValueError):audit(frames,proposals,selection,'coverage')
        frames,proposals,selection=self.data();proposals['rows'][0]['prediction']['candidates'][0][0]=float('nan')
        with self.assertRaisesRegex(ValueError,'nonfinite'):audit(frames,proposals,selection,'orientation')

    def test_queue_success_and_failure(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='geometry399-') as folder:
            root=Path(folder);queue=root/'queue'
            for ident,bad in [('positive',False),('negative',True)]:
                frames,proposals,selection=self.data()
                if bad:selection['rows'][0]['sha256']='b'*64
                inputs={}
                for key,value in dict(catalog=dict(rows=frames),retained=dict(rows=[]),proposals=proposals,selection=selection).items():
                    path=root/(ident+'-'+key+'.json');q.save(path,value);inputs[key]=pin(path)
                doc=dict(version='hcf-template-description-v1',id=ident,owner='test-NUIAK',template='T26',
                    question='Does geometry preserve image identity?',decision='Reject changed membership.',inputs=inputs,
                    parameters=dict(mode='orientation'),dependencies=[])
                templates.register(doc,queue);approval.approve(queue,ident,'test','Isolated geometry qualification.')
                self.assertEqual(q.run(queue,max_jobs=1,lock=root/'lock',job_ids=[ident]),[(ident,'failed' if bad else 'complete')])


if __name__=='__main__':unittest.main()
