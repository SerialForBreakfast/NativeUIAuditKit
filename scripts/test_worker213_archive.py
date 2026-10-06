import tarfile
import unittest
from focus_surface_intake import safe_members

class ArchiveTests(unittest.TestCase):
    def test_legacy_limit_preserved_explicit_checkpoint_budget(self):
        member=tarfile.TarInfo('checkpoints/last.pt');member.size=40*1024**2
        with self.assertRaises(ValueError):safe_members([member])
        members,total=safe_members([member],max_member_bytes=100*1024**2)
        self.assertEqual(total,member.size);self.assertEqual(len(members),1)
    def test_scope_does_not_relax_paths_or_types(self):
        for name in ('../escape','/absolute'):
            with self.assertRaises(ValueError):safe_members([tarfile.TarInfo(name)],max_member_bytes=100*1024**2)
        link=tarfile.TarInfo('link');link.type=tarfile.SYMTYPE
        with self.assertRaises(ValueError):safe_members([link],max_member_bytes=100*1024**2)
        for n in (True,0,101*1024**2):
            with self.assertRaises(ValueError):safe_members([],max_member_bytes=n)

if __name__=='__main__':unittest.main()
