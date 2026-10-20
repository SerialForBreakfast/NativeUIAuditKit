import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image
import research_queue as q
from experiment_templates import pin
import ios_training_membership478 as worker


class MembershipTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=q.ROOT/'.build')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        image=self.root/'frame.png'
        Image.new('RGB',(20,20),'white').save(image)
        self.image=image
        self.side=dict(imageSHA256=q.digest(image),elements=[
            dict(id='control',elementType='toggle',boundsPixels=dict(x=1,y=2,width=10,height=8))])
        self.row=dict(id='frame',group='UIKitControls:47701',family='UIKitControls',seed=47701,
                      labels=1,image=dict(path='frame.png',sha256=q.digest(image)),
                      sidecar=dict(path='frame.json'))
        self.inventory=dict(integrityPassed=True,errors=[],members=[])

    def prepare(self, rows=None):
        q.save(self.root/'frame.json',self.side,replace=True)
        q.save(self.root/'manifest.json',dict(rows=rows or [self.row]),replace=True)
        q.save(self.root/'summary.json',{},replace=True)
        q.save(self.root/'exclusions.json',self.inventory,replace=True)
        source=dict(manifest=pin(self.root/'manifest.json'),summary=pin(self.root/'summary.json'))
        with patch.object(worker,'review',return_value=dict(annotationContractPassed=True)):
            return worker.prepare([source],pin(self.root/'exclusions.json'),['toggle'])

    def test_admission_preserves_original_role(self):
        result=self.prepare()
        self.assertTrue(result['trainingAdmitted'])
        self.assertFalse(result['lineage'][0]['originalEligibility'])
        self.assertEqual(result['calibrationPolicy'],'none-fixed-last-training-diagnostics')

    def test_reserved_family_seed_rejected(self):
        self.inventory['members']=[dict(family='UIKitControls',seed=47701,pixelSHA256='old',imageSHA256='old')]
        with self.assertRaisesRegex(ValueError,'reserved_group'):
            self.prepare()

    def test_decoded_duplicate_rejected(self):
        with Image.open(self.image) as image:
            digest=hashlib.sha256(str(image.size).encode()+image.convert('RGBA').tobytes()).hexdigest()
        self.inventory['members']=[dict(family='Other',seed=1,pixelSHA256=digest,imageSHA256='other-encoding')]
        with self.assertRaisesRegex(ValueError,'reserved_pixels'):
            self.prepare()

    def test_unknown_class_rejected(self):
        self.side['elements'][0]['elementType']='unknown'
        with self.assertRaisesRegex(ValueError,'unknown_class'):
            self.prepare()

    def test_wrong_geometry_rejected(self):
        self.side['elements'][0]['boundsPixels']['width']=40
        with self.assertRaisesRegex(ValueError,'detector_bounds'):
            self.prepare()

    def test_uncertain_frame_not_silently_admitted(self):
        self.side['elements'][0]['occluded']=True
        with self.assertRaisesRegex(ValueError,'duplicate_identity'):
            self.prepare()

    def test_bad_exclusion_inventory_rejected(self):
        self.inventory['integrityPassed']=False
        with self.assertRaisesRegex(ValueError,'exclusion_integrity'):
            self.prepare()


if __name__=='__main__':
    unittest.main()
