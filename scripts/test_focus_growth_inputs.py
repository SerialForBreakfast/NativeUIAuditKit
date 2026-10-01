"""Generated offline fixtures; no encoder, training, device or retained test data."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image, ImageDraw
import focus_context_inputs as c
import focus_native_body_assembly as a


class WeightTests(unittest.TestCase):
    def base(self):
        rows=[]; weights={}
        for group,kind,use,mass in [('fixture','simulatorFixture','train-candidate',.7),
                                   ('os','tvos_simulator_os','train-candidate',.1),
                                   ('human','human','human-static-auxiliary',.2)]:
            for label in (0,1):
                sid=group+str(label)
                rows.append(dict(id=sid,split='train',use=use,sourceKind=kind,label=label))
                weights[sid]=mass/2
        return dict(samples=rows,fullFit=dict(weights=weights))

    def test_identity_and_exact_nonfixture_preservation(self):
        base=self.base();before=copy.deepcopy(base)
        self.assertEqual(a.weighting(base,[],a.CONTINUITY_POLICY),base['fullFit']['weights'])
        additions=[dict(base['samples'][0],id='new0'),dict(base['samples'][0],id='new1')]
        result=a.weighting(base,additions,a.CONTINUITY_POLICY)
        self.assertEqual(base,before)
        for sid in ('os0','os1','human0','human1'):self.assertEqual(result[sid],base['fullFit']['weights'][sid])
        self.assertAlmostEqual(sum(result.values()),1)
        self.assertAlmostEqual(result['fixture0']+result['new0']+result['new1'],.35)
        self.assertEqual(result['fixture1'],.35)
        self.assertEqual(result,a.weighting(base,list(reversed(additions)),a.CONTINUITY_POLICY))

    def test_invalid_inputs(self):
        base=self.base()
        for bad in [dict(base['samples'][0]),dict(base['samples'][2],id='new'),
                    dict(base['samples'][0],id='new',label=True)]:
            with self.assertRaises(ValueError):a.weighting(base,[bad],a.CONTINUITY_POLICY)
        with self.assertRaisesRegex(ValueError,'unsupported_weight_policy'):a.weighting(base,[],'guess')
        base['fullFit']['weights']['fixture0']=float('nan')
        with self.assertRaises(ValueError):a.weighting(base,[],a.CONTINUITY_POLICY)


class PixelTests(unittest.TestCase):
    def test_actual_pixels_and_mask_retain_growth(self):
        widths=[]
        for factor in (1,1.1,1.2):
            image=Image.new('RGB',(768,432)); w=100*factor
            ImageDraw.Draw(image).rectangle((100,100,100+w-1,199),fill='white')
            tx=c.transform(image.size);geo=c.geometry([100,100,w,100],tx)
            scene=c.scene_image(image,tx);mask=c.candidate_mask(geo)
            self.assertEqual(scene.getbbox(),mask.getbbox())
            widths.append(mask.getbbox()[2]-mask.getbbox()[0])
        self.assertEqual(widths,[100,110,120])

    def test_global_scaling_aspect_letterbox_and_clipping(self):
        a=c.geometry([20,40,100,80],c.transform((800,600)))
        b=c.geometry([40,80,200,160],c.transform((1600,1200)))
        self.assertEqual(a,b)
        self.assertEqual(c.candidate_mask(a).tobytes(),c.candidate_mask(b).tobytes())
        edge=c.geometry([-10,0,20,30],c.transform((768,432)))
        self.assertEqual(edge['clipped'],[True,False,False,False])
        self.assertEqual(c.candidate_mask(edge).getbbox(),(0,0,10,30))
        for bounds in ([0,0,0,1],[float('nan'),0,1,1],[900,0,1,1],[True,0,1,1]):
            with self.assertRaises(ValueError):c.geometry(bounds,c.transform((768,432)))
        with self.assertRaises(ValueError):c.transform((100000,100000))

    def test_size_is_not_a_focus_rule(self):
        # Hero/parent may be larger than focused child. Builder never sorts/ranks
        # by size or adjusts geometry according to label.
        tx=c.transform((768,432))
        self.assertGreater(c.geometry([0,0,300,200],tx)['normalizedBounds'][2],
                           c.geometry([400,0,100,100],tx)['normalizedBounds'][2])

    def test_detector_jitter_changes_target_not_scene_scale(self):
        tx=c.transform((1920,1080));image=Image.new('RGB',(1920,1080),'gray')
        before=c.scene_image(image,tx).tobytes()
        exact=c.geometry([100,100,200,120],tx)
        jitter=c.geometry([95,103,211,117],tx)
        self.assertNotEqual(c.candidate_mask(exact).tobytes(),c.candidate_mask(jitter).tobytes())
        self.assertEqual(c.scene_image(image,tx).tobytes(),before)


class CLITests(unittest.TestCase):
    def setUp(self):
        root=Path(__file__).resolve().parents[1]
        (root/'.build/tmp').mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=root/'.build/tmp')
        self.root=Path(self.temp.name)
        self.frame=self.root/'frame.png';Image.new('RGB',(768,432),'red').save(self.frame)
        self.crop=self.root/'crop.png';Image.new('RGB',(256,256),'blue').save(self.crop)
        self.rows=[dict(id='a',frame=c.h.ref(self.frame),crop=c.h.ref(self.crop),bounds=[20,30,100,80],
                        split='train',use='train-candidate',label=1)]
        self.protocol=self.root/'protocol.json'

    def tearDown(self):self.temp.cleanup()

    def save(self):
        doc=dict(version='focus-native-body-full-fit-v1',samples=self.rows)
        doc['protocolSHA256']=c.h.digest(doc);self.protocol.write_text(json.dumps(doc))

    def test_cli_whitelist_order_hashes_and_missing_accounting(self):
        self.rows += [dict(self.rows[0],id='b',label=0),dict(self.rows[0],id='c',bounds=None)]
        self.save();out=self.root/'out'
        with patch('sys.argv',['context','--protocol',str(self.protocol),'--output',str(out)]):
            self.assertEqual(c.main(),0)
        result=c.h.read(out/'manifest.json')
        self.assertEqual(result['counts'],dict(input=3,prepared=2,blocked=1,scenes=1))
        self.assertEqual(result['members'][0]['geometry'],result['members'][1]['geometry'])
        for r in result['members']:
            self.assertEqual(set(r),{'id','localCrop','sceneKey','mask','geometry'})
        self.rows.reverse();self.save()
        other=c.build(self.protocol,self.root/'other')
        self.assertEqual([r['id'] for r in other['members']],['a','b'])
        self.frame.write_bytes(b'corrupt')
        with self.assertRaisesRegex(ValueError,'changed_hash'):c.build(self.protocol,self.root/'bad')
        self.assertFalse((self.root/'bad').exists())

    def test_protected_and_duplicate_rejected_before_decode(self):
        for mode in ('challenge','duplicate'):
            rows=copy.deepcopy(self.rows)
            if mode=='challenge':self.rows[0]['split']='challenge'
            else:self.rows.append(copy.deepcopy(self.rows[0]))
            self.save()
            with patch.object(c.Image,'open',side_effect=AssertionError('must not decode')):
                with self.assertRaises(ValueError):c.build(self.protocol,self.root/mode)
            self.rows=rows

    def test_historical_geometry_joins_by_pixels_not_label(self):
        r=self.rows[0];r.pop('bounds');r.update(pairID='pair',label=0)
        path=self.root/'legacy.json'
        # Deliberately use the opposite label's name: only bound image/crop
        # identities choose the geometry, not current labels or state strings.
        doc=dict(version='1.4',pairs=[dict(pair_id='pair',focused_crop_sha256=r['crop']['sha256'],
                 frames=dict(focused=dict(sha256=r['frame']['sha256'],bounds=[1,2,30,40])))])
        path.write_text(json.dumps(doc));self.save()
        result=c.build(self.protocol,self.root/'recovered',[path])
        self.assertEqual(result['counts']['prepared'],1)
        self.assertEqual(result['members'][0]['geometry']['sceneBounds'],[1,2,30,40])
        doc['pairs'][0]['focused_crop_sha256']='wrong';path.write_text(json.dumps(doc))
        result=c.build(self.protocol,self.root/'unmatched',[path])
        self.assertEqual(result['counts']['blocked'],1)


if __name__=='__main__':unittest.main()
