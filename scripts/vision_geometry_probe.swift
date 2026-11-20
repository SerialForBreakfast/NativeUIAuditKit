import AppKit
import Foundation
import Vision

struct RequestDoc: Decodable {
    let images: [String]
}

struct RectOut: Encodable {
    let xyxy: [Double]
    let confidence: Double
}

struct TextOut: Encodable {
    let text: String
    let xyxy: [Double]
    let confidence: Double
}

struct FrameOut: Encodable {
    let path: String
    let width: Int
    let height: Int
    let rects: [RectOut]
    let texts: [TextOut]
}

func analyzeImage(path: String) -> FrameOut? {
    guard let img = NSImage(contentsOfFile: path),
          let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil)
    else { return nil }
    let w = Double(cg.width)
    let h = Double(cg.height)

    var texts: [TextOut] = []
    let textReq = VNRecognizeTextRequest()
    textReq.recognitionLevel = .accurate
    textReq.usesLanguageCorrection = false

    var rects: [RectOut] = []
    let rectReq = VNDetectRectanglesRequest()
    rectReq.minimumAspectRatio = 0.15
    rectReq.maximumAspectRatio = 15.0
    rectReq.minimumSize = 0.025
    rectReq.minimumConfidence = 0.4
    rectReq.maximumObservations = 48
    rectReq.quadratureTolerance = 12.0

    let handler = VNImageRequestHandler(cgImage: cg, options: [:])
    try? handler.perform([textReq, rectReq])

    if let obs = textReq.results {
        for o in obs {
            guard let top = o.topCandidates(1).first else { continue }
            let b = o.boundingBox
            texts.append(TextOut(
                text: top.string,
                xyxy: [
                    max(0, b.minX * w),
                    max(0, (1.0 - b.maxY) * h),
                    min(w, b.maxX * w),
                    min(h, (1.0 - b.minY) * h),
                ],
                confidence: Double(top.confidence)
            ))
        }
    }
    if let robs = rectReq.results {
        for r in robs {
            let b = r.boundingBox
            rects.append(RectOut(
                xyxy: [
                    max(0, b.minX * w),
                    max(0, (1.0 - b.maxY) * h),
                    min(w, b.maxX * w),
                    min(h, (1.0 - b.minY) * h),
                ],
                confidence: Double(r.confidence)
            ))
        }
    }
    return FrameOut(path: path, width: cg.width, height: cg.height, rects: rects, texts: texts)
}

guard CommandLine.arguments.count >= 2 else {
    fputs("Usage: vision_geometry_probe REQUEST_JSON\n", stderr)
    exit(1)
}
let reqURL = URL(fileURLWithPath: CommandLine.arguments[1])
let reqData = try Data(contentsOf: reqURL)
let reqDoc = try JSONDecoder().decode(RequestDoc.self, from: reqData)
var frames: [FrameOut] = []
for p in reqDoc.images {
    if let f = analyzeImage(path: p) {
        frames.append(f)
    }
}
let enc = JSONEncoder()
enc.outputFormatting = [.sortedKeys]
let outData = try enc.encode(frames)
FileHandle.standardOutput.write(outData)
