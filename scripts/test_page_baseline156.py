import copy
import unittest
import page_baseline156 as p


class PageBaselineTests(unittest.TestCase):
    def test_artifact_identity(self):
        f=dict(checkpointSHA256='a',manifestSHA256='b',settings={'imgsz':640})
        a=dict(model={'checkpointSHA256':'a'},corpus={'inputManifestSHA256':'b'},settings=f['settings'],categoryMap={'sha256':p.e.sha256_file(p.e.CATEGORY_MAP)})
        p.verify_artifact(a,f)
        bad=copy.deepcopy(a);bad['model']['checkpointSHA256']='wrong'
        with self.assertRaisesRegex(ValueError,'identity'):p.verify_artifact(bad,f)
        bad=copy.deepcopy(a);bad['settings']['imgsz']=1280
        with self.assertRaisesRegex(ValueError,'identity'):p.verify_artifact(bad,f)
    def test_existing_ap_matching(self):
        g={18:{'a':[(0,0,10,10)],'b':[(0,0,10,10)]}}
        self.assertEqual(p.e.compute_ap_at_iou(g,{18:[('a',.9,(0,0,10,10)),('b',.8,(0,0,10,10))]},18,.5),1)
        self.assertEqual(p.e.compute_ap_at_iou(g,{18:[]},18,.5),0)


if __name__=='__main__':unittest.main()
