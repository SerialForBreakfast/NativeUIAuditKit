import copy
import unittest
import ios_row_membership545 as m

class RowTests(unittest.TestCase):
    def side(self):
        es=[]
        def add(id,kind,b):es.append(dict(id=id,elementType=kind,boundsPixels=dict(zip(('x','y','width','height'),b))))
        add('navigationBar','navigationBar',[0,0,100,10]);add('textField_0','textField',[5,12,90,8]);add('primaryButton_0','primaryButton',[5,180,90,10])
        for i in range(4):
            add(f'listRow_{i}','listRow',[5,60+i*25,90,20]);add(f'label_row_{i}','label',[10,65+i*25,30,10])
        for i in range(2):
            add(f'listRow_toggle_{i}','listRow',[5,25+i*15,90,12]);add(f'label_toggle_{i}','label',[10,26+i*15,30,8]);add(f'toggle_{i}','toggle',[65,26+i*15,20,8])
        return dict(elements=es)
    def check(self,s):return m.controls(s,100,200,['navigationBar','textField','primaryButton','listRow','label','toggle'])
    def test_complete_source_contract(self):self.assertEqual(len(self.check(self.side())),17)
    def test_missing_and_duplicate_labels(self):
        for duplicate in (False,True):
            s=self.side();s['elements'].pop()
            if duplicate:s['elements'].append(copy.deepcopy(s['elements'][0]))
            with self.assertRaisesRegex(ValueError,'annotation_coverage'):self.check(s)
    def test_uncertain_and_excluded(self):
        for key in ('excluded','occluded','knownIssues'):
            s=self.side();s['elements'][0][key]=True
            with self.assertRaisesRegex(ValueError,'uncertain_label'):self.check(s)
    def test_aliased_row_rejected(self):
        s=self.side();s['elements'][3]['boundsPixels']=s['elements'][4]['boundsPixels']
        with self.assertRaisesRegex(ValueError,'row_contains_label'):self.check(s)
    def test_footer_overlap_rejected(self):
        s=self.side();s['elements'][2]['boundsPixels']['y']=145
        with self.assertRaisesRegex(ValueError,'footer_occlusion'):self.check(s)
    def test_offscreen_rejected(self):
        s=self.side();s['elements'][3]['boundsPixels']['x']=-5
        with self.assertRaises(ValueError):self.check(s)
class PartitionTests(unittest.TestCase):
    def docs(self):
        return [dict(trainingAdmitted=role=='train',rows=[dict(id=role,role=role,group=role,image=dict(sha256=role))],
                     lineage=[dict(id=role,decodedPixelSHA256=role)]) for role in ('train','development')]
    def test_independent_groups(self):
        self.assertFalse(m.validate_partitions(*self.docs())['overlap'])
    def test_related_frames(self):
        a,b=self.docs();b['rows'][0]['group']='train'
        with self.assertRaisesRegex(ValueError,'partition_groups'):m.validate_partitions(a,b)
    def test_reencoded_same_pixels(self):
        a,b=self.docs();b['lineage'][0]['decodedPixelSHA256']='train'
        with self.assertRaisesRegex(ValueError,'partition_pixels'):m.validate_partitions(a,b)
    def test_missing_lineage(self):
        a,b=self.docs();b['lineage']=[]
        with self.assertRaisesRegex(ValueError,'partition_lineage'):m.validate_partitions(a,b)
if __name__=='__main__':unittest.main()
