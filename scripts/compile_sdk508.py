"""Compile SDK comparisons without submitting or executing jobs."""
import argparse
from pathlib import Path
import research_queue as q
import sdk_campaign508 as campaign
import sdk_report508 as report


def compile_batch(requests, output, report_id):
    specs = [campaign.build(Path(p)) for p in requests]
    q.require(len(specs) >= 2, 'sdk_batch_requires_two_campaigns')
    q.require(len({s['id'] for s in specs}) == len(specs), 'sdk_batch_duplicate_id')
    combined = report.build(specs)
    combined['id'] = report_id
    q.require(report_id not in {s['id'] for s in specs}, 'sdk_batch_duplicate_id')
    specs.append(combined)
    for spec in specs:
        q.validate(spec)
    output = Path(output).resolve()
    q.require(output.is_relative_to(q.ROOT.resolve()), 'sdk_batch_output_outside_project')
    q.require(not output.exists(), 'sdk_batch_output_exists')
    output.mkdir(parents=True)
    for spec in specs:
        q.save(output / (spec['id'] + '.json'), spec)
    return [s['id'] for s in specs]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('requests', nargs='+')
    parser.add_argument('--output', required=True)
    parser.add_argument('--report-id', required=True)
    args = parser.parse_args()
    print('\n'.join(compile_batch(args.requests, args.output, args.report_id)))
