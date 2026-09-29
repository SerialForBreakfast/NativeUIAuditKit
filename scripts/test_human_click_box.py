import unittest
from PIL import Image, ImageDraw
from human_click_box import suggest
import human_annotation_review as h
import test_human_annotation_review as fixtures


class SuggestTests(unittest.TestCase):
    def test_flat_rounded_panel(self):
        image=Image.new('RGB',(320,200),'#202020')
        ImageDraw.Draw(image).rounded_rectangle((40,50,180,100),radius=8,fill='white')
        box=suggest(image,(80,75))
        self.assertIsNotNone(box)
        for actual,expected in zip(box[0]+box[1],[40,50,181,101]): self.assertLessEqual(abs(actual-expected),2)

    def test_background_clipped_and_invalid_click_abstain(self):
        image=Image.new('RGB',(320,200),'#202020')
        self.assertIsNone(suggest(image,(100,100)))
        self.assertIsNone(suggest(image,(-1,0)))
        self.assertIsNone(suggest(image,(float('nan'),0)))
        ImageDraw.Draw(image).rectangle((0,20,80,80),fill='white')
        self.assertIsNone(suggest(image,(20,40)))

    def test_circle_not_rectangle(self):
        image=Image.new('RGB',(320,200),'black')
        ImageDraw.Draw(image).ellipse((40,40,120,120),fill='white')
        self.assertIsNone(suggest(image,(80,80)))

    def test_boundary_numeric_dust_only(self):
        f=fixtures.ReviewTests(); f.setUp()
        try:
            batch=f.imported(); f.annotate()
            frame=batch['frames'][0]; path=f.batch/'editor/001-frame-0.json'
            doc=h.read(path)
            doc['shapes'][0]['points']=[[10,-1.4210854715202004e-14],[50,20]]
            self.assertEqual(h.parse_editor_document(batch,frame,path,doc)[0]['bounds'],[10,0.,40,20.])
            doc['shapes'][0]['points'][0][1]=-.01
            with self.assertRaises(ValueError): h.parse_editor_document(batch,frame,path,doc)
        finally: f.tearDown()


if __name__=='__main__': unittest.main()
