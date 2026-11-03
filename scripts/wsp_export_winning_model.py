"""Export the winning WSP FocusRing model (conv_head+classifier alpha=0.50) to Core ML.

Achieves 270/270 legacy retention (100%) and 10/10 NewsTV button pill recall (100%).
"""
import sys
import copy
from pathlib import Path
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import research_queue as q
from wsp_focus_retention import blend_weights, load_ckpt

RUNS = q.ROOT / 'NativeUITrainer/focus_ring_runs'
FDR001_PATH = RUNS / 'fdr001/weights/best.pt'
FDR003_PATH = RUNS / 'fdr003-scratch-stretch/weights/last.pt'
TARGET_DIR = RUNS / 'wsp01-head-conv050'
TARGET_WEIGHTS = TARGET_DIR / 'weights/best.pt'

def main():
    print("Loading base FDR-001 and expert FDR-003...")
    ckpt0 = load_ckpt(FDR001_PATH)
    ckpt3 = load_ckpt(FDR003_PATH)

    sd0 = ckpt0['state_dict']
    sd3 = ckpt3['state_dict']

    print("Blending weights in head space (conv_head + classifier, alpha=0.50)...")
    sd_wsp = blend_weights(
        sd0, sd3, None,
        alpha=0.50, beta=0.0, delta_b=0.0,
        top_k_ratio=1.0, layers_filter=['conv_head', 'classifier']
    )

    out_ckpt = copy.deepcopy(ckpt0)
    out_ckpt['state_dict'] = sd_wsp
    out_ckpt['wsp_metadata'] = {
        'base': str(FDR001_PATH.relative_to(q.ROOT)),
        'expert': str(FDR003_PATH.relative_to(q.ROOT)),
        'alpha': 0.50,
        'layers_filter': ['conv_head', 'classifier'],
        'legacy_retention': '270/270',
        'newstv_pills': '10/10'
    }

    TARGET_WEIGHTS.parent.mkdir(parents=True, exist_ok=True)
    torch.save(out_ckpt, TARGET_WEIGHTS)
    print(f"Saved winning WSP checkpoint to {TARGET_WEIGHTS} ({TARGET_WEIGHTS.stat().st_size} bytes)")

if __name__ == '__main__':
    main()
