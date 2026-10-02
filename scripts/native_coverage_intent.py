"""Producer-neutral coverage intent; not a TTR dispatch request or admission."""
import argparse
import itertools
import human_annotation_review as h

FAMILIES=('nativeArtwork','nativeWideButton','nativeListRow')


def intent():
    cases=[]
    for family in FAMILIES:
        for theme,density,content,position in itertools.product(range(2),repeat=4):
            # Four development configurations per family, retaining both themes/densities.
            role='development' if content==(theme^density) and position==density else 'training_candidate'
            cases.append(dict(id=f'{family}-{theme}{density}{content}{position}',family=family,
                theme=('dark','light')[theme],density=('sparse','dense')[density],
                contentBrightness=('dark','bright')[content],targetPosition=('interior','edge')[position],
                proposedRole=role,seed=330000+len(cases),
                requiredMeasuredAspect=[1.5,1.8] if family=='nativeArtwork' else [7,11.5]))
    return dict(version='native-coverage-intent-v1',**h.FLAGS,dispatchable=False,
        producerSchemaMapping='pending',cases=cases,caseCount=48,screenshotCount=96,
        annotationSource='observed native focus and per-frame rendered ordinary body bounds',
        requiredEvidence=['actual native component class and effect ancestry','ordinary profile and OS/renderer version',
            'settled screenshot/focus/geometry binding','same content within each focus pair',
            'actual growth in both axes','full and visible bounds with clipping/occlusion',
            'common reference window plus neighbor intersections','stable control identity',
            'no-op and content-only negatives in separate transition ledger'],
        splitCaveat='Proposed36/12 only; no admission. Related renderer/layout/source groups remain development; not independent real-app evaluation.',
        captureAuthority='not granted by this file')


def validate(value):
    h.require(value.get('dispatchable') is False and value.get('trainingEligible') is False,'intent_only')
    cases=value['cases'];h.require(len(cases)==48 and len({c['id'] for c in cases})==48,'intent_membership')
    for family in FAMILIES:
        rows=[c for c in cases if c['family']==family]
        h.require(len(rows)==16 and sum(c['proposedRole']=='development' for c in rows)==4,'family_balance')
        axes={(c['theme'],c['density'],c['contentBrightness'],c['targetPosition']) for c in rows}
        h.require(len(axes)==16,'axis_coverage')
    return value


def run(output):
    out=h.fresh(output);out.mkdir(parents=True);value=validate(intent());value['implementation']=h.ref(__file__)
    h.write(out/'intent.json',value,sealed=True)
    lines=['# Targeted native coverage intent','',
        '48pairs /96screenshots proposed; provider field mapping and generation remain pending.',
        'This is not executable TTR request syntax. Preserve all variants together by source/layout ancestry.',
        '', '| Family | Pairs | Measured body aspect | Proposed training / development |',
        '| --- | --- | --- | --- |',
        '| Native artwork | 16 | 1.5–1.8 | 12 /4 |',
        '| Native wide button | 16 | 7–11.5 | 12 /4 |',
        '| Native list row | 16 | 7–11.5 | 12 /4 |','',
        'Each family crosses dark/light theme, sparse/dense layout, dark/bright content and interior/edge position.',
        'Requested ranges must be measured, not written into annotations. Unsupported native components stay unsupported.',
        'Edge cases are a robustness stratum; begin the model comparison with contained common windows, report clipped windows separately.',
        'Do not substitute a wide painted rectangle for a native row/button or reuse cross-layout images as focus pairs.',
        '', 'Required evidence:','']+['- '+v for v in value['requiredEvidence']]
    (out/'intent.md').write_text('\n'.join(lines)+'\n');print('48 coverage cases prepared; dispatchable=false')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True)
    run(p.parse_args().output)
