"""Qualify pixel reports with synthetic software fixtures, not model evidence."""
from pathlib import Path
import tempfile
import unittest
from PIL import Image
import research_queue as q
import research_approval as approval
import hcf_templates395 as templates
from experiment_templates import pin


class ProfileTests(unittest.TestCase):
    def test_queue_accepts_complete_pairs_and_rejects_incomplete_capture(self):
        bulk=Path('/Volumes/training-drive/data/NUIAK/HCF371')
        if not Path('/Volumes/training-drive').is_mount():self.skipTest('Verified USB test storage unavailable')
        with tempfile.TemporaryDirectory(dir=bulk,prefix='software-test402-') as images, tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='pixels402-') as work:
            source=Path(images);root=Path(work);queue=root/'queue';frames=[]
            for profile,color in [('standard','black'),('hcf','white')]:
                image=source/(profile+'.png');Image.new('RGB',(2,2),color).save(image)
                frames.append(dict(case='software-test',focus='control',repeat=0,profile=profile,path=image.name,sha256=q.digest(image)))
            for valid in (True,False):
                capture=source/('capture-'+str(valid)+'.json')
                q.save(capture,dict(complete=valid,cleanup=True,frames=frames))
                artifact=root/('artifact-'+str(valid)+'.json');q.save(artifact,dict(path=str(capture),sha256=q.digest(capture)))
                ident='pixels-'+str(valid).lower()
                doc=dict(version='hcf-template-description-v1',id=ident,owner='test-NUIAK',template='T36',
                    question='Does the pixel report reject incomplete captures?',decision='Accept only the complete synthetic software fixture.',
                    inputs=dict(capture=pin(artifact)),parameters={},dependencies=[])
                templates.register(doc,queue);approval.approve(queue,ident,'test','Isolated software qualification only.')
                self.assertEqual(q.run(queue,max_jobs=1,lock=root/'lock',job_ids=[ident]),[(ident,'complete' if valid else 'failed')])
                if valid:
                    row=q.load(queue/'jobs'/ident/'attempts/1/out/report.json')['rows'][0]
                    self.assertEqual(row['changedPixels'],4)
                    self.assertEqual(row['meanAbsoluteChannelDifference'],255)


if __name__=='__main__':unittest.main()
