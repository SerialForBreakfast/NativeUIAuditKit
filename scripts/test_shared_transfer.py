import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import shared_transfer as t


class TransferTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=t.ROOT/'.build')
        self.addCleanup(self.tmp.cleanup)
        root=Path(self.tmp.name);self.local=root/'repo';self.share=root/'share'
        for p in (self.local,self.share/'nuiak',self.share/'tvtestrig'):p.mkdir(parents=True)
        self.tx=dict(version=1,requestID='test-123',sharedPath='nuiak/artifact.zip',localPath='original.zip',
            bytes=4,sha256=hashlib.sha256(b'data').hexdigest(),receiptPath='tvtestrig/receipt.yaml')
        (self.local/'original.zip').write_bytes(b'data')
        self.path=self.local/'transaction.json';self.save()
        for target,value in [('ROOT',self.local),('SHARE',self.share)]:
            ctx=patch.object(t,target,value);ctx.start();self.addCleanup(ctx.stop)
        self.mount=patch.object(t,'mounted');self.mount_mock=self.mount.start();self.addCleanup(self.mount.stop)

    def save(self):self.path.write_text(json.dumps(self.tx))
    def receipt(self,**changes):
        r=dict(schema_version=1,request_id=self.tx['requestID'],state='copied_and_verified',
               artifact=dict(file=self.tx['sharedPath'],verified_bytes=4,verified_sha256=self.tx['sha256']))
        r.update({'from':'TVTestRig','to':'NUIAK'});r.update(changes)
        (self.share/'tvtestrig/receipt.yaml').write_text(json.dumps(r))
    def run_action(self,action='inspect',execute=False):return t.run(self.path,action,execute)

    def test_default_and_dry_run_do_not_write(self):
        before=list(self.share.rglob('*'))
        self.assertEqual(self.run_action()['state'],'inspected')
        self.assertEqual(self.run_action('publish')['state'],'inputs_verified_execution_not_proven')
        self.assertEqual(before,list(self.share.rglob('*')))

    def test_publish_retry_and_no_overwrite(self):
        self.assertEqual(self.run_action('publish',True)['state'],'copied_and_verified')
        self.assertEqual(self.run_action('publish',True)['state'],'already_verified')
        (self.share/'nuiak/artifact.zip').write_bytes(b'evil')
        with self.assertRaisesRegex(ValueError,'hash_mismatch'):self.run_action('publish',True)
        self.assertEqual((self.share/'nuiak/artifact.zip').read_bytes(),b'evil')

    def test_exclusive_rename_never_replaces_existing(self):
        a=self.local/'a';b=self.local/'b';a.write_bytes(b'a');b.write_bytes(b'b')
        with self.assertRaises(OSError):t.exclusive_rename(a,b)
        self.assertEqual(a.read_bytes(),b'a');self.assertEqual(b.read_bytes(),b'b')

    def test_partial_staging_preserved_and_completed_staging_resumed(self):
        with patch.object(t,'exclusive_rename',side_effect=OSError('simulated interruption')):
            with self.assertRaises(OSError):self.run_action('publish',True)
        stage=next((self.share/'nuiak').glob('*.partial'))
        stage.write_bytes(b'd')
        with self.assertRaisesRegex(ValueError,'size_or_type'):self.run_action('publish',True)
        self.assertEqual(stage.read_bytes(),b'd')
        stage.write_bytes(b'data')
        self.assertEqual(self.run_action('publish',True)['state'],'copied_and_verified')
        self.assertFalse(stage.exists())

    def test_cleanup_requires_exact_receipt_and_keeps_original(self):
        self.run_action('publish',True)
        with self.assertRaisesRegex(ValueError,'matching_receipt_required'):self.run_action('cleanup',True)
        self.receipt(request_id='different')
        with self.assertRaisesRegex(ValueError,'receipt_identity'):self.run_action('cleanup',True)
        self.receipt();self.assertEqual(self.run_action('cleanup')['state'],'inputs_verified_execution_not_proven')
        self.assertTrue((self.share/'nuiak/artifact.zip').exists())
        self.assertEqual(self.run_action('cleanup',True)['state'],'shared_copy_removed_original_retained')
        self.assertEqual((self.local/'original.zip').read_bytes(),b'data')
        self.assertEqual(self.run_action('cleanup',True)['state'],'receipt_verified_shared_already_absent')

    def test_cleanup_receipt_artifact_mismatches(self):
        self.run_action('publish',True)
        for key,value in [('file','nuiak/other.zip'),('verified_bytes',5),('verified_sha256','0'*64)]:
            self.receipt();p=self.share/'tvtestrig/receipt.yaml';r=json.loads(p.read_text());r['artifact'][key]=value;p.write_text(json.dumps(r))
            with self.assertRaisesRegex(ValueError,'receipt_artifact'):self.run_action('cleanup',True)
            self.assertTrue((self.share/'nuiak/artifact.zip').exists())

    def test_changed_or_missing_original_blocks_cleanup(self):
        self.run_action('publish',True);self.receipt()
        original=self.local/'original.zip';original.write_bytes(b'evil')
        with self.assertRaisesRegex(ValueError,'hash_mismatch'):self.run_action('cleanup',True)
        original.unlink()
        with self.assertRaisesRegex(ValueError,'original_missing'):self.run_action('cleanup',True)
        self.assertTrue((self.share/'nuiak/artifact.zip').exists())

    def test_receive_returns_receipt_not_admission(self):
        self.tx.update(sharedPath='tvtestrig/data.zip',localPath='new.zip',receiptPath=None);self.save()
        (self.share/'tvtestrig/data.zip').write_bytes(b'data')
        r=self.run_action('receive',True)
        self.assertEqual(r['receiverReceipt']['artifact']['verified_sha256'],self.tx['sha256'])
        self.assertFalse(r['trainingEligible']);self.assertEqual(r['receiverReceipt']['intake'],'not_assessed')
        self.assertTrue((self.share/'tvtestrig/data.zip').exists())
        with self.assertRaisesRegex(ValueError,'write_namespace'):self.run_action('cleanup',True)

    def test_missing_mount_and_space(self):
        self.mount_mock.side_effect=ValueError('mount_missing')
        with self.assertRaisesRegex(ValueError,'mount_missing'):self.run_action('publish',True)
        self.mount_mock.side_effect=None
        with patch.object(t.shutil,'disk_usage',return_value=type('Usage',(),{'free':0})()):
            with self.assertRaisesRegex(ValueError,'insufficient_space'):self.run_action('publish',True)
        self.assertEqual(list((self.share/'nuiak').iterdir()),[])

    def test_traversal_symlinks_and_protected_status(self):
        for path in ('../outside','/absolute','nuiak/../other','nuiak/status.yaml'):
            self.tx['sharedPath']=path;self.save()
            with self.assertRaises(ValueError):self.run_action('publish',True)
        self.tx['sharedPath']='nuiak/artifact.zip';self.save()
        (self.share/'nuiak/artifact.zip').symlink_to(self.local/'original.zip')
        with self.assertRaisesRegex(ValueError,'symlink_or_boundary'):self.run_action('publish',True)

    def test_unknown_and_duplicate_transaction(self):
        self.tx['expiry']='yesterday';self.save()
        with self.assertRaisesRegex(ValueError,'transaction_contract'):self.run_action()
        self.path.write_text('version: 1\nversion: 1\n')
        with self.assertRaisesRegex(ValueError,'duplicate_key'):self.run_action()


if __name__=='__main__':unittest.main()
