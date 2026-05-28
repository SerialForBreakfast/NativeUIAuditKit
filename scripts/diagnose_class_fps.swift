// diagnose_class_fps.swift
// NativeUIAuditKit/scripts
//
// Generalised FP classifier for any detection class. Mirrors diagnose_textfield_fps.swift
// but handles classes that use BOTH the full-image pass and the strip pass.
//
// For each FP prediction it reports:
//   NEAR-DUPLICATE  — IoU ≥ 0.05 with a matched GT of the same class
//                     (same element, slightly off position — NMS gap or scale mismatch)
//   FALSE-CLASS     — IoU < 0.05 with all GTs (model fired on wrong element)
//
// Also reports:
//   • Confidence distribution: TP vs FP mean/median (for confidence-threshold experiment)
//   • Strip y-fraction distribution for strip-pass FPs
//   • Per-image table of worst offenders
//
// Usage (from project root):
//   swift scripts/diagnose_class_fps.swift primaryButton
//   swift scripts/diagnose_class_fps.swift toggle

import Foundation
import CoreML
import Vision
import CoreGraphics
import ImageIO

// MARK: - Config

guard CommandLine.arguments.count > 1 else {
    fputs("Usage: swift diagnose_class_fps.swift <className>\n", stderr)
    exit(1)
}
let targetClass = CommandLine.arguments[1]

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
let nearDupMinIoU  = 0.05

// Classes that use BOTH full-image and strip passes (per Run 004 routing)
let fullImageClasses: Set<String> = ["alert", "primaryButton", "toggle"]
let stripClasses:     Set<String> = ["navigationBar", "textField", "primaryButton", "toggle"]

// MARK: - Types

struct GTBox {
    let cx, cy, w, h: Double
    var x1: Double { cx - w/2 }; var x2: Double { cx + w/2 }
    var y1: Double { cy - h/2 }; var y2: Double { cy + h/2 }
}

struct Prediction {
    let conf: Float
    let cx, cy, w, h: Double
    let source: String    // "full" or "strip"
    let stripYFrac: Double
    var x1: Double { cx - w/2 }; var x2: Double { cx + w/2 }
    var y1: Double { cy - h/2 }; var y2: Double { cy + h/2 }
}

func iouGT(_ a: GTBox, _ b: Prediction) -> Double {
    let ix = max(0, min(a.x2,b.x2) - max(a.x1,b.x1))
    let iy = max(0, min(a.y2,b.y2) - max(a.y1,b.y1))
    let inter = ix * iy
    let union = a.w*a.h + b.w*b.h - inter
    return union > 0 ? inter/union : 0
}
func iouPred(_ a: Prediction, _ b: Prediction) -> Double {
    let ix = max(0, min(a.x2,b.x2) - max(a.x1,b.x1))
    let iy = max(0, min(a.y2,b.y2) - max(a.y1,b.y1))
    let inter = ix * iy
    let union = a.w*a.h + b.w*b.h - inter
    return union > 0 ? inter/union : 0
}
func nms(_ preds: [Prediction], thresh: Double) -> [Prediction] {
    let sorted = preds.sorted { $0.conf > $1.conf }
    var kept: [Prediction] = []; var sup = Set<Int>()
    for (i, a) in sorted.enumerated() {
        if sup.contains(i) { continue }; kept.append(a)
        for (j, b) in sorted.enumerated() where j > i {
            if sup.contains(j) { continue }
            if iouPred(a, b) > thresh { sup.insert(j) }
        }
    }
    return kept
}

// MARK: - Image helpers

func cropCGImage(source: CGImage, x: Int, y: Int, width: Int, height: Int) -> CGImage? {
    guard let ctx = CGContext(data: nil, width: width, height: height,
                              bitsPerComponent: 8, bytesPerRow: 0,
                              space: CGColorSpaceCreateDeviceRGB(),
                              bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue) else { return nil }
    ctx.draw(source, in: CGRect(x: -x, y: -(source.height - y - height),
                                width: source.width, height: source.height))
    return ctx.makeImage()
}

func runRequest(on image: CGImage, model: VNCoreMLModel) throws -> [VNRecognizedObjectObservation] {
    let req = VNCoreMLRequest(model: model)
    req.imageCropAndScaleOption = .scaleFill
    try VNImageRequestHandler(cgImage: image, options: [:]).perform([req])
    return req.results as? [VNRecognizedObjectObservation] ?? []
}

// MARK: - Load model + annotations

print("Loading model...")
let compiledURL = try MLModel.compileModel(at: modelURL)
let vnModel = try VNCoreMLModel(for: MLModel(contentsOf: compiledURL))
print("Model loaded ✓")

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

// All validation images (we want FPs from non-target images too)
let targetEntries = annEntries   // process all; GTs may be empty for some images
let gtImages = annEntries.filter { $0.annotation.contains { $0.label == targetClass } }
print("All val images: \(annEntries.count) | images with \(targetClass) GT: \(gtImages.count)\n")
print(String(repeating: "─", count: 70))

// MARK: - Per-image analysis

var totalTP = 0, totalNearDup = 0, totalFalseClass = 0, totalMissed = 0, totalGT = 0
var tpConfs: [Float] = [], fpConfs: [Float] = []
var nearDupIoUs: [Double] = []
var fpStripYFracs: [Double] = [], fpFullImageCount = 0

struct ImgResult {
    let filename: String; let nGT, nTP, nNearDup, nFalseClass, nMissed: Int
}
var imageResults: [ImgResult] = []

var processed = 0
for entry in annEntries {
    let gts: [GTBox] = entry.annotation
        .filter { $0.label == targetClass }
        .map { GTBox(cx: $0.coordinates.x, cy: $0.coordinates.y,
                     w: $0.coordinates.width, h: $0.coordinates.height) }

    let imgURL = valImagesDir.appending(path: entry.imagefilename)
    guard let src = CGImageSourceCreateWithURL(imgURL as CFURL, nil),
          let cgImg = CGImageSourceCreateImageAtIndex(src, 0, nil) else { continue }

    var rawPreds: [Prediction] = []

    // Full-image pass (if class uses it)
    if fullImageClasses.contains(targetClass) {
        let obs = (try? runRequest(on: cgImg, model: vnModel)) ?? []
        for o in obs where o.confidence >= confThreshold
                        && o.labels.first?.identifier == targetClass {
            let b = o.boundingBox
            rawPreds.append(Prediction(conf: o.confidence,
                cx: Double(b.midX), cy: 1.0 - Double(b.midY),
                w: Double(b.width), h: Double(b.height),
                source: "full", stripYFrac: -1))
        }
    }

    // Strip pass (if class uses it)
    if stripClasses.contains(targetClass) {
        let imgH = cgImg.height, imgW = cgImg.width
        let stripH = max(1, Int(Double(imgH) * 0.22))
        let stride  = max(1, stripH / 2)
        var y = 0
        while y + stripH <= imgH {
            if let strip = cropCGImage(source: cgImg, x: 0, y: y, width: imgW, height: stripH) {
                let obs = (try? runRequest(on: strip, model: vnModel)) ?? []
                let stripTopVision    = 1.0 - Double(y + stripH) / Double(imgH)
                let stripHeightVision = Double(stripH) / Double(imgH)
                let stripYFrac        = Double(y) / Double(imgH)
                for o in obs where o.confidence >= confThreshold
                                && o.labels.first?.identifier == targetClass {
                    let b = o.boundingBox
                    let fullVisionMidY = stripTopVision + Double(b.midY) * stripHeightVision
                    rawPreds.append(Prediction(
                        conf: o.confidence,
                        cx: Double(b.midX), cy: 1.0 - fullVisionMidY,
                        w: Double(b.width), h: Double(b.height) * stripHeightVision,
                        source: "strip", stripYFrac: stripYFrac))
                }
            }
            y += stride
        }
    }

    let preds = nms(rawPreds, thresh: nmsThreshold)

    // Match to GTs
    var matchedGTs = Set<Int>(); var matchedPreds = Set<Int>()
    var tp = 0
    for (pi, pred) in preds.sorted(by: { $0.conf > $1.conf }).enumerated() {
        var bestIoU = 0.0, bestIdx = -1
        for (gi, gt) in gts.enumerated() {
            if matchedGTs.contains(gi) { continue }
            let s = iouGT(gt, pred)
            if s > bestIoU { bestIoU = s; bestIdx = gi }
        }
        if bestIoU >= tpIoUThreshold {
            tp += 1; matchedGTs.insert(bestIdx); matchedPreds.insert(pi)
            tpConfs.append(pred.conf)
        }
    }

    // Classify FPs
    var nearDup = 0, falseClass = 0
    for (pi, pred) in preds.sorted(by: { $0.conf > $1.conf }).enumerated() {
        if matchedPreds.contains(pi) { continue }
        fpConfs.append(pred.conf)
        let maxIoU = gts.map { iouGT($0, pred) }.max() ?? 0.0
        if maxIoU >= nearDupMinIoU {
            nearDup += 1; nearDupIoUs.append(maxIoU)
            if pred.source == "strip" { fpStripYFracs.append(pred.stripYFrac) }
            else { fpFullImageCount += 1 }
        } else {
            falseClass += 1
            if pred.source == "strip" { fpStripYFracs.append(pred.stripYFrac) }
            else { fpFullImageCount += 1 }
        }
    }

    let missed = gts.count - tp
    totalTP += tp; totalNearDup += nearDup; totalFalseClass += falseClass
    totalMissed += missed; totalGT += gts.count
    if nearDup + falseClass > 0 || missed > 0 {
        imageResults.append(ImgResult(filename: entry.imagefilename, nGT: gts.count,
            nTP: tp, nNearDup: nearDup, nFalseClass: falseClass, nMissed: missed))
    }
    processed += 1
    if processed % 200 == 0 { print("  \(processed)/\(annEntries.count)...") }
}

// MARK: - Report

let totalFP = totalNearDup + totalFalseClass
let totalPred = totalTP + totalFP

func avg(_ a: [Float]) -> Float { a.isEmpty ? 0 : a.reduce(0,+)/Float(a.count) }
func med(_ a: [Float]) -> Float {
    guard !a.isEmpty else { return 0 }
    let s = a.sorted(); let n = s.count
    return n % 2 == 0 ? (s[n/2-1]+s[n/2])/2 : s[n/2]
}

print("\n── \(targetClass) FP Classification (\(annEntries.count) val images) ──────────────────")
print("  Total GT instances   : \(totalGT)  (in \(gtImages.count) images)")
print("  Total predictions    : \(totalPred)")
print("  True positives       : \(totalTP)  recall=\(String(format:"%.3f", totalGT > 0 ? Double(totalTP)/Double(totalGT) : 0))")
print("  Missed GTs           : \(totalMissed)")
print("  Total FPs            : \(totalFP)  precision=\(String(format:"%.3f", totalPred > 0 ? Double(totalTP)/Double(totalPred) : 0))")
print()
print("  FP breakdown:")
print("    NEAR-DUPLICATE (IoU ≥ \(nearDupMinIoU) with a GT): \(totalNearDup)  (\(String(format:"%.1f", totalFP > 0 ? Double(totalNearDup)/Double(totalFP)*100 : 0))%)")
print("    FALSE-CLASS    (IoU < \(nearDupMinIoU), no GT nearby): \(totalFalseClass)  (\(String(format:"%.1f", totalFP > 0 ? Double(totalFalseClass)/Double(totalFP)*100 : 0))%)")

// ── Confidence experiment ──────────────────────────────────────────
print("\n── Confidence distribution (TP vs FP) ─────────────────────────────")
print("  TP confidence — mean: \(String(format:"%.3f", avg(tpConfs)))  median: \(String(format:"%.3f", med(tpConfs)))  n=\(tpConfs.count)")
print("  FP confidence — mean: \(String(format:"%.3f", avg(fpConfs)))  median: \(String(format:"%.3f", med(fpConfs)))  n=\(fpConfs.count)")

// Precision at various thresholds
print("\n  Precision at confidence thresholds (recall in parentheses):")
for thresh: Float in [0.10, 0.30, 0.50, 0.70, 0.90, 0.95] {
    let tpAbove = tpConfs.filter { $0 >= thresh }.count
    let fpAbove = fpConfs.filter { $0 >= thresh }.count
    let predAbove = tpAbove + fpAbove
    let prec = predAbove > 0 ? Double(tpAbove)/Double(predAbove) : 0
    let rec  = totalGT > 0 ? Double(tpAbove)/Double(totalGT) : 0
    let indicator = prec >= 0.50 ? "✓" : "✗"
    print("  \(indicator) conf≥\(String(format:"%.2f", thresh)): precision=\(String(format:"%.3f", prec))  recall=\(String(format:"%.3f", rec))  pred=\(predAbove)")
}

// ── Strip y-fraction of FPs ────────────────────────────────────────
if !fpStripYFracs.isEmpty {
    print("\n── FP strip y-start distribution ──────────────────────────────────")
    let buckets: [(Double,Double,String)] = [
        (0.0,0.15,"0.00–0.15 (top / navBar zone)"),
        (0.15,0.35,"0.15–0.35 (upper-mid)"),
        (0.35,0.55,"0.35–0.55 (center)"),
        (0.55,0.75,"0.55–0.75 (lower-mid)"),
        (0.75,1.01,"0.75–1.00 (bottom / tab bar zone)")
    ]
    for (lo, hi, label) in buckets {
        let n = fpStripYFracs.filter { $0 >= lo && $0 < hi }.count
        let bar = String(repeating: "█", count: fpStripYFracs.isEmpty ? 0 : n * 30 / (fpStripYFracs.count + 1))
        print("  \(label.padding(toLength: 38, withPad:" ", startingAt:0)): \(String(format:"%4d", n))  \(bar)")
    }
    print("  From full-image pass: \(fpFullImageCount)")
}

// ── Near-dup IoU histogram ─────────────────────────────────────────
if !nearDupIoUs.isEmpty {
    print("\n── Near-duplicate IoU distribution ────────────────────────────────")
    for (lo, hi) in [(0.05,0.10),(0.10,0.20),(0.20,0.30),(0.30,0.40),(0.40,0.50)] {
        let n = nearDupIoUs.filter { $0 >= lo && $0 < hi }.count
        print("  \(String(format:"%.2f", lo))–\(String(format:"%.2f", hi)) : \(n)")
    }
}

// ── Worst images ──────────────────────────────────────────────────
print("\n── Top 12 worst images by FP count ────────────────────────────────")
print("  filename                               GT  TP  nearDup  falseClass  missed")
for r in imageResults.sorted(by: { ($0.nNearDup+$0.nFalseClass) > ($1.nNearDup+$1.nFalseClass) }).prefix(12) {
    let name = r.filename.padding(toLength: 40, withPad:" ", startingAt:0)
    print("  \(name) \(r.nGT)   \(r.nTP)   \(r.nNearDup)       \(r.nFalseClass)          \(r.nMissed)")
}

print("\n── Interpretation ──────────────────────────────────────────────────")
print("  NEAR-DUPLICATE >> FALSE-CLASS → pipeline fix (NMS/dedup), no retrain")
print("  FALSE-CLASS >> NEAR-DUPLICATE → hard-negative training data needed")
if !fpConfs.isEmpty && !tpConfs.isEmpty {
    let gap = avg(tpConfs) - avg(fpConfs)
    if gap > 0.05 {
        print("  Confidence gap TP–FP = \(String(format:"%.3f", gap)) → per-class threshold may help")
    } else {
        print("  Confidence gap TP–FP = \(String(format:"%.3f", gap)) → confidence threshold won't help (saturation)")
    }
}
print(String(repeating: "─", count: 70))
