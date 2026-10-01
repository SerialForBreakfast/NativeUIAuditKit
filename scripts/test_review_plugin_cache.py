"""Qt cache layout/identity checks; generated files stay under .build."""
from pathlib import Path
import shutil
import tempfile
import unittest

import human_review_editor as e


class PluginCacheTests(unittest.TestCase):
    def setUp(self):
        parent=e.ROOT/'.build/plugin-cache-tests';parent.mkdir(parents=True,exist_ok=True)
        self.root=Path(tempfile.mkdtemp(dir=parent))
        self.plugins=self.root/'Qt5/plugins';(self.plugins/'platforms').mkdir(parents=True)
        (self.root/'Qt5/lib').mkdir()
        self.source=self.plugins/'platforms/libqcocoa.dylib';self.source.write_bytes(b'generated-plugin')

    def tearDown(self):shutil.rmtree(self.root)

    def test_repeated_cache_preserves_relative_framework_lookup_and_source(self):
        before=self.source.read_bytes();flags=self.source.stat().st_flags
        cached=e.cache_platform_plugins(self.plugins,self.root/'runtime')
        copied=cached/'platforms/libqcocoa.dylib'
        self.assertEqual(copied.read_bytes(),before)
        self.assertEqual((copied.parent/'../../lib').resolve(),self.root/'Qt5/lib')
        self.assertEqual(e.cache_platform_plugins(self.plugins,self.root/'runtime'),cached)
        self.assertEqual(self.source.read_bytes(),before);self.assertEqual(self.source.stat().st_flags,flags)

    def test_modified_cache_not_silently_overwritten(self):
        cached=e.cache_platform_plugins(self.plugins,self.root/'runtime')
        (cached/'platforms/libqcocoa.dylib').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'changed_qt_plugin_cache'):
            e.cache_platform_plugins(self.plugins,self.root/'runtime')

    def test_wrong_or_nonlink_library_rejected(self):
        cached=e.cache_platform_plugins(self.plugins,self.root/'runtime')
        link=cached.parent/'lib';link.unlink();other=self.root/'other';other.mkdir();link.symlink_to(other)
        with self.assertRaisesRegex(ValueError,'changed_qt_framework_link'):
            e.cache_platform_plugins(self.plugins,self.root/'runtime')
        link.unlink();link.mkdir()
        with self.assertRaisesRegex(ValueError,'qt_framework_link_collision'):
            e.cache_platform_plugins(self.plugins,self.root/'runtime')


if __name__=='__main__':unittest.main()
