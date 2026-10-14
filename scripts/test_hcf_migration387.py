"""Keep retained HCF pixels and labels unchanged after relocation."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import hcf_compare371 as h


class HCFMigrationTests(unittest.TestCase):
    def test_explicit_path_move_checks_original_hash(self):
        with tempfile.TemporaryDirectory(dir=h.q.ROOT/'.build/debug-output') as name:
            root=Path(name);out=root/'out';out.mkdir()
            (root/'image.png').write_bytes(b'original pixels')
            h.q.save(out/'config.json',dict(roles=['retained'],sourceProjectRoot='/old/project'))
            row=dict(id='retained-1',role='retained',path='/old/project/image.png',
                     sha256=h.q.digest(root/'image.png'),focus='item-1',group='retained-group')
            def docs():return [dict(rows=[dict(row)])]
            with patch.object(h.q,'ROOT',root),patch.object(h,'OUT',out), \
                 patch.object(h.study,'dependency',side_effect=lambda _:docs()):
                rows,cfg=h.corpus()
                self.assertEqual(rows[0]['path'],str(root/'image.png'))
                self.assertEqual(rows[0]['focus'],row['focus'])
                self.assertEqual(rows[0]['sha256'],row['sha256'])
                (root/'image.png').write_bytes(b'changed')
                with self.assertRaisesRegex(ValueError,'comparison_image_changed'):h.corpus()


if __name__=='__main__':unittest.main()
