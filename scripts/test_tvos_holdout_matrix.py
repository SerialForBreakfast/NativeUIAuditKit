import unittest
from tvos_holdout_matrix import MatrixError,validate
M={('Fixture','Audit'):250,('Fixture','Detection'):250}
def rows(): return [{'id':'a','contentSHA256':'a','app':'Fixture','surface':'Audit','os':'tvOS','device':'AppleTV','provenance':'capture','annotationStatus':'groundTruth'},{'id':'b','contentSHA256':'b','app':'Fixture','surface':'Detection','os':'tvOS','device':'AppleTV','provenance':'capture','annotationStatus':'unlabeled'}]
class T(unittest.TestCase):
 def test_counts(self): self.assertEqual(validate(rows(),M)['labeledMAPExamples'],1)
 def test_invalid_duplicate_prediction(self):
  r=rows(); r.append(dict(r[0],id='x'))
  with self.assertRaisesRegex(MatrixError,'duplicate'): validate(r,M)
  r=rows(); r[0]['annotationStatus']='prediction'
  with self.assertRaisesRegex(MatrixError,'prediction'): validate(r,M)
if __name__=='__main__': unittest.main()
