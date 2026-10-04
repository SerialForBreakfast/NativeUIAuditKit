import unittest
from unittest.mock import patch
import adapt_reflow117 as a


class ReflowTests(unittest.TestCase):
    def test_historical_batch_boundary(self):
        torch=a.r.d.torch_runtime();x=torch.arange(433);calls=[]
        def fake(net,part,config):calls.append(len(part));return part
        with patch.object(a.r.c,'score_change',side_effect=fake):out=a.score(None,x)
        self.assertEqual(calls,[424,9]);self.assertTrue(torch.equal(out,x))
        with self.assertRaises(ValueError):a.score(None,x[:424])

    def test_group_accounting(self):
        self.assertEqual(a.CONFIG['originalGroupCount']+a.CONFIG['derivedGroupCount'],433)
        self.assertEqual(a.CONFIG['originalGroupCount'],207)
        self.assertEqual(a.CONFIG['epochs'],600)


if __name__=='__main__':unittest.main()
