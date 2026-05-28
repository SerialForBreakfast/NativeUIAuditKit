// diagnose_textfield_fps.swift
// NativeUIAuditKit/scripts
//
// Classifies each textField false positive from the strip pass as either:
//
//   A) NEAR-DUPLICATE — FP has partial IoU with a real textField GT (same element
//      detected from a different strip, slightly offset in y). These would be fixed
//      by tighter NMS or strip-level deduplication. No retraining needed.
//
//   B) FALSE-CLASS — FP has zero IoU with any textField GT (model fired on a
//      non-textField element). These require hard-negative training data.
//
// Thresholds used:
//   - IoU ≥ 0.50 → TP (matched correctly)
//   - 0.05 ≤ IoU < 0.50 → NEAR-DUPLICATE (some overlap but not matched)
//   - IoU < 0.05 → FALSE-CLASS (no meaningful overlap with any GT textField)
//
// Also reports: strip index distribution, y-fraction distribution, worst images.
//
// Usage (from project root):
//   swift scripts/diagnose_textfield_fps.swift

import Foundation
import CoreML
import Vision
import CoreGraphics
import ImageIO

// MARK: - Config

let projectRoot = URL(filePath: #filePath)
    .deletingLastPathComponent()
    .deletingLastPathComponent()

let modelURL = projectRoot
    .appending(path: "NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/NativeUIDetector_v1.mlpackage.mlmodel")

let valAnnotationURL = URL(filePath: "/Users/josephmccraw/Library/Developer/CoreSimulator/Devices/812EDC32-DB8D-49D6-B130-2279180CCDEB/data/Containers/Data/Application/E0711EF5-B600-47B2-A7B8-D5BA63DE1D83/Documents/dataset/createml_export/validation/annotations.json")

let valImagesDir = URL(filePath: "/Users/josephmccraw/Library/Developer/CoreSimulator/Devices/812EDC32-DB8D-49D6-B130-2279180CCDEB/data/Containers/Data/Application/E0711EF5-B600-47B2-A7B8-D5BA63DE1D83/Documents/dataset/createml_export/validation/images")

let confThreshold: Float = 0.10
let nmsThreshold   = 0.30
let tpIoUThreshold = 0.50

// IoU boundary between "near-duplicate" and "false-class"
let nearDupMinIoU  = 0.05   // anything ≥ this with a GT textField = near-dup

// MARK: - Types

struct GTBox {
    let cx, cy, w, h: Double
    var x1: Double { cx - w/2 }
    var x2: Double { cx + w/2 }
    var y1: Double { cy - h/2 }
    var y2: Double { cy + h/2 }
}

struct Prediction {
    let conf: Float
    let cx, cy, w, h: Double
    let stripIdx: Int
    let stripYFrac: Double   // y of strip top, as fraction of image height (0=top, 1=bottom)
    var x1: Double { cx - w/2 }
    var x2: Double { cx + w/2 }
    var y1: Double { cy - h/2 }
    var y2: Double { cy + h/2 }
}

func iouGT(_ a: GTBox, _ b: Prediction) -> Double {
    let ix = max(0, min(a.x2, b.x2) - max(a.x1, b.x1))
    let iy = max(0, min(a.y2, b.y2) - max(a.y1, b.y1))
    let inter = ix * iy
    let union = a.w*a.h + b.w*b.h - inter
    return union > 0 ? inter/union : 0
}

func iouPred(_ a: Prediction, _ b: Prediction) -> Double {
    let ix = max(0, min(a.x2, b.x2) - max(a.x1, b.x1))
    let iy = max(0, min(a.y2, b.y2) - max(a.y1, b.y1))
    let inter = ix * iy
    let union = a.w*a.h + b.w*b.h - inter
    return union > 0 ? inter/union : 0
}

func nmsPreds(_ preds: [Prediction], iouThresh: Double) -> [Prediction] {
    let sorted = preds.sorted { $0.conf > $1.conf }
    var kept: [Prediction] = []
    var suppressed = Set<Int>()
    for (i, a) in sorted.enumerated() {
        if suppressed.contains(i) { continue }
        kept.append(a)
        for (j, b) in sorted.enumerated() where j > i {
            if suppressed.contains(j) { continue }
            if iouPred(a, b) > iouThresh { suppressed.insert(j) }
        }
    }
    return kept
}

// MARK: - Image helpers

func cropCGImage(source: CGImage, x: Int, y: Int, width: Int, height: Int) -> CGImage? {
    guard let ctx = CGContext(
        data: nil, width: width, height: height,
        bitsPerComponent: 8, bytesPerRow: 0,
        space: CGColorSpaceCreateDeviceRGB(),
        bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue
    ) else { return nil }
    ctx.draw(source, in: CGRect(x: -x, y: -(source.height - y - height),
                                 width: source.width, height: source.height))
    return ctx.makeImage()
}

// MARK: - Load model

print("Loading model...")
let compiledURL = try MLModel.compileModel(at: modelURL)
let vnModel = try VNCoreMLModel(for: MLModel(contentsOf: compiledURL))
print("Model loaded ✓\n")

// MARK: - Load annotations

struct AnnEntry: Decodable {
    let imagefilename: String
    let annotation: [AnnBox]
    struct AnnBox: Decodable {
        let label: String
        let coordinates: Coords
        struct Coords: Decodable { let x, y, width, height: Double }
    }
}

let annData = try Data(contentsOf: valAnnotationURL)
let annEntries = try JSONDecoder().decode([AnnEntry].self, from: annData)

// Only process images that have at least one textField GT
let tfEntries = annEntries.filter { $0.annotation.contains { $0.label == "textField" } }
print("Images with textField GT: \(tfEntries.count)")
print("Running strip pass on each...\n")
print(String(repeating: "─", count: 70))

// MARK: - Per-image analysis

var totalTP        = 0
var totalNearDup   = 0   // FP with IoU ≥ nearDupMinIoU vs any GT textField
var totalFalseClass = 0  // FP with IoU < nearDupMinIoU vs all GT textFields
var totalMissed    = 0   // GT textFields with no matching prediction

// For distribution analysis
var nearDupIoUs: [Double] = []
var falseClassStripYFracs: [Double] = []
var nearDupStripYFracs: [Double] = []

struct ImageResult {
    let filename: String
    let nGT: Int
    let nTP: Int
    let nNearDup: Int
    let nFalseClass: Int
    let nMissed: Int
}
var imageResults: [ImageResult] = []

for entry in tfEntries {
    let imgURL = valImagesDir.appending(path: entry.imagefilename)
    guard let src = CGImageSourceCreateWithURL(imgURL as CFURL, nil),
          let cgImg = CGImageSourceCreateImageAtIndex(src, 0, nil) else {
        print("⚠ Could not load \(entry.imagefilename)")
        continue
    }

    let gtBoxes: [GTBox] = entry.annotation
        .filter { $0.label == "textField" }
        .map { GTBox(cx: $0.coordinates.x, cy: $0.coordinates.y,
                     w: $0.coordinates.width, h: $0.coordinates.height) }

    // Run strip pass, collect textField predictions with strip metadata
    let imgH = cgImg.height, imgW = cgImg.width
    let stripH = max(1, Int(Double(imgH) * 0.22))
    let stride  = max(1, stripH / 2)
    var rawPreds: [Prediction] = []
    var y = 0, stripIdx = 0

    while y + stripH <= imgH {
        if let strip = cropCGImage(source: cgImg, x: 0, y: y, width: imgW, height: stripH) {
            let req = VNCoreMLRequest(model: vnModel)
            req.imageCropAndScaleOption = .scaleFill
            try? VNImageRequestHandler(cgImage: strip, options: [:]).perform([req])

            let obs = (req.results as? [VNRecognizedObjectObservation] ?? [])
                .filter { $0.confidence >= confThreshold &&
                          $0.labels.first?.identifier == "textField" }

            let stripTopVision    = 1.0 - Double(y + stripH) / Double(imgH)
            let stripHeightVision = Double(stripH) / Double(imgH)
            let stripYFrac        = Double(y) / Double(imgH)

            for o in obs {
                let b = o.boundingBox
                let fullVisionMidY = stripTopVision + Double(b.midY) * stripHeightVision
                let fullH  = Double(b.height) * stripHeightVision
                let fullCX = Double(b.midX)
                let fullCY = 1.0 - fullVisionMidY

                rawPreds.append(Prediction(
                    conf: o.confidence,
                    cx: fullCX, cy: fullCY, w: Double(b.width), h: fullH,
                    stripIdx: stripIdx, stripYFrac: stripYFrac
                ))
            }
        }
        y += stride
        stripIdx += 1
    }

    // NMS
    let preds = nmsPreds(rawPreds, iouThresh: nmsThreshold)

    // Match predictions to GTs (greedy, descending confidence)
    var matchedGTs = Set<Int>()
    var matchedPreds = Set<Int>()
    var tp = 0, nearDup = 0, falseClass = 0

    for (pi, pred) in preds.sorted(by: { $0.conf > $1.conf }).enumerated() {
        var bestIoU = 0.0, bestIdx = -1
        for (gi, gt) in gtBoxes.enumerated() {
            if matchedGTs.contains(gi) { continue }
            let score = iouGT(gt, pred)
            if score > bestIoU { bestIoU = score; bestIdx = gi }
        }
        if bestIoU >= tpIoUThreshold {
            tp += 1
            matchedGTs.insert(bestIdx)
            matchedPreds.insert(pi)
        }
    }

    // Classify FPs
    let sortedPreds = preds.sorted(by: { $0.conf > $1.conf })
    for (pi, pred) in sortedPreds.enumerated() {
        if matchedPreds.contains(pi) { continue }  // it's a TP, skip

        // Find best IoU with any GT textField (regardless of matched status)
        let maxGTIoU = gtBoxes.map { iouGT($0, pred) }.max() ?? 0.0

        if maxGTIoU >= nearDupMinIoU {
            nearDup += 1
            nearDupIoUs.append(maxGTIoU)
            nearDupStripYFracs.append(pred.stripYFrac)
        } else {
            falseClass += 1
            falseClassStripYFracs.append(pred.stripYFrac)
        }
    }

    let missed = gtBoxes.count - tp
    totalTP        += tp
    totalNearDup   += nearDup
    totalFalseClass += falseClass
    totalMissed    += missed

    imageResults.append(ImageResult(
        filename: entry.imagefilename,
        nGT: gtBoxes.count, nTP: tp,
        nNearDup: nearDup, nFalseClass: falseClass,
        nMissed: missed
    ))
}

// MARK: - Report

let totalFP = totalNearDup + totalFalseClass
let totalPred = totalTP + totalFP

print("\n── textField FP Classification ─────────────────────────────────────")
print("  Images with textField GT : \(tfEntries.count)")
print("  Total predictions        : \(totalPred)")
print("  True positives (IoU≥0.50): \(totalTP)  (recall=\(String(format:"%.3f", Double(totalTP)/Double(totalTP+totalMissed))))")
print("  Missed GTs               : \(totalMissed)")
print("  Total FPs                : \(totalFP)  (precision=\(String(format:"%.3f", Double(totalTP)/Double(totalPred))))")
print()
print("  FP breakdown:")
print("    NEAR-DUPLICATE  (IoU ≥ \(nearDupMinIoU) with a GT textField): \(totalNearDup)  (\(String(format:"%.1f", Double(totalNearDup)/Double(max(1,totalFP))*100))%)")
print("    FALSE-CLASS     (IoU < \(nearDupMinIoU), no GT nearby)      : \(totalFalseClass)  (\(String(format:"%.1f", Double(totalFalseClass)/Double(max(1,totalFP))*100))%)")

// Near-dup IoU histogram
if !nearDupIoUs.isEmpty {
    print("\n── Near-duplicate IoU distribution (0=no overlap, 0.5=would-be-TP) ──")
    let buckets = [(0.05,0.10,"0.05–0.10"), (0.10,0.20,"0.10–0.20"), (0.20,0.30,"0.20–0.30"),
                   (0.30,0.40,"0.30–0.40"), (0.40,0.50,"0.40–0.50")]
    for (lo, hi, label) in buckets {
        let n = nearDupIoUs.filter { $0 >= lo && $0 < hi }.count
        let bar = String(repeating: "█", count: n * 30 / (nearDupIoUs.count + 1))
        print("  \(label) : \(String(format:"%4d", n))  \(bar)")
    }
    let avg = nearDupIoUs.reduce(0,+) / Double(nearDupIoUs.count)
    print("  avg near-dup IoU: \(String(format:"%.3f", avg))")
}

// Y-fraction distribution
func yFracHistogram(_ fracs: [Double], label: String) {
    guard !fracs.isEmpty else { return }
    print("\n── \(label) — strip y-start distribution ──")
    let buckets: [(Double,Double,String)] = [
        (0.0,0.15,"0.00–0.15 (top, navBar zone)"),
        (0.15,0.35,"0.15–0.35 (upper-mid)"),
        (0.35,0.55,"0.35–0.55 (center)"),
        (0.55,0.75,"0.55–0.75 (lower-mid)"),
        (0.75,1.01,"0.75–1.00 (bottom)")
    ]
    for (lo, hi, label) in buckets {
        let n = fracs.filter { $0 >= lo && $0 < hi }.count
        let bar = String(repeating: "█", count: n * 30 / (fracs.count + 1))
        print("  \(label.padding(toLength: 35, withPad:" ", startingAt:0)): \(String(format:"%4d", n))  \(bar)")
    }
}

yFracHistogram(nearDupStripYFracs, label: "Near-duplicate FPs")
yFracHistogram(falseClassStripYFracs, label: "False-class FPs")

// Worst images
print("\n── Top 10 worst images by total FP count ───────────────────────────")
print("  filename                               GT  TP  nearDup  falseClass  missed")
let worst = imageResults.sorted { ($0.nNearDup+$0.nFalseClass) > ($1.nNearDup+$1.nFalseClass) }.prefix(10)
for r in worst {
    let name = r.filename.padding(toLength: 40, withPad: " ", startingAt: 0)
    print("  \(name) \(r.nGT)   \(r.nTP)   \(r.nNearDup)        \(r.nFalseClass)           \(r.nMissed)")
}

print("\n── Interpretation ──────────────────────────────────────────────────")
print("  If NEAR-DUPLICATE >> FALSE-CLASS:")
print("    → Same textField detected from multiple strips; tighter dedup may help")
print("    → Consider: lower NMS threshold for textField, or x-overlap grouping")
print("  If FALSE-CLASS >> NEAR-DUPLICATE:")
print("    → Model fires on non-textField elements in strip context")
print("    → Requires hard-negative training data (sliders, dividers, search bars)")
print(String(repeating: "─", count: 70))
