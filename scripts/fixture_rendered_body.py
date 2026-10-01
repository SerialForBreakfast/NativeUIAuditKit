"""Validate TTR's additive rendered-body v1 evidence, never infer geometry."""
import math


def validate(body, size, element_id, generation):
    def require(ok, reason):
        if not ok:
            raise ValueError('rendered_body:'+reason)

    def vector(value):
        return (isinstance(value, list) and len(value) == 4 and
                all(type(v) in (int, float) and math.isfinite(v) for v in value))

    if body is None:
        return None  # Legacy absence is unavailable, not measured.
    require(isinstance(body, dict), 'object')
    require(type(body.get('version')) is int and body['version'] == 1 and
            body.get('role') == 'rendered_control_body' and
            body.get('coordinate_space') == 'image_top_left_pixels', 'protocol')
    require(body.get('element_id') == element_id and
            type(body.get('generation')) is int and body['generation'] == generation, 'identity')
    require(body.get('source') in ('uikit_focused_frame_guide',
            'native_body_presentation_layer', 'unsupported_native_control'), 'source')
    if body.get('availability') == 'unavailable':
        require(body.get('unavailable_reason') in ('unsupported_native_control',
                'not_rendered', 'non_affine_transform', 'projection_failed'), 'unavailable_or_moving')
        require(all(body.get(k) is None for k in ('full_pixel_bounds', 'visible_pixel_bounds',
                'visible_normalized_bounds', 'clipping')), 'unavailable_geometry')
        return None
    require(body.get('availability') == 'measured' and body.get('unavailable_reason') is None
            and body['source'] != 'unsupported_native_control', 'availability')
    f = body.get('full_pixel_bounds')
    require(vector(f) and f[2] > 0 and f[3] > 0, 'full_bounds')
    p, n = body.get('visible_pixel_bounds'), body.get('visible_normalized_bounds')
    if body.get('clipping') == 'fully_clipped':
        require(p is None and n is None, 'fully_clipped_geometry')
        return None
    require(vector(p) and vector(n), 'visible_bounds')
    x, y, w, h = p
    require(x >= 0 and y >= 0 and w > 0 and h > 0 and
            x+w <= size[0]+.01 and y+h <= size[1]+.01, 'visible_bounds')
    require(x >= f[0]-.01 and y >= f[1]-.01 and
            x+w <= f[0]+f[2]+.01 and y+h <= f[1]+f[3]+.01, 'containment')
    require(0 <= n[0] < n[2] <= 1.00001 and 0 <= n[1] < n[3] <= 1.00001, 'normalized')
    projected = [n[0]*size[0], n[1]*size[1], (n[2]-n[0])*size[0], (n[3]-n[1])*size[1]]
    require(all(abs(a-b) <= .01 for a, b in zip(p, projected)), 'normalization')
    differs = any(abs(a-b) > .01 for a, b in zip(f, p))
    require(body.get('clipping') == ('partially_clipped' if differs else None), 'clipping')
    return p
