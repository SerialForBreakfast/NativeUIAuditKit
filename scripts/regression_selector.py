#!/usr/bin/env python3
"""Deterministic, inference-free synthetic regression-suite builder."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
FORMAT="synthetic-regression-v1"; SEED=42
class SelectorError(ValueError): pass
def digest(p: Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def build(candidates:list[dict], excluded:list[dict], target:int=250)->dict:
 seen=set(); blocked=set(); families=set()
 for x in excluded:
  blocked.update((x.get('id'),x.get('imageSHA256'),x.get('labelSHA256'))); families.add(x.get('family'))
 rows=[]; gaps=set()
 for x in candidates:
  required=('id','image','label','sourceSplit','platform','family','width','height','classes')
  if not all(k in x for k in required): raise SelectorError('invalid_member')
  image,label=Path(x['image']),Path(x['label'])
  if not image.is_file() or not label.is_file(): raise SelectorError('missing_pixel_or_label')
  ih,lh=digest(image),digest(label)
  if x['id'] in seen or x['id'] in blocked or ih in blocked or lh in blocked or x['family'] in families: raise SelectorError('leakage')
  seen.add(x['id']); row={k:x[k] for k in ('id','sourceSplit','platform','family','width','height','classes')}; row.update(imageSHA256=ih,labelSHA256=lh,aspectBucket='wide' if x['width']>x['height'] else 'tall' if x['height']>x['width'] else 'square',smallElement=bool(x.get('smallElement',False))); rows.append(row)
 rows.sort(key=lambda r: hashlib.sha256(f"{SEED}:{r['id']}".encode()).hexdigest())
 chosen=rows[:target]
 present={c for r in chosen for c in r['classes']}; all_classes={c for r in rows for c in r['classes']}; gaps=sorted(all_classes-present)
 return {'formatVersion':FORMAT,'algorithmVersion':1,'seed':SEED,'target':target,'members':chosen,'coverageExceptions':{'uncoveredClasses':gaps,'availableMembers':len(rows)}}
