import unittest
import replay_proposal181 as p


class SelectionTests(unittest.TestCase):
    def test_catalog_family_preserves_original_row(self):
        row=dict(id='native',pixelSHA256='p');labels={'native':{0}}
        self.assertEqual(p.select([row],[],labels,1,{'native':'UIKitControls'}),[row])
        self.assertNotIn('family',row)
        with self.assertRaisesRegex(Exception,'family_provenance_missing'):p.select([row],[],labels,1)

    def test_order_and_duplicate_pixels(self):
        rows=[dict(id=str(i),family='f',pixelSHA256=str(i//2)) for i in range(6)]
        labels={r['id']:{0} for r in rows}
        self.assertEqual(p.select(rows,[],labels,3),p.select(list(reversed(rows)),[],labels,3))
        self.assertEqual([r['id'] for r in p.select(rows,[],labels,3)],['0','2','4'])

    def test_empty_and_exhaustion(self):
        rows=[dict(id='a',family='f',pixelSHA256='a')]
        with self.assertRaisesRegex(Exception,'insufficient_unique_positives'):p.select(rows,[],{'a':set()},1)

    def test_low_support_preferred(self):
        kept=[dict(id='k',family='f',pixelSHA256='k')]
        rows=[dict(id=x,family='f',pixelSHA256=x) for x in ('a','b')]
        self.assertEqual(p.select(rows,kept,{'k':{0},'a':{0},'b':{1}},1)[0]['id'],'b')


if __name__=='__main__':unittest.main()
