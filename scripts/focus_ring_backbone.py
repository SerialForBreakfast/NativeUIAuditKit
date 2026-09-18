#!/usr/bin/env python3
"""
focus_ring_backbone.py — MobileNetV4-Conv-Small in torch.nn only.

`import timm` (and `timm.layers`) hangs in this environment because package
inits star-import 100+ architectures plus torchvision FX. Train, eval, and
export all construct this backbone instead of calling `timm.create_model`.

Architecture matches timm 1.0.29 `mobilenetv4_conv_small` (pretrained=False):
stem 3x3 s2 → ConvBnAct / UniversalInvertedResidual stages → GAP → 1x1 head.
"""

from __future__ import annotations

from typing import Optional

import torch
from torch import nn


def make_divisible(v: float, divisor: int = 8, min_value: Optional[int] = None, round_limit: float = 0.9) -> int:
    """Round channel counts the same way timm `make_divisible` does."""
    min_value = min_value or divisor
    new_v = max(min_value, int(v + divisor / 2) // divisor * divisor)
    if new_v < round_limit * v:
        new_v += divisor
    return new_v


def _conv_bn_act(
    in_chs: int,
    out_chs: int,
    kernel_size: int,
    stride: int = 1,
    groups: int = 1,
    apply_act: bool = True,
) -> nn.Sequential:
    """Same-padded Conv2d + BatchNorm2d, optional ReLU."""
    padding = kernel_size // 2
    layers: list[nn.Module] = [
        nn.Conv2d(in_chs, out_chs, kernel_size, stride=stride, padding=padding, groups=groups, bias=False),
        nn.BatchNorm2d(out_chs),
    ]
    if apply_act:
        layers.append(nn.ReLU(inplace=True))
    return nn.Sequential(*layers)


class ConvBnAct(nn.Module):
    """Plain conv block (`cn_*` in the MobileNetV4 arch string)."""

    def __init__(self, in_chs: int, out_chs: int, kernel_size: int, stride: int = 1):
        super().__init__()
        self.block = _conv_bn_act(in_chs, out_chs, kernel_size, stride=stride)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.block(x)


class UniversalInvertedResidual(nn.Module):
    """UIB block (`uir_*`): optional start DW, 1x1 expand, optional mid DW, 1x1 project."""

    def __init__(
        self,
        in_chs: int,
        out_chs: int,
        dw_kernel_size_start: int = 0,
        dw_kernel_size_mid: int = 3,
        stride: int = 1,
        exp_ratio: float = 1.0,
    ):
        super().__init__()
        self.has_skip = in_chs == out_chs and stride == 1
        if dw_kernel_size_start:
            start_stride = stride if not dw_kernel_size_mid else 1
            self.dw_start = _conv_bn_act(
                in_chs, in_chs, dw_kernel_size_start, stride=start_stride, groups=in_chs, apply_act=False
            )
        else:
            self.dw_start = nn.Identity()

        mid_chs = make_divisible(in_chs * exp_ratio)
        self.pw_exp = _conv_bn_act(in_chs, mid_chs, 1)

        if dw_kernel_size_mid:
            self.dw_mid = _conv_bn_act(
                mid_chs, mid_chs, dw_kernel_size_mid, stride=stride, groups=mid_chs
            )
        else:
            self.dw_mid = nn.Identity()

        self.pw_proj = _conv_bn_act(mid_chs, out_chs, 1, apply_act=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        shortcut = x
        x = self.dw_start(x)
        x = self.pw_exp(x)
        x = self.dw_mid(x)
        x = self.pw_proj(x)
        if self.has_skip:
            x = x + shortcut
        return x


def _parse_token(token: str) -> dict:
    """Decode one timm arch token such as `uir_r1_a5_k5_s2_e3_c96`."""
    parts = token.split("_")
    block_type = parts[0]
    opts: dict[str, str] = {}
    for part in parts[1:]:
        opts[part[0]] = part[1:]
    repeats = int(opts.get("r", "1"))
    stride = int(opts.get("s", "1"))
    out_chs = int(opts["c"])
    if block_type == "cn":
        return {
            "kind": "cn",
            "repeats": repeats,
            "stride": stride,
            "out_chs": out_chs,
            "kernel_size": int(opts["k"]),
        }
    if block_type == "uir":
        return {
            "kind": "uir",
            "repeats": repeats,
            "stride": stride,
            "out_chs": out_chs,
            "dw_start": int(opts.get("a", "0")),
            "dw_mid": int(opts.get("k", "0")),
            "exp_ratio": float(opts.get("e", "1")),
        }
    raise ValueError(f"unsupported block token: {token}")


# timm `mobilenetv4_conv_small` arch_def (non-hybrid, channel_multiplier=1.0).
_MNV4_CONV_SMALL = [
    ["cn_r1_k3_s2_e1_c32", "cn_r1_k1_s1_e1_c32"],
    ["cn_r1_k3_s2_e1_c96", "cn_r1_k1_s1_e1_c64"],
    ["uir_r1_a5_k5_s2_e3_c96", "uir_r4_a0_k3_s1_e2_c96", "uir_r1_a3_k0_s1_e4_c96"],
    ["uir_r1_a3_k3_s2_e6_c128", "uir_r1_a5_k5_s1_e4_c128", "uir_r1_a0_k5_s1_e4_c128", "uir_r1_a0_k5_s1_e3_c128", "uir_r2_a0_k3_s1_e4_c128"],
    ["cn_r1_k1_s1_c960"],
]


class MobileNetV4ConvSmall(nn.Module):
    """Binary-capable MobileNetV4-Conv-Small. `num_classes=1` for FocusRingDetector."""

    def __init__(self, num_classes: int = 1, in_chans: int = 3):
        super().__init__()
        stem_size = 32
        self.conv_stem = nn.Conv2d(in_chans, stem_size, 3, stride=2, padding=1, bias=False)
        self.bn1 = nn.Sequential(nn.BatchNorm2d(stem_size), nn.ReLU(inplace=True))

        stages: list[nn.Module] = []
        in_chs = stem_size
        for tokens in _MNV4_CONV_SMALL:
            parsed = [_parse_token(t) for t in tokens]
            expanded: list[dict] = []
            for spec in parsed:
                for _ in range(spec["repeats"]):
                    expanded.append(dict(spec))
            blocks: list[nn.Module] = []
            for idx, spec in enumerate(expanded):
                stride = spec["stride"] if idx == 0 else 1
                out_chs = spec["out_chs"]
                if spec["kind"] == "cn":
                    blocks.append(ConvBnAct(in_chs, out_chs, spec["kernel_size"], stride=stride))
                else:
                    blocks.append(
                        UniversalInvertedResidual(
                            in_chs,
                            out_chs,
                            dw_kernel_size_start=spec["dw_start"],
                            dw_kernel_size_mid=spec["dw_mid"],
                            stride=stride,
                            exp_ratio=spec["exp_ratio"],
                        )
                    )
                in_chs = out_chs
            stages.append(nn.Sequential(*blocks))
        self.blocks = nn.Sequential(*stages)

        head_chs = 1280
        self.global_pool = nn.AdaptiveAvgPool2d(1)
        self.conv_head = nn.Conv2d(in_chs, head_chs, 1, bias=False)
        self.norm_head = nn.Sequential(nn.BatchNorm2d(head_chs), nn.ReLU(inplace=True))
        self.flatten = nn.Flatten(1)
        self.classifier = nn.Linear(head_chs, num_classes)
        self._init_weights()

    def _init_weights(self) -> None:
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode="fan_out", nonlinearity="relu")
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.ones_(m.weight)
                nn.init.zeros_(m.bias)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.conv_stem(x)
        x = self.bn1(x)
        x = self.blocks(x)
        x = self.global_pool(x)
        x = self.conv_head(x)
        x = self.norm_head(x)
        x = self.flatten(x)
        return self.classifier(x)


def mobilenetv4_conv_small(pretrained: bool = False, num_classes: int = 1, **_: object) -> MobileNetV4ConvSmall:
    """Factory matching the `timm.create_model('mobilenetv4_conv_small', ...)` call site."""
    if pretrained:
        raise ValueError("ImageNet pretrained weights are not bundled; train from scratch")
    return MobileNetV4ConvSmall(num_classes=num_classes)


def parameter_count(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())


if __name__ == "__main__":
    m = mobilenetv4_conv_small(num_classes=1)
    m.eval()
    with torch.no_grad():
        y = m(torch.zeros(2, 3, 256, 256))
    print(f"params={parameter_count(m)}  out={tuple(y.shape)}")
