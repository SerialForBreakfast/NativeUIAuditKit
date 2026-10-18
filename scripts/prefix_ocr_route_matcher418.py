"""T82 adapter: Prefix-Anchored Weighted Levenshtein Automaton for Clipped-OCR TTR Route Recovery."""
from __future__ import annotations

import math
import research_queue as q
from template_adapters395 import document, resolve_inputs

OUT = None


def parameters(values: dict) -> dict:
    q.require(
        isinstance(values, dict)
        and set(values) == {"anchorPhrase", "maxTailCost"},
        "ocr_matcher_parameters",
    )
    anchor = values["anchorPhrase"]
    max_cost = values["maxTailCost"]
    q.require(isinstance(anchor, str) and len(anchor.strip()) >= 3, "ocr_matcher_anchor_phrase")
    q.require(
        isinstance(max_cost, (int, float)) and not isinstance(max_cost, bool) and math.isfinite(max_cost) and 0.0 <= max_cost <= 0.30,
        "ocr_matcher_tail_cost_range",
    )
    return dict(anchorPhrase=anchor.strip(), maxTailCost=float(max_cost))


def match_prefix_anchored_observation(
    before: dict,
    after: dict,
    anchor_phrase: str = "Focus Style",
    max_tail_cost: float = 0.15,
) -> dict[str, object]:
    """Verifies exact page, focusKey, settingValue, and prefix through anchor_phrase, allowing right-edge clipped tail OCR."""
    for obs in (before, after):
        q.require(
            isinstance(obs, dict) and {"page", "focusKey", "settingValue", "fullOcrLine"} <= set(obs),
            "ocr_matcher_observation_fields",
        )
    if before["page"] != after["page"]:
        return {"matched": False, "reason": "page_mismatch", "tailCost": 1.0}
    if before["focusKey"] != after["focusKey"]:
        return {"matched": False, "reason": "focus_mismatch", "tailCost": 1.0}
    if str(before["settingValue"]).strip() != str(after["settingValue"]).strip():
        return {"matched": False, "reason": "setting_value_mismatch", "tailCost": 1.0}

    line_b = str(before["fullOcrLine"])
    line_a = str(after["fullOcrLine"])
    idx_b = line_b.find(anchor_phrase)
    idx_a = line_a.find(anchor_phrase)
    if idx_b < 0 or idx_a < 0:
        return {"matched": False, "reason": "anchor_phrase_missing", "tailCost": 1.0}

    end_b = idx_b + len(anchor_phrase)
    end_a = idx_a + len(anchor_phrase)
    prefix_b = " ".join(line_b[:end_b].split())
    prefix_a = " ".join(line_a[:end_a].split())
    if prefix_b != prefix_a:
        return {"matched": False, "reason": "prefix_mismatch", "tailCost": 1.0}

    tail_b = " ".join(line_b[end_b:].split()).rstrip(".… ")
    tail_a = " ".join(line_a[end_a:].split()).rstrip(".… ")
    if tail_b == tail_a:
        return {"matched": True, "reason": "exact_match", "tailCost": 0.0}

    common_len = 0
    for cb, ca in zip(tail_b, tail_a):
        if cb == ca:
            common_len += 1
        else:
            break

    min_len = min(len(tail_b), len(tail_a))
    max_len = max(len(tail_b), len(tail_a), 1)
    # Require that the shorter clipped tail matches the prefix of the longer tail up to at most 2 boundary glyph splits
    prefix_divergence = min_len - common_len
    if prefix_divergence > 2:
        return {"matched": False, "reason": "tail_substantive_mismatch", "tailCost": 1.0}

    clipped_fraction = (max_len - common_len) / max_len
    weighted_tail_cost = round(0.15 * clipped_fraction + 0.04 * prefix_divergence, 6)
    matched = weighted_tail_cost <= max_tail_cost
    return {
        "matched": matched,
        "reason": "prefix_anchored_tail_clip_match" if matched else "tail_cost_exceeded",
        "tailCost": weighted_tail_cost,
        "commonTailChars": common_len,
    }


def run() -> None:
    cfg = q.load(OUT.parents[2] / "spec.json")["template"]
    params = parameters(cfg["parameters"])
    refs = resolve_inputs(cfg, OUT)
    obs_doc = document(refs["observationsPath"])
    adv_doc = document(refs["adversarialPath"])

    valid_pairs = obs_doc.get("pairs", [])
    adv_pairs = adv_doc.get("pairs", [])
    q.require(valid_pairs and adv_pairs, "ocr_matcher_empty_corpus")

    valid_results = []
    for p in valid_pairs:
        res = match_prefix_anchored_observation(
            p["before"],
            p["after"],
            anchor_phrase=params["anchorPhrase"],
            max_tail_cost=params["maxTailCost"],
        )
        res["id"] = p["id"]
        valid_results.append(res)

    adv_results = []
    for p in adv_pairs:
        res = match_prefix_anchored_observation(
            p["before"],
            p["after"],
            anchor_phrase=params["anchorPhrase"],
            max_tail_cost=params["maxTailCost"],
        )
        res["id"] = p["id"]
        adv_results.append(res)

    false_accepts = [r["id"] for r in adv_results if r["matched"]]
    q.require(not false_accepts, "ocr_matcher_unsafe_adversarial_accept")

    summary = {
        "version": "prefix-ocr-route-matcher-v1",
        "parameters": params,
        "validMatchedCount": sum(r["matched"] for r in valid_results),
        "validTotal": len(valid_results),
        "adversarialRejectedCount": sum(not r["matched"] for r in adv_results),
        "adversarialTotal": len(adv_results),
        "validResults": valid_results,
        "adversarialResults": adv_results,
        "inputs": refs,
        "modelAccepted": False,
    }
    q.save(OUT / "benchmark_summary.json", summary)
    q.save(
        OUT / "artifact-receipt.json",
        {
            "version": "research-artifact-v1",
            "outputs": [{"path": "benchmark_summary.json", "sha256": q.digest(OUT / "benchmark_summary.json")}],
        },
    )
