"""Receipt checks and failure isolation for combined research reporting."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import research_overview453 as report


class OverviewTests(unittest.TestCase):
    def setUp(self):
        parent=Path(__file__).resolve().parent.parent/'.build'
        parent.mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.spec={'id':'case-decision'}
        self.entry=dict(job='case-decision',specSHA256=report.digest(self.spec),title='Matched correction')
        self.path=self.root/'jobs/case-decision/attempts/1'
        self.path.mkdir(parents=True)
        self.doc=dict(version='research-campaign-decision-v1',modelAccepted=False,outcome='contradicted',
            limitation='Development only.',rows=[dict(id='one',group='original',profile='standard',arm='detector',
                baseline='correct',candidate='miss',gain=False,loss=True,newWrong=False,noFocus=False)])
        self.write(self.root/'jobs/case-decision/spec.json',self.spec)
        self.receipt()

    def write(self,path,value):
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(value))

    def receipt(self,status='complete'):
        path=self.path/'out/decision.json';self.write(path,self.doc)
        self.write(self.path/'result.json',dict(status=status,specSHA256=self.entry['specSHA256'],
            outputs=[dict(path='decision.json',sha256=hashlib.sha256(path.read_bytes()).hexdigest())]))

    def test_two_schemas_and_case_links(self):
        for version in ('research-campaign-decision-v1','model-batch-decision-v1'):
            self.doc['version']=version;self.receipt()
            value=report.campaign(self.entry,self.root)
            self.assertEqual(value['slices'][0]['losses'],1)
            self.assertEqual(value['cases'][0]['id'],'one')
            self.assertEqual(value['modelAcceptance'],'not-granted')

    def test_changed_output_is_unavailable_not_success(self):
        self.doc['rows'][0]['loss']=False
        self.write(self.path/'out/decision.json',self.doc)
        value=report.overview(dict(version='research-overview-v1',campaigns=[self.entry]),self.root)
        self.assertEqual(value['campaigns'][0]['evidence'],'verification-failed')
        self.assertNotIn('slices',value['campaigns'][0])

    def test_detector_campaign_keeps_profile_and_case_links(self):
        self.doc['version']='detector-campaign-decision-v1'
        del self.doc['rows'][0]['arm']
        self.receipt()
        value=report.campaign(self.entry,self.root)
        self.assertEqual(value['slices'][0]['arm'],'detector')
        self.assertEqual(value['cases'][0]['id'],'one')
        self.assertEqual(value['slices'][0]['losses'],1)
        self.assertNotIn('arm',self.doc['rows'][0])

    def test_pending_failed_and_missing_do_not_accept(self):
        self.receipt('failed')
        self.assertEqual(report.campaign(self.entry,self.root)['execution'],'failed')
        self.receipt();(self.path/'out/decision.json').unlink()
        with self.assertRaises(OSError):report.campaign(self.entry,self.root)

    def test_duplicate_unknown_profile_missing_fields_and_promotion_fail(self):
        for change in ('duplicate','profile','missing','promoted'):
            doc=copy.deepcopy(self.doc)
            if change=='duplicate':doc['rows'].append(doc['rows'][0])
            elif change=='profile':doc['rows'][0]['profile']='unknown'
            elif change=='missing':del doc['rows'][0]['gain']
            else:doc['modelAccepted']=True
            with self.assertRaises((ValueError,KeyError)):report.summarize(doc)

    def test_path_and_spec_changes_fail(self):
        with self.assertRaises(ValueError):report.campaign(dict(self.entry,job='../escape'),self.root)
        with self.assertRaises(ValueError):report.campaign(dict(self.entry,specSHA256='changed'),self.root)

    def test_separate_profiles_and_duplicate_campaigns(self):
        self.doc['rows'].append(dict(self.doc['rows'][0],profile='hcf'));self.receipt()
        value=report.campaign(self.entry,self.root)
        self.assertEqual([s['observations'] for s in value['slices']],[1,1])
        with self.assertRaises(ValueError):report.overview(dict(version='research-overview-v1',campaigns=[self.entry,self.entry]),self.root)

    def test_one_bad_campaign_does_not_hide_other_results(self):
        value=report.overview(dict(version='research-overview-v1',campaigns=[self.entry,dict(job='missing',specSHA256='bad')]),self.root)
        self.assertEqual([r['execution'] for r in value['campaigns']],['complete','unavailable'])

    def test_markdown_escapes_displayed_content(self):
        entry=dict(self.entry,title='<script>alert(1)</script>')
        value=report.overview(dict(version='research-overview-v1',campaigns=[entry]),self.root)
        text=report.markdown(value)
        self.assertNotIn('<script>',text)
        self.assertIn('one / original / standard / detector',text)


if __name__=='__main__':unittest.main()
