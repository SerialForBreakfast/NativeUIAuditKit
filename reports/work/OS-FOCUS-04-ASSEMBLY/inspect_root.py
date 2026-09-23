"""Contact sheets from already production-rendered crops; no cropper or inference."""
import json
from pathlib import Path
from PIL import Image, ImageDraw

HERE=Path(__file__).resolve().parent
root=HERE/"root-runtime-crops"
doc=json.loads((root/"manifest.json").read_text())
for start in range(0,len(doc["pairs"]),4):
    pairs=doc["pairs"][start:start+4]
    sheet=Image.new("RGB",(1024,560),"#202020"); draw=ImageDraw.Draw(sheet)
    for i,pair in enumerate(pairs):
        for j,role in enumerate(("focused","unfocused")):
            with Image.open(root/pair["frames"][role]["crop"]) as crop:
                if crop.size!=(256,256): raise ValueError("invalid_crop_size")
                sheet.paste(crop,(i*256,j*280))
            draw.text((i*256+3,j*280+258),pair["elementID"][:24]+" "+role,fill="white")
    sheet.save(HERE/f"root-review-{start//4}.png")
print(doc["manifestSHA256"])
