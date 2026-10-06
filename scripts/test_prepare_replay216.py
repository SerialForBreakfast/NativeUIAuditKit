import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import prepare_replay216 as p


class Replay216Tests(unittest.TestCase):
    def test_matched_slots(self):
        old=[f'old-{i}' for i in range(1509)];new=[f'new-{i}' for i in range(60)]
        a=p.slot_plan(old,new)
        self.assertEqual(a,p.slot_plan(old,new))
        self.assertEqual([len(v) for v in a.values()],[1569,1569])
        self.assertEqual(a['control'][:1509],a['treatment'][:1509])
        self.assertEqual(len(set(a['control'])),1509)
        self.assertEqual(len(set(a['treatment'])),1569)

    def test_duplicate_or_cross_role_ids(self):
        old=[str(i) for i in range(1509)]
        for new in [old[:60],['new']*60,[]]:
            with self.assertRaisesRegex(ValueError,'slot_membership'):p.slot_plan(old,new)

    def test_pixel_roles(self):
        p.check_pixels(['a','b'],['c'])
        with self.assertRaisesRegex(ValueError,'duplicate'):p.check_pixels(['a','a'],[])
        with self.assertRaisesRegex(ValueError,'reserved'):p.check_pixels(['a'],['a'])

    def test_resident_label_and_role(self):
        row=dict(role='train',image='a',label='b')
        refs={'a':dict(sha256='i'),'b':dict(sha256='l')}
        image=SimpleNamespace(image_sha256='i',label_sha256='l')
        p.resident_match(row,image,refs)
        for changed in [dict(row,role='validation'),dict(row,label='a')]:
            with self.assertRaisesRegex(ValueError,'resident_changed'):p.resident_match(changed,image,refs)

    def test_archive_bounds(self):
        good=SimpleNamespace(size=1,isfile=lambda:True)
        p.check_archive([good])
        for bad in [[good]*2101,[SimpleNamespace(size=17*1024**2,isfile=lambda:True)],
                    [SimpleNamespace(size=1,isfile=lambda:False)]]:
            with self.assertRaisesRegex(ValueError,'archive_budget'):p.check_archive(bad)

    def test_actual_entrypoint_collision_and_changed_source(self):
        base=p.ROOT/'.build/debug-output';base.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as directory:
            root=Path(directory)
            with self.assertRaisesRegex(ValueError,'collision'):p.prepare(root)
            target=root/'new'
            with patch.object(p,'sha',return_value='changed'):
                with self.assertRaisesRegex(ValueError,'source_changed'):p.prepare(target)
            self.assertFalse(target.exists())


if __name__=='__main__':unittest.main()
