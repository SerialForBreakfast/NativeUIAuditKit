"""Checks for real-source crop intervention and label qualification."""
import copy
import tempfile
import unittest
from pathlib import Path
import research_queue as q
import proposal_crop_training421 as p
from template_inputs398 import pin


class ProposalCropTests(unittest.TestCase):
    def test_correspondence_filter(self):
        frame=dict(id='f',sha256='a'*64,group='g',role='train',width=100,height=100,boxes={'c':[10,10,20,20]})
        m=dict(imageSHA256='a'*64,control='c',group='g',role='train',body=[10,10,20,20],proposal=[11,10,20,20])
        doc=dict(version='training-proposals-v1',role='train',matches=[m])
        accepted,excluded=p.correspondences([doc],[frame]);self.assertEqual(len(accepted),1);self.assertEqual(excluded,0)
        for field,value in (('role','development'),('group','other'),('body',[1,1,2,2])):
            bad=copy.deepcopy(doc);bad['matches'][0][field]=value
            with self.assertRaises(ValueError):p.correspondences([bad],[frame])
        bad=copy.deepcopy(doc);bad['matches'][0]['proposal']=[15,15,2,2]
        with self.assertRaisesRegex(ValueError,'offset_no_supported_controls'):p.correspondences([bad],[frame])
        with self.assertRaisesRegex(ValueError,'offset_duplicate'):p.correspondences([doc,doc],[frame])

    def test_modes_preserve_original_and_seed(self):
        frame=dict(sha256='a'*64,boxes={'c':[10,10,20,20]})
        row=dict(control='c',box=[10,10,20,20])
        accepted={('a'*64,'c'):[11,10,20,20]}
        self.assertEqual(p.changed_box(row,frame,accepted,'unchanged'),row['box'])
        self.assertEqual(p.changed_box(row,frame,accepted,'measured'),[11,10,20,20])
        self.assertEqual(p.changed_box(row,frame,accepted,'jitter'),p.changed_box(row,frame,accepted,'jitter'))
        self.assertIsNone(p.changed_box(row,frame,{},'measured'))
        self.assertIsNone(p.changed_box(dict(row,jitter={'variant':0}),frame,accepted,'measured'))

    def test_label_audit_actual_queue(self):
        import hcf_templates395 as t
        import research_approval as approval
        source=q.QUEUE/'jobs/nctrl417-admission/attempts/1/out/admission.json'
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='labels421-') as folder:
            root=Path(folder);queue=root/'queue'
            for name,ref in [('valid',pin(source)),('invalid',None)]:
                if ref is None:
                    bad=q.load(source);bad['trainingAdmitted']=False;path=root/'bad.json';q.save(path,bad);ref=pin(path)
                doc=dict(version='hcf-template-description-v1',id='labels-'+name,owner='test-NUIAK',template='T92',
                    question='Do retained scene labels and training groups pass source checks?',
                    decision='Reject changed labels or unapproved admission. Do not infer complete general UI labels.',
                    inputs=dict(admission=ref),parameters={},dependencies=[])
                t.register(doc,queue);approval.approve(queue,doc['id'],'test','Isolated label qualification.')
                self.assertEqual(q.run(queue,max_jobs=1,lock=root/'lock',job_ids=[doc['id']]),[(doc['id'],'complete' if name=='valid' else 'failed')])


if __name__=='__main__':unittest.main()
