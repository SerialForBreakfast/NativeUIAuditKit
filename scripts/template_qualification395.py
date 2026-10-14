"""Run fixed software checks through the queue. Do not claim model accuracy."""
import os
import subprocess
import sys
import research_queue as q

OUT = None
SUITES = {
    'contracts': ['test_templates395', 'test_experiment_templates'],
    'native-dispatch': ['test_template_native395', 'test_screenshot395'],
    'inference-contracts': ['test_template_inference395', 'test_focus_export_parity'],
}


def run():
    spec = q.load(OUT.parents[2] / 'spec.json')
    suite = spec['qualificationSuite']
    q.require(suite in SUITES, 'unknown_qualification_suite')
    for ref in spec['inputs']:
        q.require(q.digest(q.local_path(q.ROOT, ref['path'])) == ref['sha256'], 'changed_test_input')
    cache = OUT / 'cache'
    cache.mkdir()
    env = dict(os.environ, PYTHONPATH=str(q.MODULES), PYTHONDONTWRITEBYTECODE='1', TMPDIR=str(cache))
    result = subprocess.run([sys.executable, '-m', 'unittest', '-v', *SUITES[suite]],
                            cwd=q.ROOT, env=env, capture_output=True, text=True, timeout=300)
    q.save(OUT / 'qualification.json', dict(
        version='template-software-qualification-v1', suite=suite,
        passed=result.returncode == 0, modelAccepted=False,
        stdout=result.stdout[-12000:], stderr=result.stderr[-24000:],
        limitation='Stubs test contracts and failure handling. They do not qualify native effects or model accuracy.'))
    q.require(result.returncode == 0, 'software_qualification_failed')
    q.save(OUT / 'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path='qualification.json', sha256=q.digest(OUT / 'qualification.json'))]))
