import copy
import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import placement172 as p
from test_diagnostic171 import source


def plan():
    value=p.d.catalog(source());value['sourceCatalog']={'path':'test-only','sha256':'0'*64}
    value['seal']=p.h.digest(value)
    return value


class PlacementTests(unittest.TestCase):
    def test_frozen_phase_separation(self):
        with patch.object(p.h,'checked'),patch.object(p.h,'read',return_value=source()):
            phases=p.planned(plan())
        a,b=phases.values()
        self.assertEqual((len(a),len(b)),(24,264))
        self.assertFalse({r['group'] for r in a}&{r['group'] for r in b})
        self.assertEqual(len({r['id'] for r in a+b}),288)
        self.assertEqual(len({(r['family'],r['scale'],r['placement'],r['tint']) for r in a}),24)

    def test_changed_plan(self):
        doc=plan();doc['rows'].pop()
        with self.assertRaisesRegex(Exception,'plan_seal'):p.planned(doc)
        doc['seal']=p.h.digest({k:v for k,v in doc.items() if k!='seal'})
        with patch.object(p.h,'checked'),patch.object(p.h,'read',return_value=source()):
            with self.assertRaisesRegex(Exception,'changed_plan'):p.planned(doc)

    def test_position_and_metadata(self):
        recipe=dict(width=600,scale=2,layoutDirection='rtl',placement='leading',tint='system-blue')
        row=dict(resolvedVariation=dict(placement='leading',tint='system-blue',rtl=True,
            requestedCenterX=250,activeRGBA=[0,.3,1,1],inactiveRGBA=[.2,.2,.2,.1]))
        p.check_position(recipe,row,[240,100,20,6])
        rounded=copy.deepcopy(row);rounded['resolvedVariation']['activeRGBA']=[1.000000119]*3+[1]
        p.check_position(recipe,rounded,[240,100,20,6])
        for key,value in [('rtl',False),('placement','trailing'),('tint','unknown'),('activeRGBA',[float('nan')]*4),('activeRGBA',[1.1]*4)]:
            bad=copy.deepcopy(row);bad['resolvedVariation'][key]=value
            with self.subTest(key=key),self.assertRaises(Exception):p.check_position(recipe,bad,[240,100,20,6])
        for box in ([200,100,20,6],[275,100,20,6]):
            with self.assertRaises(Exception):p.check_position(recipe,row,box)

    def test_prepare_collision_is_read_only(self):
        with patch.object(p,'OUT',p.h.ROOT),patch.object(p,'planned') as planner:
            with self.assertRaisesRegex(Exception,'output_collision'):p.prepare()
            planner.assert_not_called()

    def test_duplicate_annotation_identity_rejects_conflicting_bounds(self):
        element=dict(id='page',elementType='pageControl',boundsPoints=dict(x=10,y=20,width=30,height=5),
            boundsVisionNormalized=dict(x=.1,y=.2,width=.3,height=.05))
        original={'elements':[element]};same=copy.deepcopy(original);same['generatorVersion']='new-renderer'
        self.assertEqual(p.annotation_identity(original),p.annotation_identity(same))
        changed=copy.deepcopy(original);changed['elements'][0]['boundsPoints']['x']+=1
        self.assertNotEqual(p.annotation_identity(original),p.annotation_identity(changed))

    def test_execution_rejects_wrong_or_unbooted_target_before_dispatch(self):
        for state,udid,reason in [('Booted','wrong','wrong_target'),('Shutdown',p.n.TARGET,'runtime_not_booted')]:
            devices={'devices':{'com.apple.CoreSimulator.SimRuntime.iOS-26-5':[
                dict(udid=udid,state=state,isAvailable=True,name='iPhone 17 Pro')]}}
            with patch.object(p,'catalog',return_value=(None,{})),patch.object(p.shutil,'disk_usage',return_value=SimpleNamespace(free=10*1024**3)), \
                 patch.object(p.subprocess,'check_output',return_value=json.dumps(devices).encode()),patch.object(p.subprocess,'run') as launch:
                with self.subTest(state=state),self.assertRaisesRegex(Exception,reason):p.execute('qualification')
                launch.assert_not_called()


if __name__=='__main__':unittest.main()
