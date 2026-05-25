// test_model_predictions.swift
// NativeUIAuditKit/scripts
//
// Runs the trained NativeUIDetector model on a single validation image and prints
// raw VNCoreMLRequest predictions. Use this to diagnose mAP≈0 by comparing
// predicted boxes to known ground truth before the SAHI inference layer exists.
//
// Usage (from project root):
//   swift scripts/test_model_predictions.swift [path/to/image.png]
//
// Default image: validation/img_000409.png (alert + primaryButton ground truth)

import Foundation
import CoreML
import Vision
import CoreGraphics
import ImageIO

let projectRoot = URL(filePath: #filePath)
    .deletingLastPathComponent()   // scripts/
    .deletingLastPathComponent()   // project root

let modelURL = projectRoot
    .appending(path: "NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/NativeUIDetector_v1.mlpackage.mlmodel")

let defaultImage = URL(filePath: "/Users/josephmccraw/Library/Developer/CoreSimulator/Devices/812EDC32-DB8D-49D6-B130-2279180CCDEB/data/Containers/Data/Application/E0711EF5-B600-47B2-A7B8-D5BA63DE1D83/Documents/dataset/createml_export/validation/images/img_000809.png")

let imgURL: URL
if CommandLine.arguments.count > 1 {
    imgURL = URL(filePath: CommandLine.arguments[1])
} else {
    imgURL = defaultImage
}

print("Model : \(modelURL.path)")
print("Image : \(imgURL.path)")
print()

// Compile + load
let compiledURL = try MLModel.compileModel(at: modelURL)
let model = try MLModel(contentsOf: compiledURL)
let vnModel = try VNCoreMLModel(for: model)

// Load image
guard let src = CGImageSourceCreateWithURL(imgURL as CFURL, nil),
      let cgImg = CGImageSourceCreateImageAtIndex(src, 0, nil) else {
    fputs("Failed to load image\n", stderr)
    exit(1)
}
print("Image size : \(cgImg.width)×\(cgImg.height) px")
print()

// Run inference
let req = VNCoreMLRequest(model: vnModel)
req.imageCropAndScaleOption = .scaleFill

let handler = VNImageRequestHandler(cgImage: cgImg)
try handler.perform([req])

let results = (req.results as? [VNRecognizedObjectObservation]) ?? []
print("Raw detections: \(results.count) (all confidences)")
print()

// Known ground truth for img_000809 in Create ML normalized top-left coords:
//   navigationBar: cx=0.500 cy=0.104 w=1.000 h=0.063
print("Ground truth (Create ML normalized, top-left origin):")
print("  navigationBar: cx=0.500 cy=0.104 w=1.000 h=0.063")
print()

print("Predictions (Vision coords → converted to Create ML normalized top-left):")
print(String(repeating: "-", count: 80))

for (i, r) in results.enumerated() {
    let b = r.boundingBox  // Vision: bottom-left origin, normalized
    let label = r.labels.first?.identifier ?? "unknown"
    let conf = r.confidence

    // Vision → Create ML top-left normalized:
    //   cx = b.midX  (x origin same)
    //   cy = 1 - b.midY  (flip y from bottom-left to top-left)
    let cx = b.midX
    let cy = 1.0 - b.midY

    // IoU helper against alert ground truth
    func iou(cx1: Double, cy1: Double, w1: Double, h1: Double,
             cx2: Double, cy2: Double, w2: Double, h2: Double) -> Double {
        let x1l = cx1 - w1/2, x1r = cx1 + w1/2, y1t = cy1 - h1/2, y1b = cy1 + h1/2
        let x2l = cx2 - w2/2, x2r = cx2 + w2/2, y2t = cy2 - h2/2, y2b = cy2 + h2/2
        let ix = max(0, min(x1r,x2r) - max(x1l,x2l))
        let iy = max(0, min(y1b,y2b) - max(y1t,y2t))
        let inter = ix * iy
        let union = w1*h1 + w2*h2 - inter
        return union > 0 ? inter/union : 0
    }

    let iouNavBar = iou(cx1: cx, cy1: cy, w1: Double(b.width),  h1: Double(b.height),
                        cx2: 0.5, cy2: 0.104, w2: 1.0, h2: 0.063)

    print("[\(i)] \(label.padding(toLength: 18, withPad: " ", startingAt: 0)) conf=\(String(format:"%.4f",conf))  cx=\(String(format:"%.3f",cx)) cy=\(String(format:"%.3f",cy)) w=\(String(format:"%.3f",b.width)) h=\(String(format:"%.3f",b.height))  IoU(navBar)=\(String(format:"%.3f",iouNavBar))")
}
