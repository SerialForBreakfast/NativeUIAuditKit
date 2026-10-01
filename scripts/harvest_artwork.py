"""Source-pinned artwork-v1 checks, without executing producer code."""
import base64
import hashlib
import io
import json
import math
import re


def swift_json(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'),
                      allow_nan=False).replace('/', '\\/').encode()


def artwork_identity(value, require):
    fields = {'version', 'familyID', 'seed', 'split', 'motifs', 'assets'}
    require(isinstance(value, dict) and fields <= set(value) <= fields | {'palette'}, 'artwork_fields')
    require(value.get('palette') in (None, 'bright'), 'artwork_palette')
    identifier = lambda x: isinstance(x, str) and re.fullmatch(r'[A-Za-z0-9_-]{1,80}', x)
    require(type(value['version']) is int and value['version'] == 1 and
            type(value['seed']) is int and 0 <= value['seed'] < 2**64 and
            identifier(value['familyID']) and value['split'] in ('training', 'calibration', 'held-out'),
            'artwork_identity')
    motifs, assets = value['motifs'], value['assets']
    allowed = {'icon','bands','landscape','flat','linear_gradient','radial_gradient',
               'checkerboard','texture','typography','imported','emblem','cityscape'}
    require(isinstance(motifs, list) and 1 <= len(motifs) <= 10 and
            all(isinstance(m, str) and m in allowed for m in motifs) and
            len(set(motifs)) == len(motifs), 'artwork_motifs')
    require(isinstance(assets, list) and len(assets) <= 4 and
            (('imported' in motifs) == bool(assets)), 'artwork_assets')
    ids, hashes = set(), set()
    fields = {'id','familyID','sha256','width','height','png','source','creator','license',
              'attribution','redistributionAllowed','derivativesAllowed','fit',
              'transformedSHA256','preprocessing','colorSpace'}
    for a in assets:
        require(isinstance(a, dict) and set(a) == fields, 'artwork_asset_fields')
        require(identifier(a['id']) and a['id'] not in ids and a['familyID'] == value['familyID'],
                'artwork_asset_identity')
        require(all(isinstance(a[k], str) and 0 < len(a[k]) <= limit for k,limit in
                    [('source',512),('creator',256),('attribution',1024)]) and
                a['license'] in ('CC0-1.0','CC-BY-4.0','owned') and
                a['redistributionAllowed'] is True and a['derivativesAllowed'] is True,
                'artwork_rights_declaration')
        require(a['fit'] in ('fit','fill') and a['preprocessing'] == 'original_png_v1' and
                a['colorSpace'] == 'sRGB' and all(type(a[k]) is int and 1 <= a[k] <= 512
                                               for k in ('width','height')), 'artwork_geometry')
        require(isinstance(a['png'], str) and len(a['png']) <= 43692, 'artwork_png_size')
        try:
            data = base64.b64decode(a['png'], validate=True)
        except (ValueError, TypeError):
            require(False, 'artwork_png_encoding')
        h = hashlib.sha256(data).hexdigest()
        require(len(data) <= 32768 and h == a['sha256'] == a['transformedSHA256'] and
                h not in hashes, 'artwork_asset_hash')
        try:
            from PIL import Image
            with Image.open(io.BytesIO(data)) as image:
                require(image.format == 'PNG' and image.size == (a['width'],a['height']) and
                        getattr(image,'n_frames',1) == 1 and image.getexif().get(274,1) == 1,
                        'artwork_png_geometry')
                image.load()
                # Keep source color assertion separate; this intake supports explicit
                # sRGB PNG chunks, not an arbitrary unverified ICC conversion.
                require(image.info.get('srgb') in (0,1,2,3), 'artwork_png_srgb')
        except (OSError, SyntaxError) as exc:
            require(False, 'artwork_png_decode:' + type(exc).__name__)
        ids.add(a['id']); hashes.add(h)
    canonical = {k:v for k,v in value.items() if k != 'palette' or v is not None}
    return 'artwork@1:' + hashlib.sha256(swift_json(canonical)).hexdigest()


def validate_hierarchy(scene, require):
    recipe = scene['recipe']
    canvas = (recipe.get('appearance') or {}).get('canvas') or {}
    elements = scene['elements']
    presentation = canvas.get('presentation')
    if presentation != 'nested_tabs_v1':
        require(all(e.get('parent_element_id') is None for e in elements), 'unexpected_parent')
        return
    count, selected = canvas['tabCount'], canvas['selectedIndex']
    require(len(elements) == recipe['element_count'], 'hierarchy_count')
    # Producer IDs use ceil(sqrt(count)), NOT the canvas's visual column count.
    columns = min(8, max(2, math.ceil(math.sqrt(recipe['element_count']))))
    ids = [f'grid_cell_{i // columns}_{i % columns}' for i in range(recipe['element_count'])]
    by_id = {e['element_id']:e for e in elements}
    require(set(by_id) == set(ids), 'hierarchy_membership')
    parent = ids[selected]
    for index, eid in enumerate(ids):
        element = by_id[eid]
        require(element.get('parent_element_id') == (None if index < count else parent),
                'hierarchy_parent')
        # Preserve legacy exports and the producer's corrected bordered-button role.
        require(element['taxonomy_class'] in ('primaryButton', 'secondaryButton'), 'hierarchy_taxonomy')
        traits = element.get('accessibility_traits', [])
        require(isinstance(traits,list) and ('isSelected' in traits) == (index == selected),
                'hierarchy_selection')
        if canvas.get('labels') is not None:
            require(element.get('text_content') == canvas['labels'][index], 'hierarchy_label')
