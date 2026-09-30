"""Offline matched-trial plan and delivered-bundle review. No capture or models."""
import argparse
from collections import Counter
from pathlib import Path
from PIL import Image, ImageDraw

import focus_offline_diagnosis as o
import focus_geometry_diagnostic as geometry
from ttr_focus_manifest import derive as intake
from harvest_sidecar_v2 import recipe_hash


def proposal(path, expected):
    path = o.local(path)
    o.require(o.ref(path)['sha256'] == expected, 'changed_proposal')
    doc = o.read(path)
    cases = doc['cases']
    o.require(doc['schema_version'] == 1 and len(cases) == 8 and doc['capture_pairs'] == 64,
              'unsupported_trial')
    o.require(len({c['case_id'] for c in cases}) == 8, 'duplicate_case')
    for c in cases:
        o.require(c['split'] == 'calibration' and c['recipe']['appearance']['artwork']['split'] == 'calibration',
                  'protected_role')
        o.require(c['recipe_sha256'] == recipe_hash(c['recipe']), 'changed_recipe')
        ids = c['all_target_ids']
        o.require(len(ids) == len(set(ids)) == c['capture_pairs'] == c['recipe']['element_count'], 'target_count')
        common = c['common_target_pairs']
        o.require(len(common) == 4 and len({r['target_id'] for r in common}) == 4
                  and all(r['target_id'] in ids and r['reference_competitor_id'] in ids for r in common), 'common_membership')
    o.require(sum(c['capture_pairs'] for c in cases) == 64, 'trial_total')
    # Recompute density correspondence rather than trusting the supplied booleans.
    density = []
    for small in [c for c in cases if c['capture_pairs'] == 4]:
        canvas = small['recipe']['appearance']['canvas']
        art = small['recipe']['appearance']['artwork']
        matches = [c for c in cases if c['capture_pairs'] == 12
                   and c['recipe']['appearance']['canvas']['showLabels'] == canvas['showLabels']
                   and c['recipe']['appearance']['artwork'].get('palette') == art.get('palette')]
        o.require(len(matches) == 1, 'missing_or_ambiguous_density_partner')
        big = matches[0]; by_id = {r['target_id']:r for r in big['common_target_pairs']}
        for r in small['common_target_pairs']:
            other = by_id[r['target_id']]
            same = r['reference_competitor_id'] == other['reference_competitor_id']
            o.require(r['density_comparison_competitor_matched'] is same and
                      other['density_comparison_competitor_matched'] is same, 'incorrect_match_flag')
            density.append(dict(small=small['case_id'], dense=big['case_id'], target=r['target_id'],
                competitorMatched=same, status='planned-not-captured', sizeAndPositionControlled=False))
    o.require(sum(r['competitorMatched'] for r in density) == 8, 'matched_comparison_count')
    return doc, density


def sheet(output, number, pair, reports, directories, manifest):
    page = Image.new('RGB', (1100, 680), '#202020'); draw = ImageDraw.Draw(page)
    draw.text((15,10), f"{number:03d} {pair['elementID']} / {pair['pair_id']} - DIAGNOSTIC, NOT APPROVED", fill='white')
    for col, state in enumerate(('focused', 'unfocused')):
        with Image.open(o.checked(dict(path=str((o.ROOT/manifest['sourceRoot']/pair['frames'][state]['path']).relative_to(o.ROOT)),
                                      sha256=pair['frames'][state]['sha256']))) as im:
            preview = im.convert('RGB'); original=im.size; preview.thumbnail((530,280))
            overlay=ImageDraw.Draw(preview)
            for role,color in ((geometry.WRAPPER,'cyan'),(geometry.ROLE,'magenta')):
                row=next(r for r in reports[role]['records'] if r['binding']['pairID']==pair['pair_id'] and r['binding']['state']==state)
                box=row['binding']['selectedBounds']
                if box:
                    x,y,w,h=box;sx=preview.width/original[0];sy=preview.height/original[1]
                    overlay.rectangle((x*sx,y*sy,(x+w)*sx,(y+h)*sy),outline=color,width=2)
            page.paste(preview,(col*550+10,45))
        draw.text((col*550+10,30), state+' native observation', fill='white')
        for i, role in enumerate((geometry.WRAPPER, geometry.ROLE)):
            row = next(r for r in reports[role]['records'] if r['binding']['pairID'] == pair['pair_id'] and r['binding']['state'] == state)
            x,y = col*550+10+i*270,370
            draw.text((x,y-30), 'wrapper' if i==0 else 'nominal artwork layout', fill='white')
            if row['status'] == 'rendered':
                with Image.open(directories[role]/row['crop']['path']) as im: page.paste(im.convert('RGB'),(x,y))
            else: draw.text((x,y), row['status']+': '+str(row['reason']), fill='orange')
    name=f'{number:03d}.png'; page.save(output/name); return name


def run(proposal_path, expected, delivery_path, output):
    output=o.local(output); o.require(not output.exists(), 'output_collision')
    doc, comparisons=proposal(proposal_path, expected)
    delivery=o.read(o.local(delivery_path)) if delivery_path else dict(version='focus-trial-delivery-v1',cases=[])
    o.require(delivery['version']=='focus-trial-delivery-v1', 'unsupported_delivery')
    cases={c['case_id']:c for c in doc['cases']}
    supplied=delivery['cases']
    o.require(len({c['caseID'] for c in supplied}) == len(supplied) and
              all(c['caseID'] in cases for c in supplied), 'duplicate_or_unexpected_delivery')
    deliveries={c['caseID']:c for c in supplied}
    output.mkdir(parents=True)
    report=dict(version='focus-trial-review-v1', proposal=o.ref(o.local(proposal_path)),
        delivery=o.ref(o.local(delivery_path)) if delivery_path else None,
        trainingAdmission=False, captureExecuted=False, modelExecution=False, liveQualified=False,
        cases=[], densityComparisons=comparisons)
    for number,(name,case) in enumerate(cases.items(),1):
        record=dict(caseID=name,expectedPairs=case['capture_pairs'],status='missing_delivery',targets=[])
        report['cases'].append(record)
        if name not in deliveries: continue
        destination=output/f'case-{number:02d}'; destination.mkdir()
        try:
            spec=deliveries[name]
            index=o.checked(spec['index']); receipt=o.checked(spec['receipt'])
            o.require(index.name=='dataset-index.json' and receipt.name=='harvest-receipt.json'
                      and receipt.parent==index.parent, 'receipt_bundle_binding')
            preview=intake(index.parent,destination/'intake',name,'matched-trial:'+expected,test_only=True,dry_run=True)
            pairs=preview['pairs']
            o.require(len(pairs)==case['capture_pairs'] and {p['elementID'] for p in pairs}==set(case['all_target_ids']),
                      'incomplete_or_changed_targets')
            for p in pairs:
                o.require(p['original_split']=='validation', 'protected_or_wrong_split')
                for key in ('focusedScene','baselineScene'):
                    scene=p['observationBinding'][key]
                    o.require(recipe_hash(scene['recipe'])==case['recipe_sha256'], 'recipe_not_proposed')
                    o.require({e['element_id'] for e in scene['elements']}==set(case['all_target_ids']), 'incomplete_competitor_set')
                i=case['all_target_ids'].index(p['elementID'])
                competitor=case['all_target_ids'][(i+1)%len(case['all_target_ids'])]
                o.require(p['frames']['unfocused']['observedFocusID']==competitor, 'changed_competitor')
            manifest=intake(index.parent,destination/'intake',name,'matched-trial:'+expected,test_only=True)
            path=destination/'intake/focus_dataset_manifest.json'
            reports={}; directories={}
            for role in (geometry.WRAPPER,geometry.ROLE):
                directories[role]=destination/role
                reports[role]=geometry.derive(path,geometry.sha(path),directories[role],role)
            common={r['target_id']:r for r in case['common_target_pairs']}
            for n,p in enumerate(manifest['pairs'],1):
                r=common.get(p['elementID'])
                record['targets'].append(dict(elementID=p['elementID'],pairID=p['pair_id'],
                    commonTarget=r is not None, competitorMatchedDensity=r['density_comparison_competitor_matched'] if r else False,
                    geometry={role:[dict(state=row['binding']['state'],bounds=row['binding']['selectedBounds'],
                                         status=row['status'],reason=row['reason']) for row in reports[role]['records']
                                    if row['binding']['pairID']==p['pair_id']] for role in reports},
                    review='pending', page=sheet(destination,n,p,reports,directories,manifest)))
            record.update(status='prepared_for_review', pairCount=len(pairs),
                manifest=o.ref(path),
                geometryCounts={k:v['counts'] for k,v in reports.items()})
            o.checked(spec['index']);o.checked(spec['receipt'])
        except (OSError,ValueError,KeyError,TypeError,StopIteration) as e:
            record.update(status='failed',error=str(e))
    proposal(proposal_path,expected)
    if delivery_path:o.checked(report['delivery'])
    ready={r['caseID'] for r in report['cases'] if r['status']=='prepared_for_review'}
    for comparison in comparisons:
        if {comparison['small'],comparison['dense']} <= ready:
            comparison['status']='ready_for_visual_review' if comparison['competitorMatched'] else 'unmatched_competitor_diagnostic_only'
    report['caseCounts']=dict(Counter(r['status'] for r in report['cases']))
    report['allCasesPrepared']=all(r['status']=='prepared_for_review' for r in report['cases'])
    o.write(output/'review.json',report)
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--proposal',required=True,type=Path);p.add_argument('--proposal-sha256',required=True)
    p.add_argument('--delivery',type=Path);p.add_argument('--output',required=True,type=Path)
    a=p.parse_args()
    r=run(a.proposal,a.proposal_sha256,a.delivery,a.output)
    print(r['caseCounts'])
    raise SystemExit(0 if r['allCasesPrepared'] else 2)
