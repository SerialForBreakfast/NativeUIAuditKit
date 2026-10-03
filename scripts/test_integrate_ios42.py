import copy
import unittest
import integrate_ios42 as i


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.entries=[dict(fileName=f'train/img_{n:06d}.png') for n in range(666)]
        self.patch=dict(version='ios-page-dot-corpus-patch-v1',split='train',count=666,
            members=[dict(imageID=e['fileName'].replace('train/','train/images/')) for e in self.entries])

    def test_exact_replacement_membership(self):
        self.assertEqual(len(i.replacement_map(self.entries,self.patch)),666)

    def test_duplicate_patch_rejected(self):
        self.patch['members'][-1]=copy.deepcopy(self.patch['members'][0])
        with self.assertRaisesRegex(ValueError,'invalid_patch_member'):i.replacement_map(self.entries,self.patch)

    def test_evaluation_replacement_rejected(self):
        self.entries[0]['fileName']='test/img_000000.png';self.patch['members'][0]['imageID']='test/images/img_000000.png'
        with self.assertRaisesRegex(ValueError,'invalid_patch_member'):i.replacement_map(self.entries,self.patch)

    def test_unknown_replacement_rejected(self):
        self.patch['members'][0]['imageID']='train/images/img_999999.png'
        with self.assertRaisesRegex(ValueError,'invalid_patch_member'):i.replacement_map(self.entries,self.patch)

    def test_count_mismatch_rejected(self):
        self.patch['members'].pop()
        with self.assertRaisesRegex(ValueError,'membership_count'):i.replacement_map(self.entries,self.patch)

    def test_duplicate_original_rejected(self):
        self.entries.append(copy.deepcopy(self.entries[0]))
        with self.assertRaisesRegex(ValueError,'duplicate_source'):i.replacement_map(self.entries,self.patch)


if __name__=='__main__':unittest.main()
