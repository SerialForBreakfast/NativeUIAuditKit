import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
import artifact_storage as s
import focus_dataset_contract as f
import photos_focus_pilot as p
import human_annotation_review as h


class StorageTests(unittest.TestCase):
    def setUp(self):
        base=s.ROOT/'.build/debug-output/storage-tests';base.mkdir(parents=True,exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=base);self.addCleanup(self.tmp.cleanup)
        top=Path(self.tmp.name);self.root=top/'repo';self.root.mkdir()
        self.base=top/'ssd';self.base.mkdir();self.reg=self.root/'registry.json'
        self.logical=self.root/'reports/work/example/artifacts'
        self.physical=self.base/'live/reports/work/example/artifacts';self.physical.mkdir(parents=True)
        for obj,name,value in ((s,'ROOT',self.root),(s,'BASE',self.base),(s,'REGISTRY',self.reg),
                               (f,'ROOT',self.root),(p,'ROOT',self.root)):
            ctx=patch.object(obj,name,value);ctx.start();self.addCleanup(ctx.stop)
        s._cache=None;s._mounted=None
        self.doc=dict(version='artifact-storage-v1',device='/dev/disk25s1',mappings=[
            dict(logical='reports/work/example/artifacts',physical='live/reports/work/example/artifacts')])
        self.reg.write_text(json.dumps(self.doc))

    def test_logical_reference_and_member_keep_identity(self):
        (self.physical/'x.json').write_text('{"x":1}')
        with patch.object(s,'mounted'):
            actual=f.member(self.root,'reports/work/example/artifacts/x.json')
            self.assertEqual(actual,self.physical/'x.json')
            self.assertEqual(p.ref(actual)['path'],'reports/work/example/artifacts/x.json')
            self.assertEqual(p.ref(actual),p.ref(self.logical/'x.json'))
            self.assertEqual(p.checked(self.root,p.ref(actual)),actual)

    def test_outputs_and_unknown_external_paths_rejected(self):
        with self.assertRaisesRegex(ValueError,'read_only'):p.fresh(self.logical/'new.json')
        with self.assertRaises(ValueError):s.resolve_input(self.base/'unknown')
        with patch.object(s,'mounted'):
            with self.assertRaises(ValueError):p.fresh(self.physical/'new.json')

    def test_external_editor_snapshot_retains_logical_image_binding(self):
        image=self.physical/'sample.png';image.write_bytes(b'hash-binding-fixture')
        frame=dict(editorStem='sample',size=[10,10],image={'sha256':p.sha(image)},proposals=[])
        doc=dict(version=h.EDITOR,nuiak={},imagePath='sample.png',imageData=None,
                 imageWidth=10,imageHeight=10,flags={k:True for k in h.FRAME_FLAGS},shapes=[])
        with patch.object(s,'mounted'),patch.object(h,'ROOT',self.root),patch.object(h,'binding',return_value={}):
            self.assertEqual(h.parse_editor_document({'id':'fixture'},frame,self.physical/'sample.json',doc),[])

    def test_no_mount_never_falls_back_to_existing_local_copy(self):
        self.logical.mkdir(parents=True);(self.logical/'x').write_text('local')
        with patch.object(s,'mounted',side_effect=s.StorageError('storage_volume_unavailable')):
            with self.assertRaisesRegex(ValueError,'volume_unavailable'):f.member(self.root,'reports/work/example/artifacts/x')

    def test_overlaps_traversal_and_source_code_mappings_rejected(self):
        for row in (dict(logical='reports/work/example/artifacts/sub',physical='live/other'),
                    dict(logical='scripts',physical='live/code'),
                    dict(logical='reports/work/../secret',physical='live/secret')):
            self.doc['mappings'].append(row);self.reg.write_text(json.dumps(self.doc));s._cache=None
            with self.assertRaises(ValueError):s.mappings()
            self.doc['mappings'].pop()

    def test_symlink_escape_and_missing_file(self):
        (self.physical/'escape').symlink_to(self.root)
        with patch.object(s,'mounted'):
            with self.assertRaises(ValueError):f.member(self.root,'reports/work/example/artifacts/escape/file')
            with self.assertRaisesRegex(ValueError,'missing_pixels'):f.member(self.root,'reports/work/example/artifacts/missing')

    def test_no_registry_retains_local_behavior(self):
        self.reg.unlink();p0=self.root/'a';p0.write_text('a')
        self.assertEqual(s.resolve_input(p0),p0)
        self.assertEqual(s.local_output(self.root/'new'),self.root/'new')

    def test_mount_checks_wrong_device_and_absent_volume(self):
        with patch.object(Path,'is_mount',return_value=False):
            with self.assertRaisesRegex(ValueError,'volume_unavailable'):s.mounted('/dev/disk25s1')
        with patch.object(Path,'is_mount',return_value=True),patch.object(Path,'stat',autospec=True,
                side_effect=lambda p:SimpleNamespace(st_dev=1 if p==s.VOLUME else 2)),\
                patch.object(s.subprocess,'check_output',return_value='/dev/disk99 on /Volumes/training-drive (apfs, local, nodev)'):
            with self.assertRaisesRegex(ValueError,'wrong_volume'):s.mounted('/dev/disk25s1')


if __name__=='__main__':unittest.main()
