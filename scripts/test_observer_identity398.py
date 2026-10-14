"""Check the production digest vector and explicit rejection paths."""
from pathlib import Path
import tempfile
import unittest
import copy
import research_queue as q
from observer_identity398 import compiled_digest, verify_receipt


class DigestTests(unittest.TestCase):
    def test_receipt_positive_and_negative(self):
        row=dict(id='one',parentSHA256='a'*64,candidateID='box1',bounds=[1,2,3,4],
                 modelInputRGBSHA256='b'*64,score=.9,state='scored')
        expected=dict(bundleSHA256='c'*64,results=[row])
        receipt=dict(version='ttr-crop-observer-v2',navigationAuthority=False,backend='Vision',
            bundleSHA256='c'*64,compiledDigestAlgorithm='compiled-tree-sha256-v1',
            compiledBeforeSHA256='d'*64,compiledAfterSHA256='d'*64,
            osVersion='15',architecture='arm64',compilerVersion='test',sourceRevision='test',results=[row])
        self.assertEqual(verify_receipt(receipt,expected)['verifiedFrames'],1)
        for field,value in [('compiledAfterSHA256','e'*64),('navigationAuthority',True),('osVersion','')]:
            changed=copy.deepcopy(receipt);changed[field]=value
            with self.assertRaises(ValueError):verify_receipt(changed,expected)
        for field,value in [('parentSHA256','f'*64),('state','failed'),('score',float('nan')),('score',.8)]:
            changed=copy.deepcopy(receipt);changed['results'][0][field]=value
            with self.assertRaises(ValueError):verify_receipt(changed,expected)

    def test_vector_and_changed_bytes(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build') as folder:
            root=Path(folder); (root/'nested').mkdir()
            (root/'a.bin').write_bytes(bytes([0,1,255]))
            (root/'nested/b.txt').write_bytes(b'focus\n')
            expected='7d6c6b1e9b9bf952e0963de83fc3348c5d599d54ad6c5110edf13ccbf1f6cac7'
            self.assertEqual(compiled_digest(root),expected)
            (root/'a.bin').write_bytes(b'changed')
            self.assertNotEqual(compiled_digest(root),expected)

    def test_empty_and_link_rejected(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build') as folder:
            root=Path(folder)
            with self.assertRaisesRegex(ValueError,'empty'): compiled_digest(root)
            (root/'link').symlink_to(root)
            with self.assertRaisesRegex(ValueError,'special'): compiled_digest(root)


if __name__=='__main__': unittest.main()
