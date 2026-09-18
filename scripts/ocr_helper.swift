import Vision
import Cocoa

let args = CommandLine.arguments
guard args.count > 1 else { exit(1) }
let imagePath = args[1]

guard let img = NSImage(contentsOfFile: imagePath),
      let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { exit(1) }

var items: [(String, Double, Double)] = []
let req = VNRecognizeTextRequest { req, _ in
    guard let obs = req.results as? [VNRecognizedTextObservation] else { return }
    for o in obs {
        if let s = o.topCandidates(1).first?.string {
            let b = o.boundingBox
            items.append((s, b.origin.x * 1920.0, (1.0 - b.origin.y - b.size.height) * 1080.0))
        }
    }
}
req.recognitionLevel = .accurate
try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
items.sort { $0.2 < $1.2 }
for i in items {
    print("\(i.0)|\(Int(i.1))|\(Int(i.2))")
}
