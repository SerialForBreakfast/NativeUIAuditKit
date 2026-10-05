import tempfile
from pathlib import Path
import unittest
import ios_label_audit149 as a


class AuditTests(unittest.TestCase):
    def test_letterbox_scale_not_stretch(self):
        row=a.geometry([.5,.5,9/1179,180/2556],1179,2556)
        self.assertAlmostEqual(row[3],9*640/2556)
        self.assertAlmostEqual(row[4],2*row[3])
        self.assertAlmostEqual(row[2],.05)

    def test_invalid_geometry_and_paths(self):
        for box in ([.5,.5,0,.2],[.5,.5,2,.2],[.5,.5,float('nan'),.2]):
            with self.assertRaises(ValueError):a.geometry(box,100,100)
        for path in ('../outside','/absolute','x/../y'):
            with self.assertRaises(ValueError):a.safe(a.ROOT,path)

    def test_summary_support(self):
        s=a.summarize([[.1,.1,1,2,4],[.2,.2,1,4,8]])
        self.assertEqual(s['count'],2);self.assertEqual(s['shortEdgeBelow3At640'],1)
        self.assertEqual(s['median'][3],3)

    def test_entrypoint_collision_before_corpus_access(self):
        with tempfile.TemporaryDirectory(dir=a.ROOT/'.build') as d:
            p=Path(d)/'existing.json';p.write_text('retained')
            with self.assertRaises(ValueError):a.run(p)
            with self.assertRaises(ValueError):a.current(p)
            self.assertEqual(p.read_text(),'retained')


if __name__=='__main__':unittest.main()
