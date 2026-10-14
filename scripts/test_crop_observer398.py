"""Check observer wrapping without claiming consumer inference."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace
import research_queue as q
import crop_observer398 as observer


class ObserverTests(unittest.TestCase):
    def test_success_and_process_failure(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build') as folder:
            root=Path(folder);(root/'Package.swift').touch();(root/'.build').mkdir()
            model=root/'model';model.mkdir();(model/'weights').write_bytes(b'test')
            item=dict(id='one',sha256='a'*64,bounds=[1,2,3,4])
            request=dict(version=1,mode='vision',root=str(root),model=str(model),items=[item])
            tool=root/'.build/FocusRingTool'
            reply=dict(results=[dict(id='one',probability=.9,modelInputRGBSHA256='b'*64)])
            with patch.object(observer.subprocess,'run',return_value=SimpleNamespace(returncode=0,stdout=json.dumps(reply))):
                result=observer.run(request,tool,'c'*64,'test')
                self.assertEqual(result['results'][0]['parentSHA256'],'a'*64)
                self.assertFalse(result['navigationAuthority'])
            with patch.object(observer.subprocess,'run',return_value=SimpleNamespace(returncode=1)):
                with self.assertRaisesRegex(ValueError,'vision_failed'):observer.run(request,tool,'c'*64,'test')
            with self.assertRaisesRegex(ValueError,'tool_boundary'):observer.run(request,root/'other','c'*64,'test')


if __name__=='__main__':unittest.main()
