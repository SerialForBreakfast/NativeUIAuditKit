import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from PIL import Image
import recording_intake349 as r


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=r.h.ROOT/'.build');self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def archive(self,bad_dimensions=False):
        b=io.BytesIO();Image.new('RGB',(20,10),'red').save(b,format='PNG');pixels=b.getvalue();digest=hashlib.sha256(pixels).hexdigest()
        manifest=dict(schemaVersion=2,sessionID='session',targetDeviceID='device',frameCount=1)
        frame=dict(frameID='f1',sha256=digest,sourceDeviceID='device',connectionGeneration=1,sequenceNumber=1,
            role='standalone',capturedMonotonicNanoseconds=1,dimensions=dict(width=21 if bad_dimensions else 20,height=10))
        inventory=dict(path='images/frame-'+digest+'.png',bytes=len(pixels),sha256=digest)
        files={'manifest.json':json.dumps(manifest).encode(),'events.jsonl':json.dumps({'frame':{'_0':frame}}).encode(),
            'files.jsonl':json.dumps(inventory).encode(),inventory['path']:pixels}
        archive=self.root/'test-original-recording.tar.gz'
        with tarfile.open(archive,'w:gz') as a:
            for name,data in files.items():
                item=tarfile.TarInfo('recording/'+name);item.size=len(data);a.addfile(item,io.BytesIO(data))
        offer=self.root/'offer.json';offer.write_text(json.dumps(dict(version=2,files=[dict(file='tvtestrig/'+archive.name,
            bytes=archive.stat().st_size,sha256=r.h.sha(archive))])))
        return offer
    def test_complete_private_intake(self):
        result=r.run(self.archive(),self.root/'intake')
        self.assertEqual(result['counts']['frames'],1);self.assertFalse(result['trainingEligible'])
        self.assertEqual(result['frames']['f1']['size'],[20,10])
    def test_dimension_conflict(self):
        with self.assertRaisesRegex(ValueError,'frame_dimensions_disagree'):
            r.run(self.archive(True),self.root/'intake')
    def test_changed_archive(self):
        offer=self.archive();(self.root/'test-original-recording.tar.gz').write_bytes(b'bad')
        with self.assertRaisesRegex(ValueError,'size_or_type'):r.run(offer,self.root/'intake')
    def test_traversal_rejected(self):
        archive=self.root/'bad.tar'
        with tarfile.open(archive,'w') as a:
            item=tarfile.TarInfo('../outside');item.size=1;a.addfile(item,io.BytesIO(b'x'))
        with self.assertRaises(ValueError):r.extract(archive,self.root/'intake')
        self.assertFalse((self.root/'intake').exists())
    def test_distinct_counter_times_remain_unqualified(self):
        frame=dict(frameID='f',sourceDeviceID='d',connectionGeneration=1,capturedMonotonicNanoseconds=40,
            role='postInputSettled',sha256='a'*64)
        action=dict(actionID='a',targetDeviceID='d',command='right',outcome='completed',connectionGeneration=2,
            commandTiming={k:dict(monotonic=dict(nanoseconds=v)) for k,v in [('enqueued',10),('transmitted',20),('completed',30)]})
        events=[{'frame':{'_0':frame}},{'action':{'_0':action}},
            {'dispatch':dict(actionID='a',target='d',command='right',monotonicNanoseconds=5)},
            {'association':dict(actionID='a',frameID='f',role='postInputSettled',sha256='a'*64)}]
        result=r.audit.analyze(dict(schemaVersion=2,targetDeviceID='d',sessionID='s'),events)
        self.assertEqual(result['counts']['associatedReady'],0)
        self.assertEqual(len(result['reportedAssociationTiming']),1)
        self.assertFalse(result['reportedAssociationTiming'][0]['qualified'])


if __name__=='__main__':unittest.main()
