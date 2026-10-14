"""Qualify the exact TTR HCF caller. Preserve every reply and cleanup result."""
import argparse
import json
from pathlib import Path
import subprocess
import time

import research_queue as q
import direct_tvos_capture as d
from focus_batch_harness import lock
from native343 import TARGET

TTR = Path.home() / 'Developer/TVTestRig'
APP = TTR/'.local-work/nuiak-hcf362/DerivedData/Build/Products/Debug/TVTestRig.app'
CLI = APP/'Contents/Helpers/aatv'


class Client:
    def __init__(self, output):
        self.output = output
        self.count = 0

    def call(self, name, *args, timeout=160):
        self.count += 1
        stem = f'{self.count:03d}-{name}'
        with (self.output/(stem+'.json')).open('x') as out, (self.output/(stem+'.stderr')).open('x') as err:
            result = subprocess.run([str(CLI), '--project', str(TTR), '--json', *args],
                                    stdout=out, stderr=err, timeout=timeout)
        doc = q.load(self.output/(stem+'.json'))
        q.require(result.returncode == 0 and doc.get('success') is True, name+':'+str(doc.get('error')))
        return next(iter(doc['data'].values()))['_0']

    def remote(self, action, session=None):
        args = ['simulator', 'remote', action, '--simulator-udid', TARGET]
        if session:
            args += ['--session', session]
        return self.call(action, *args)

    def terminal(self, receipt, desired):
        deadline = time.monotonic()+90
        while receipt['state'] != desired:
            q.require(receipt['state'] not in ('failed', 'uncertain', 'closed'), 'remote_state:'+receipt['state'])
            q.require(time.monotonic() < deadline, 'remote_deadline')
            time.sleep(1)
            receipt = self.remote('status', receipt['operationID'])
        return receipt


def run(output, normalize=False):
    q.require(not output.exists(), 'output_collision')
    output.mkdir(parents=True)
    if normalize:
        from hcf_settings368 import Client as NavigationClient
        c = NavigationClient(output)
    else:
        c = Client(output)
    session = None
    report = dict(complete=False, settingChanged=False, restoration='not_started',
                  target=TARGET, trainingEligible=False)
    with lock():
        try:
            ready = c.call('readiness', 'simulator', 'readiness', '--simulator-udid', TARGET)
            q.require(ready['can_run'] and all(r['state'] == 'clear' for r in ready['ownership']), 'target_not_clear')
            q.save(output/'fixture-before.json', d.Fixture('http://127.0.0.1:8080').snapshot())
            receipt = c.remote('connect')
            session = receipt['operationID']
            q.save(output/'session.json', receipt)
            c.terminal(receipt, 'ready')
            # Setup activates only the named Settings app on the approved Simulator.
            report['settingsActivation'] = d.run(['xcrun', 'simctl', 'launch', TARGET, 'com.apple.TVSettings'])
            value = c.call('hcf-roundtrip', 'route', 'hcf', '--desired', 'hcf', '--mode', 'roundtrip',
                           '--map-dir', str(TTR/'.local-work/nuiak-hcf362/hcf-map'),
                           '--simulator-udid', TARGET, '--session', session)
            report['route'] = value
            hcf = value['hcf']
            report['restoration'] = hcf['restoration']
            report['settingChanged'] = hcf['inputsAttempted'] > 0
            q.require(hcf['status'] == 'completed' and hcf['desiredVerified'], 'hcf_not_verified')
            q.require(hcf['observed'] == hcf['original'] and hcf['restoration'] in ('verified', 'not_required'), 'restore_not_verified')
            report['complete'] = True
        except Exception as error:
            report['error'] = str(error)
        finally:
            if session:
                try:
                    report['disconnect'] = c.terminal(c.remote('disconnect', session), 'closed')
                except Exception as error:
                    report['cleanupError'] = str(error)
                    report['complete'] = False
            try:
                # Restore the Fixture foreground after the owned session closes.
                if session and report.get('disconnect', {}).get('state') == 'closed':
                    report['fixtureActivation'] = d.run(['xcrun', 'simctl', 'launch', TARGET, d.BUNDLE])
                report['fixtureAfter'] = d.Fixture('http://127.0.0.1:8080').snapshot()['device']
                report['postflight'] = c.call('postflight', 'simulator', 'readiness', '--simulator-udid', TARGET)
            except Exception as error:
                report['postflightError'] = str(error)
                report['complete'] = False
            q.save(output/'qualification.json', report)
    print(json.dumps({k: report.get(k) for k in ('complete', 'restoration', 'error', 'cleanupError', 'postflightError')}))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    path = args.output.absolute()
    q.require(path.is_relative_to(q.ROOT) and not any(p.is_symlink() for p in [path, *path.parents]), 'output_boundary')
    raise SystemExit(0 if run(path)['complete'] else 1)
