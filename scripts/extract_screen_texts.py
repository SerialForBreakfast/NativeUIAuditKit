"""Extract Vision OCR observations and visual elements across the 8 RC561 holdout screens."""
import sys
import subprocess
import json
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import research_queue as q

CAPTURES_DIR = q.ROOT / 'reports/work/RC561/captures'
SWIFT_SCRIPT = """
import Vision
import Foundation

let path = CommandLine.arguments[1]
let url = URL(fileURLWithPath: path)
let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
let handler = VNImageRequestHandler(url: url)
try handler.perform([request])
var results: [[String: Any]] = []
for obs in request.results ?? [] {
    let text = obs.topCandidates(1).first?.string ?? ""
    let bb = obs.boundingBox
    results.append([
        "text": text,
        "x": bb.origin.x,
        "y": bb.origin.y,
        "w": bb.size.width,
        "h": bb.size.height
    ])
}
let data = try JSONSerialization.data(withJSONObject: results)
FileHandle.standardOutput.write(data)
"""

def get_text_boxes(image_path):
    proc = subprocess.run(
        ['swift', '-e', SWIFT_SCRIPT, str(image_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False
    )
    if proc.returncode != 0:
        print(f"Error running Swift OCR on {image_path.name}: {proc.stderr.decode('utf-8')}")
        return []
    return json.loads(proc.stdout.decode('utf-8'))

def main():
    captures = sorted(CAPTURES_DIR.glob('*.png'))
    for cap in captures:
        boxes = get_text_boxes(cap)
        print(f"\n=== {cap.name} (Found {len(boxes)} text regions) ===")
        for b in boxes[:10]:
            # Convert Vision coords (origin bottom-left, normalized) to pixels (origin top-left)
            # w=3840, h=2160
            x = round(b['x'] * 3840, 1)
            y = round((1.0 - b['y'] - b['h']) * 2160, 1)
            w = round(b['w'] * 3840, 1)
            h = round(b['h'] * 2160, 1)
            print(f"  '{b['text']}': x={x}, y={y}, w={w}, h={h}")
        if len(boxes) > 10:
            print(f"  ... and {len(boxes) - 10} more.")

if __name__ == '__main__':
    main()
