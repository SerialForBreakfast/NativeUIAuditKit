import copy
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import compose_worker213 as worker


class WorkerCompositionTests(unittest.TestCase):
    def inputs(self):
        row=dict(imageID='one',width=100,height=200,status='ok',detections=[
            dict(classID=2,score=.8,xyxyPixels=[10,10,20,20])])
        req=SimpleNamespace(images=[SimpleNamespace(image_id='one',width=100,height=200)])
        return dict(results=[row]),dict(results=[copy.deepcopy(row)]),[dict(imageID='one',cropID=None,reason='no_candidate')],dict(results=[]),18,req

    def test_actual_merge_preserves_non_page(self):
        args=self.inputs();before=copy.deepcopy(args[:4])
        output,counts=worker.composed(*args)
        self.assertEqual(args[:4],before)
        self.assertEqual(output,args[0]);self.assertEqual(counts,{'no_extra':1})

    def test_missing_membership_and_mutated_nonpage(self):
        args=list(self.inputs());args[2]=[]
        with self.assertRaisesRegex(ValueError,'base_membership'):worker.composed(*args)
        args=list(self.inputs());args[1]['results'][0]['detections'][0]['score']=.9
        with self.assertRaisesRegex(ValueError,'non_page_change'):worker.composed(*args)

    def test_entry_collision_before_collection(self):
        with patch.object(worker.c,'collect') as collect:
            with self.assertRaisesRegex(ValueError,'collision'):worker.run(Path(__file__).absolute())
            collect.assert_not_called()


if __name__=='__main__':unittest.main()
