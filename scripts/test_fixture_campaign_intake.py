"""Real campaign CLI/crop/review integration with generated, non-training native evidence."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image
import fixture_campaign_intake as c
import human_annotation_review as h
import human_intake_audit as audit
import human_regression_review as regression
from harvest_sidecar_v2 import recipe_hash
from test_ttr_sidecar_v2 import write_bundle,reindex
from test_ttr_competitor import competitor_meta
from test_fixture_semantic_inventory import inventory
from test_fixture_structure import recipe as structural_recipe


def dump(path,value):
    path.write_text(json.dumps(value))


def seal_plan(plan):
    encoded=json.dumps(plan['manifest'],sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
    plan['plan_sha256']=hashlib.sha256(plan['compiler'].encode()+encoded).hexdigest()


def generated(root, families=('composite_card','hero','home_icon','ranked_row')):
    cases=[];bundles=[]
    for n,kind in enumerate(families):
        case_id=f'{kind}-{n}'
        bundle=root/case_id;meta=competitor_meta(write_bundle(bundle));r=structural_recipe(kind)
        comp=r['appearance']['composition'];region=comp['regions'][0]
        region['frame']=[0,0,1920,1080];region['items'].append(dict(region['items'][0],id='x'))
        r['element_count']=2;r['seed']=n+7;r['recipe_hash']=recipe_hash(r)
        # Different families need genuinely distinct test pixels to exercise
        # sampling coverage rather than defeating dedup with renamed files.
        for name in ('u.png','f.png'):
            with Image.open(bundle/name) as im:im.putpixel((0,0),(n+1,2,3));im.save(bundle/name)
        def walk(v):
            if isinstance(v,dict):
                for child in list(v.values()):walk(child)
                if 'scene_width' in v:
                    v['recipe']=copy.deepcopy(r)
                    for e in v['elements']:
                        e['parent_element_id']='region';x,y,w,height=e['pixel_bounds']
                        e['rendered_body_geometry']=dict(version=1,role='rendered_control_body',
                            coordinate_space='image_top_left_pixels',source='uikit_focused_frame_guide',
                            generation=v['focus_observation']['generation'],element_id=e['element_id'],
                            availability='measured',full_pixel_bounds=[x,y,w,height],
                            visible_pixel_bounds=[x,y,w,height],visible_normalized_bounds=[x/64,y/48,(x+w)/64,(y+height)/48])
                    v['semantic_inventory']=inventory(v)
            elif isinstance(v,list):
                for child in v:walk(child)
        walk(meta)
        for role,name,key in [('unfocused','u.png','reference_capture'),('focused','f.png','focused_capture')]:
            meta[role+'_sha256']=h.sha(bundle/name);meta[key]['frame_png_sha256']=h.sha(bundle/name)
        (bundle/'m.json').write_text(json.dumps(meta))
        for name in ('manifest.json','calibration.json'):
            rows=h.read(bundle/name);rows[0]['sha256']=h.sha(bundle/'f.png');dump(bundle/name,rows)
        reindex(bundle);bundles.append(bundle)
        cases.append(dict(case_id=case_id,recipe=r,target_element_ids=['e'],split_group='validation',
                          independence_group='fixture_procedural_renderer_v1'))
    plan=dict(version=1,compiler='structural-appearance-v1',requested_pairs=len(cases),attainable_pairs=len(cases),
              manifest=dict(cases=cases));seal_plan(plan)
    path=root/'plan.json';h.write(path,plan);protected=root/'protected.json';h.write(protected,{})
    return path,bundles,protected


class CampaignTests(unittest.TestCase):
    def setUp(self):
        base=h.ROOT/'.build/debug-output';base.mkdir(parents=True,exist_ok=True)
        self.root=Path(tempfile.mkdtemp(dir=base,prefix='campaign-test-'))
        self.addCleanup(shutil.rmtree,self.root)
        self.plan,self.bundles,self.protected=generated(self.root)
        self.output=self.root/'output'

    def run_pipeline(self):return c.run(self.plan,self.bundles,self.protected,self.output)

    def test_actual_cli_full_review_crop_and_resume_preserves_edits(self):
        before={p:h.sha(p) for b in self.bundles for p in b.iterdir()}
        args=[sys.executable,str(h.ROOT/'scripts/fixture_campaign_intake.py'),'--plan',str(self.plan),
              '--protected',str(self.protected),'--output',str(self.output)]
        for b in self.bundles:args+=['--bundle',str(b)]
        result=subprocess.run(args,capture_output=True,text=True,timeout=60)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        row=json.loads(result.stdout);self.assertEqual(row['cases'],4)
        self.assertEqual(row['crops'],dict(expected=16,completed=16));self.assertEqual(row['review']['uniqueReview'],8)
        a=self.output/'attempt-001';review=a/'audit/review/batch.json';queue=a/'audit/combined-queue.json'
        self.assertEqual(len(regression.queue_scope(queue,review)),8)
        report=audit.validate_plan(a/'audit/plan.json');self.assertEqual(len(report['sampling']['strata']),8)
        self.assertTrue(all(len(s['selected'])==1 for s in report['sampling']['strata'].values()))
        doc=h.validate_batch(review);self.assertTrue(all(p['geometryRole']=='rendered_control_body' for f in doc['frames'] for p in f['proposals']))
        editor=next((a/'audit/review/editor').glob('*.json'));d=h.read(editor);d['description']='human';dump(editor,d);digest=h.sha(editor)
        with patch.object(c.batch,'prepare',side_effect=AssertionError('repeated crop')):
            resumed=self.run_pipeline();self.assertEqual(resumed['review']['uniqueReview'],8)
        self.assertEqual(h.sha(editor),digest);self.assertEqual(before,{p:h.sha(p) for p in before})

    def test_missing_duplicate_and_unexpected_recipe_reject(self):
        with self.assertRaisesRegex(ValueError,'missing_captured'):c.coverage(self.plan,self.bundles[:-1],self.protected)
        with self.assertRaisesRegex(ValueError,'duplicate_captured'):c.coverage(self.plan,self.bundles+[self.bundles[0]],self.protected)
        p=h.read(self.plan);p['manifest']['cases']=p['manifest']['cases'][:-1];p['requested_pairs']=p['attainable_pairs']=3;seal_plan(p);dump(self.plan,p)
        with self.assertRaisesRegex(ValueError,'unexpected_captured'):self.run_pipeline()
        self.assertFalse(self.output.exists())

    def test_plan_tamper_target_and_sampling_reject(self):
        original=h.read(self.plan);p=copy.deepcopy(original);p['plan_sha256']='0'*64;dump(self.plan,p)
        with self.assertRaisesRegex(ValueError,'digest'):self.run_pipeline()
        p=copy.deepcopy(original);p['manifest']['cases'][0]['target_element_ids']=['x'];seal_plan(p);dump(self.plan,p)
        with self.assertRaisesRegex(ValueError,'mixed_review_target'):self.run_pipeline()
        dump(self.plan,original)
        with self.assertRaisesRegex(ValueError,'sample_count'):c.run(self.plan,self.bundles,self.protected,self.output,count=7)

    def test_protected_before_image_decode(self):
        dump(self.protected,{'sha256':h.sha(self.bundles[0]/'f.png')})
        with patch('harvest_bundle_validation._png_size',side_effect=AssertionError('decoded')):
            with self.assertRaisesRegex(ValueError,'protected'):self.run_pipeline()
        self.assertFalse(self.output.exists())

    def test_resume_changed_input_and_output_reject(self):
        self.run_pipeline();p=self.output/'attempt-001/campaign-review.md';p.write_text('tampered')
        with self.assertRaises(ValueError):self.run_pipeline()

    def test_interrupted_attempt_is_preserved(self):
        def interrupt(roots,output,*args,**kwargs):
            output.mkdir();(output/'partial').write_text('retained');raise KeyboardInterrupt()
        with patch.object(c.batch,'prepare',side_effect=interrupt):
            with self.assertRaises(KeyboardInterrupt):self.run_pipeline()
        self.assertFalse((self.output/'active.lock').exists())
        self.assertEqual(self.run_pipeline()['coverage']['cases'],4)
        self.assertTrue((self.output/'attempt-001/partial').is_file())
        self.assertTrue((self.output/'attempt-002/campaign.json').is_file())

    def test_completion_membership_and_seal(self):
        self.run_pipeline()
        extra=self.output/'attempt-001/unexpected.json';extra.write_text('{}')
        with self.assertRaisesRegex(ValueError,'changed_output_membership'):self.run_pipeline()
        extra.unlink()
        marker=self.output/'completed.json';record=h.read(marker);record['files']=[];dump(marker,record)
        with self.assertRaisesRegex(ValueError,'changed_or_unsupported'):self.run_pipeline()

    def test_missing_body_fails_before_crop(self):
        path=self.bundles[0]/'m.json';d=h.read(path)
        def walk(v):
            if isinstance(v,dict):
                v.pop('rendered_body_geometry',None)
                for child in v.values():walk(child)
            elif isinstance(v,list):
                for child in v:walk(child)
        walk(d);dump(path,d);reindex(self.bundles[0])
        with patch.object(c.batch,'prepare',side_effect=AssertionError('crop')):
            with self.assertRaisesRegex(ValueError,'unresolved_campaign_body'):self.run_pipeline()

    def test_lock_and_changed_plan_preserve_completed_work(self):
        self.run_pipeline()
        lock=self.output/'active.lock';lock.write_text('another owner')
        with self.assertRaisesRegex(ValueError,'locked'):self.run_pipeline()
        lock.unlink()
        with self.assertRaisesRegex(ValueError,'changed_campaign'):c.run(
            self.plan,self.bundles,self.protected,self.output,seed=43)

    def test_stratified_duplicates_conflicts_and_missing_population(self):
        self.run_pipeline();path=self.output/'attempt-001/native-review/batch.json'
        real,docs=audit.source_documents(path);original=copy.deepcopy(real)
        # Sampling-unit test: bypass only source validation, not selection logic.
        f=copy.deepcopy(real['frames'][0]);f.update(id='zz-alias',editorStem='099-alias',duplicateOf=None)
        real['frames'].append(f);docs[f['id']]=docs[real['frames'][0]['id']]
        with patch.object(audit,'source_documents',return_value=(real,docs)):
            result=audit.plan(path,count=8,exception_limit=0,focus_element='e',family_focus=True)
        self.assertEqual(result['counts']['eligible'],8)
        self.assertTrue(any('campaign_exact_duplicate_pixels' in row['excluded'] for row in result['frames']))
        f['proposals'][0]['state']='unknown'
        with patch.object(audit,'source_documents',return_value=(real,docs)):
            with self.assertRaisesRegex(ValueError,'missing_eligible'):audit.plan(
                path,count=8,focus_element='e',family_focus=True)
        with patch.object(audit,'source_documents',return_value=(original,docs)):
            first=audit.plan(path,count=8,focus_element='e',family_focus=True,seed=77)
            self.assertEqual(first,audit.plan(path,count=8,focus_element='e',family_focus=True,seed=77))


if __name__=='__main__':unittest.main()
