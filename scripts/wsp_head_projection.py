"""WSP-01: Closed-form Weight-Space Detection Head Linear Projection.

Transforms a 41-class YOLO11 detector to the 13-role ROLES559 taxonomy
without backpropagation or retraining (ADR-0033).
Projects classification convolution weights W_13 = P * W_41 and b_13 = P * b_41 across all 3 detection scales.
"""
import sys
import copy
from pathlib import Path
import json
import torch
import torch.nn as nn
from ultralytics import YOLO

sys.path.insert(0, str(Path(__file__).resolve().parent))
import research_queue as q
from roles559 import ROLES, CLASS_ROLE

def build_projection_matrix(class_names_41, roles=ROLES, mode='max_pooling'):
    """Build projection matrix P in R^(13 x 41).
    mode: 'sum', 'mean', or 'binary'.
    """
    num_classes = len(class_names_41)
    num_roles = len(roles)
    P = torch.zeros((num_roles, num_classes), dtype=torch.float32)

    for c_idx, c_name in class_names_41.items():
        role = CLASS_ROLE.get(c_name)
        if role is not None and role in roles:
            r_idx = roles.index(role)
            P[r_idx, c_idx] = 1.0

    if mode == 'mean':
        # Row-normalize by number of constituent subclasses
        row_sums = P.sum(dim=1, keepdim=True).clamp(min=1.0)
        P = P / row_sums

    return P

def project_yolo_head(model_path, out_path, mode='mean'):
    print(f"Loading 41-class model from {model_path}...")
    yolo = YOLO(str(model_path))
    model = yolo.model
    names_41 = model.names
    
    if len(names_41) != 41:
        raise ValueError(f"Expected 41 classes, got {len(names_41)}")

    P = build_projection_matrix(names_41, ROLES, mode=mode)
    print(f"Built projection matrix P: shape {P.shape} (mode={mode})")

    detect_head = model.model[-1]
    print(f"Detect head has {len(detect_head.cv3)} scales. Projecting classification layers...")

    for i, branch in enumerate(detect_head.cv3):
        conv = branch[-1]
        # conv.weight shape: [41, C_in, 1, 1]
        w_41 = conv.weight.data
        b_41 = conv.bias.data if conv.bias is not None else None

        c_out, c_in, kh, kw = w_41.shape
        w_flat = w_41.view(c_out, -1)  # [41, C_in]
        w_proj = torch.matmul(P, w_flat).view(len(ROLES), c_in, kh, kw)

        new_conv = nn.Conv2d(c_in, len(ROLES), kernel_size=(kh, kw), stride=conv.stride, padding=conv.padding, bias=(b_41 is not None))
        new_conv.weight.data = w_proj

        if b_41 is not None:
            b_proj = torch.matmul(P, b_41)
            new_conv.bias.data = b_proj

        branch[-1] = new_conv
        print(f"  Scale {i}: Conv2d({c_in}, 41) -> Conv2d({c_in}, {len(ROLES)})")

    # Update head attributes
    detect_head.nc = len(ROLES)
    detect_head.no = len(ROLES) + detect_head.reg_max * 4
    model.nc = len(ROLES)
    model.names = {i: name for i, name in enumerate(ROLES)}

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save projected model checkpoint
    ckpt = {
        'model': model,
        'epoch': -1,
        'best_fitness': None,
        'date': '2026-11-02',
        'wsp_projection': {
            'source': str(model_path),
            'mode': mode,
            'source_classes': 41,
            'target_roles': 13
        }
    }
    torch.save(ckpt, out_path)
    print(f"Successfully saved projected 13-role YOLO model to {out_path} ({out_path.stat().st_size} bytes)")
    return yolo

def main():
    src = q.ROOT / 'NativeUITrainer/yolo_runs/phase6a_r013/weights/best.pt'
    dst = q.ROOT / 'NativeUITrainer/yolo_runs/wsp_projected_r013/weights/best.pt'
    projected_model = project_yolo_head(src, dst, mode='mean')

    print("\nVerifying inference on sample image with projected head...")
    sample_img = q.ROOT / 'reports/work/RC561/captures/tvcatalog-buttons.png'
    if sample_img.exists():
        results = projected_model.predict(str(sample_img), conf=0.25, iou=0.45, verbose=False)
        boxes = results[0].boxes
        print(f"Detections with projected 13-role head: {len(boxes)}")
        cls_counts = {}
        for c, conf in zip(boxes.cls, boxes.conf):
            cls_name = ROLES[int(c)]
            cls_counts[cls_name] = cls_counts.get(cls_name, 0) + 1
        print("Role counts:")
        for r, cnt in sorted(cls_counts.items(), key=lambda x: -x[1]):
            print(f"  {r:<18}: {cnt}")

if __name__ == '__main__':
    main()
