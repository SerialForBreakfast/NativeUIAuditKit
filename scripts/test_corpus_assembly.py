import unittest
from corpus_assembly import AssemblyError,assemble
class T(unittest.TestCase):
 def rows(self): return [{'id':'a','split':'training','contentSHA256':'a','family':'f1','source':'synthetic','classes':[1]},{'id':'b','split':'validation','contentSHA256':'b','family':'f2','source':'synthetic','classes':[2]},{'id':'c','split':'held-out','contentSHA256':'c','family':'f3','source':'fixture','classes':[3]}]
 def test_deterministic_and_train_only(self):
  a=assemble(self.rows()); self.assertEqual(a,assemble(list(reversed(self.rows())))); self.assertEqual(a['trainingClassCounts'],{1:1}); self.assertEqual(a['uncoveredClasses'],[2,3])
 def test_leakage_rejected(self):
  rows=self.rows(); rows.append(dict(rows[0],id='x',split='test'))
  with self.assertRaisesRegex(AssemblyError,'content'): assemble(rows)
  rows=self.rows(); rows.append(dict(rows[0],id='x',contentSHA256='different',split='test'))
  with self.assertRaisesRegex(AssemblyError,'family'): assemble(rows)
if __name__=='__main__': unittest.main()
