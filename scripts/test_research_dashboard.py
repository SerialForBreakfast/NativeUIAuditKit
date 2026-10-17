"""Test local controls through HTTP and the actual queue runner."""
import http.client
import json
import threading
import time
import unittest
from test_research_queue import QueueTests
from research_dashboard_server import Controller, Server
from generate_research_dashboard import render_html
import research_queue as q


class DashboardTests(QueueTests):
    def test_readiness_labels_through_http(self):
        spec = self.spec_v2()
        self.submit(spec, approve=False)
        code, body = self.request('/api/state')
        self.assertEqual(code, 200)
        row = json.loads(body)['jobs'][0]
        self.assertEqual(row['state'], 'pending')
        self.assertEqual(row['displayState'], 'awaiting-approval')
        self.assertEqual(self.request('/api/add', {'jobs': [{'id': 'job-a', 'sha256': q.text_digest(spec)}]})[0], 200)
        self.assertEqual(self.control.snapshot()['jobs'][0]['displayState'], 'ready')
        self.input.write_text('{}')
        row = self.control.snapshot()['jobs'][0]
        self.assertEqual(row['displayState'], 'blocked')
        self.assertIn('input_changed', row['readinessReasons'])

    def test_clear_state_filters_and_safe_fallback(self):
        from research_dashboard_states import classify
        self.assertEqual(classify({'state': 'pending', 'approved': True})[0], 'unchecked')
        self.assertEqual(classify({'state': 'pending'}, {'ready': False, 'blockers': [
            {'requirement': 'input_changed'}, {'requirement': 'not_approved'}]})[0], 'blocked')
        page = render_html({'jobs': []})
        for text in ('Pending (all not started)', 'Awaiting approval', 'READINESS UNCHECKED',
                     'Runner active — waiting', 'j.readinessReasons.map(reasonLabel)', 'id="chip-awaiting"'):
            self.assertIn(text, page)
        self.assertNotIn("j.state==='pending'&&j.approved", page)

    def test_superseded_needs_complete_replacement(self):
        from research_dashboard_states import supersede
        rows = [dict(job='old', state='blocked', displayState='blocked', readinessReasons=['input_changed']),
                dict(job='stale', state='exhausted', displayState='exhausted', readinessReasons=[]),
                dict(job='new', state='complete', displayState='complete', readinessReasons=[]),
                dict(job='open', state='pending', displayState='blocked', readinessReasons=['x']),
                dict(job='waiting', state='pending', displayState='blocked', readinessReasons=['x'])]
        supersede(rows, {'old': ('new', 'Reason.'), 'stale': ('new', 'Reason.'),
                         'waiting': ('open', 'Reason.'), 'new': ('old', 'Reason.')})
        states = {row['job']: row['displayState'] for row in rows}
        self.assertEqual(states, dict(old='superseded', stale='superseded', new='complete',
                                      open='blocked', waiting='blocked'))
        self.assertEqual(rows[0]['supersededBy'], 'new')
        self.assertIn('id="chip-superseded"', render_html({'jobs': []}))

    def test_backlog_panel_summary(self):
        from research_dashboard_states import backlog_summary
        value = backlog_summary([dict(job='x', task='B405-073', authority='diagnostic', state='pending',
                                      displayState='ready', wallSeconds=None)], q.ROOT)
        self.assertEqual(value['readyJobs'], 1)
        self.assertTrue(value['refill'])
        self.assertEqual(next(r for r in value['records'] if r['id'] == 'B405-073')['ready'], 1)
        page = render_html({'jobs': [], 'backlog': value})
        self.assertIn('id="backlog-table"', page)
        self.assertIn('backlog-grooming cycle', page)
        for text in ('id="glance-state"', 'id="glance-next"', 'id="superseded-rows"', 'id="rows-empty"', 'No active or waiting jobs'):
            self.assertIn(text, page)
        self.assertIn('topBlockers', value)
        self.assertIsInstance(value['reviewPending'], list)

    def test_add_during_continuous_execution(self):
        first = self.spec(); self.submit(first)
        self.assertEqual(self.request('/api/start-all', {})[0], 200)
        second = self.spec_v2(id='job-b'); self.submit(second, approve=False)
        payload = {'jobs': [{'id': 'job-b', 'sha256': q.text_digest(second)}]}
        self.assertEqual(self.request('/api/add', payload, token=False)[0], 403)
        self.assertEqual(self.request('/api/add', payload, origin=False)[0], 403)
        self.assertEqual(self.request('/api/add', payload)[0], 200)
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline and q.state(self.queue/'jobs/job-b')[0] != 'complete':
            time.sleep(.1)
        self.assertEqual(q.state(self.queue/'jobs/job-b')[0], 'complete')
        self.assertEqual(len(q.attempts_of(self.queue/'jobs/job-b')), 1)
        self.assertEqual(self.request('/api/add', payload)[0], 200)
        self.request('/api/stop', {})
        self.wait_done()
        self.assertTrue((self.queue/'campaigns/TEST338.json').exists())

    def setUp(self):
        super().setUp()
        self.control=Controller(self.queue,self.modules,self.lock)
        self.server=Server(0,self.control)
        self.worker=threading.Thread(target=self.server.serve_forever)
        self.worker.start()

    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.worker.join()
        super().tearDown()

    def request(self,path,body=None,token=True,origin=True,host=None):
        c=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=5)
        headers={'Content-Type':'application/json'}
        if token:headers['Authorization']='Bearer '+self.server.token
        if origin:headers['Origin']=self.server.origin
        if host:headers['Host']=host
        c.request('POST' if body is not None else 'GET',path,json.dumps(body) if body is not None else None,headers)
        r=c.getresponse();raw=r.read();status=r.status;c.close();return status,raw

    def wait_done(self):
        self.control.thread.join(timeout=5)
        self.assertFalse(self.control.busy)

    def test_http_start_and_progress(self):
        self.submit(self.spec())
        code,_=self.request('/api/start',{'jobs':['job-a']});self.assertEqual(code,200)
        self.wait_done()
        code,body=self.request('/api/state');self.assertEqual(code,200)
        row=json.loads(body)['jobs'][0]
        self.assertEqual(row['state'],'complete');self.assertEqual(row['progress']['completed'],1)
        self.assertNotIn('eta',row)

    def test_measured_entrypoint_through_http(self):
        import research_evidence as evidence
        def pin(path):
            return dict(path=q.relative(path),sha256=q.digest(path))
        # These labels test software. They are not model evaluation evidence.
        rows=[dict(id='fixture',label=1,prediction=1,role='development',group='fixture',
                   inputs=[pin(self.input)],theme='dark_standard',archetype='shelf')]
        predictions=self.base/'predictions.json';q.save(predictions,rows)
        members=self.base/'members.json';q.save(members,[{k:v for k,v in rows[0].items() if k!='prediction'}])
        doc=dict(version=evidence.VERSION,task='focus-change',dataRole='development',
                 labelAuthority='authored',sourceDomain='authored',model=pin(self.input),
                 preprocessing=pin(self.input),settings=pin(self.input),membership=pin(members),predictions=pin(predictions))
        source=self.base/'evidence.json';q.save(source,doc)
        spec=self.spec(adapter=dict(type='python-callable',steps=['benchmark_evaluator.measured_run'],
                       outputAttributes=['benchmark_evaluator.OUTPUT_DIR']),
                       stage=[{'from':pin(source),'to':'evidence.json'}])
        q.submit(self.write_spec(spec),self.queue,q.MODULES)
        import research_approval
        research_approval.approve(self.queue,'job-a','test','isolated test fixture approval',q.MODULES)
        self.control.modules=q.MODULES
        self.assertEqual(self.request('/api/start',{'jobs':['job-a']})[0],200)
        self.wait_done()
        row=self.control.snapshot()['jobs'][0]
        self.assertEqual(row['state'],'complete', (self.attempt()/'stderr.log').read_text())
        self.assertEqual(row['evidenceKind'],'measured')
        self.assertEqual(row['measured']['metrics']['truePositive'],1)
        self.assertEqual(row['modelAcceptance'],'not-assessed')

    def test_current_task_panel_is_prominent(self):
        page=render_html({'jobs':[]})
        self.assertIn('aria-label="Current task"',page)
        self.assertLess(page.index('id="active"'),page.index('id="rows"'))
        self.assertIn('Decision rule:',page)
        self.assertIn('waiting for a worker event',page)
        self.assertIn('Another queue runner owns this task.',page)
        self.assertIn('busy||Boolean(active)',page)
        self.assertIn('id="toggle-run"',page)
        self.assertIn('id="stats-bar"',page)
        self.assertIn('▶ Run all ready',page)
        self.assertIn('■ Stop after task',page)

    def test_continuous_runs_ready_once_then_stops(self):
        self.submit(self.spec())
        self.assertEqual(self.request('/api/start-all',{})[0],200)
        deadline=time.monotonic()+4
        while time.monotonic()<deadline and q.state(self.queue/'jobs/job-a')[0]!='complete':time.sleep(.02)
        self.assertEqual(q.state(self.queue/'jobs/job-a')[0],'complete')
        self.assertTrue(self.control.busy)
        self.assertEqual(self.request('/api/stop',{})[0],200)
        self.wait_done()
        self.assertEqual(len(q.state(self.queue/'jobs/job-a')[1]),1)

    def test_continuous_does_not_retry_failure(self):
        self.submit(self.spec(adapter=dict(type='python-callable',steps=['rq_fixture.slow'],outputAttributes=['rq_fixture.OUT'])))
        self.control.start_all()
        deadline=time.monotonic()+3
        while time.monotonic()<deadline and self.control.current is None:time.sleep(.02)
        self.control.cancel.set()
        deadline=time.monotonic()+3
        while time.monotonic()<deadline and q.state(self.queue/'jobs/job-a')[0]=='running':time.sleep(.02)
        self.control.stop.set();self.wait_done()
        self.assertEqual(len(q.state(self.queue/'jobs/job-a')[1]),1)

    def test_cancel_owned_job(self):
        self.submit(self.spec(adapter=dict(type='python-callable',steps=['rq_fixture.slow'],outputAttributes=['rq_fixture.OUT'])))
        self.control.start(['job-a'])
        deadline=time.monotonic()+3
        while time.monotonic()<deadline and not (self.attempt()/'progress.json').exists():time.sleep(.02)
        self.assertEqual(q.state(self.queue/'jobs/job-a')[0],'running')
        self.assertEqual(self.request('/api/cancel',{})[0],200)
        self.wait_done()
        self.assertEqual(q.state(self.queue/'jobs/job-a')[0],'cancelled')

    def test_duplicate_start(self):
        self.submit(self.spec(adapter=dict(type='python-callable',steps=['rq_fixture.slow'],outputAttributes=['rq_fixture.OUT'])))
        self.control.start(['job-a'])
        with self.assertRaisesRegex(ValueError,'batch_running'):self.control.start(['job-a'])
        self.control.stop.set();self.control.cancel.set();self.wait_done()

    def test_stop_after_current_preserves_next(self):
        adapter=dict(type='python-callable',steps=['rq_fixture.brief'],outputAttributes=['rq_fixture.OUT'])
        self.submit(self.spec(adapter=adapter));self.submit(self.spec(id='job-b'))
        self.control.start(['job-a','job-b'])
        deadline=time.monotonic()+3
        while time.monotonic()<deadline and not (self.attempt()/'progress.json').exists():time.sleep(.02)
        self.assertEqual(self.request('/api/stop',{})[0],200)
        self.wait_done()
        self.assertEqual(q.state(self.queue/'jobs/job-a')[0],'complete')
        self.assertEqual(q.state(self.queue/'jobs/job-b')[0],'pending')

    def test_output_limit_stops_child(self):
        adapter=dict(type='python-callable',steps=['rq_fixture.oversized'],outputAttributes=['rq_fixture.OUT'])
        self.submit(self.spec(adapter=adapter,limits=dict(timeoutSeconds=20,maxOutputBytes=10000,maxAttempts=2)))
        self.control.start(['job-a']);self.wait_done()
        self.assertEqual(q.load(self.attempt()/'result.json')['reason'],'output_limit')

    def test_eta_needs_matching_history(self):
        for id in ('job-a','job-b','job-c'):self.submit(self.spec(id=id))
        self.run_queue()
        self.assertTrue(all('eta' not in r for r in self.control.snapshot()['jobs']))

    def test_http_auth_and_origin(self):
        for kwargs in ({'token':False},{'origin':False},{'host':'evil.example'}):
            self.assertEqual(self.request('/api/start',{'jobs':['job-a']},**kwargs)[0],403)

    def test_path_and_arbitrary_fields(self):
        self.assertEqual(self.request('/api/start',{'jobs':['../escape']})[0],400)
        self.assertEqual(self.request('/api/start',{'jobs':['job-a'],'command':'anything'})[0],400)

    def test_html_escapes_script(self):
        page=render_html({'jobs':[{'hypothesis':'</script><script>alert(1)</script>'}]})
        self.assertNotIn('</script><script>alert',page)
        self.assertNotIn('https://',page)


    def test_snapshot_cache_is_shared_and_invalidated(self):
        from unittest import mock
        self.submit(self.spec())
        calls=[]
        original=self.control.snapshot
        def slow():
            calls.append(1);time.sleep(0.3);return original()
        with mock.patch.object(self.control,'snapshot',side_effect=slow):
            replies=[]
            threads=[threading.Thread(target=lambda:replies.append(self.control.state_reply())) for _ in range(4)]
            for t in threads:t.start()
            for t in threads:t.join()
            self.assertEqual(len(calls),1)
            self.assertEqual({r['snapshotId'] for r in replies},{1})
            code,body=self.request('/api/state?since=1')
            self.assertEqual(json.loads(body),dict(json.loads(body),unchanged=True))
            self.assertNotIn('jobs',json.loads(body))
            self.assertEqual(self.request('/api/stop',{})[0],200)
            code,body=self.request('/api/state?since=1')
            self.assertEqual(json.loads(body)['snapshotId'],2)
            self.assertIn('jobs',json.loads(body))
            self.assertEqual(len(calls),2)

    def test_old_snapshot_is_served_while_rebuilding(self):
        from unittest import mock
        self.submit(self.spec())
        first=self.control.state_reply()
        self.assertFalse(first['stale'])
        self.control.cache['started']-=60  # Age the snapshot without an action.
        release=threading.Event()
        original=self.control.snapshot
        def slow():
            release.wait(5);return original()
        with mock.patch.object(self.control,'snapshot',side_effect=slow):
            start=time.monotonic()
            reply=self.control.state_reply()
            self.assertLess(time.monotonic()-start,1)
            self.assertTrue(reply['stale'])
            self.assertEqual(reply['snapshotId'],first['snapshotId'])
            release.set()
            for _ in range(50):
                if not self.control.building:break
                time.sleep(.1)
        self.assertEqual(self.control.state_reply()['snapshotId'],first['snapshotId']+1)


if __name__=='__main__':unittest.main()
