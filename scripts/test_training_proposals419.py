"""Training-only proposal preparation and queue failure checks."""
import copy
import tempfile
import unittest
from pathlib import Path
import research_queue as q
import training_proposals419 as p
from template_inputs398 import pin


class ProposalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=q.ROOT/'.build', prefix='proposals419-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = q.QUEUE/'jobs/nctrl417-admission/attempts/1/out/admission.json'

    def test_retained_preparation(self):
        for family in ('button', 'row', 'tab'):
            out=self.root/family; out.mkdir()
            result=p.prepare(q.load(self.source), family, out)
            self.assertTrue(result['frames'])
            self.assertEqual({f['role'] for f in result['frames']}, {'train'})
            self.assertEqual(len({f['sha256'] for f in result['frames']}), len(result['frames']))
            self.assertFalse(result['modelAccepted'])

    def test_admission_failures(self):
        original=q.load(self.source)
        bad=copy.deepcopy(original); bad['trainingAdmitted']=False
        with self.assertRaisesRegex(ValueError,'proposal_admission'): p.prepare(bad,'button',self.root)
        bad=copy.deepcopy(original); bad['rows'][0]['role']='invalid'
        with self.assertRaisesRegex(ValueError,'proposal_role'): p.prepare(bad,'button',self.root)
        bad=copy.deepcopy(original); row=copy.deepcopy(bad['rows'][0]); row['role']='audit'; bad['rows'].append(row)
        with self.assertRaisesRegex(ValueError,'proposal_group_leak'): p.prepare(bad,'button',self.root)
        bad=copy.deepcopy(original)
        for row in bad['rows']:
            if row['role']=='train' and row['family']=='button': row['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'proposal_image_changed|proposal_pixel_conflict'): p.prepare(bad,'button',self.root)

    def frame(self):
        return dict(id='f',group='g',sha256='a'*64,width=100,height=100,role='train',boxes={'a':[10,10,20,20]})

    def predictions(self, boxes):
        return dict(status='success',inputSHA256='a'*64,width=100,height=100,
            runtime=dict(result=dict(elements=[dict(boundingBoxPixels=dict(zip(('x','y','width','height'),b))) for b in boxes])))

    def test_unique_match_and_sampling(self):
        result=p.match(self.frame(),self.predictions([[12,10,20,20],[80,80,10,10],[-1,0,1,1]]))
        self.assertEqual(result['matches'][0]['offset'],[.1,0.,0.,0.])
        self.assertEqual(result['unmatchedProposals'],1)
        self.assertEqual(result['rejected'],1)
        self.assertEqual(p.sample(result['matches'],10,371),p.sample(result['matches'],10,371))
        for count,seed in ((0,1),(1,0),(True,1)):
            with self.assertRaisesRegex(ValueError,'proposal_sample_settings'): p.sample(result['matches'],count,seed)

    def test_ambiguous_missing_and_identity(self):
        self.assertFalse(p.match(self.frame(),self.predictions([[10,10,20,20],[11,10,20,20]]))['matches'])
        self.assertEqual(p.match(self.frame(),self.predictions([]))['missed'],['a'])
        frame=self.frame(); frame['role']='development'
        with self.assertRaisesRegex(ValueError,'proposal_frames_role'): p.match(frame,self.predictions([]))
        doc=self.predictions([]); doc['inputSHA256']='b'*64
        with self.assertRaisesRegex(ValueError,'proposal_prediction_identity'): p.match(self.frame(),doc)
        with self.assertRaisesRegex(ValueError,'proposal_nonfinite'): p.match(self.frame(),self.predictions([[float('nan'),1,1,1]]))

    def test_actual_queue_positive_reuse_and_failure(self):
        import hcf_templates395 as templates
        import research_approval as approval
        queue=self.root/'queue'
        for family in ('button','row','invalid'):
            ident='prepare-'+family
            doc=dict(version='hcf-template-description-v1',id=ident,owner='test-NUIAK',template='T87',
                question='Can training-only preparation preserve admitted identities and reject unsupported families?',
                decision='Require verified training images. Reject unsupported families before producing results.',
                inputs=dict(admission=pin(self.source)),parameters=dict(family=family),dependencies=[])
            templates.register(doc,queue)
            approval.approve(queue,ident,'test','Isolated preparation qualification; no training or capture.')
            result=q.run(queue,max_jobs=1,lock=self.root/'lock',job_ids=[ident])
            self.assertEqual(result,[(ident,'failed' if family=='invalid' else 'complete')])


if __name__=='__main__': unittest.main()
