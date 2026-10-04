import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
import shadow_feedback_contract as c


def case(source='reviewed',relation='changed',probability=.05):
    binding=dict(case_id='synthetic-case',action_id='test-action',before_observation_id='before',after_observation_id='after',
                 before_sha256='a'*64,after_sha256='b'*64)
    return dict(binding=binding,prediction=dict(binding=dict(binding),model_id=c.MODEL,state='scored',
        probability=probability,decision=c.decision(probability)),label=dict(binding=dict(binding),source=source,
        relation=relation,review_id='synthetic-review' if source=='reviewed' else ''),
        context=dict(highlight_geometry='stationary',content_motion='scrolling'))


def module(**values):
    return dict(dict(module_present=False,enabled=False,model_loads=0,pixel_reads=0,inference_calls=0,
        state='skipped',queue_peak=0,queue_limit=8,navigation_before=['down'],navigation_after=['down']),**values)


class ContractTests(unittest.TestCase):
    def test_stationary_highlight_identity_change_is_miss(self):
        result=c.evaluate(case());self.assertFalse(result['correct']);self.assertEqual(result['accuracy_denominator'],1)

    def test_animated_content_same_identity_is_not_focus_change(self):
        value=case(relation='unchanged');value['context']['content_motion']='animated'
        self.assertTrue(c.evaluate(value)['correct'])

    def test_native_hints_not_accuracy(self):
        result=c.evaluate(case('native_hint'))
        self.assertTrue(result['native_hint_disagreement']);self.assertIsNone(result['correct'])
        self.assertEqual(result['accuracy_denominator'],0)

    def test_abstention_and_unknown_have_no_accuracy(self):
        value=c.evaluate(case(probability=.5));self.assertTrue(value['abstained']);self.assertEqual(value['accuracy_denominator'],0)
        self.assertEqual(c.evaluate(case('unknown','unknown'))['accuracy_denominator'],0)

    def test_failures_not_negative_predictions(self):
        for state in c.STATES-{'scored'}:
            value=case();value['prediction'].update(state=state,probability=None,decision=None)
            self.assertEqual(c.evaluate(value)['accuracy_denominator'],0)
            value['prediction'].update(probability=0,decision='unchanged')
            with self.assertRaisesRegex(ValueError,'failure_is_not_prediction'):c.evaluate(value)

    def test_binding_and_review_integrity(self):
        for section in ('prediction','label'):
            value=case();value[section]['binding']['action_id']='wrong'
            with self.assertRaisesRegex(ValueError,'association_mismatch'):c.evaluate(value)
        value=case();value['label']['review_id']=''
        with self.assertRaisesRegex(ValueError,'missing_review'):c.evaluate(value)
        value=case();value['prediction']['truth']='changed'
        with self.assertRaises(ValueError):c.evaluate(value)

    def test_probabilities_thresholds_and_model(self):
        for p in (True,float('nan'),float('inf'),-.1,1.1):
            with self.assertRaises(ValueError):c.decision(p)
        self.assertEqual(c.decision(.15),'unchanged');self.assertEqual(c.decision(.85),'changed')
        value=case();value['prediction']['model_id']='FDR021'
        with self.assertRaisesRegex(ValueError,'model_id'):c.evaluate(value)
        value=case();value['prediction']['decision']='changed'
        with self.assertRaisesRegex(ValueError,'decision_mismatch'):c.evaluate(value)

    def test_absent_and_off_zero_access(self):
        for value in (module(),module(module_present=True),module(enabled=True,state='model_unavailable')):
            self.assertTrue(c.optional_module(value)['contract_passed'])
            value['pixel_reads']=1
            with self.assertRaisesRegex(ValueError,'optional_access'):c.optional_module(value)

    def test_queue_navigation_and_scored_access(self):
        for value in (module(queue_peak=9),module(navigation_after=['select']),
                      module(module_present=True,enabled=True,state='scored')):
            with self.assertRaises(ValueError):c.optional_module(value)
        self.assertFalse(c.optional_module(module(module_present=True,enabled=True,state='scored',model_loads=1,
            pixel_reads=2,inference_calls=1))['execution_attested'])

    def test_document_membership_and_test_only(self):
        doc=dict(version=c.VERSION,test_only=True,cases=[case()],module_cases=[module()])
        self.assertFalse(c.run(doc)['training_eligible'])
        doc['cases']*=2
        with self.assertRaisesRegex(ValueError,'duplicate_case'):c.run(doc)
        doc['version']='v2'
        with self.assertRaises(ValueError):c.run(doc)

    def test_duplicate_json_rejected(self):
        root=Path(__file__).resolve().parents[1]/'.build'
        # Portable tests allow a caller-owned TMPDIR, never create repo-independent caches.
        import os
        root=Path(os.environ.get('TMPDIR',root))
        with tempfile.TemporaryDirectory(dir=root) as tmp:
            path=Path(tmp)/'bad.json';path.write_text('{"version":1,"version":1}')
            with self.assertRaisesRegex(ValueError,'duplicate_key'):c.load(path)

    def test_existing_cli_join_and_mismatches(self):
        v=case('unknown','unknown'); b=v['binding']
        pair=dict(id=b['case_id'],actionID=b['action_id'],beforeObservationID=b['before_observation_id'],
            afterObservationID=b['after_observation_id'],before=dict(path='/test/a',sha256=b['before_sha256']),
            after=dict(path='/test/b',sha256=b['after_sha256']))
        raw=json.dumps(dict(schemaVersion=1,mode='off',root='/test',pairs=[pair])).encode()
        reply=dict(schemaVersion=1,task='focus-change-only',requestSHA256=hashlib.sha256(raw).hexdigest(),
            mode='off',modelID=c.MODEL,backend='cpuOnly',inputEncoding='paired-rgb-letterbox192x128-pillow-bilinear-v1',
            changedThreshold=.85,unchangedThreshold=.15,releaseEligible=False,modelLoaded=False,
            compiledTreeSHA256='not_loaded',failed=0,results=[dict(id=b['case_id'],actionID=b['action_id'],
                beforeObservationID=b['before_observation_id'],afterObservationID=b['after_observation_id'],
                beforeSHA256=b['before_sha256'],afterSHA256=b['after_sha256'],state='skipped')])
        self.assertEqual(c.normalize_cli(raw,reply,[v['label']])['accounting']['assessed'],0)
        for key,value in [('failed',1),('modelLoaded',True),('requestSHA256','0'*64),('compiledTreeSHA256','wrong')]:
            changed=copy.deepcopy(reply);changed[key]=value
            with self.assertRaises(ValueError):c.normalize_cli(raw,changed,[v['label']])
        scored_request=json.loads(raw);scored_request['mode']='score'
        scored_raw=json.dumps(scored_request).encode()
        for model,tree in c.MODEL_TREES.items():
            scored_reply=copy.deepcopy(reply)
            scored_reply.update(mode='score',modelID=model,modelLoaded=True,compiledTreeSHA256=tree,
                requestSHA256=hashlib.sha256(scored_raw).hexdigest())
            scored_reply['results'][0].update(state='scored',probability=.05,decision='unchanged')
            self.assertEqual(c.normalize_cli(scored_raw,scored_reply,[v['label']])['accounting']['cases'],1)
            scored_reply['compiledTreeSHA256']='0'*64
            with self.assertRaisesRegex(ValueError,'loaded_artifact'):
                c.normalize_cli(scored_raw,scored_reply,[v['label']])


if __name__=='__main__':unittest.main()
