"""Test campaign dispatch without navigation or capture."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import research_queue as q
import ttr_campaign_queue493 as adapter

OUT = None


def queue_qualification():
    """Run software fixtures through the actual queue. Never contact TTR."""
    spec=q.load(OUT.parents[2]/'spec.json')
    c=q.load(q.ROOT/spec['inputs'][0]['path'])
    marker_root=OUT/'software-root';marker_root.mkdir()
    with patch.object(q,'ROOT',marker_root), patch.object(adapter,'fixture_binding',return_value={}):
        adapter.execute(c,Client(OUT),OUT,intake=lambda *_: ([],[]))
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
        dict(path='session-result.json',sha256=q.digest(OUT/'session-result.json'))]))


def config():
    manifest=q.load(q.ROOT/'reports/work/ADRSPIKES493/session-1-manifest.json')
    manifest['budget'].update(max_wall_clock_seconds=600,max_retained_bytes=100000000)
    return dict(version='ttr-campaign-queue-v1',manifest=manifest,order=1,
                helper=dict(path=str(Path.home()/'Developer/TVTestRig/.local-work/build/Helpers/aatv')))


class Client:
    def __init__(self, output, failure=None):
        self.calls=[]; self.output=output; self.failure=failure
    def call(self,*args,**kwargs):
        self.calls.append(args)
        if tuple(args[:2]) == self.failure: raise RuntimeError('injected_failure')
        if args[0]=='simulator': return dict(can_run=True,ownership=[dict(state='clear')])
        if args[0]=='status': return dict(commandActive=False,observationActive=False,queuedCommandCount=0)
        if args[:2]==('campaign','status'): return dict(state='completed',completed_cases=4,failed_cases=0)
        if args[:2]==('campaign','export'): return dict(export_path=str(self.output/'corpus'))
        return {}


class CampaignTests(unittest.TestCase):
    def setUp(self):
        parent=q.ROOT/'.build/adr493-tests'; parent.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=parent)
        self.root=Path(self.temp.name); self.out=self.root/'out';self.out.mkdir()
        self.root_patch=patch.object(q,'ROOT',self.root);self.root_patch.start()
        self.binding=patch.object(adapter,'fixture_binding',return_value={});self.binding.start()
    def tearDown(self):
        self.binding.stop();self.root_patch.stop();self.temp.cleanup()
    def cfg(self):
        with patch.object(q,'ROOT',Path(__file__).resolve().parents[1]):return config()
    def execute(self,c,client):
        return adapter.execute(c,client,self.out,intake=lambda *_: ([dict(path='a.png',sha256='0'*64)]*8,[]))
    def test_success_and_duplicate_refusal(self):
        c=self.cfg();client=Client(self.out);self.execute(c,client)
        self.assertTrue(q.load(self.out/'session-result.json')['cleanup'])
        with self.assertRaisesRegex(ValueError,'already_attempted'):self.execute(c,client)
        self.assertEqual(sum(x[:2]==('campaign','start') for x in client.calls),1)
    def test_reuse_uses_same_adapter(self):
        c=self.cfg();c['order']=2;c['manifest']['reuse_runner']=True
        self.execute(c,Client(self.out));self.assertTrue(q.load(self.out/'session-result.json')['reuse'])
    def test_lost_start_preserves_marker_and_cancels_only_own_campaign(self):
        c=self.cfg();client=Client(self.out,('campaign','start'))
        with self.assertRaisesRegex(RuntimeError,'injected'):self.execute(c,client)
        self.assertIn(('campaign','cancel',c['manifest']['campaign_id']),client.calls)
        self.assertTrue(list((self.root/'.build').glob('campaign493-*')))
    def test_export_failure_never_recaptures(self):
        client=Client(self.out,('campaign','export'))
        with self.assertRaisesRegex(RuntimeError,'injected'):self.execute(self.cfg(),client)
        self.assertEqual(sum(x[:2]==('campaign','start') for x in client.calls),1)
        self.assertFalse((self.out/'capture-evidence.json').exists())
    def test_scope_rejections(self):
        for field,value in [('version','wrong'),('order',2)]:
            c=self.cfg();c[field]=value
            with self.assertRaises(ValueError):adapter.validate_config(c)
        c=self.cfg();c['manifest']['budget']['max_wall_clock_seconds']=800
        with self.assertRaisesRegex(ValueError,'producer_budget'):adapter.validate_config(c)
    def test_ownership_blocks_dispatch(self):
        client=Client(self.out)
        with patch.object(adapter,'readiness',side_effect=ValueError('occupied')):
            with self.assertRaisesRegex(ValueError,'occupied'):self.execute(self.cfg(),client)
        self.assertEqual(client.calls,[])

    def test_capture_allowance_is_scoped(self):
        root=Path(__file__).resolve().parents[1]
        s=q.load(root/'reports/work/ADRSPIKES493/session-1-queue-spec.json')
        with patch.object(q,'ROOT',root):
            q.validate(s)
            bad=copy.deepcopy(s);bad['id']='unapproved-session'
            with self.assertRaisesRegex(ValueError,'campaign_approved_scope'):q.validate(bad)
            bad=copy.deepcopy(s);bad['limits']['maxOutputBytes']=250000001
            with self.assertRaisesRegex(ValueError,'capture_limits'):q.validate(bad)
            bad=copy.deepcopy(s);bad['adapter']['steps']=['template_bridge395.capture']
            with self.assertRaisesRegex(ValueError,'capture_limits'):q.validate(bad)

    def test_observed_labels_use_endpoints_not_case_document(self):
        c=self.cfg();folder=self.out/'corpus';folder.mkdir()
        for item in c['manifest']['cases']:
            case=folder/item['case_id'];case.mkdir()
            q.save(case/'transition-case.json',dict(case_id=item['case_id']))
            (case/'before.png').write_bytes(b'fixture');(case/'after.png').write_bytes(b'fixture')
        with patch('focus_corrected_transition_audit.validate_case',return_value=(
                dict(cleanup='verified'),dict(focus='first',controls=[]),dict(focus='second',controls=[]))):
            images,labels=adapter.export_labels(folder,c['manifest'])
        self.assertEqual(len(images),8)
        self.assertEqual([x['focus'] for x in labels],['first','second']*4)
        self.assertTrue(all(not x['trainingEligible'] for x in labels))

    def test_report_requires_both_repetitions_and_matching_labels(self):
        for times,changed,expected in [([10,5,5,10],False,'supported'),
                                      ([10,5,11,10],False,'inconclusive'),
                                      ([10,5,5,10],True,'contradicted')]:
            documents={};dependencies=[]
            for index,seconds in enumerate(times,1):
                prefix=str(index)
                documents[prefix+'/session-result.json']=dict(order=index,reuse=index in (2,3),
                    totalSeconds=seconds,acceptedFrames=8,cleanup=True)
                documents[prefix+'/labels.json']=dict(rows=[dict(case='one',endpoint='before',
                    focus='changed' if changed and index==2 else 'same')])
                dependencies.append(dict(outputs=[dict(path=prefix+'/'+n) for n in ('session-result.json','labels.json')]))
            saved={}
            def load(path):
                return dependencies if str(path).endswith('dependencies.json') else documents[str(path)]
            with patch.object(adapter,'OUT',self.out),patch.object(adapter,'checked',side_effect=lambda p:p['path']), \
                 patch.object(q,'load',side_effect=load),patch.object(q,'save',side_effect=lambda p,d:saved.update({p.name:d})), \
                 patch.object(q,'digest',return_value='0'*64):
                adapter.compare()
            self.assertEqual(saved['comparison.json']['outcome'],expected)
