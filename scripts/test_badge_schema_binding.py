import copy
import hashlib
import re
import json
from pathlib import Path
import unittest
from annotation_schema_validation import validate_sidecar_structure,AnnotationSchemaError
from test_annotation_schema_versions import valid_sidecar
from validate_reconstructed_corpus import check_schema
R=Path(__file__).resolve().parents[1]
class Tests(unittest.TestCase):
 def test_schema_and_map_keep41entries(self):
  old=json.loads((R/'Research/schemas/category_map.json').read_text())['categories']
  self.assertEqual([c['id'] for c in old],list(range(41)))
  new=json.loads((R/'Research/schemas/annotation.schema.v1.3.json').read_text())
  base=json.loads((R/'Research/schemas/annotation.schema.v1.2.json').read_text())
  e=new['properties']['elements']['items']['properties']['elementType'];before=base['properties']['elements']['items']['properties']['elementType']['enum']
  self.assertEqual(e['enum'],before+['badge'])
  check_schema('badge',e,new)
  with self.assertRaises(ValueError):check_schema('badge',base['properties']['elements']['items']['properties']['elementType'],base)
  self.assertEqual(new['properties']['elements']['items']['properties']['state'],base['properties']['elements']['items']['properties']['state'])
  restored=copy.deepcopy(new)
  for key in ('$id','title','description'):restored[key]=base[key]
  restored['properties']['schemaVersion']=base['properties']['schemaVersion']
  restored['required'].remove('taxonomyVersion')
  del restored['properties']['taxonomyVersion']
  restored['properties']['elements']['items']['properties']['elementType']['enum'].remove('badge')
  self.assertEqual(restored,base)
 def test_runtime_identity_from_exact_canonical_taxonomy_bytes(self):
  base=json.loads((R/'Research/schemas/category_map.json').read_text())['categories']
  append=json.loads((R/'Research/schemas/category_map.v1.1.json').read_text())['append']
  source=(R/'NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/ModelTaxonomyBinding.swift').read_text()
  for version,categories in [('1.0',base),('1.1',base+append)]:
   canonical=json.dumps({'version':version,'categories':categories},sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('utf-8')
   constant=re.search(r'case "'+re.escape(version)+r'": return "([0-9a-f]{64})"',source).group(1)
   self.assertEqual(hashlib.sha256(canonical).hexdigest(),constant)
   for field,value in [('id',99),('name','changed')]:
    changed=copy.deepcopy(categories);changed[0][field]=value
    data=json.dumps({'version':version,'categories':changed},sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('utf-8')
    self.assertNotEqual(hashlib.sha256(data).hexdigest(),constant)
   reordered=list(reversed(categories))
   data=json.dumps({'version':version,'categories':reordered},sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('utf-8')
   self.assertNotEqual(hashlib.sha256(data).hexdigest(),constant)
   self.assertNotEqual(hashlib.sha256(json.dumps([c['name'] for c in categories],separators=(',',':')).encode()).hexdigest(),constant)
  labels=source.split('legacyLabels: [String] = [',1)[1].split(']',1)[0]
  self.assertEqual(re.findall(r'"([A-Za-z]+)"',labels),[c['name'] for c in base])
 def test_declared_version_routes_real_guard(self):
  new=valid_sidecar('1.3',1);new['taxonomyVersion']='1.1';new['elements']=[{'elementType':'primaryButton'},{'elementType':'badge'}]
  self.assertEqual(validate_sidecar_structure(new).name,'annotation.schema.v1.3.json')
  for v in ('1.0','1.1','1.2'):
   old=copy.deepcopy(new);old['schemaVersion']=v;old['image']['scale']=2
   with self.assertRaises(AnnotationSchemaError):validate_sidecar_structure(old)
  for value in (None,'1.0','unknown'):
   bad=copy.deepcopy(new);bad['taxonomyVersion']=value
   with self.assertRaises(AnnotationSchemaError):validate_sidecar_structure(bad)
if __name__=='__main__':unittest.main()
