import copy
import json
from pathlib import Path
import tempfile
import unittest
import generator_asset_plan as a


class Tests(unittest.TestCase):
    def fixture(self):
        resources=[dict(id=str(i),kind='thumbnail',sha256=str(i)*64,bytes=1,source='worker',
            sourceRevision='pinned',ancestryGroups=['family'],dataRole='unassigned',sourceRecord={'extra':'retained'}) for i in (1,2)]
        review=dict(schemaVersion='artwork204-review-v1',sourceSHA256='a'*64,evidence='local-review',
            useScope='research',familyRoles={'family':'train'},reviewedIDs=['1'])
        return dict(schema='generator-resource-inventory-v1',resources=resources),review

    def test_review_not_inherited_by_sibling(self):
        v,r=self.fixture();out=a.normalize_artwork204(v,r,'a'*64)['resources']
        self.assertEqual([x['dataRole'] for x in out],['train','train'])
        self.assertEqual([x['reviewStatus'] for x in out],['verified','pending'])
        self.assertEqual(out[0]['sourceRecord']['producer'],v['resources'][0])

    def test_reject_hash_unknown_ids_families_duplicates(self):
        v,r=self.fixture()
        for change in [dict(sourceSHA256='b'*64),dict(reviewedIDs=['unknown']),dict(reviewedIDs=['1','1']),dict(familyRoles={'missing':'train'})]:
            with self.assertRaises(ValueError):a.normalize_artwork204(v,dict(r,**change),'a'*64)

    def test_reject_role_collision_via_hash(self):
        v,r=self.fixture();v['resources'][1].update(ancestryGroups=['reserved'],sha256='1'*64)
        r.update(familyRoles={'family':'train','reserved':'test'},reviewedIDs=['1','2'])
        with self.assertRaises(ValueError):a.normalize_artwork204(v,r,'a'*64)

    def test_reject_preassigned_producer_role(self):
        v,r=self.fixture();v['resources'][0]['dataRole']='train'
        with self.assertRaises(ValueError):a.normalize_artwork204(v,r,'a'*64)

    def test_inventory_parser_boundaries(self):
        root=Path('.build/debug-output');root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as folder:
            p=Path(folder)/'inventory.json'
            for raw in ['{"a":1,"a":2}','{"a":NaN}','['*34+'0'+']'*34]:
                p.write_text(raw)
                with self.assertRaises(ValueError):a.inventory_metadata(p)
            p.write_text(json.dumps({'rows':[{'id':i} for i in range(6000)]}))
            self.assertEqual(len(a.inventory_metadata(p)['rows']),6000)
            with self.assertRaises(ValueError):a.inventory_metadata(p,'a'*64)


if __name__=='__main__':unittest.main()
