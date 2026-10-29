"""Check geometry comparisons without model execution."""
import unittest
from sdk_geometry506 import matches

class GeometryTests(unittest.TestCase):
    def element(self, **changes):
        return dict(identity={'id':'control'},geometryAvailable=True,observedVisibleEnabled=True,pixelBounds=[10,20,30,40],**changes)

    def test_native_consumer_rows(self):
        import research_queue as q
        from sdk_geometry506 import prepare
        _,frames=prepare(q.load(q.ROOT/'reports/work/SDK506/request.json'))
        rows=matches(frames[0]['elements'],[])
        self.assertEqual(len(rows),4)
        self.assertTrue(all(r['id'] and not r['covered'] for r in rows))

    def test_exact_missing_and_ambiguous_proposals(self):
        e=self.element();p=dict(boundingBoxPixels=dict(x=10,y=20,width=30,height=40))
        self.assertEqual(matches([e],[p])[0]['bestIoU'],1)
        self.assertFalse(matches([e],[])[0]['covered'])
        self.assertEqual(matches([e],[p,p])[0]['candidates'],2)

    def test_nonvisible_elements_are_not_scored(self):
        e=self.element();e['observedVisibleEnabled']=False
        self.assertEqual(matches([e],[]),[])

    def test_invalid_predictions_fail(self):
        for width in [-1,float('nan')]:
            with self.assertRaisesRegex(ValueError,'sdk_prediction_geometry'):
                matches([self.element()],[dict(boundingBoxPixels=dict(x=0,y=0,width=width,height=2))])

class ThresholdTests(unittest.TestCase):
    def request(self):
        import research_queue as q
        r=q.load(q.ROOT/'reports/work/STREAM521/sdk521-geometry-01-request.json')
        r['candidateConfidence']=0.10
        r['models']['scoped']=dict(r['models']['general'])
        return r

    def test_matched_threshold_and_default(self):
        from sdk_geometry506 import prepare
        r=self.request()
        self.assertEqual(len(prepare(r)[1]),7)
        del r['candidateConfidence']
        self.assertEqual(len(prepare(r)[1]),7)

    def test_invalid_threshold_model_and_missing_cache(self):
        from sdk_geometry506 import prepare
        for change,error in [
            (lambda r:r.update(candidateConfidence=.05),'sdk_candidate_confidence'),
            (lambda r:r['models']['scoped'].update(sha256='0'*64),'sdk_threshold_model_changed'),
            (lambda r:r.pop('cachedGeneral'),'sdk_threshold_baseline_required'),
        ]:
            r=self.request();change(r)
            with self.assertRaisesRegex(ValueError,error):prepare(r)

    def test_cache_configuration_stays_strict(self):
        from unittest.mock import patch
        import research_queue as q
        from sdk_geometry506 import prepare
        original=q.load
        r=self.request()
        target=r['cachedGeneral'][0]['path']
        def altered(path):
            d=original(path)
            if str(path).endswith(target):d['configuration']['minConfidence']=.10
            return d
        with patch('sdk_geometry506.q.load',side_effect=altered):
            with self.assertRaisesRegex(ValueError,'sdk_cache_identity'):prepare(r)

    def test_matched_spec_has_unique_evidence_paths(self):
        from unittest.mock import patch
        import research_queue as q
        from sdk_geometry506 import build
        original=q.load
        path=q.ROOT/'reports/work/STREAM521/sdk521-geometry-01-request.json'
        r=self.request()
        with patch('sdk_geometry506.q.load',side_effect=lambda p:r if p==path else original(p)):
            spec=build(path)
        q.validate(spec)
        self.assertEqual(len(spec['evidence']['reads']),len(set(spec['evidence']['reads'])))

class ResolutionTests(ThresholdTests):
    def request(self):
        r=super().request();r.pop('candidateConfidence');r['candidateImageSize']=960
        return r

    def test_resolution_rejects_multiple_factors(self):
        from sdk_geometry506 import prepare
        r=self.request();r['candidateConfidence']=.10
        with self.assertRaisesRegex(ValueError,'sdk_resolution_factor'):prepare(r)
        r=self.request();r['candidateImageSize']=640
        with self.assertRaisesRegex(ValueError,'sdk_resolution_factor'):prepare(r)
        r=self.request();r['models']['scoped']['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'sdk_resolution_baseline'):prepare(r)

    def test_resolution_runtime_uses_requested_size_and_retains_cache(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        import research_queue as q
        import sdk_geometry506 as m
        from experiment_templates import pin
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build') as directory:
            root=Path(directory);request=self.request();request['id']='resolution-test'
            path=root/'request.json';q.save(path,request)
            job=root/'jobs'/request['id'];out=job/'attempts/1/out';out.mkdir(parents=True)
            q.save(job/'spec.json',m.build(path))
            def infer(model,frames,confidence,size,destination):
                self.assertEqual((confidence,size),(.25,960))
                for i,ref in enumerate(request['cachedGeneral']):
                    raw=q.load(q.ROOT/ref['path']);raw['configuration']['imageSize']=size
                    raw['runtime']['detector']['imageSize']=size
                    q.save(destination/('%03d.json'%i),raw)
                return raw['runtime']['detector']
            with patch.object(m,'OUT',out),patch.object(m.inference,'pytorch',side_effect=infer) as invoke:
                m.run()
            self.assertEqual(invoke.call_count,1)
            result=q.load(out/'benchmark_summary.json')
            self.assertEqual(result['comparison']['changedFactor'],'resolution')
            self.assertEqual(result['models']['scoped']['identity']['imageSize'],960)
            self.assertEqual(result['models']['general']['identity']['imageSize'],1280)
            self.assertEqual(result['candidateLostSuccesses'],0)

    # Parent tests exercise confidence-only requests, which have different gates.
    def test_matched_threshold_and_default(self):
        from sdk_geometry506 import prepare
        self.assertEqual(len(prepare(self.request())[1]),7)
    def test_invalid_threshold_model_and_missing_cache(self):
        from sdk_geometry506 import prepare
        r=self.request();r.pop('cachedGeneral')
        with self.assertRaisesRegex(ValueError,'sdk_resolution_baseline'):prepare(r)
