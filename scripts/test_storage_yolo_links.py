import json
import os
import hashlib
from unittest.mock import patch
import unittest
import storage_yolo_links as y
import export_coco as e
from test_artifact_storage import StorageTests


class YoloStorageTests(unittest.TestCase):
    def setUp(self):
        StorageTests.setUp(self)
        self.corpus=self.root/'NativeUITrainer/reconstructed_corpora/example'
        self.corpus.mkdir(parents=True)
        self.original=self.corpus/'a.png';self.original.write_bytes(b'immutable-pixels')
        self.copy=self.base/'live/NativeUITrainer/reconstructed_corpora/example'
        self.copy.mkdir(parents=True);(self.copy/'a.png').write_bytes(self.original.read_bytes())
        (self.copy/'manifest.json').write_text('{}')
        self.link=self.root/'NativeUITrainer/export/train/images/a.png'
        self.link.parent.mkdir(parents=True);self.link.symlink_to(self.original)
        self.doc['mappings'].append(dict(logical=str(self.corpus.relative_to(self.root)),
                                       physical=str(self.copy.relative_to(self.base))))
        self.reg.write_text(json.dumps(self.doc))
        for target,kwargs in ((y.s,'mounted'),):
            ctx=patch.object(target,kwargs);ctx.start();self.addCleanup(ctx.stop)
        ctx=patch.object(y.subprocess,'check_output',return_value=b'');ctx.start();self.addCleanup(ctx.stop)
        self.inventory=y.plan([self.corpus])

    def test_rebind_and_post_removal_verification(self):
        self.assertEqual(y.rebind(self.inventory),1)
        self.original.unlink()
        self.assertEqual(len(y.verify(self.inventory,True)),1)
        self.assertEqual(self.link.read_bytes(),b'immutable-pixels')
        self.assertEqual(self.inventory['rows'][0]['old'],str(self.original))

    def test_changed_destination_and_changed_link_fail_before_mutation(self):
        (self.copy/'a.png').write_bytes(b'corrupt')
        with self.assertRaisesRegex(ValueError,'destination_changed'):y.rebind(self.inventory)
        self.assertEqual(os.readlink(self.link),str(self.original))
        (self.copy/'a.png').write_bytes(self.original.read_bytes())
        self.link.unlink();self.link.symlink_to(self.copy/'a.png')
        with self.assertRaisesRegex(ValueError,'link_changed'):y.rebind(self.inventory)

    def test_unmounted_and_tampered_inventory_rejected(self):
        with patch.object(y.s,'mounted',side_effect=ValueError('unmounted')):
            with self.assertRaisesRegex(ValueError,'unmounted'):y.rebind(self.inventory)
        self.inventory['rows'][0]['source']='../escape'
        with self.assertRaisesRegex(ValueError,'inventory_changed'):y.rebind(self.inventory)

    def test_explicit_export_input_maps_and_missing_input_never_falls_back(self):
        with patch.object(e,'PROJECT_ROOT',self.root):
            self.assertEqual(e.discover_dataset(str(self.corpus)),self.copy)
            with self.assertRaisesRegex(ValueError,'explicit_dataset_missing'):
                e.discover_dataset(str(self.root/'missing'))

    def test_frozen_export_ignores_extras_but_rejects_missing_changed_duplicate_members(self):
        root=self.corpus; (root/'train').mkdir()
        png=root/'train/a.png';png.write_bytes(b'original');png.with_suffix('.json').write_text('{}')
        (root/'train/a 2.png').write_bytes(b'duplicate');(root/'train/a 2.json').write_text('{}')
        entry=dict(fileName='train/a.png',split='train',sha256=hashlib.sha256(b'original').hexdigest())
        manifest=root/'manifest.json';manifest.write_text(json.dumps(dict(entries=[entry])))
        self.assertEqual(len(e.manifest_pairs(root)),1)
        png.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'changed_manifest'):e.manifest_pairs(root)
        png.write_bytes(b'original');manifest.write_text(json.dumps(dict(entries=[entry,entry])))
        with self.assertRaisesRegex(ValueError,'invalid_manifest'):e.manifest_pairs(root)
        manifest.write_text(json.dumps(dict(entries=[entry])));png.with_suffix('.json').unlink()
        with self.assertRaisesRegex(ValueError,'missing_manifest'):e.manifest_pairs(root)


if __name__=='__main__':unittest.main()
