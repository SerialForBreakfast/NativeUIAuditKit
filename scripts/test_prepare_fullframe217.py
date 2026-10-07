from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch
import prepare_fullframe217 as p


class Fullframe217Tests(unittest.TestCase):
    def test_family_from_bound_sidecar(self):
        annotation={'generatorProfile':{'templateFamily':'KitchenSink'}}
        self.assertEqual(p.source_family({},annotation),'KitchenSink')
        self.assertEqual(p.source_family({'family':'KitchenSink'},annotation),'KitchenSink')
        with self.assertRaisesRegex(ValueError,'family_binding'):
            p.source_family({'family':'Other'},annotation)

    def test_slots(self):
        old=[f'old{i}' for i in range(1509)];new=[f'native{i}' for i in range(60)]
        full=[f'full{i}' for i in range(189)]
        parent={'control':old+old[:60],'treatment':old+new}
        result=p.slots(parent,full)
        self.assertEqual(result,p.slots(parent,full))
        self.assertEqual([len(v) for v in result.values()],[1758,1758])
        self.assertEqual(result['control'][:1698],result['treatment'][:1698])
        self.assertEqual(result['treatment'][-60:],new)
        for bad in [full[:-1],full[:-1]+full[:1],old[:189]]:
            with self.assertRaises(ValueError):p.slots(parent,bad)
        for bad in [dict(parent,treatment=old+new[:-1]),dict(parent,control=old+new)]:
            with self.assertRaises(ValueError):p.slots(bad,full)

    def test_ancestry_and_pixels(self):
        row=dict(id='train/a.png',split='train',pixelSHA256='pixel',image={'sha256':'image'})
        p.check_reserved([row],[],set(),set(),[])
        for args in [([row,row],[],set(),set(),[]),([dict(row,split='test')],[],set(),set(),[]),
                     ([row],[],{'image'},set(),[]),([row],[],set(),{'a'},[]),
                     ([row],[],set(),set(),['pixel']),([row],[dict(row,id='test/a.png')],set(),set(),[])]:
            with self.assertRaises(ValueError):p.check_reserved(*args)

    def test_archive_limits(self):
        good=SimpleNamespace(size=1,isfile=lambda:True)
        p.archive_bounds([good])
        for bad in [[good]*601,[SimpleNamespace(size=17*1024**2,isfile=lambda:True)],
                    [SimpleNamespace(size=1,isfile=lambda:False)]]:
            with self.assertRaisesRegex(ValueError,'archive_budget'):p.archive_bounds(bad)

    def test_real_entrypoint_collision_and_changed_source(self):
        base=p.ROOT/'.build/debug-output';base.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as directory:
            root=Path(directory)
            with self.assertRaisesRegex(ValueError,'collision'):p.prepare(root)
            with patch.object(p,'sha',return_value='changed'):
                with self.assertRaisesRegex(ValueError,'source_changed'):p.prepare(root/'new')
            self.assertFalse((root/'new').exists())


if __name__=='__main__':unittest.main()
