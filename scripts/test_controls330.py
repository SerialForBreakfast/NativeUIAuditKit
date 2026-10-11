"""Check coordinates and label-independent region selection."""
import unittest
from unittest.mock import patch
from pathlib import Path
from types import SimpleNamespace
import json
import numpy as np
import controls330 as c


class Controls330Tests(unittest.TestCase):
    def test_letterbox_coordinates(self):
        self.assertEqual(c.encoded_box([0,0,3840,2160],[3840,2160]),[0,10,192,108])

    def test_centered_fixed_budget(self):
        x=np.zeros((6,128,192),np.float32);x[3:,40:45,90:95]=1
        result=c.select(x,[[1600,500,500,500]],[3840,2160])
        self.assertEqual(len(result),1)
        self.assertTrue(0<=result[0][0]<=160 and 0<=result[0][1]<=96)

    def test_identical_empty_and_duplicate(self):
        x=np.zeros((6,128,192),np.float32)
        self.assertEqual(c.select(x,[],[192,128]),[])
        self.assertEqual(c.select(x,[[0,0,32,32]],[192,128]),[])
        x[3:,:32,:32]=1
        self.assertEqual(c.select(x,[[0,0,32,32]]*3,[192,128]),[(0,0)])

    def test_frame_reversal_keeps_regions(self):
        x=np.random.default_rng(42).random((6,128,192),dtype=np.float32)
        props=[[0,0,20,20],[150,80,30,40],[60,40,20,20]]
        self.assertEqual(c.select(x,props,[192,128]),c.select(np.concatenate((x[3:],x[:3])),props,[192,128]))

    def test_invalid_input(self):
        with self.assertRaises(Exception):c.select(np.full((6,128,192),np.nan),[],[192,128])

    def test_pixel_boxes_clip_without_y_flip(self):
        payload=dict(status='success',width=192,height=128,
            configuration=dict(minConfidence=.25,ocr=False,platform='tvOS',strict=False),
            runtime=dict(result=dict(elements=[dict(confidenceSource='pixelModel',confidence=.9,
                boundingBoxPixels=dict(x=-2,y=7,width=12,height=20),state=dict(isFocused=True))])))
        self.assertEqual(c.boxes(payload),[[0,7,10,20]])
        payload['runtime']['result']['elements'][0]['state']['isFocused']=False
        self.assertEqual(c.boxes(payload),[[0,7,10,20]])

    def test_iou(self):
        self.assertEqual(c.iou([0,0,5,5],[0,0,5,5]),1)
        self.assertEqual(c.iou([0,0,5,5],[10,10,5,5]),0)

    def test_collect_entrypoint_initializes_and_checks_hash(self):
        pin=dict(path='frame.png',sha256='expected')
        membership=dict(rows=[dict(role='train',images=[pin,pin]),dict(role='development',images=[])])
        payload=dict(status='success',width=192,height=128,inputSHA256='expected',totalMs=1,
            configuration=dict(minConfidence=.25,ocr=False,platform='tvOS',strict=False),
            runtime=dict(detector=dict(modelID='test',treeSHA256='test'),result=dict(elements=[])))
        def execute(*args,**kwargs):
            messages=[json.loads(line) for line in kwargs['input'].splitlines()]
            self.assertEqual(messages[1]['method'],'notifications/initialized')
            self.assertEqual(len(messages),3)
            return SimpleNamespace(returncode=0,stderr='',stdout='\n'.join(map(json.dumps,[
                dict(id=0,result={}),dict(id=1,result=dict(structuredContent=payload))])))
        with patch.object(c,'OUT',Path('/unused-no-write-focus330')),patch.object(c.b,'read',return_value=membership),\
             patch.object(c.b,'checked',return_value=Path('frame.png')),patch.object(c.b,'ref',return_value=pin),\
             patch.object(c.b,'write') as write,patch.object(c.subprocess,'run',side_effect=execute):
            c.collect()
            self.assertEqual(len(write.call_args.args[1]['rows']),1)
            payload['inputSHA256']='altered'
            with self.assertRaisesRegex(ValueError,'image_identity'):c.collect()

    def test_report_counts(self):
        from report_controls330 import counts
        self.assertEqual(counts([.1,.9,.5],[0,0,1]),dict(rows=3,correct=1,falseChange=1,missedChange=0,abstentions=1))
        self.assertEqual(counts([],[])['rows'],0)


if __name__=='__main__':unittest.main()
