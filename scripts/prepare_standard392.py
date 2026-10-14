"""Prepare matched Standard requests without starting capture or changing the queue."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import uuid


def prepare(root, helper, output, project=None):
    root, output = Path(root).resolve(), Path(output).resolve()
    # Preserve the helper name. The shared executable uses argv[0] to select CLI mode.
    helper = Path(helper).absolute()
    if not output.is_relative_to(root) or output.exists():
        raise ValueError('fresh_project_output_required')
    output.mkdir(parents=True)
    rows = []
    for label, source in [('movement', 'NX02-a-directional.json'), ('content', 'NX02-b-content-only.json')]:
        path = root/'docs/experiment-graph-v1-requests'/source
        request = copy.deepcopy(json.loads(path.read_text()))
        request.update(request_id=str(uuid.uuid5(uuid.NAMESPACE_URL, 'standard392-p02-'+label)),
                       seeds=[392001, 392002], positions=[0], backgrounds=['dark'], artwork_styles=['city'])
        request['budget'].update(max_cases=2, max_wall_clock_seconds=600, max_retained_bytes=100_000_000)
        # Preserve the producer's calibration-only contract. These are not training examples.
        if request['source_role'] != 'calibration':
            raise ValueError('unexpected_source_role')
        (output/(label+'-request.json')).write_text(json.dumps(request, indent=2)+'\n')
        command = [str(helper)] + (['--project', str(project)] if project else [])
        result = subprocess.run(command + ['--json', 'campaign', 'plan', '--request-json', json.dumps(request)],
                                text=True, capture_output=True, timeout=60)
        (output/(label+'-plan.json')).write_text(result.stdout)
        (output/(label+'-plan.stderr')).write_text(result.stderr)
        try:
            reply = json.loads(result.stdout)
        except json.JSONDecodeError:
            reply = {}
        rows.append(dict(id=label, exitCode=result.returncode,
                         accepted=result.returncode == 0 and reply.get('success') is True,
                         sourceSHA256=hashlib.sha256(path.read_bytes()).hexdigest(),
                         requestSHA256=hashlib.sha256((output/(label+'-request.json')).read_bytes()).hexdigest()))
    report = dict(version='standard392-producer-preparation-v1', rows=rows,
        helperSHA256=hashlib.sha256(helper.read_bytes()).hexdigest(), captureStarted=False,
        trainingEligible=False, sourceRole='calibration',
        groups=['standard392-p02-392001', 'standard392-p02-392002'],
        requirements=['Verify Standard OS state before capture.',
                      'Keep movement and content counterparts in the same ancestry group.',
                      'Verify matching geometry and observed focus before comparison.',
                      'Check current target ownership, storage and restoration before dispatch.',
                      'Do not train on these calibration-only requests.'],
        decision='Use the pilot to verify native movement versus content changes before larger production.')
    (output/'preparation.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--root', required=True)
    p.add_argument('--helper', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--project', help='Use the workspace shown by the running TTR app.')
    a = p.parse_args()
    prepare(a.root, a.helper, a.output, a.project)
