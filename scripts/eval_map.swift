// eval_map.swift
// NativeUIAuditKit/scripts
//
// Custom mAP@0.5 evaluation using VNCoreMLRequest with .scaleFill.
// MLObjectDetector.evaluation(on:) uses .scaleFit internally and cannot be overridden,
// which gives mAP≈0 for portrait screenshots (see BP-25). This script is the source
// of truth for model accuracy gates.
//
// Usage (from project root):
//   swift scripts/eval_map.swift
//
// Outputs per-class AP@0.5 and overall mAP@0.5.

import Foundation
import CoreML
import Vision
import CoreGraphics
import ImageIO

// MARK: - Config

let projectRoot = URL(filePath: #filePath)
    .deletingLastPathComponent()   // scripts/
    .deletingLastPathComponent()   // project root

let modelURL = projectRoot
    .appending(path: "NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/NativeUIDetector_v1.mlpackage.mlmodel")

let valAnnotationURL = URL(filePath: "/Users/josephmccraw/Library/Developer/CoreSimulator/Devices/812EDC32-DB8D-49D6-B130-2279180CCDEB/data/Containers/Data/Application/E0711EF5-B600-47B2-A7B8-D5BA63DE1D83/Documents/dataset/createml_export/validation/annotations.json")

let valImagesDir = URL(filePath: "/Users/josephmccraw/Library/Developer/CoreSimulator/Devices/812EDC32-DB8D-49D6-B130-2279180CCDEB/data/Containers/Data/Application/E0711EF5-B600-47B2-A7B8-D5BA63DE1D83/Documents/dataset/createml_export/validation/images")

let confThreshold: Float = 0.1   // low threshold — collect all predictions, sort by conf for PR curve
let iouThreshold  = 0.5

// MARK: - Types

struct GTBox {
    let label: String
    let cx, cy, w, h: Double
}

struct Prediction {
    let label: String
    let conf: Float
    let cx, cy, w, h: Double
}

// MARK: - AP helper

/// Computes average precision from a sorted (descending confidence) list of
/// matched/unmatched predictions vs total ground-truth count for one class.
func computeAP(detections: [(conf: Float, isTP: Bool)], nGT: Int) -> Double {
    guard nGT > 0 else { return 0 }
    var tp = 0, fp = 0
    var precisions: [Double] = [], recalls: [Double] = []
    for d in detections.sorted(by: { $0.conf > $1.conf }) {
        if d.isTP { tp += 1 } else { fp += 1 }
        let p = Double(tp) / Double(tp + fp)
        let r = Double(tp) / Double(nGT)
        precisions.append(p)
        recalls.append(r)
    }
    // 11-point interpolation
    var ap = 0.0
    for t in stride(from: 0.0, through: 1.0, by: 0.1) {
        let pMax = zip(recalls, precisions)
            .filter { $0.0 >= t }
            .map { $0.1 }
            .max() ?? 0
        ap += pMax
    }
    return ap / 11.0
}

// MARK: - IoU

func iou(_ a: GTBox, _ b: Prediction) -> Double {
    let ax1 = a.cx - a.w/2, ax2 = a.cx + a.w/2, ay1 = a.cy - a.h/2, ay2 = a.cy + a.h/2
    let bx1 = Double(b.cx) - Double(b.w)/2, bx2 = Double(b.cx) + Double(b.w)/2
    let by1 = Double(b.cy) - Double(b.h)/2, by2 = Double(b.cy) + Double(b.h)/2
    let ix = max(0, min(ax2,bx2) - max(ax1,bx1))
    let iy = max(0, min(ay2,by2) - max(ay1,by1))
    let inter = ix * iy
    let union = a.w*a.h + Double(b.w)*Double(b.h) - inter
    return union > 0 ? inter/union : 0
}

// MARK: - Load annotation JSON

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
print("Loaded \(annEntries.count) validation images")

// Build GT map
var gtMap: [String: [GTBox]] = [:]   // imagefilename → [GTBox]
var classGTCount: [String: Int] = [:]
for entry in annEntries {
    gtMap[entry.imagefilename] = entry.annotation.map {
        let c = $0.coordinates
        classGTCount[$0.label, default: 0] += 1
        return GTBox(label: $0.label, cx: c.x, cy: c.y, w: c.width, h: c.height)
    }
}

// MARK: - Load model

let compiledURL = try MLModel.compileModel(at: modelURL)
let model = try MLModel(contentsOf: compiledURL)
let vnModel = try VNCoreMLModel(for: model)

// MARK: - Run inference on all validation images

// classPredictions: label → [(conf, isTP)]
var classPredictions: [String: [(conf: Float, isTP: Bool)]] = [:]
var processed = 0

let fm = FileManager.default
let imagePaths = try fm.contentsOfDirectory(at: valImagesDir, includingPropertiesForKeys: nil)
    .filter { $0.pathExtension == "png" }
    .sorted { $0.lastPathComponent < $1.lastPathComponent }

print("Running inference on \(imagePaths.count) images...")

for imgURL in imagePaths {
    let filename = imgURL.lastPathComponent
    guard let gts = gtMap[filename], !gts.isEmpty else { continue }

    guard let src = CGImageSourceCreateWithURL(imgURL as CFURL, nil),
          let cgImg = CGImageSourceCreateImageAtIndex(src, 0, nil) else { continue }

    let req = VNCoreMLRequest(model: vnModel)
    req.imageCropAndScaleOption = .scaleFill   // BP-25: must match training preprocessing
    try VNImageRequestHandler(cgImage: cgImg).perform([req])

    let visionResults = (req.results as? [VNRecognizedObjectObservation]) ?? []

    // Convert Vision bottom-left normalized → top-left normalized (match annotation format)
    let preds: [Prediction] = visionResults
        .filter { $0.confidence >= confThreshold }
        .map { obs in
            let b = obs.boundingBox
            let label = obs.labels.first?.identifier ?? "unknown"
            return Prediction(
                label: label,
                conf: obs.confidence,
                cx: Double(b.midX),
                cy: 1.0 - Double(b.midY),   // flip y: Vision bottom-left → top-left
                w: Double(b.width),
                h: Double(b.height)
            )
        }

    // Match predictions to GTs (greedy, highest-conf first)
    // Per class: each GT can only be matched once
    var matchedGTs = Set<Int>()  // indices into gts

    for pred in preds.sorted(by: { $0.conf > $1.conf }) {
        // Find best IoU match among same-class GTs
        var bestIoU = 0.0
        var bestIdx = -1
        for (gi, gt) in gts.enumerated() {
            guard gt.label == pred.label, !matchedGTs.contains(gi) else { continue }
            let score = iou(gt, pred)
            if score > bestIoU {
                bestIoU = score
                bestIdx = gi
            }
        }
        let isTP = bestIoU >= iouThreshold
        if isTP { matchedGTs.insert(bestIdx) }
        classPredictions[pred.label, default: []].append((conf: pred.conf, isTP: isTP))
    }

    processed += 1
    if processed % 100 == 0 {
        print("  \(processed)/\(imagePaths.count)")
    }
}

// MARK: - Compute per-class AP

print()
print("── mAP Evaluation (IoU@0.5, .scaleFill) ──────────────────────────────")
var apValues: [Double] = []
let allClasses = Array(classGTCount.keys).sorted()

for cls in allClasses {
    let nGT = classGTCount[cls] ?? 0
    let dets = classPredictions[cls] ?? []
    let ap = computeAP(detections: dets, nGT: nGT)
    apValues.append(ap)
    let nTP = dets.filter { $0.isTP }.count
    print("  AP@0.5  \(cls.padding(toLength: 20, withPad: " ", startingAt: 0)): \(String(format: "%.4f", ap))   (GT=\(nGT)  TP=\(nTP)  pred=\(dets.count))")
}

let mAP = apValues.isEmpty ? 0 : apValues.reduce(0, +) / Double(apValues.count)
print()
print("  mAP@0.5 : \(String(format: "%.4f", mAP))")
print()
if mAP >= 0.70 {
    print("  ✓ Gate DS-G6 PASS (mAP ≥ 0.70)")
} else if mAP >= 0.50 {
    print("  ~ Gate DS-G5 PASS but DS-G6 FAIL (need ≥ 0.70 for Phase 7)")
} else {
    print("  ✗ Below DS-G5 floor (mAP < 0.50)")
}
