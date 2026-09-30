"""Reproduce representative diagnostics from saved scores only; never loads a model."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
from focus_dataset_contract import digest
from focus_mixed_assembly import checked, reference
from focus_representative_validation import summarize, STRATA
from focus_surface_intake import require, fresh, write


def errors(rows,predictions):
    values={p['id']:p['probability'] for p in predictions}
    # Reuse the actual metrics implementation to reject missing/duplicate/bad scores.
    summarize(rows,predictions)
    result=[]
    for r in rows:
        score=values[r['id']]
        if (score>=.85)!=bool(r['label']):
            result.append(dict(id=r['id'],kind='miss' if r['label'] else 'false-positive',
                               score=score,stratum=r.get('stratum'),image=r['image'],
                               crop=r['crop'],bounds=r['bounds']))
    return sorted(result,key=lambda r:(r['kind'],r['score'] if r['kind']=='miss' else -r['score'],r['id']))


def build(protocol,comparison,real,output):
    output=fresh(output)
    p=json.loads(protocol.read_text());c=json.loads(comparison.read_text());realdata=json.loads(real.read_text())
    require(c['protocol']==reference(protocol),'changed_protocol')
    frozen=dict(p);seal=frozen.pop('seal',None)
    require(digest(frozen)==seal and p['role']=='development-diagnostics','changed_or_protected_protocol')
    all_errors={};lines=['# Representative focus validation — 2026-09-29','',
        'Fixed threshold **0.85**. Native bounds; production16%/256 crops. Both frozen models scored312/312 inputs; no failed predictions.',
        'Paired targets and complete-frame competitors are separate correlated populations, not624 independent examples.',
        'These are development diagnostics; no independent qualification or export parity claim.','',
        '## SYNTH05 native-fixture diagnostic','',
        '| Stratum | Positive / paired negative support | Shipped TP / FP | FDR-010 TP / FP |',
        '|---|---:|---:|---:|']
    verified={}
    for model,result in c['results'].items():
        require(result['state']=='complete' and not result['invalidPredictions'] and not result['unscored'],'incomplete_scores')
        values={x['id']:x for x in result['predictions']}
        summarize(p['samples'],result['predictions'])
        for kind in ('pair','competition'):
            rows=[r for r in p['samples'] if r['kind']==kind]
            policy=None if kind=='pair' else dict(populations=dict(candidate=[r['id'] for r in rows],auxiliary=[],unresolved=[]),frames=p['frames'])
            measured=summarize(rows,[values[r['id']] for r in rows],policy)
            require(measured==result['subsets'][kind],'published_metrics_not_reproduced')
        for row in p['samples']:
            for key in ('image','crop'):
                ref=row[key]
                if ref['path'] not in verified:checked(ref);verified[ref['path']]=ref
        all_errors[model]=errors(p['samples'],result['predictions'])
    for s in STRATA[:4]:
        a=c['results']['shipped']['subsets']['pair']['strata'][s];b=c['results']['fdr010']['subsets']['pair']['strata'][s]
        lines.append(f"| {s} | {a['positiveSupport']} / {a['negativeSupport']} | {a['tp']} / {a['fp']} | {b['tp']} / {b['fp']} |")
    lines+=['','Complete-frame selection (50 frames):']
    for m,r in c['results'].items():
        frame=r['subsets']['competition']['metrics']['completeFrameSelection']
        lines.append(f"- {m}: {json.dumps(frame['counts'],sort_keys=True)}; absent outcomes=0.")
    lines+=['','The candidate handles the18 native button/tab/row cases but misses all32 artwork positives. Its75% macro recall hides a zero artwork stratum; it is not a pass.',
        'The shipped model has7 unique-correct,4 wrong and39 no-focus frames. FDR-010 has18 unique-correct,0 wrong and32 no-focus.',
        'All native selected-but-unfocused tab competitors remain negative. Bright selection is not focus.',
        'One reported Simulator/OS, dark theme, seed7, shared procedural ancestry: no independent-source claim.','',
        '## Retained real-screen transfer','',
        'All362 saved scores per model were checked;315 settled candidate crops enter the descriptive table.47 remain outside that population. Preserve per-benchmark exclusions and complete-frame coverage.',
        '| Stratum | Positive / negative support | Shipped TP / FP | FDR-010 TP / FP |','|---|---:|---:|---:|']
    for s in STRATA:
        a=realdata['combinedSettledDiagnostics']['shipped']['strata'][s];b=realdata['combinedSettledDiagnostics']['fdr010']['strata'][s]
        lines.append(f"| {s} | {a['positiveSupport']} / {a['negativeSupport']} | {a['tp']} / {a['fp']} | {b['tp']} / {b['fp']} |")
    lines+=['','Four-stratum macro recall: shipped50.89%, FDR-0109.23%. Real buttons/tabs both0 for FDR-010, despite synthetic success. Unknown independence and tiny support preclude broad performance claims.',
        'The24-frame benchmark retains13 complete settled frames: shipped3 unique-correct, candidate2. The separate eight-frame benchmark is not silently added to the complete-frame denominator.',
        'The companion `real-transfer.json` preserves each benchmark, exclusions, incomplete frame states and source bindings.','',
        '## Decision','',
        '**Do not export FDR-010 or repeat unchanged training.** Keep shipped unchanged. Collect missing artwork/focus-mechanism/context diversity and genuine OS transfer references; retain buttons/tabs/rows for nonregression.',
        'Backend differences: shipped CoreML CPU; candidate PyTorch CPU. This is not export parity, and elapsed times are not directly comparable latency.',
        'Ranked machine-readable misses and false positives are in `errors.json`; every entry binds exact sample ID, original image, bounds and qualified crop. No new crop or image inference was used to render this report.']
    output.mkdir(parents=True)
    write(output/'errors.json',dict(version='focus-representative-errors-v1',protocol=reference(protocol),comparison=reference(comparison),models=all_errors))
    (output/'metrics.md').write_text('\n'.join(lines)+'\n')
    selection=dict(version='focus-next-selection-contract-v1',status='proposal-requires-separate-training-approval',
        inputs=[reference(protocol),reference(comparison),reference(real)],threshold=.85,
        cohortRole='development-exposed',independentQualification=False,trainingAdmission=False,
        freezeBeforeNextTraining=True,retentionRule='Preserve existing nine-pair18/18 floor; no eligible epoch means no checkpoint.',
        proposedSelection='Among retention-eligible epochs, minimize four-stratum equally weighted BCE on a separately approved representative selection set, with equal source-group weighting within each stratum.',
        requiredSupport=['buttons','tabs','artwork','rows'],missingSupport='Blocks selection; never substitute zero loss.',
        reviewBeforeExecution=['Freeze exact selection membership and source-group assignments; current frozen cohorts are diagnostic references, not automatically wired into trainer.',
            'Approve representative selection policy and separate untouched qualification source plan.',
            'Preserve real per-stratum recall/FP, complete-frame decisions and existing production gates; aggregate loss alone cannot authorize release.'],
        scope='No trainer change, new run, challenge scoring, export or promotion.')
    selection['seal']=digest(selection);write(output/'next-selection.json',selection)
    print(json.dumps(dict(metricReproduction='exact',errorCounts={k:len(v) for k,v in all_errors.items()})))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('protocol','comparison','real','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();build(**vars(a))
