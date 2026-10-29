"""Reject the observed report defects before model inference starts."""
import copy
import unittest
from unittest.mock import patch
import detector_native_inference as m

class MetadataTests(unittest.TestCase):
    def labels(self):
        return dict(version=m.VERSION,role='development',trainingEligible=False,platform='iOS',labelReview='reviewed',frames=[dict(screen='rows',group='g',sha256='a'*64,image=dict(path='x',sha256='a'*64),width=20,height=20,controls=[dict(id='row',bounds=[0,0,10,10],**{'class':'listRow'})])])
    def test_missing_review_rejected(self):
        labels=self.labels();del labels['labelReview']
        with self.assertRaisesRegex(ValueError,'detector_label_review'):m.validate(labels)
    def test_missing_screen_rejected(self):
        labels=self.labels();del labels['frames'][0]['screen']
        with self.assertRaisesRegex(ValueError,'detector_screen'):m.validate(labels)
    def test_complete_metadata_passes_without_inference(self):
        with patch.object(m,'checked',return_value=None):self.assertEqual(len(m.validate(self.labels())),1)

if __name__=='__main__':unittest.main()

class TemplateAdmissionTests(MetadataTests):
    def test_template_checks_metadata_before_submission(self):
        import tempfile
        from pathlib import Path
        import research_queue as q
        import hcf_templates395 as templates
        from experiment_templates import pin
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build') as folder:
            root=Path(folder);image=root/'image';image.write_bytes(b'input');model=root/'model';model.write_bytes(b'model')
            labels=self.labels();frame=labels['frames'][0];frame['image']=pin(image);frame['sha256']=q.digest(image)
            path=root/'labels.json';q.save(path,labels)
            doc=dict(version='hcf-template-description-v1',id='metadata-check',owner='Maximum-mini-NUIAK',template='T56',question='Do complete metadata pass before inference?',decision='Require complete report inputs before execution.',inputs=dict(labels=pin(path),model=pin(model)),parameters=dict(engine='pytorch',confidence=.5,imageSize=640,slice='class'),dependencies=[])
            self.assertEqual(templates.build(doc)['template']['id'],'T56')
            del labels['frames'][0]['screen'];q.save(path,labels,replace=True);doc['inputs']['labels']=pin(path)
            with self.assertRaisesRegex(ValueError,'detector_screen'):templates.build(doc)
