"""Generated software contracts. These fixtures do not establish model quality."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image
import research_queue as q
from template_inputs398 import pin
import sdk_native589 as n


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        parent=q.ROOT/'.build/native589-tests';parent.mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=parent);self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.addCleanup(patch.stopall);patch.object(n.sdk,'portable',return_value={}).start()
        patch('sdk_packet502.review',return_value=dict(reviewable=True)).start()

    def fixture(self,prefix):
        captures=[dict(job=prefix+str(i),specSHA256=str(i)*64,group=prefix+'-group-'+str(i),split='train' if i<6 else 'validation') for i in range(8)]
        approval=self.root/(prefix+'-approval.json');q.save(approval,dict(version='native-profile-policy589-v1',decision='approved',policy=n.POLICY,userMessage='generated test record',chatContext='isolated test',captures=captures,researchOnly=True,independentQualification=False))
        config=dict(target='target',withinFamilyDevelopment=True,captures=captures,approval=pin(approval),exclusions=dict(groups=[],contentGroups=[],sourceFamilies=[],images=[]))
        frames=[];rows=[];pairs=[]
        for i,plan in enumerate(captures):
            folder=self.root/(prefix+str(i));folder.mkdir();doc=dict(continuityAssessment=dict(state='bounded_session_inference',basis='supervisor_ledger_and_native_read_receipts',policy='owned_session_bracket_v2',value='standard',unavailable=['external_setting_mutations'],endpoints={}),focusStyleContinuity=dict(coverage='owned_commands_only',externalChangesObserved=False,targetID='target',clockID='supervisor',profileReads={},endpoints={}),coverage={},focusStyleEvidence={})
            pending=[]
            for j,side in enumerate(('before','after')):
                p=folder/side;p.mkdir();image=p/'frame.png';Image.new('RGB',(6,6),(i*2+j,8,9)).save(image)
                e=p/'evidence.json';q.save(e,dict(mapping=dict(orientation='up')));manifest=p/'manifest.json';q.save(manifest,dict(cases=[dict(frames=[dict(evidence='evidence.json')])]))
                doc[side]=dict(packet=side,caseID=side,manifestSHA256=q.digest(manifest));capture=prefix+str(i)+side
                doc['coverage'][side]=dict(coordinateSpace='screen_pixels',truncated=False)
                doc['continuityAssessment']['endpoints'][side]=capture;doc['focusStyleContinuity']['endpoints'][side]=dict(captureID=capture)
                controls=[dict(identity=dict(id='button'+str(k)),pixelBounds=[k*3,0,3,6]) for k in range(2)]
                f=dict(id=prefix+str(i)+'-'+side,group=plan['group'],contentGroup=plan['group'],split=plan['split'],role='review_only',trainingEligible=False,
                    appID='example.ttr.navigation.consumer',sourceID='target',endpoint=side,image=pin(image),sha256=q.digest(image),family='one-sample-family',profile='unknown',missing=['observed_profile_unqualified','geometry_alignment_unqualified'],focusID='button'+str(j),focusState='focused',controls=controls)
                pending.append(f)
            mp=folder/'pair.json';q.save(mp,doc);ref=pin(mp);pairs.append(ref)
            for j,f in enumerate(pending):
                f['pair']=ref;frames.append(f)
                for k,c in enumerate(f['controls']):
                    crop=folder/(f['endpoint']+str(k)+'.png');Image.new('RGB',(256,256),(i*4+j*2+k,0,1)).save(crop)
                    rows.append(dict(id=f['id']+f'-control-{k:03}',frame=f['endpoint'],pair=ref,identity=c['identity'],control=c['identity']['id'],box=c['pixelBounds'],label=int(c['identity']['id']==f['focusID']),sourceImage=f['image'],role='review_only',profile='unknown',trainingEligible=False,path=str(crop),sha256=q.digest(crop),group=f['group'],family=f['family']))
        source=self.root/(prefix+'-source.json');q.save(source,dict(commit='a'*40));raw=dict(admission=None,pairs=pairs,source=pin(source));data=dict(frames=frames,requestSHA256=q.text_digest(raw));crops=dict(frames=frames,rows=rows,trainingEligible=False,preprocessing={'generated':'contract'})
        return config,raw,data,crops

    def test_two_configurations_use_one_admission_contract(self):
        for name in ('first','second'):
            cfg,raw,data,crops=self.fixture(name);original=copy.deepcopy(crops);result=n.admit_rows(cfg,raw,data,crops)
            self.assertEqual(crops,original);self.assertTrue(result['trainingEligible'])
            self.assertFalse(result['independentQualificationEligible'])
            self.assertEqual(Counter(r['role'] for r in result['rows']),{'train':24,'development':8})
            self.assertTrue(all(r['producerProfile']=='unknown' and r['profileEvidence']['directFrameObservation'] is False for r in result['rows']))

    def test_consent_and_old_roles_cannot_expand(self):
        cfg,raw,data,crops=self.fixture('bounds')
        bad=copy.deepcopy(cfg);bad['captures'][0]['split']='test'
        with self.assertRaisesRegex(ValueError,'approval_membership'):n.admit_rows(bad,raw,data,crops)
        bad=copy.deepcopy(data);bad['frames'][0]['role']='development'
        altered=copy.deepcopy(crops);altered['frames']=bad['frames']
        with self.assertRaisesRegex(ValueError,'original_role'):n.admit_rows(cfg,raw,bad,altered)
        bad=copy.deepcopy(cfg);bad['exclusions']['groups']=[cfg['captures'][0]['group']]
        with self.assertRaisesRegex(ValueError,'excluded_groups'):n.admit_rows(bad,raw,data,crops)

    def test_profile_and_geometry_gaps_stay_explicit(self):
        cfg,raw,data,crops=self.fixture('gaps')
        for update in ({'value':'hcf'},{'state':'unknown'},{'unavailable':[]}):
            p=n.checked(raw['pairs'][0]);d=q.load(p);d['continuityAssessment'].update(update)
            with self.assertRaises(ValueError):n.profile_evidence(d,data['frames'][0])
        changed=copy.deepcopy(data);changed['frames'][0]['missing'].append('focus_unavailable')
        new=copy.deepcopy(crops);new['frames']=changed['frames']
        with self.assertRaisesRegex(ValueError,'unresolved_evidence'):n.admit_rows(cfg,raw,changed,new)

    def test_wrong_crop_label_and_bytes_reject(self):
        cfg,raw,data,crops=self.fixture('labels');changed=copy.deepcopy(crops);changed['rows'][0]['label']=1-changed['rows'][0]['label']
        with self.assertRaisesRegex(ValueError,'crop_label'):n.admit_rows(cfg,raw,data,changed)
        changed=copy.deepcopy(crops);changed['rows'][0]['sha256']='0'*64
        with self.assertRaises(ValueError):n.admit_rows(cfg,raw,data,changed)

    def test_matched_exposure_preserves_roles_and_protected_pixels(self):
        cfg,raw,data,crops=self.fixture('exposure');admitted=n.admit_rows(cfg,raw,data,crops);replay=[]
        for i in range(4):
            p=self.root/('replay'+str(i)+'.png');Image.new('RGB',(256,256),(180+i,1,0)).save(p)
            replay.append(dict(id='replay'+str(i),image=pin(p),label=i%2,group='replay'+str(i),source='legacy-replay',role='train'))
        arms=n.matched_rows(admitted,replay,set());self.assertEqual(len(arms['control']),len(arms['native']))
        self.assertTrue(all(r['role']=='train' for rows in arms.values() for r in rows))
        self.assertTrue(all(r['source']!='sdk-native' for r in arms['control']))
        self.assertTrue(any(r['source']=='sdk-native' for r in arms['native']))
        with self.assertRaisesRegex(ValueError,'protected_pixels'):n.matched_rows(admitted,replay,{admitted['rows'][0]['pixelSHA256']})
        changed=copy.deepcopy(admitted);changed['rows'][-1]['group']=replay[0]['group']
        with self.assertRaisesRegex(ValueError,'group_leak'):n.matched_rows(changed,replay,set())


    def test_unmapped_empty_nofocus_frames_supply_no_training_crops(self):
        cfg,raw,data,crops=self.fixture('empty')
        omitted={f['id'] for f in data['frames'] if f['group']==cfg['captures'][5]['group']}
        for f in data['frames']:
            if f['id'] not in omitted:continue
            f.update(controls=[],focusID=None,focusState='no_focus')
            pair=q.load(n.checked(f['pair']));packet=n.checked(f['pair']).parent/pair[f['endpoint']]['packet']
            q.save(packet/'evidence.json',dict(mapping=None),replace=True)
        crops['frames']=copy.deepcopy(data['frames'])
        crops['rows']=[r for r in crops['rows'] if not any(r['id'].startswith(i+'-control-') for i in omitted)]
        admitted=n.admit_rows(cfg,raw,data,crops)
        empty=[f for f in admitted['frames'] if f['id'] in omitted]
        self.assertEqual(len(empty),2)
        self.assertTrue(all(not f['trainingEligible'] and not f['cropGeometryVerified'] and f['cropCount']==0 for f in empty))
        self.assertTrue(all(f['missing']==['geometry_alignment_unqualified'] for f in empty))
        self.assertFalse(any(r['frame'] in omitted for r in admitted['rows']))
        self.assertEqual(len(admitted['frames']),16)

    def test_unmapped_eligible_controls_still_reject(self):
        cfg,raw,data,crops=self.fixture('unmapped')
        f=data['frames'][0];pair=q.load(n.checked(f['pair']));packet=n.checked(f['pair']).parent/pair[f['endpoint']]['packet']
        q.save(packet/'evidence.json',dict(mapping=None),replace=True)
        with self.assertRaisesRegex(ValueError,'native589_orientation'):n.admit_rows(cfg,raw,data,crops)

    def test_existing_trainer_receives_only_fixed_training_rows(self):
        cfg,raw,data,crops=self.fixture('caller');admitted=n.admit_rows(cfg,raw,data,crops)
        protocol=self.root/'protocol.json';q.save(protocol,dict(generated=True));cfg['replayProtocol']=pin(protocol)
        rows=[r for r in admitted['rows'] if r['role']=='train'];member=self.root/'member.json'
        q.save(member,dict(trainingAdmitted=True,profilePolicy=n.POLICY,approval=cfg['approval'],replayProtocol=cfg['replayProtocol'],planSHA256=q.text_digest(cfg),rows=rows))
        init=self.root/'initial.pt';init.write_bytes(b'generated initializer')
        out=self.root/'training';out.mkdir();patch.object(n,'OUT',out).start()
        patch.object(n,'request',return_value=(dict(id='generated-train'),cfg,dict(membership=pin(member),initialization=pin(init)))).start()
        patch('focus_corpus568.replay_members',return_value=[]).start()
        def resident(rows,initial,destination,**options):
            self.assertTrue(all(r['role']=='train' for r in rows))
            self.assertEqual(options,dict(epochs=30,batch=16,seed=371,profile='balanced',deduplicate=False,selection='fixed-last',repeat=1))
            (destination/'final.pt').write_bytes(b'generated software output')
            q.save(destination/'history.json',[dict(epoch=i,trainLoss=.5) for i in range(1,31)])
            return dict(epochs=30,developmentCrops=0,selection='fixed-last')
        with patch('train_focus_ring_detector.train_native_hcf',side_effect=resident) as mocked:n.train()
        self.assertEqual(mocked.call_count,1);self.assertFalse(q.load(out/'model.json')['modelAccepted'])
        exposure=q.load(out/'fit.json')['exposure']
        self.assertEqual(exposure['imageOccurrencesPerEpoch'],len(rows))
        self.assertEqual(exposure['uniqueTrainImages'],len({n.pixel(dict(path=q.relative(Path(r['path'])),sha256=r['sha256'])) for r in rows}))
        history=q.load(out/'history.json');history.pop();q.save(out/'history.json',history,replace=True)
        with patch('train_focus_ring_detector.train_native_hcf',return_value=dict(epochs=30,developmentCrops=0,selection='fixed-last')):
            with self.assertRaisesRegex(ValueError,'training_history'):n.train()

    def test_optional_teacher_reuses_only_exact_training_anchors(self):
        cfg,raw,data,crops=self.fixture('teacher');admitted=n.admit_rows(cfg,raw,data,crops)
        protocol=self.root/'protocol.json';q.save(protocol,dict(generated=True));cfg['replayProtocol']=pin(protocol)
        rows=[r for r in admitted['rows'] if r['role']=='train'];rows+=rows[:2];member=self.root/'member.json'
        q.save(member,dict(trainingAdmitted=True,profilePolicy=n.POLICY,approval=cfg['approval'],replayProtocol=cfg['replayProtocol'],planSHA256=q.text_digest(cfg),rows=rows))
        init=self.root/'initial.pt';init.write_bytes(b'generated initializer')
        anchors=self.root/'anchors.json';q.save(anchors,dict(version='teacher-anchors-v1',rows=rows[:2]))
        teacher=self.root/'teacher.json';q.save(teacher,dict(model=pin(init),anchors=pin(anchors),weight=1.0))
        out=self.root/'training';out.mkdir();refs=dict(membership=pin(member),initialization=pin(init),teacherPreservation=pin(teacher))
        patch.object(n,'OUT',out).start();patch.object(n,'request',return_value=(dict(id='generated-teacher'),cfg,refs)).start()
        patch('focus_corpus568.replay_members',return_value=[]).start()
        def resident(rows,initial,destination,**options):
            self.assertEqual(options['teacher_preservation'],q.load(teacher))
            self.assertTrue(all(r['role']=='train' for r in rows))
            (destination/'final.pt').write_bytes(b'generated teacher output')
            q.save(destination/'history.json',[dict(epoch=i,trainLoss=.5) for i in range(1,31)])
            return dict(epochs=30,developmentCrops=0,selection='fixed-last')
        with patch('train_focus_ring_detector.train_native_hcf',side_effect=resident):n.train()
        report=q.load(out/'fit.json');self.assertIsNotNone(report['teacherPreservation'])
        self.assertEqual(report['exposure']['imageOccurrencesPerEpoch'],26)
        self.assertEqual(report['exposure']['uniqueTrainingRows'],24)
        self.assertEqual(report['exposure']['uniqueTrainImages'],24)
        changed=q.load(anchors);changed['rows'][0]['role']='development';q.save(anchors,changed,replace=True)
        config=q.load(teacher);config['anchors']=pin(anchors);q.save(teacher,config,replace=True);refs['teacherPreservation']=pin(teacher)
        with patch('train_focus_ring_detector.train_native_hcf') as train:
            with self.assertRaises(ValueError):n.train()
            train.assert_not_called()

    def test_native_wrong_selection_vetoes_other_supported_reports(self):
        root=self.root/'comparison';root.mkdir();refs={}
        for key in ('reference','control','native'):
            p=root/(key+'.json');q.save(p,dict(generated=True));refs[key]=pin(p)
        p=root/'native-scores.json';q.save(p,dict(reports={name:dict(rows=[dict(id='case',outcome=outcome)]) for name,outcome in [('baseline','correct'),('control','miss'),('native','wrong')]}));refs['nativeScores']=pin(p)
        patch.object(n,'OUT',root).start();patch.object(n,'request',return_value=({},None,refs)).start()
        with patch('focus_replay568.compare_reports',return_value=dict(outcome='supported',modelAccepted=False)):n.compare()
        result=q.load(root/'benchmark_summary.json');self.assertEqual(result['outcome'],'contradicted')
        self.assertEqual(result['nativeDevelopment']['lostBaselineSuccesses'],['case'])


class CompilerTests(unittest.TestCase):
    def test_two_definitions_bind_final_producer_hashes_without_registration(self):
        from sdk_native_graph589 import compile_request
        cfg=q.load(q.ROOT/'reports/work/NATIVE589/campaign-r2.json')
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build/native589-tests') as folder:
            for suffix in ('a','b'):
                r=Path(folder)/('request-'+suffix+'.json');q.save(r,dict(cfg,id='generated-native589-'+suffix))
                m=compile_request(r,Path(folder)/suffix,limit_overrides={('generated-native589-'+suffix+'-control-train'):dict(timeoutSeconds=10800,maxOutputBytes=2147483648)});self.assertEqual(len(m['jobs']),8)
                known={}
                for row in m['jobs']:
                    spec=q.load(n.checked(row['spec']));q.validate(spec)
                    for dep in spec['dependencies']:
                        if dep['job'] in known:self.assertEqual(dep['specSHA256'],q.text_digest(known[dep['job']]))
                    known[spec['id']]=spec
                self.assertEqual(sum(v['authority']=='training' for v in known.values()),2)
                self.assertEqual(known['generated-native589-'+suffix+'-control-train']['limits']['timeoutSeconds'],10800)
                self.assertFalse(m['executionStarted'])


from collections import Counter
if __name__=='__main__':unittest.main()
