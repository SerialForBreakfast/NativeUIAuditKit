// Read-only Vision reproduction of the existing ROI anchor test; no policy change.
import Foundation
import CoreGraphics
import ImageIO
import Vision

let url = URL(fileURLWithPath: CommandLine.arguments[1])
let source = CGImageSourceCreateWithURL(url as CFURL, nil)!
let image = CGImageSourceCreateImageAtIndex(source, 0, nil)!
func recognize(_ roi: CGRect) throws -> [VNRecognizedTextObservation] {
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = true
    request.recognitionLanguages = ["en-US", "en-GB"]
    request.regionOfInterest = roi
    try VNImageRequestHandler(cgImage: image, options: [:]).perform([request])
    return request.results ?? []
}
let full = try recognize(CGRect(x: 0, y: 0, width: 1, height: 1))
let target = full.first { ($0.topCandidates(1).first?.string.count ?? 0) >= 3 }!
let box = target.boundingBox
let w = Double(image.width), h = Double(image.height), pad = 20.0
let px = max(0, box.minX*w-pad), py = max(0, (1-box.maxY)*h-pad)
let pw = box.width*w+2*pad, ph = box.height*h+2*pad
let roi = CGRect(x: px/w, y: 1-(py+ph)/h, width: pw/w, height: ph/h)
print("target:", target.topCandidates(1)[0].string, "box:", box, "roi:", roi)
for item in try recognize(roi) { print("roi text:", item.topCandidates(1)[0].string, "box:", item.boundingBox) }
