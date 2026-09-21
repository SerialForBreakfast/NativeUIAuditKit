"""Compile/reconcile immutable FocusRing recipe plans. Never operates a device."""
import argparse
from collections import Counter
import json
import sys
from pathlib import Path

from focus_dataset_contract import digest, local, text
from focus_ring_readiness import MIN
from simulator_focus_manifest import FAMILY_MAP, THEME_MAP

# Source-reviewed FixtureRecipe.swift bounds, TTR 562bd3a; catalog must name its
# producer revision. Live planned IDs must still be reconciled, never inferred.
LIMITS = {"gridMatrix": (1,64), "mediaShelf":(1,30), "settingsList":(1,40),
          "actionDialog":(1,6), "heroCarousel":(1,10), "focusMaze":(4,36), "kitchenSink":(41,41)}


class PlanError(ValueError): pass


def coverage(rows):
    scenes, themes, negatives, splits = Counter(), Counter(), Counter(), Counter()
    for row in rows:
        count = len(row["targets"])
        scenes[row["family"]] += count
        themes[row["family"] + "/" + row["theme"]] += count
        splits[row["split"]] += count
        if row["split"] == "test" and row["theme"] in {"light", "highContrast"}:
            for target in row["targets"]:
                if target["type"] in {"imageView", "collectionItem"}:
                    negatives[row["theme"] + "/" + target["type"]] += 1
    gaps = [f"{s}:missing_{max(0,n-scenes[s])}" for s,n in MIN.items() if scenes[s] < n]
    for scene in ("gridMatrix", "mediaShelf"):
        for theme in ("light", "highContrast"):
            if not scenes[scene] or themes[scene+"/"+theme] * 5 < scenes[scene]:
                gaps.append(f"{scene}/{theme}:below_20_percent")
    for theme in ("light", "highContrast"):
        for kind in ("imageView", "collectionItem"):
            if not negatives[theme+"/"+kind]: gaps.append(f"{theme}/{kind}:empty_test_negatives")
    if sum(negatives.values()) < 100: gaps.append("held_out_negatives:below_100")
    return {"pairs": sum(scenes.values()), "sceneCounts": dict(scenes), "themeCounts": dict(themes),
            "splitPairs": dict(splits), "hardNegativePotential": dict(negatives), "gaps": gaps}


def compile_plan(catalog):
    if not isinstance(catalog, dict) or catalog.get("version") != "focus-recipe-catalog-v1":
        raise PlanError("unsupported_catalog")
    text(catalog.get("producerReference")); text(catalog.get("reviewReference"))
    if catalog.get("evidenceKind") not in {"test-only", "source-reviewed"}: raise PlanError("invalid_catalog_evidence")
    excluded = catalog.get("developmentSeeds")
    if not isinstance(excluded, list) or any(type(s) is not int or s < 0 for s in excluded): raise PlanError("invalid_development_seeds")
    recipes = catalog.get("recipes")
    if not isinstance(recipes, list) or not recipes: raise PlanError("empty_catalog")
    seed_groups = catalog.get("seedGroups")
    if not isinstance(seed_groups,dict): raise PlanError("explicit_related_seed_groups_required")
    development_groups = catalog.get("developmentGroups",[])
    if not isinstance(development_groups,list): raise PlanError("invalid_development_groups")
    seen, seeds, rows = set(), set(), []
    for entry in recipes:
        r = entry["recipe"]
        if r.get("schema_version") != 1 or r.get("archetype") not in FAMILY_MAP or r.get("theme") not in THEME_MAP:
            raise PlanError("unsupported_recipe")
        seed = r.get("seed")
        if type(seed) is not int or seed < 0 or seed in excluded: raise PlanError("development_or_invalid_seed")
        group = text(seed_groups.get(str(seed)))
        if group in development_groups: raise PlanError("development_group_leakage")
        low, high = LIMITS[FAMILY_MAP[r["archetype"]]]
        if type(r.get("element_count")) is not int or not low <= r["element_count"] <= high:
            raise PlanError("invalid_element_count")
        if r.get("density") not in {"compact", "regular", "spacious"} or type(r.get("step_index")) is not int or r["step_index"] < 0:
            raise PlanError("unsupported_variation")
        targets = entry.get("expectedTargets")
        # Some templates (notably hero) use fixed controls independently of the
        # requested count. Bound claims by family capacity, not that input count.
        if not isinstance(targets, list) or not targets or len(targets) > high:
            raise PlanError("invalid_expected_targets")
        ids = [text(t.get("id")) for t in targets]
        if len(set(ids)) != len(ids): raise PlanError("duplicate_target")
        for t in targets: text(t.get("type"))
        key = digest(r)
        if key in seen: raise PlanError("duplicate_recipe")
        seen.add(key); seeds.add(seed)
        rows.append({"id": key, "recipe": r, "group": group,
                     "family": FAMILY_MAP[r["archetype"]], "theme": THEME_MAP[r["theme"]],
                     "targets": sorted(targets, key=lambda t:t["id"])})
    # Exact ratio by recipe group; all families/themes/variants of a seed stay together.
    groups={row["group"] for row in rows}
    if len(groups) < 10 or len(groups) % 10: raise PlanError("group_count_must_be_multiple_of_10")
    ordered = sorted(groups, key=lambda group:digest({"splitSalt": catalog.get("splitSalt", "focus-v1"), "group":group}))
    assignments = {group: "train" if i < len(groups)*.8 else "validation" if i < len(groups)*.9 else "test" for i,group in enumerate(ordered)}
    for row in rows: row["split"] = assignments[row["group"]]
    rows.sort(key=lambda r:r["id"])
    # Never split a recipe group across batches; reject oversized groups instead.
    batches, current = [], []
    for name in ordered:
        group = [r["id"] for r in rows if r["group"] == name]
        if len(group) > 100: raise PlanError("group_exceeds_batch_limit")
        if len(current)+len(group) > 100: batches.append(current); current=[]
        current += group
    if current: batches.append(current)
    value = {"version": "focus-capture-plan-v1", "catalogSHA256": digest(catalog),
             "producerReference": catalog["producerReference"], "evidenceKind":catalog["evidenceKind"],
             "developmentSeeds": sorted(set(excluded)), "recipes": rows,
             "groupCounts": dict(Counter(assignments.values())),
             "batches": [{"id": digest(ids), "recipeIDs":ids, "timeoutSeconds":600} for ids in batches],
             "plannedCoverage": coverage(rows), "countsAre": "unverified expected targets; not captured pairs",
             "captureAuthorized": False, "trainingEligible":False}
    return {**value, "planSHA256": digest(value)}


def reconcile(plan, ledger):
    if plan.get("version") != "focus-capture-plan-v1" or digest({k:v for k,v in plan.items() if k!="planSHA256"}) != plan.get("planSHA256"):
        raise PlanError("changed_plan")
    if ledger.get("version") != "focus-capture-ledger-v1" or ledger.get("planSHA256") != plan["planSHA256"]:
        raise PlanError("incompatible_ledger")
    batches = {b["id"]:b for b in plan["batches"]}
    rows = {r["id"]:r for r in plan["recipes"]}
    states, accepted, hashes, pair_ids, blocked = {}, [], {}, set(), []
    content_pairs=set()
    for attempt in ledger.get("attempts", []):
        bid = attempt.get("batchID")
        if bid not in batches or bid in states: raise PlanError("unknown_or_duplicate_batch_attempt")
        states[bid] = attempt.get("state")
        if attempt.get("state") != "completed" or attempt.get("cleanup") != "clear":
            blocked.append(bid); continue
        receipt = attempt.get("receiptSHA256")
        if not isinstance(receipt,str) or len(receipt)!=64 or any(c not in "0123456789abcdef" for c in receipt): raise PlanError("missing_receipt_hash")
        members = attempt.get("recipes", [])
        if len(members) != len(batches[bid]["recipeIDs"]) or {m.get("recipeID") for m in members} != set(batches[bid]["recipeIDs"]):
            raise PlanError("incomplete_batch_accounting")
        for member in members:
            row=rows[member["recipeID"]]
            if member.get("split")!=row["split"]: raise PlanError("split_drift")
            pairs=member.get("acceptedPairs", [])
            rejected=member.get("rejectedTargetIDs", [])
            expected={t["id"] for t in row["targets"]}
            observed=[p["targetID"] for p in pairs]+rejected
            if len(observed)!=len(set(observed)) or set(observed)!=expected: raise PlanError("target_accounting_mismatch")
            supported=[]
            for p in pairs:
                pid=text(p.get("pairID"))
                if pid in pair_ids: raise PlanError("duplicate_pair")
                pair_ids.add(pid)
                if p.get("labelSource")!="fixtureCallback" or p.get("unfocusedVerified") is not True: raise PlanError("unverified_pair")
                for role in ("focusedSHA256","unfocusedSHA256"):
                    sha=p.get(role)
                    if not isinstance(sha,str) or len(sha)!=64 or any(c not in "0123456789abcdef" for c in sha): raise PlanError("invalid_image_hash")
                    if sha in hashes and hashes[sha]!=row["split"]: raise PlanError("content_split_leakage")
                    hashes[sha]=row["split"]
                content=(p["focusedSHA256"],p["unfocusedSHA256"],p["targetID"])
                if content in content_pairs: raise PlanError("duplicate_pair_content")
                content_pairs.add(content)
                supported += [t for t in row["targets"] if t["id"]==p["targetID"]]
            accepted.append({**row,"targets":supported})
    missing=[b for b in plan["batches"] if b["id"] not in states]
    return {"planSHA256":plan["planSHA256"], "blockedBatches":blocked,
            "resumeBatches": [] if blocked else missing,
            "acceptedCoverage":coverage(accepted), "completedBatches":len(states)-len(blocked),
            "evidenceScope":"ledger claims; actual bytes and corpus approval still require intake validator",
            "trainingEligible":False, "captureAuthorized":False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--catalog",type=Path); p.add_argument("--plan",type=Path)
    p.add_argument("--ledger",type=Path); p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    try:
        out=local(a.output)
        if out.exists(): raise PlanError("output_collision")
        if a.catalog and not a.plan and not a.ledger: result=compile_plan(json.loads(a.catalog.read_text()))
        elif a.plan and a.ledger and not a.catalog: result=reconcile(json.loads(a.plan.read_text()),json.loads(a.ledger.read_text()))
        else: raise PlanError("choose_catalog_or_plan_and_ledger")
        out.parent.mkdir(parents=True,exist_ok=True)
        with out.open("x") as stream: json.dump(result,stream,indent=2)
        print(json.dumps({"planSHA256":result["planSHA256"],"trainingEligible":False})); return 0
    except (OSError,ValueError,KeyError,TypeError) as error:
        print(str(error),file=sys.stderr); return 2

if __name__=="__main__": raise SystemExit(main())
