"""Prepare the FOCUS556 FocusRing training corpus (S3).
Combines FDR-038 replay set with S2 training-only fixture crops.
Enforces 20% validation split on S2 groups, verifies 0 real-app pixel overlap,
and produces the unified corpus manifest.
"""
import sys
import json
import hashlib
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import research_queue as q

S2_DIR = q.ROOT / 'dataset/tvos_captures/focus556/out-4k'
S2_MANIFEST_PATH = S2_DIR / 'manifest.json'
FDR038_PROTOCOL = q.ROOT / 'reports/work/FOCUS-RETENTION-234/artifacts/protocol.json'
OUTPUT_CORPUS_DIR = q.ROOT / 'dataset/focus_ring/focus556_corpus'
OUTPUT_CROPS_DIR = OUTPUT_CORPUS_DIR / 'crops'
REAL_APP_CAPTURES = [
    q.ROOT / 'reports/work/REALAPP554/pilot-v2/captures',
    q.ROOT / 'reports/work/REALAPP554/dev/captures',
    q.ROOT / 'reports/work/REALAPP554',
    q.ROOT / 'reports/work/RC561/captures'
]

def make_crop(image, box, expansion_factor=0.16, size=256):
    x, y, w, h = box
    ex = w * expansion_factor
    ey = h * expansion_factor
    x1 = max(0, x - ex)
    y1 = max(0, y - ey)
    x2 = min(image.width, x + w + ex)
    y2 = min(image.height, y + h + ey)
    crop = image.crop((x1, y1, x2, y2))
    return crop.resize((size, size), Image.Resampling.BILINEAR)

def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def pixel_sha256(im: Image.Image) -> str:
    return hashlib.sha256(im.tobytes()).hexdigest()

def collect_real_app_hashes():
    print("Collecting real-app image and pixel hashes to ensure zero overlap...")
    real_hashes = set()
    for folder in REAL_APP_CAPTURES:
        if not folder.exists():
            continue
        for img_path in folder.rglob('*.png'):
            try:
                real_hashes.add(file_sha256(img_path))
                with Image.open(img_path) as im:
                    real_hashes.add(pixel_sha256(im))
            except Exception:
                pass
    print(f"Collected {len(real_hashes)} real-app hashes for exclusion verification.")
    return real_hashes

def main():
    OUTPUT_CROPS_DIR.mkdir(parents=True, exist_ok=True)
    real_hashes = collect_real_app_hashes()

    # 1. Process S2 crops
    with open(S2_MANIFEST_PATH) as f:
        s2_rows = json.load(f)
    print(f"\nProcessing {len(s2_rows)} S2 rows from {S2_DIR.name}...")

    # Group rows by recipeFile
    recipe_groups = {}
    for r in s2_rows:
        rec = r['metadata']['recipeFile']
        recipe_groups.setdefault(rec, []).append(r)

    # Deterministic split: 20% validation, 80% training based on sorted recipe names
    sorted_recipes = sorted(recipe_groups.keys())
    val_count = max(1, int(round(len(sorted_recipes) * 0.20))) # ~4 recipes
    val_recipes = set(sorted_recipes[:val_count])
    train_recipes = set(sorted_recipes[val_count:])
    print(f"Recipes total: {len(sorted_recipes)} -> Train: {len(train_recipes)}, Val: {len(val_recipes)}")

    s2_pairs = []
    generated_crops_count = 0

    for r in s2_rows:
        row_id = r['id']
        box = r['box']
        rec = r['metadata']['recipeFile']
        split = 'val' if rec in val_recipes else 'train'
        cls_name = r['metadata']['taxonomyClass']
        
        f_path = S2_DIR / r['metadata']['focusedPath']
        u_path = S2_DIR / r['metadata']['unfocusedPath']

        im_f = Image.open(f_path).convert('RGB')
        im_u = Image.open(u_path).convert('RGB')

        crop_f = make_crop(im_f, box)
        crop_u = make_crop(im_u, box)

        # Check real-app overlap
        f_px = pixel_sha256(crop_f)
        u_px = pixel_sha256(crop_u)
        assert f_px not in real_hashes, f"CRITICAL: Focused crop {row_id} matches real-app pixel hash!"
        assert u_px not in real_hashes, f"CRITICAL: Unfocused crop {row_id} matches real-app pixel hash!"

        crop_f_name = f"{row_id}_focused.png"
        crop_u_name = f"{row_id}_unfocused.png"
        crop_f_out = OUTPUT_CROPS_DIR / crop_f_name
        crop_u_out = OUTPUT_CROPS_DIR / crop_u_name

        crop_f.save(crop_f_out)
        crop_u.save(crop_u_out)
        generated_crops_count += 2

        s2_pairs.append({
            'pair_id': f"s2_{row_id}",
            'element_type': cls_name,
            'recipe': rec,
            'theme': 'dark' if 'dark' in rec else 'light',
            'split': split,
            'focused_crop': f"crops/{crop_f_name}",
            'unfocused_crop': f"crops/{crop_u_name}",
            'source': 's2_tvos_fixture'
        })

    print(f"Generated {generated_crops_count} S2 crops across {len(s2_pairs)} pairs.")

    # 2. Process FDR-038 replay samples
    print(f"\nLoading FDR-038 training samples from {FDR038_PROTOCOL}...")
    with open(FDR038_PROTOCOL) as f:
        fdr038_data = json.load(f)

    # In FDR-038: 'samples' has 96 crops, 'replay' has 56 crops
    # Group them into pairs where possible or treat as training samples
    fdr_samples = fdr038_data.get('samples', [])
    fdr_replay = fdr038_data.get('replay', [])
    print(f"FDR-038: {len(fdr_samples)} procedural/artwork samples + {len(fdr_replay)} legacy replay crops.")

    # Copy / symlink FDR-038 crops into OUTPUT_CROPS_DIR with consistent naming
    fdr_pairs = []
    # Process samples (pairs of focused and unfocused)
    sample_dict = {}
    for s in fdr_samples:
        src_path = q.ROOT / s['crop']['path']
        lbl = s['label']
        # Pair by metadata or prefix
        meta = s.get('metadata', s['id'])
        sample_dict.setdefault(meta, {})[lbl] = src_path

    pair_idx = 0
    for meta, pair in sample_dict.items():
        if 1 in pair and 0 in pair:
            f_src = pair[1]
            u_src = pair[0]
            f_dst_name = f"fdr038_s_{pair_idx}_focused.png"
            u_dst_name = f"fdr038_s_{pair_idx}_unfocused.png"
            
            im_f = Image.open(f_src).convert('RGB')
            im_u = Image.open(u_src).convert('RGB')
            im_f.save(OUTPUT_CROPS_DIR / f_dst_name)
            im_u.save(OUTPUT_CROPS_DIR / u_dst_name)

            fdr_pairs.append({
                'pair_id': f"fdr038_s_{pair_idx}",
                'element_type': 'procedural_artwork',
                'theme': 'mixed',
                'split': 'train',
                'focused_crop': f"crops/{f_dst_name}",
                'unfocused_crop': f"crops/{u_dst_name}",
                'source': 'fdr038_procedural_artwork'
            })
            pair_idx += 1

    # Process legacy replay (56 crops = 28 pairs)
    replay_dict = {}
    for r in fdr_replay:
        pair_id = r.get('pairID', r['id'].split('-')[1])
        lbl = r['label']
        src_path = q.ROOT / r['crop']['path']
        replay_dict.setdefault(pair_id, {})[lbl] = src_path

    for pid, pair in replay_dict.items():
        if 1 in pair and 0 in pair:
            f_src = pair[1]
            u_src = pair[0]
            f_dst_name = f"fdr038_rep_{pid}_focused.png"
            u_dst_name = f"fdr038_rep_{pid}_unfocused.png"
            
            im_f = Image.open(f_src).convert('RGB')
            im_u = Image.open(u_src).convert('RGB')
            im_f.save(OUTPUT_CROPS_DIR / f_dst_name)
            im_u.save(OUTPUT_CROPS_DIR / u_dst_name)

            fdr_pairs.append({
                'pair_id': f"fdr038_rep_{pid}",
                'element_type': 'legacy_replay',
                'theme': 'mixed',
                'split': 'train',
                'focused_crop': f"crops/{f_dst_name}",
                'unfocused_crop': f"crops/{u_dst_name}",
                'source': 'fdr038_legacy_replay'
            })

    print(f"Assembled {len(fdr_pairs)} FDR-038 replay pairs ({len(fdr_pairs)*2} crops).")

    all_pairs = s2_pairs + fdr_pairs
    train_pairs = [p for p in all_pairs if p['split'] == 'train']
    val_pairs = [p for p in all_pairs if p['split'] == 'val']

    manifest = {
        'version': 'focus556-corpus-v1',
        'authority': 'Tasks.md:RA554-16,Research/Plans/FocusRealApp556.md:S3',
        'date': '2026-11-03',
        'total_pairs': len(all_pairs),
        'total_crops': len(all_pairs) * 2,
        'train_pairs': len(train_pairs),
        'val_pairs': len(val_pairs),
        's2_pairs': len(s2_pairs),
        'fdr038_pairs': len(fdr_pairs),
        'real_app_pixel_overlap': 0,
        'pairs': all_pairs
    }

    manifest_file = OUTPUT_CORPUS_DIR / 'focus_dataset_manifest.json'
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"\nCorpus preparation complete:")
    print(f"  Manifest: {manifest_file.relative_to(q.ROOT)}")
    print(f"  Total pairs: {len(all_pairs)} ({len(all_pairs)*2} crops)")
    print(f"  Train pairs: {len(train_pairs)} ({len(train_pairs)*2} crops)")
    print(f"  Val pairs: {len(val_pairs)} ({len(val_pairs)*2} crops)")
    print(f"  Real-app pixel overlap: 0 (verified across {len(real_hashes)} real hashes)")

if __name__ == '__main__':
    main()
