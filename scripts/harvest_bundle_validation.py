"""Fail-closed offline validator/normalizer for harvest-compatibility-v1."""
from __future__ import annotations
import hashlib, json, math, struct, zlib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
KNOWN = {x["name"] for x in json.loads((ROOT / "Research/schemas/category_map.json").read_text())["categories"]}
LIMIT_FILE = 32 * 1024 * 1024
LIMIT_TOTAL = 256 * 1024 * 1024

class HarvestValidationError(ValueError): pass

def _read(root: Path, name: str) -> bytes:
    p = root / name
    if not name or Path(name).name != name or p.is_symlink() or not p.is_file(): raise HarvestValidationError("unsafe_or_invalid_manifest")
    data = p.read_bytes()
    if len(data) > LIMIT_FILE: raise HarvestValidationError("invalid_image")
    return data

def _json(root: Path, name: str) -> Any:
    try: return json.loads(_read(root, name))
    except (UnicodeDecodeError, json.JSONDecodeError) as e: raise HarvestValidationError("unsafe_or_invalid_manifest") from e

def _png_size(data: bytes) -> tuple[int, int]:
    """Decode enough PNG structure to prove a non-interlaced image is readable."""
    if not data.startswith(b"\x89PNG\r\n\x1a\n"): raise HarvestValidationError("invalid_image")
    offset=8; width=height=bit_depth=color_type=None; chunks=[]; ended=False
    while offset < len(data):
        if offset + 12 > len(data): raise HarvestValidationError("invalid_image")
        length=struct.unpack(">I",data[offset:offset+4])[0]; kind=data[offset+4:offset+8]; start=offset+8; end=start+length
        if end + 4 > len(data) or zlib.crc32(kind+data[start:end]) & 0xffffffff != struct.unpack(">I",data[end:end+4])[0]: raise HarvestValidationError("invalid_image")
        body=data[start:end]; offset=end+4
        if kind == b"IHDR":
            if width is not None or len(body) != 13: raise HarvestValidationError("invalid_image")
            width,height,bit_depth,color_type,compression,filter_method,interlace=struct.unpack(">IIBBBBB",body)
            if not width or not height or compression or filter_method or interlace or color_type not in (0,2,3,4,6): raise HarvestValidationError("invalid_image")
        elif kind == b"IDAT": chunks.append(body)
        elif kind == b"IEND":
            if body or ended or offset != len(data): raise HarvestValidationError("invalid_image")
            ended=True
        elif not kind[0] & 0x20: raise HarvestValidationError("invalid_image")
    if width is None or not chunks or not ended: raise HarvestValidationError("invalid_image")
    channels={0:1,2:3,3:1,4:2,6:4}[color_type]
    if bit_depth not in (1,2,4,8,16) or (color_type in (2,4,6) and bit_depth not in (8,16)): raise HarvestValidationError("invalid_image")
    row_bytes=(width*channels*bit_depth+7)//8
    try: decoded=zlib.decompress(b"".join(chunks))
    except zlib.error as e: raise HarvestValidationError("invalid_image") from e
    if len(decoded) != height*(row_bytes+1) or any(decoded[row*(row_bytes+1)] > 4 for row in range(height)): raise HarvestValidationError("invalid_image")
    return width,height

def validate_bundle(directory: Path) -> dict[str, Any]:
    root = directory.resolve(strict=False)
    if not root.is_dir() or ".partial-" in root.name: raise HarvestValidationError("incomplete_run")
    index = _json(root, "dataset-index.json")
    receipt = _json(root, "harvest-receipt.json")
    if not isinstance(index, dict) or index.get("datasetLayoutVersion") != 1 or index.get("telemetryContract") != "harvest-canonical-v1; source-version-unverified" or index.get("provenance") != "unverified-pixel-telemetry-binding" or index.get("normalizedCoordinates") != "xyxy-top-left-unit" or index.get("pixelCoordinates") != "xywh-top-left-pixels": raise HarvestValidationError("unsupported_version")
    if not isinstance(receipt, dict) or receipt.get("schemaVersion") != 1: raise HarvestValidationError("unsupported_version")
    if receipt.get("outcome") != "completed" or receipt.get("failure") is not None or not isinstance(receipt.get("acceptedRowCount"), int) or receipt["acceptedRowCount"] <= 0: raise HarvestValidationError("incomplete_run")
    artifacts = index.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) > 10000: raise HarvestValidationError("unsafe_or_invalid_manifest")
    data: dict[str, bytes] = {}; total = 0
    for a in artifacts:
        if not isinstance(a, dict) or not isinstance(a.get("path"), str) or a["path"] in data: raise HarvestValidationError("unsafe_or_invalid_manifest")
        b = _read(root, a["path"]); total += len(b)
        if total > LIMIT_TOTAL or a.get("byteCount") != len(b) or a.get("sha256") != hashlib.sha256(b).hexdigest(): raise HarvestValidationError("integrity_failed")
        data[a["path"]] = b
    required = {"manifest.json", "training.json", "calibration.json", "held-out.json"}
    if not required <= data.keys(): raise HarvestValidationError("unsafe_or_invalid_manifest")
    rows = _json(root, "manifest.json")
    if not isinstance(rows, list) or len(rows) != receipt["acceptedRowCount"]: raise HarvestValidationError("unsafe_or_invalid_manifest")
    if len({r.get("id") for r in rows if isinstance(r, dict)}) != len(rows): raise HarvestValidationError("unsafe_or_invalid_manifest")
    for split in ("training", "calibration", "held-out"):
        if _json(root, split + ".json") != [r for r in rows if r.get("split") == split]: raise HarvestValidationError("invalid_metadata")
    expected = set(required)
    for row in rows:
        if isinstance(row, dict) and isinstance(row.get("metadata"), dict): expected.update(row["metadata"].get(k) for k in ("unfocusedPath", "focusedPath", "metadataPath"))
    if expected != set(data): raise HarvestValidationError("unsafe_or_invalid_manifest")
    normalized=[]; unknown=0; seen_baselines={}
    for row in rows:
        if row.get("split") not in ("training","calibration","held-out") or not isinstance(row.get("metadata"),dict): raise HarvestValidationError("invalid_metadata")
        m=row["metadata"]; names=[m.get("unfocusedPath"),m.get("focusedPath"),m.get("metadataPath")]
        if not all(isinstance(n,str) and n in data for n in names): raise HarvestValidationError("unsafe_or_invalid_manifest")
        a_size=_png_size(data[names[0]]); b_size=_png_size(data[names[1]])
        if a_size != b_size: raise HarvestValidationError("invalid_image")
        size=a_size
        meta=_json(root,names[2]); elems=meta.get("elements") if isinstance(meta,dict) else None
        focus=meta.get("focused_element_id") if isinstance(meta,dict) else None
        focused=[e for e in elems or [] if isinstance(e,dict) and e.get("is_focused")]
        if meta.get("id") != row.get("id") or not meta.get("is_settled") or len(focused)!=1 or focused[0].get("element_id") != focus or focus != row.get("expectedFocus") or focused[0].get("pixel_bounds") != row.get("box"): raise HarvestValidationError("invalid_metadata")
        usable=[]
        for e in elems:
            n=e.get("normalized_bounds"); p=e.get("pixel_bounds")
            if not (isinstance(n,list) and isinstance(p,list) and len(n)==len(p)==4 and all(isinstance(x,(int,float)) and math.isfinite(x) for x in n+p) and 0<=n[0]<n[2]<=1 and 0<=n[1]<n[3]<=1 and p[0]>=0 and p[1]>=0 and p[2]>0 and p[3]>0 and p[0]+p[2]<=size[0] and p[1]+p[3]<=size[1]): raise HarvestValidationError("invalid_metadata")
            if e.get("taxonomy_class") in KNOWN: usable.append(e)
            else: unknown += 1
        digest=hashlib.sha256(data[names[0]]).hexdigest()
        if digest in seen_baselines and seen_baselines[digest] != row["split"]: raise HarvestValidationError("invalid_metadata")
        seen_baselines[digest]=row["split"]
        if not usable: continue
        normalized.append({"id":row["id"],"split":row["split"],"platform":"tvOS","producer":index.get("producer"),"producerBuild":index.get("producerBuild"),"identityEvidence":None,"provenance":"unverified-pixel-telemetry-binding","eligibleForTraining":False,"elements":usable})
    return {"contractVersion":"harvest-compatibility-v1","integrity":"pass","producer":index.get("producer"),"producerBuild":index.get("producerBuild"),"identityEvidence":None,"provenance":"unverified-pixel-telemetry-binding","eligibleForTraining":False,"unknownClassCount":unknown,"usableRows":normalized}
