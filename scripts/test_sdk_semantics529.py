import copy
import unittest
from sdk_semantics529 import semantics,transition,transformed_bounds,classify

class SemanticsTests(unittest.TestCase):
    def control(self):return dict(identity=dict(id='cell',lifetime='life1',revision=1),className='UIButton',accessibilityTraits=1,parentID='list')
    def frame(self):return dict(appID='app',processID='p',runID='r',focusID='cell',controls=[self.control()])
    def test_optional_fields_and_public_provenance(self):
        x=semantics(self.control());self.assertIsNone(x['publicAccessibility']);self.assertTrue(x['identityComplete'])
        c=self.control();c['publicAccessibility']={'label':'Play'};self.assertEqual(semantics(c)['publicAccessibility'],{'label':'Play'})
        c['accessibilityTraits']=True
        with self.assertRaisesRegex(ValueError,'traits'):semantics(c)
    def test_identity_lifetime_revision_parent(self):
        a=self.frame();b=copy.deepcopy(a);b['controls'][0]['parentID']='overlay'
        self.assertEqual(transition(a,b)['observed'],'unchanged')
        b['controls'][0]['identity']['revision']=2;self.assertEqual(transition(a,b)['relation'],'revised_control')
        b['controls'][0]['identity']['lifetime']='life2';self.assertEqual(transition(a,b)['relation'],'replaced_control')
        self.assertEqual(transition(a,b)['observed'],'move')
        b['runID']='r2';self.assertFalse(transition(a,b)['eligible'])
    def test_unknown_is_not_no_focus(self):
        a=self.frame();b=copy.deepcopy(a);b['controls'][0]['identity'].pop('lifetime')
        self.assertFalse(transition(a,b)['eligible']);b['focusID']=None
        self.assertEqual(transition(a,b)['observed'],'departure');a['focusID']=None
        self.assertEqual(transition(a,b)['observed'],'no_focus')
        b['focusState']='unknown';self.assertEqual(transition(a,b)['observed'],'unknown')
    def test_transform_clipping_and_invalid(self):
        x=transformed_bounds([-2,1,5,3],[2,0,0,2,0,0],[10,10])
        self.assertEqual(x['visible'],[0,2,6,6]);self.assertTrue(x['clipped'])
        with self.assertRaisesRegex(ValueError,'geometry'):transformed_bounds([0,0,1,1],[0]*6,[10,10])
    def test_reviewed_conjunction_ambiguity_and_unknown(self):
        c=self.control();r=dict(id='button',class_='button')
        r={'id':'button','class':'button','match':{'nativeClass':'UIButton','traitsAll':1},'reviewer':'test','evidence':'software-only'}
        self.assertEqual(classify(c,[r])['taxonomyClass'],'button')
        other=copy.deepcopy(r);other['class']='tab';self.assertEqual(classify(c,[r,other])['state'],'ambiguous')
        c['className']='Custom';self.assertEqual(classify(c,[r])['state'],'unmapped')
        r['match']={'nativeClass':'Custom'}
        with self.assertRaisesRegex(ValueError,'mapping_match'):classify(c,[r])

if __name__=='__main__':unittest.main()
