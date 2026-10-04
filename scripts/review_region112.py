"""Render all retained Region focus strips for visual label review, not model crops."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw
from intake_shadow111 import read, member, sha
from shadow_feedback_contract import require


def render(root,out):
    root=root.resolve();out=out.resolve();out.relative_to(Path(__file__).resolve().parents[1])
    require(not out.exists(),'output_collision')
    manifest=read(root/'manifest.json');survey=read(root/'survey.json')
    require(len(survey['records'])==95 and manifest['frames']==95,'review_scope')
    out.mkdir(parents=True);index=[]
    for start in range(0,95,24):
        sheet=Image.new('RGB',(1800,1800),'#333333');draw=ImageDraw.Draw(sheet)
        for offset,r in enumerate(survey['records'][start:start+24]):
            path=member(root,r['image']);require(sha(path)==r['image_sha256'],'changed_pixels')
            # Fixed screen region, not a prediction- or label-derived body/crop.
            # Includes adjacent rows so the bright selected row can be distinguished.
            with Image.open(path) as im:
                require(im.size==(3840,2160),'viewport')
                strip=im.convert('RGB').crop((2080,1590,3720,1840)).resize((820,125))
            x=(offset%2)*900;y=(offset//2)*150
            sheet.paste(strip,(x+65,y+20));draw.text((x+5,y+60),str(r['sequence']),fill='white')
            index.append(dict(sequence=r['sequence'],image_sha256=r['image_sha256'],
                sheet=f'review-{start//24+1}.png',cell=offset,region=[2080,1590,3720,1840]))
        sheet.save(out/f'review-{start//24+1}.png')
    (out/'index.json').write_text(json.dumps(dict(source_manifest_sha256=sha(root/'manifest.json'),
        purpose='visual_identity_review_not_training_crop',records=index),indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();render(a.root,a.output)
