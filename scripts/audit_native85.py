"""Coverage of retained native captures; never data admission or model evaluation."""
import argparse
from collections import Counter
from pathlib import Path
import human_annotation_review as h
from inventory_transition_sources import observed_scroll
from intake_native76 import verify_selection, collection_selection


def summarize(rows):
    h.require(len({r['id'] for r in rows}) == len(rows), 'duplicate_case')
    counts = lambda key: dict(Counter(str(r[key]) for r in rows))
    pixels = Counter(p for r in rows for p in r['pixels'])
    boxes = [b for r in rows for b in r['focusedBodies']]
    return dict(pairs=len(rows), kinds=counts('kind'), themes=counts('theme'),
        styles=counts('style'), observedScroll=counts('scroll'),
        uniquePixels=len(pixels), repeatedPixelOccurrences=sum(n-1 for n in pixels.values()),
        measuredFocusedBodies=len(boxes), smallFocusedBodies=sum(max(b[2:]) < 100 for b in boxes),
        trainingEligible=False, independentEvaluationEligible=False)


def run(output):
    out=h.fresh(output)
    rich=h.ROOT/'reports/work/NATIVE-INTAKE-76/received/ttr-native-rich24-20261003-r1'
    collection=h.ROOT/'reports/work/NATIVE-INTAKE-83/received/ttr-native-collection-36-20261003'
    verify_selection(rich,h.read(rich/'qualified-cases.json'))
    verify_selection(collection,collection_selection(collection),expected_pairs=36)
    paths=[('table-r2','native76-intake-v1'),('collection-r2','native83-inspection-v1')]
    rows=[];sources=[]
    for folder,version in paths:
        source=h.ROOT/'reports/work/NATIVE-84'/folder/'intake.json'
        report=h.sealed(source,version);sources.append(h.ref(source))
        for row in report['results']:
            if row.get('lane')=='table12':continue
            h.require(row['consumer']=='passed-inspection-only','unqualified_intake')
            for image in row['images']:h.checked(h.ROOT,{k:image[k] for k in ('path','sha256')})
            bundle=h.local(h.ROOT/row['images'][0]['path']).parent
            transition=bundle/'transition-case.json'
            if transition.exists():
                raw=h.read(transition)
                scenes=[e['capture_endpoint']['before_scene'] for e in raw['endpoints']]
                scroll=observed_scroll(raw)[0];kind='recorded-action'
                evidence=[h.ref(transition)]
            else:
                metas=list(bundle.glob('*_metadata.json'));h.require(len(metas)==1,'metadata_count')
                raw=h.read(metas[0]);scenes=[raw['baseline_scene'],raw['focused_scene']]
                scroll=None;kind='appearance-pair';evidence=[h.ref(metas[0])]
            bodies=[]
            for scene in scenes:
                selected=[e for e in scene['elements'] if e['element_id']==scene['focused_element_id']]
                h.require(len(selected)==1 and selected[0]['is_focused'] is True,'measured_focus')
                body=selected[0].get('rendered_body_geometry',{})
                h.require(body.get('availability')=='measured','body_unmeasured')
                bodies.append(body['visible_pixel_bounds'])
            recipe=scenes[0]['recipe'];canvas=recipe['appearance']['canvas']
            rows.append(dict(id=row['caseID'],kind=kind,theme=recipe['theme'],
                style=canvas.get('collectionStyle','rich-table'),scroll=scroll,
                recipeHash=recipe['recipe_hash'],focusedBodies=bodies,evidence=evidence,
                pixels=[i['decodedSHA256'] for i in row['images']],
                sourceRole='calibration',ancestry='fixture_procedural_renderer_v1'))
    h.require(len(rows)==60,'expected_sixty')
    report=dict(version='native85-coverage-v1',**h.FLAGS,sources=sources,
        membershipSHA256=h.digest(rows),members=rows,summary=summarize(rows),
        limitations=['Declared themes are not a visual quality score.',
            'Appearance pairs do not supply directional-action or no-scroll labels.',
            'All members share Fixture ancestry; none becomes independent final evaluation.',
            'Geometry is measured visible control-body bounds, not atomic framebuffer attestation.'])
    out.mkdir(parents=True);h.write(out/'coverage.json',report,sealed=True)
    print(report['summary'])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True)
    run(parser.parse_args().output)
