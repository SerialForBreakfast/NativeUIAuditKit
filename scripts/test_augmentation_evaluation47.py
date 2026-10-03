import unittest
from unittest.mock import patch
from evaluate_augmentation47 import expected_controls
from summarize_augmentation47 import terminal


class EvaluationTests(unittest.TestCase):
    def test_geometry_reconstructed_from_original(self):
        f=dict(size=[3840,2160],controls=[dict(id='a',state='focused',bounds=[600,600,600,300])])
        for variant,offset in [('top',0),('center',140),('bottom',280),('aligned-128',12),('aligned128',268)]:
            controls,y=expected_controls(f,variant)
            self.assertEqual(y,offset);self.assertEqual(controls[0]['bounds'],[100,100+offset,100,50])
        self.assertEqual(expected_controls(f,'rect1280'),(f['controls'],None))
        with self.assertRaises(ValueError):expected_controls(f,'unknown')

    def test_terminal_matching_and_pair_counts(self):
        frames=[dict(id=f'case-{i//2}-{i%2}',split='evaluation',annotation={}) for i in range(500)]
        rows=[dict(id=f['id'],predictedBounds=[[0,0,10,10]],tp=1,fp=0,fn=0) for f in frames]
        report=dict(frames=rows,totals=dict(tp=500,fp=0,fn=0),exactFrames=500,seconds=1)
        ann={'controls':[dict(id='item-0',state='focused',bounds=[0,0,10,10])]}
        with patch('summarize_augmentation47.h.checked',return_value=None),patch('summarize_augmentation47.h.read',return_value=ann):
            r=terminal({'frames':frames},report)
            self.assertEqual(r['completePairs'],250);self.assertEqual(r['exactFrames'],500)
            report['totals']['fp']=1
            with self.assertRaisesRegex(ValueError,'terminal_aggregate'):terminal({'frames':frames},report)


if __name__=='__main__':unittest.main()
