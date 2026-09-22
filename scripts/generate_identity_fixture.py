#!/usr/bin/env python3
"""Deterministic supplied-observation cases: TEST ONLY, no real OCR or captures."""
import argparse
import copy
import json
from pathlib import Path
from identity_benchmark import ROOT, require


def policy():
    return dict(version="identity-policy-v1",reference="synthetic-policy-not-calibrated",frozenOn="test-only",
                supportedLocales=["en","es"],confidenceThreshold=.75,labelFraction=.6,minHorizontalOverlap=.6,
                maxWidthRatio=1.5,minimumRowMatches=1,minimumScreenScore=.5,minimumMargin=.2,maxAgeMs=250,toolTimeoutSeconds=10)


def snapshot(prefix):
    texts=[dict(id="title",text="General",confidence=.99,bounds=[.1,.05,.5,.07])]
    rows=[]
    for i,(label,value) in enumerate((("Name","Office"),("Version","1.0"))):
        y=.3+i*.2;rows.append(dict(id=prefix+str(i),confidence=.99,bounds=[.1,y,.8,.12]))
        texts += [dict(id="label"+str(i),text=label,confidence=.99,bounds=[.15,y+.02,.25,.05]),
                  dict(id="value"+str(i),text=value,confidence=.99,bounds=[.7,y+.02,.15,.05])]
    return dict(observationID=prefix+"-observation",contextEpoch="epoch1",locale="en",capturedMs=100,observedMs=110,
                status="success",evidenceKind="test-only",adapterReference="synthetic-observation-generator-v1",texts=texts,rows=rows,overlays=[])


def base_case():
    ref=dict(screenID="general",locale="en",required=["General"],optional=[],forbidden=["Delete"],titleRegion=[0,0,1,.2],
             snapshot=snapshot("r"),rowIDs={"r0":"name","r1":"version"})
    return dict(id="ordinary",group="synthetic-journey-v1",partition="development",sourceKind="test-only",
                sourceReference="deterministic-observations-v1",labelOrigin="synthetic-generator",reviewReference="software-only",
                scenario="ordinary",references=[ref],query=snapshot("q"),truth=dict(expectedScreenID="general",rows={"q0":"name","q1":"version"}))


def corpus():
    cases=[]
    for name,scenario in (("ordinary","ordinary"),("changed-value","changed-value"),("scroll","scroll"),
                          ("repeated-label","repeated-label"),("spanish","localization"),("unsupported-french","localization"),
                          ("hidden-row","hidden-row"),("overlay","overlay"),("stale","stale"),
                          ("ambiguous-screen","ambiguous-screen"),("missing-anchor","missing-anchor"),
                          ("substring-collision","ambiguous-screen"),("failed-recognition","missing-anchor"),
                          ("changed-epoch","ordinary"),("changed-screen","ordinary")):
        c=base_case();c.update(id=name,scenario=scenario);q=c["query"];r=c["references"][0]
        if name=="changed-value":
            for t in q["texts"]:
                if t["id"].startswith("value"):t["text"]="New value"
        elif name in ("scroll","hidden-row"):
            q["rows"]=q["rows"][1:];q["texts"]=[t for t in q["texts"] if t["id"] not in ("label0","value0")];del c["truth"]["rows"]["q0"]
            if name=="scroll":
                q["rows"][0]["bounds"][1]-=.2
                for t in q["texts"]:
                    if t["id"]!="title":t["bounds"][1]-=.2
        elif name=="repeated-label":
            for s in (q,r["snapshot"]):
                for t in s["texts"]:
                    if t["id"].startswith("label"):t["text"]="Name"
        elif name=="spanish":
            r["locale"]="es"
            for s in (q,r["snapshot"]):
                s["locale"]="es"
                for t in s["texts"]:
                    if t["id"]=="label0":t["text"]="Nombre"
                    if t["id"]=="label1":t["text"]="Versión"
        elif name=="unsupported-french":q["locale"]="fr";q["texts"][0]["text"]="Général"
        elif name=="overlay":q["overlays"]=[dict(confidence=.99,bounds=[.2,.2,.6,.6])]
        elif name=="stale":q["observedMs"]=2000
        elif name=="ambiguous-screen":
            other=copy.deepcopy(r);other["screenID"]="other-general";c["references"].append(other)
        elif name=="missing-anchor":q["texts"][0]["text"]="Other"
        elif name=="substring-collision":
            q["texts"][0]["text"]="General Information";c["truth"]={"expectedScreenID":None,"rows":{"q0":None,"q1":None}}
        elif name=="failed-recognition":q.update(status="failed",rows=[],texts=[]);c["truth"]["rows"]={}
        elif name=="changed-epoch":c.update(cachedEpoch="epoch0",cachedScreenID="general")
        elif name=="changed-screen":c["cachedScreenID"]="other-screen"
        cases.append(c)
    return dict(version="identity-benchmark-v1",corpusID="PER-06-test-only-v1",cases=cases)


def generate(output):
    output=output.absolute();require(output.resolve().is_relative_to(ROOT) and not output.exists() and not output.is_symlink(),"new_project_local_destination_required")
    output.mkdir(parents=True)
    for name,value in (("manifest.json",corpus()),("policy.json",policy())):
        (output/name).write_text(json.dumps(value,indent=2,sort_keys=True))
    return output


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--output",type=Path,required=True);print(generate(p.parse_args().output))
