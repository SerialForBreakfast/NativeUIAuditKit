// eval_map.swift
// NativeUIAuditKit/scripts
//
// Custom mAP@0.5 evaluation using the full 3-pass inference pipeline.
// MLObjectDetector.evaluation(on:) uses .scaleFit internally and cannot be
// overridden — gives mAP≈0 for portrait screenshots. See BP-25.
//
// ── IMPORTANT FOR STRIP-TRAINED MODELS (Run 003+) ───────────────────────────
// The strip-trained model detects navigationBar and textField via the strip
// pass, NOT the full-image pass. Evaluating with only a full-image VNCoreML-
// Request will show AP=0 for those classes even if the model is correct.
// This script runs all 3 passes + NMS, matching NativeUIDetectionRequest.
//
// Passes:
//   1. Full image (.scaleFill) — alert, large containers
//   2. SAHI 640×640 tiles, 480px stride, 2× upscale — toggle, primaryButton
//   3. Horizontal strips, 22% height, 50% overlap — navigationBar, textField
//
// Usage (from project root):
//   swift scripts/eval_map.swift
//
// Optional: set environment variable WRITE_YOLO_PREDS=1 to write YOLO-format
// prediction files to reports/yolo_preds/ for use with confusion_matrix.py.
//
// Outputs:
//   - Per-class AP@0.5 to stdout
//   - DS-G5 / DS-G6 gate status
//   - reports/eval_results.json  (always written)
//   - reports/yolo_preds/        (only if WRITE_YOLO_PREDS=1)

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

/// Confidence threshold for collecting predictions.
/// Low (0.1) so all candidates go into the PR curve; NMS then deduplicates.
let confThreshold: Float = 0.1
let iouMatchThreshold = 0.5   // IoU required for a TP match
let nmsIoUThreshold   = 0.45  // IoU for duplicate suppression across passes

/// Write YOLO-format prediction files (for confusion_matrix.py)?
let writeYoloPreds = ProcessInfo.processInfo.environment["WRITE_YOLO_PREDS"] == "1"

// MARK: - Types

struct GTBox {
    let label: String
    let cx, cy, w, h: Double   // Create ML top-left normalized
}

struct Prediction {
    let label: String
    let conf: Float
    let cx, cy, w, h: Double   // Create ML top-left normalized

    var rect: CGRect {
        CGRect(x: cx - w/2, y: cy - h/2, width: w, height: h)
    }
}

// MARK: - Image helpers

func cropCGImage(source: CGImage, x: Int, y: Int, width: Int, height: Int) -> CGImage? {
    guard let ctx = CGContext(
        data: nil, width: width, height: height,
        bitsPerComponent: 8, bytesPerRow: 0,
        space: CGColorSpaceCreateDeviceRGB(),
        bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue
    ) else { return nil }
    // Flip draw offset: expose rows [y, y+height) from the top of source.
    let drawY = -(source.height - y - height)
    ctx.draw(source, in: CGRect(x: -x, y: drawY, width: source.width, height: source.height))
    return ctx.makeImage()
}

func upscale(_ image: CGImage, factor: Int) -> CGImage? {
    let w = image.width * factor
    let h = image.height * factor
    guard let ctx = CGContext(
        data: nil, width: w, height: h,
        bitsPerComponent: 8, bytesPerRow: 0,
        space: CGColorSpaceCreateDeviceRGB(),
        bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue
    ) else { return nil }
    ctx.interpolationQuality = .none
    ctx.draw(image, in: CGRect(x: 0, y: 0, width: w, height: h))
    return ctx.makeImage()
}

// MARK: - VNCoreMLRequest runner

func runRequest(on image: CGImage, model: VNCoreMLModel) throws -> [VNRecognizedObjectObservation] {
    let req = VNCoreMLRequest(model: model)
    req.imageCropAndScaleOption = .scaleFill   // BP-25: must match training preprocessing
    try VNImageRequestHandler(cgImage: image, options: [:]).perform([req])
    return req.results as? [VNRecognizedObjectObservation] ?? []
}

// MARK: - Three-pass inference

/// Full image pass (.scaleFill). Catches alert, large containers.
func fullImagePass(image: CGImage, model: VNCoreMLModel) throws -> [Prediction] {
    let obs = try runRequest(on: image, model: model)
    return obs
        .filter { $0.confidence >= confThreshold }
        .map { visionObsToPrediction($0) }
}

/// SAHI 640×640 tile pass on 2× upscaled image. Catches toggle, primaryButton.
func sahiTilePass(image: CGImage, model: VNCoreMLModel) throws -> [Prediction] {
    guard let upscaled = upscale(image, factor: 2) else { return [] }
    let W = upscaled.width, H = upscaled.height
    let tileSize = 640, stride = 480
    var result: [Prediction] = []

    var y = 0
    while y < H {
        let tileH = min(tileSize, H - y)
        var x = 0
        while x < W {
            let tileW = min(tileSize, W - x)
            guard let tile = cropCGImage(source: upscaled, x: x, y: y, width: tileW, height: tileH) else {
                x += stride; continue
            }
            let obs = try runRequest(on: tile, model: model)
            let remapped: [Prediction] = obs
                .filter { $0.confidence >= confThreshold }
                .map { o -> Prediction in
                    let b = o.boundingBox  // Vision bottom-left
                    // 1. Convert tile-local Vision → tile-local top-left
                    let tileCX = Double(b.midX)
                    let tileCY = 1.0 - Double(b.midY)
                    // 2. Map tile top-left coords → full-upscaled-image top-left coords
                    let tileXFrac = Double(x) / Double(W)
                    let tileYFrac = Double(y) / Double(H)
                    let tileWFrac = Double(tileW) / Double(W)
                    let tileHFrac = Double(tileH) / Double(H)
                    let fullCX = tileXFrac + tileCX * tileWFrac
                    let fullCY = tileYFrac + tileCY * tileHFrac
                    let fullW  = Double(b.width)  * tileWFrac
                    let fullH  = Double(b.height) * tileHFrac
                    return Prediction(
                        label: o.labels.first?.identifier ?? "unknown",
                        conf: o.confidence,
                        cx: fullCX, cy: fullCY, w: fullW, h: fullH
                    )
                }
            result += remapped
            x += stride
        }
        y += stride
    }
    return result
}

/// Horizontal strip pass (22% height, 50% overlap). Catches navigationBar, textField.
/// This is the critical pass for the strip-trained model (Run 003+).
func stripPass(image: CGImage, model: VNCoreMLModel) throws -> [Prediction] {
    let imageH = image.height
    let imageW = image.width
    let stripH = max(1, Int(Double(imageH) * 0.22))
    let stride  = max(1, stripH / 2)
    var result: [Prediction] = []

    var y = 0
    while y + stripH <= imageH {
        guard let strip = cropCGImage(source: image, x: 0, y: y, width: imageW, height: stripH) else {
            y += stride; continue
        }
        let obs = try runRequest(on: strip, model: model)
        let remapped: [Prediction] = obs
            .filter { $0.confidence >= confThreshold }
            .map { o -> Prediction in
                let b = o.boundingBox  // Vision bottom-left, strip-local

                // Strip occupies rows [y, y+stripH) from top of full image.
                // Vision bottom-left: strip bottom = 1.0 - (y+stripH)/imageH from full image bottom.
                let stripTopVision    = 1.0 - Double(y + stripH) / Double(imageH)
                let stripHeightVision = Double(stripH) / Double(imageH)

                // Strip-local Vision y → full-image Vision y → full-image top-left y
                let fullVisionMidY = stripTopVision + Double(b.midY) * stripHeightVision
                let fullVisionH    = Double(b.height) * stripHeightVision
                let fullCX = Double(b.midX)            // width is full image width, no x scaling
                let fullCY = 1.0 - fullVisionMidY       // flip Vision bottom-left → top-left
                let fullH  = fullVisionH

                return Prediction(
                    label: o.labels.first?.identifier ?? "unknown",
                    conf: o.confidence,
                    cx: fullCX, cy: fullCY, w: Double(b.width), h: fullH
                )
            }
        result += remapped
        y += stride
    }
    return result
}

/// Convert VNRecognizedObjectObservation (Vision bottom-left) → Prediction (top-left normalized).
func visionObsToPrediction(_ obs: VNRecognizedObjectObservation) -> Prediction {
    let b = obs.boundingBox
    return Prediction(
        label: obs.labels.first?.identifier ?? "unknown",
        conf: obs.confidence,
        cx: Double(b.midX),
        cy: 1.0 - Double(b.midY),  // flip Vision bottom-left → top-left
        w: Double(b.width),
        h: Double(b.height)
    )
}

// MARK: - NMS (same-class, greedy, descending confidence)

func iouPred(_ a: Prediction, _ b: Prediction) -> Double {
    let ax1 = a.cx - a.w/2, ax2 = a.cx + a.w/2
    let ay1 = a.cy - a.h/2, ay2 = a.cy + a.h/2
    let bx1 = b.cx - b.w/2, bx2 = b.cx + b.w/2
    let by1 = b.cy - b.h/2, by2 = b.cy + b.h/2
    let ix = max(0, min(ax2,bx2) - max(ax1,bx1))
    let iy = max(0, min(ay2,by2) - max(ay1,by1))
    let inter = ix * iy
    let union = a.w*a.h + b.w*b.h - inter
    return union > 0 ? inter/union : 0
}

func nms(_ preds: [Prediction], iouThresh: Double) -> [Prediction] {
    let sorted = preds.sorted { $0.conf > $1.conf }
    var kept: [Prediction] = []
    var suppressed = Set<Int>()
    for (i, a) in sorted.enumerated() {
        if suppressed.contains(i) { continue }
        kept.append(a)
        for (j, b) in sorted.enumerated() where j > i {
            if suppressed.contains(j) { continue }
            guard a.label == b.label else { continue }
            if iouPred(a, b) > iouThresh { suppressed.insert(j) }
        }
    }
    return kept
}

// MARK: - AP computation

func iouGT(_ a: GTBox, _ b: Prediction) -> Double {
    let ax1 = a.cx - a.w/2, ax2 = a.cx + a.w/2, ay1 = a.cy - a.h/2, ay2 = a.cy + a.h/2
    let bx1 = b.cx - b.w/2, bx2 = b.cx + b.w/2, by1 = b.cy - b.h/2, by2 = b.cy + b.h/2
    let ix = max(0, min(ax2,bx2) - max(ax1,bx1))
    let iy = max(0, min(ay2,by2) - max(ay1,by1))
    let inter = ix * iy
    let union = a.w*a.h + b.w*b.h - inter
    return union > 0 ? inter/union : 0
}

func computeAP(detections: [(conf: Float, isTP: Bool)], nGT: Int) -> Double {
    guard nGT > 0 else { return 0 }
    var tp = 0, fp = 0
    var precisions: [Double] = [], recalls: [Double] = []
    for d in detections.sorted(by: { $0.conf > $1.conf }) {
        if d.isTP { tp += 1 } else { fp += 1 }
        precisions.append(Double(tp) / Double(tp + fp))
        recalls.append(Double(tp) / Double(nGT))
    }
    var ap = 0.0
    for t in stride(from: 0.0, through: 1.0, by: 0.1) {
        let pMax = zip(recalls, precisions).filter { $0.0 >= t }.map { $0.1 }.max() ?? 0
        ap += pMax
    }
    return ap / 11.0
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

let annData    = try Data(contentsOf: valAnnotationURL)
let annEntries = try JSONDecoder().decode([AnnEntry].self, from: annData)
print("Loaded \(annEntries.count) validation images")

var gtMap: [String: [GTBox]] = [:]
var classGTCount: [String: Int] = [:]
for entry in annEntries {
    gtMap[entry.imagefilename] = entry.annotation.map {
        let c = $0.coordinates
        classGTCount[$0.label, default: 0] += 1
        return GTBox(label: $0.label, cx: c.x, cy: c.y, w: c.width, h: c.height)
    }
}

// MARK: - Load model

print("Loading model from: \(modelURL.lastPathComponent)")
let compiledURL = try MLModel.compileModel(at: modelURL)
let model       = try MLModel(contentsOf: compiledURL)
let vnModel     = try VNCoreMLModel(for: model)

// MARK: - YOLO output setup (optional)

var yoloOutputDir: URL? = nil
let classNames = Array(classGTCount.keys).sorted()  // deterministic class order

if writeYoloPreds {
    let dir = projectRoot.appending(path: "reports/yolo_preds", directoryHint: .isDirectory)
    try FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
    yoloOutputDir = dir

    // Write class index file for confusion_matrix.py
    let classesContent = classNames.enumerated()
        .map { "\($0.offset) \($0.element)" }
        .joined(separator: "\n")
    try (classesContent + "\n").write(
        to: dir.appending(path: "classes.txt"), atomically: true, encoding: .utf8)

    print("Writing YOLO predictions to: \(dir.path)")
}

// MARK: - Run inference on all validation images

var classPredictions: [String: [(conf: Float, isTP: Bool)]] = [:]
var processed = 0
let startTime = Date()

let fm = FileManager.default
let imagePaths = try fm.contentsOfDirectory(at: valImagesDir, includingPropertiesForKeys: nil)
    .filter { $0.pathExtension == "png" }
    .sorted { $0.lastPathComponent < $1.lastPathComponent }

print("Running 3-pass inference on \(imagePaths.count) images...")
print("  Passes: full-image + SAHI tiles + horizontal strips")

for imgURL in imagePaths {
    let filename = imgURL.lastPathComponent
    guard let gts = gtMap[filename], !gts.isEmpty else { continue }

    guard let src   = CGImageSourceCreateWithURL(imgURL as CFURL, nil),
          let cgImg = CGImageSourceCreateImageAtIndex(src, 0, nil) else { continue }

    // Run all three passes, merge with NMS
    var allPreds: [Prediction] = []
    allPreds += (try? fullImagePass(image: cgImg, model: vnModel)) ?? []
    allPreds += (try? sahiTilePass(image: cgImg, model: vnModel))  ?? []
    allPreds += (try? stripPass(image: cgImg, model: vnModel))     ?? []
    let preds = nms(allPreds, iouThresh: nmsIoUThreshold)

    // Match predictions to GTs
    var matchedGTs = Set<Int>()
    for pred in preds.sorted(by: { $0.conf > $1.conf }) {
        var bestIoU = 0.0, bestIdx = -1
        for (gi, gt) in gts.enumerated() {
            guard gt.label == pred.label, !matchedGTs.contains(gi) else { continue }
            let score = iouGT(gt, pred)
            if score > bestIoU { bestIoU = score; bestIdx = gi }
        }
        let isTP = bestIoU >= iouMatchThreshold
        if isTP { matchedGTs.insert(bestIdx) }
        classPredictions[pred.label, default: []].append((conf: pred.conf, isTP: isTP))
    }

    // Write YOLO-format predictions if requested
    if let yoloDir = yoloOutputDir {
        // YOLO format: class_id cx cy w h conf  (top-left normalized coords)
        let classToID = Dictionary(uniqueKeysWithValues: classNames.enumerated().map { ($0.element, $0.offset) })
        let lines = preds.compactMap { pred -> String? in
            guard let id = classToID[pred.label] else { return nil }
            return "\(id) \(pred.cx) \(pred.cy) \(pred.w) \(pred.h) \(pred.conf)"
        }.joined(separator: "\n")
        let stem = (filename as NSString).deletingPathExtension
        let outURL = yoloDir.appending(path: "\(stem).txt")
        try? lines.write(to: outURL, atomically: true, encoding: .utf8)
    }

    processed += 1
    if processed % 100 == 0 {
        let elapsed = Date().timeIntervalSince(startTime)
        let rate = Double(processed) / elapsed
        let remaining = Double(imagePaths.count - processed) / rate
        print("  \(processed)/\(imagePaths.count)  (\(String(format: "%.0f", remaining))s remaining)")
    }
}

// MARK: - Compute per-class AP and report

print()
print("── mAP Evaluation — 3-pass pipeline (IoU@0.5, NMS@0.45) ──────────────")
print("   Full-image + SAHI tiles + horizontal strips")
print()

var apValues: [Double] = []
var perClassResults: [[String: Any]] = []
let allClasses = Array(classGTCount.keys).sorted()

for cls in allClasses {
    let nGT = classGTCount[cls] ?? 0
    let dets = classPredictions[cls] ?? []
    let ap   = computeAP(detections: dets, nGT: nGT)
    apValues.append(ap)
    let nTP  = dets.filter { $0.isTP }.count
    let gateFlag = ap >= 0.50 ? "✓" : "✗"
    print("  \(gateFlag) AP@0.5  \(cls.padding(toLength: 20, withPad: " ", startingAt: 0)): \(String(format: "%.4f", ap))   GT=\(nGT)  TP=\(nTP)  pred=\(dets.count)")
    perClassResults.append(["class": cls, "ap50": ap, "nGT": nGT, "nTP": nTP, "nPred": dets.count])
}

let mAP = apValues.isEmpty ? 0 : apValues.reduce(0, +) / Double(apValues.count)
let allClassesPass = apValues.allSatisfy { $0 >= 0.50 }
let elapsed = Date().timeIntervalSince(startTime)

print()
print("  mAP@0.5 : \(String(format: "%.4f", mAP))   (\(Int(elapsed))s elapsed)")
print()

switch (mAP >= 0.70, mAP >= 0.50, allClassesPass) {
case (true, _, true):
    print("  ✓✓ DS-G5 PASS + DS-G6 PASS — ready for Phase 7")
case (true, _, false):
    print("  ~  DS-G6 mAP PASS but some class AP < 0.50 — investigate failing classes")
case (false, true, true):
    print("  ~  DS-G5 PASS (all class APs ≥ 0.50) but DS-G6 FAIL (mAP \(String(format: "%.3f", mAP)) < 0.70)")
case (false, true, false):
    print("  ✗  DS-G5 FAIL — some class APs < 0.50, mAP \(String(format: "%.3f", mAP))")
default:
    print("  ✗  Below DS-G5 floor (mAP \(String(format: "%.3f", mAP)) < 0.50)")
}

// MARK: - Write eval_results.json

let results: [String: Any] = [
    "mAP50":        mAP,
    "iouThreshold": iouMatchThreshold,
    "nmsThreshold": nmsIoUThreshold,
    "confThreshold": Double(confThreshold),
    "nValidationImages": processed,
    "perClass":     perClassResults,
    "passes":       ["full-image", "SAHI-640-480stride-2xupscale", "horizontal-strips-22pct-50overlap"],
    "evalDate":     ISO8601DateFormatter().string(from: Date()),
    "dsG5Pass":     allClassesPass,
    "dsG6Pass":     mAP >= 0.70
]

let reportsDir = projectRoot.appending(path: "reports", directoryHint: .isDirectory)
try? FileManager.default.createDirectory(at: reportsDir, withIntermediateDirectories: true)
let jsonURL = reportsDir.appending(path: "eval_results.json")
let jsonData = try JSONSerialization.data(withJSONObject: results, options: [.prettyPrinted, .sortedKeys])
try jsonData.write(to: jsonURL)
print()
print("Results written to: \(jsonURL.path)")

if writeYoloPreds, let dir = yoloOutputDir {
    print("YOLO predictions written to: \(dir.path)")
    print("Run: python scripts/confusion_matrix.py --gt-dir <val-annotations-dir> --pred-dir \(dir.path) --version 1")
}
