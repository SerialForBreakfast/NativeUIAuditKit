# Explicit category binding v1

Implemented BADGE-A software contract; no new model weights or training data.

## Taxonomy and identity

The frozen category_map.json categories retain IDs0–40. Taxonomy1.1 resolves that
array followed by category_map.v1.1.json's append entry, ID41 `badge`. Never sort
the resolved array. Badge means a notification/status dot or count marker, not
decorative artwork, a page indicator or an ordinary button title.

`categoryMapSHA256` hashes UTF-8 JSON of `{version,categories}`: sorted object keys,
compact comma/colon separators, ASCII escaping, no trailing newline. Categories
include all id/name/supercategory fields. It is neither a file hash nor a model hash.

| Version | Resolved taxonomy SHA256 |
|---|---|
| 1.0 | `dfc38ffe3b9ee3434f9523e5ca91a6a700fbe32a00249c5cf90cf89885a30660` |
| 1.1 | `4debce8e33bd10aade0c7b7a1c1f625c6c5db8db5af542faffc9d4ab4187beef` |

## Model manifests

Opt in with `taxonomyProfile: nativeui-category-binding-v1`, supported
`taxonomyVersion` and the corresponding `categoryMapSHA256`. A nonempty unique
subset of taxonomy labels, in model-specific channel order, plus padding is valid.
Declared confidence width equals all mapped channels, including padding. A subset
does not claim complete41/42-class coverage. Tensor indices are not category IDs.
Unknown explicit profile/kind/label or missing/wrong binding fails, without fallback.

Absent/nil profile preserves custom IDs, supplied channel maps and tolerant legacy
unknown-kind padding. Unsupported legacy labels remain filtered, including badge.
The detector applies this boundary before creating observations. Metadata validation
does not prove artifact identity, training quality or actual loaded tensor shape;
existing loaded-model checks and qualification remain separate.

## Annotation writer

Annotation1.3 explicitly declares taxonomyVersion1.1 and permits badge while retaining
every1.2 constraint. It preserves enclosing and badge boxes. The public writer throws
before creating output when badge is supplied under legacy1.0 or measured1.2. It
does not silently drop annotations or change the selected schema. Old schema files
and category-map files remain unchanged.

Tests independently derive identities from existing category files, verify complete
schema structural parity, and exercise legacy/strict decoder, actual label-conversion
caller and public writer behavior. Full native-model badge inference awaits an actual
qualified candidate. This additive enum/API needs a minor release, not retrofitting
shipped model descriptors. BADGE-B remains gated on the existing41-class milestone.
