"""Publish pre-inference visual review; no model output is used for labels."""
import copy
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/"scripts"))
from perception_benchmark import validate_manifest, verify_evidence

source=json.loads((ROOT/"reports/work/PER-DATA/manifest.json").read_text())
by_id={c["caseID"]:c for c in source["cases"]}
chosen={"office_home_initial":0,"office_home_step01":1,"office_home_step02":2,
        "office_session2_home":2,"office_home_step03":8,"office_home_col5":11}
cases=[]
for name, focus in chosen.items():
    case=copy.deepcopy(by_id[name])
    grid=name in {"office_home_step03","office_home_col5"}
    rows=[]
    for row in range(4 if grid else 1):
        for col,x in enumerate((90,388,686,984,1282,1580)):
            i=row*6+col; y=100+row*260 if grid else 824
            box=[x,y,250,150]
            if i==focus: box=[x-28,y-17,306,184]
            rows.append({"id":f"tile-{i}","box":box})
    case.update(focusUnknown=False,reviewer="NUIAK agent visual review 2026-09-23; not independent human review",
                reviewScope="All fully visible Home tiles; appearance-only focus from enlarged tile and visible label/context; rounded tile body excludes shadow",
                appearanceStratum="home-grid" if grid else "home-top-shelf",
                clippedExclusions="Bottom next row visible only as fragments; excluded" if not grid else "none",
                renderingCaveat="Several tiles have blank/placeholder artwork; this is not full native-app artwork coverage")
    case["labels"]={"origin":"reviewedVisual","rows":rows,"chevrons":[],"dialog":None,
                    "focus":{"elementID":f"tile-{focus}","frameID":name,"basis":"visualAppearanceOnly"}}
    cases.append(case)
manifest={"formatVersion":"perception-benchmark-v1","cases":cases}
verify_evidence(validate_manifest(manifest))
with (HERE/"manifest.json").open("x") as f: json.dump(manifest,f,indent=2)
with (HERE/"dispositions.json").open("x") as f:
    json.dump({"reviewed":list(chosen),"excluded":{"office_home_top_right":"App-switcher screenshot, not a live Home focus state"},
               "basis":"Visual inspection before inference, no callback or model-derived labels",
               "unknownJourney":"All six retained in legacy44-unknown-journey, including near-repeated Settings-tile views",
               "trainingEligible":False,"releaseEligible":False},f,indent=2)
print(json.dumps({"frames":len(cases),"boxes":sum(len(c["labels"]["rows"]) for c in cases)}))
