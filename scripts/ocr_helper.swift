import Vision
import Cocoa

let args = CommandLine.arguments
guard args.count > 1 else { exit(1) }
let imagePath = args[1]
let structured = args.dropFirst(2).contains("--json")

guard let img = NSImage(contentsOfFile: imagePath),
      let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { exit(1) }

var items: [(String, Double, Double)] = []
var regions: [[String: Any]] = []
let req = VNRecognizeTextRequest { req, _ in
    guard let obs = req.results as? [VNRecognizedTextObservation] else { return }
    for o in obs {
        if let s = o.topCandidates(1).first?.string {
            let b = o.boundingBox
            items.append((s, b.origin.x * 1920.0, (1.0 - b.origin.y - b.size.height) * 1080.0))
            regions.append(["text": s, "confidence": Double(o.topCandidates(1).first!.confidence),
                "xyxy": [b.minX * Double(cg.width), (1-b.maxY) * Double(cg.height),
                         b.maxX * Double(cg.width), (1-b.minY) * Double(cg.height)]])
        }
    }
}
req.recognitionLevel = .accurate
do { try VNImageRequestHandler(cgImage: cg, options: [:]).perform([req]) }
catch { fputs("ocr_failed\n", stderr); exit(2) }
if structured {
    let doc: [String: Any] = ["version": "vision-ocr-regions-v1", "width": cg.width,
        "height": cg.height, "coordinates": "top-left-pixel-xyxy", "regions": regions]
    let data = try JSONSerialization.data(withJSONObject: doc, options: [.sortedKeys])
    FileHandle.standardOutput.write(data)
    exit(0)
}
items.sort { $0.2 < $1.2 }
for i in items {
    print("\(i.0)|\(Int(i.1))|\(Int(i.2))")
}
