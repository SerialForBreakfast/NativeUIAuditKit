#!/usr/bin/env python3
"""Create a small deterministic TEST-ONLY sequence corpus; never capture/train."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw
from transition_benchmark import ROOT, file_hash, require


def generate(output):
    output = output.absolute()
    require(output.resolve().is_relative_to(ROOT) and not output.exists() and not output.is_symlink(), "new_project_local_destination_required")
    output.mkdir(parents=True)
    sequences = []
    cases = [("static","static"), ("crossfade","crossfade"), ("focus-animation","focus-animation"),
             ("scroll","scroll"), ("background-carousel","background-carousel"), ("no-focus","static"),
             ("missing-frame","static"), ("stale-cache","static"), ("timeout","static")]
    for name, scenario in cases:
        frames = []
        for i in range(6):
            ms = i*100 if name != "timeout" else i*250
            f = dict(id=str(i), observationID=f"{name}-{i}", capturedMs=ms, observedMs=ms,
                     focus="none" if name in ("no-focus","timeout") else "present",
                     truth="unstable" if name in ("crossfade","focus-animation","scroll") and i<3 else "ready")
            if name == "missing-frame" and i==2:
                f["missing"]=True;frames.append(f);continue
            if name == "stale-cache" and i>=2:
                f.update(observationID=f"{name}-0", capturedMs=0)
            image=Image.new("RGB",(128,128),(25,25,25));draw=ImageDraw.Draw(image)
            phase=min(i,3)
            draw.rectangle((16,16,95,95),fill=(100+phase*40,)*3 if name=="crossfade" else (100,100,100))
            x=20+phase*12 if name in ("focus-animation","scroll") else 20
            draw.rectangle((x,25,x+8,80),fill=(240,240,240))
            if name=="background-carousel":draw.rectangle((108,108,127,127),fill=(220 if i%2 else 30,)*3)
            path=output/f"{name}-{i}.png";image.save(path)
            f.update(path=path.name,sha256=file_hash(path),width=128,height=128);frames.append(f)
        sequences.append(dict(id=name,group=name,partition="development",sourceKind="test-only",
                              sourceReference="generate_transition_fixture-v1",labelOrigin="synthetic-generator",
                              reviewReference="deterministic-software-fixture-not-capture",scenario=scenario,startMs=0,
                              foregroundRegions=[[16,16,80,80]],regionOrigin="caller-configured",focusSource="test-only",frames=frames))
    policy=dict(version="transition-policy-v1",reference="synthetic-illustration-not-calibrated",frozenOn="test-only",
                distanceThreshold=.001,noiseThreshold=10,stableMs=200,minimumFrames=3,maxGapMs=150,
                maxAgeMs=100,timeoutMs=1000,toolTimeoutSeconds=60)
    for name,value in (("manifest.json",dict(version="transition-sequences-v1",corpusID="PER-05-test-only-v1",sequences=sequences)),("policy.json",policy)):
        (output/name).write_text(json.dumps(value,indent=2,sort_keys=True))
    return output


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--output",type=Path,required=True)
    print(generate(parser.parse_args().output))
