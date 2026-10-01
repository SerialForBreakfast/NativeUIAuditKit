import copy,json,tempfile,unittest
from unittest.mock import patch
from pathlib import Path
import focus_reviewed_export as e

class TraceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=e.ROOT/'.build/debug-output');self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        f=self.root/'artifact';f.write_bytes(b'fixture')
        self.r=e.ref(f)
        rep=dict(kind='mobilenet_v3_small_frozen',features=576,weights=self.r)
        self.ck=dict(checkpointKind='frozen-pretrained-linear-head-v1',protocolSHA256='p',representation=rep)
        self.d=dict(version='focus-complete-trace-v1',checkpoint=self.r,encoder=self.r,protocol=self.r,
            protocolSHA256='p',representation=rep,trace=self.r,reference=self.r)
    def save(self,d):
        d=copy.deepcopy(d);d['seal']=e.digest(d);p=self.root/'receipt';p.write_text(json.dumps(d));return p
    def test_valid(self):
        d=e.checked_trace(self.save(self.d),self.r['sha256'],self.ck)
        self.assertEqual(d['encoder'],self.r)
    def test_wrong_head_protocol_representation(self):
        for field,value in [('checkpointKind','last'),('protocolSHA256','different'),('representation',{})]:
            ck={**self.ck,field:value}
            with self.subTest(field=field),self.assertRaises(ValueError):e.checked_trace(self.save(self.d),self.r['sha256'],ck)
    def test_changed_artifact_or_seal(self):
        p=self.save(self.d);(self.root/'artifact').write_bytes(b'changed')
        with self.assertRaises(ValueError):e.checked_trace(p,self.r['sha256'],self.ck)
        d=json.loads(p.read_text());d['protocolSHA256']='changed';p.write_text(json.dumps(d))
        with self.assertRaises(ValueError):e.sealed(p)
    def test_wrong_checkpoint_hash(self):
        with self.assertRaises(ValueError):e.checked_trace(self.save(self.d),'wrong',self.ck)

    def test_export_precision_is_explicit_and_legacy_default_unchanged(self):
        import export_focus_ring_coreml as exporter
        argv=['export','--weights','unused','--experimental-id','test']
        with patch('sys.argv',argv):
            args=exporter.parse_args()
            self.assertEqual(args.precision,'fp16')
            self.assertIsNone(args.pixel_contract)
        with patch('sys.argv',argv+['--precision','fp32']): self.assertEqual(exporter.parse_args().precision,'fp32')
        with patch('sys.argv',argv+['--pixel-contract','png-straight-rgb-v1']):
            self.assertEqual(exporter.parse_args().pixel_contract,'png-straight-rgb-v1')

if __name__=='__main__':unittest.main()
