// eval_yolo_map.swift
// NativeUIAuditKit/scripts
//
// mAP@0.5 evaluation using the YOLO11n CoreML model (best.mlpackage).
// Uses direct MLModel inference (no Vision framework) with letterbox preprocessing.
//
// The YOLO CoreML model requires exactly 640×640 input. Each image is letterboxed
// (aspect-ratio-preserving, gray fill = 114,114,114) before inference. Predicted
// boxes are inverse-letterboxed back to original image coordinates before AP matching.
//
// The model's NMS is baked in (nms=True at export). A light greedy NMS is still run
// post-inference to catch any remaining near-duplicates. No multi-pass routing is
// needed — YOLO handles multi-scale detection internally.
//
// Usage (from project root):
//   swift scripts/eval_yolo_map.swift
//
// Outputs:
//   - Per-class AP@0.5 to stdout
//   - DS-G5 / DS-G6 gate status
//   - reports/eval_results_yolo_coreml.json  (always written)

import Foundation
import CoreML
import CoreGraphics
import ImageIO
import CoreVideo

// MARK: - Config

let projectRoot = URL(filePath: #filePath)
    .deletingLastPathComponent()   // scripts/
    .deletingLastPathComponent()   // project root

let modelURL = projectRoot
    .appending(path: "NativeUITrainer/yolo_runs/yolo11n_e100/weights/best.mlpackage")

let valAnnotationURL = URL(filePath: "/Users/josephmccraw/Library/Developer/CoreSimulator/Devices/812EDC32-DB8D-49D6-B130-2279180CCDEB/data/Containers/Data/Application/E0711EF5-B600-47B2-A7B8-D5BA63DE1D83/Documents/dataset/createml_export/validation/annotations.json")

let valImagesDir = URL(filePath: "/Users/josephmccraw/Library/Developer/CoreSimulator/Devices/812EDC32-DB8D-49D6-B130-2279180CCDEB/data/Containers/Data/Application/E0711EF5-B600-47B2-A7B8-D5BA63DE1D83/Documents/dataset/createml_export/validation/images")

/// Class names in YOLO training order (must match training class IDs 0–4).
let yoloClassNames = ["alert", "navigationBar", "primaryButton", "textField", "toggle"]

let yoloImgSize    = 640
let confFloor: Float = 0.001   // low floor so the full PR curve is captured
let iouMatchThreshold = 0.5    // IoU required for a TP match
let nmsIoUThreshold   = 0.30   // post-inference NMS IoU threshold

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

// MARK: - Letterbox helpers

struct LetterboxResult {
    let image: CGImage
    let newW: Int   // content width  in the 640×640 frame
    let newH: Int   // content height in the 640×640 frame
    let padX: Int   // horizontal padding (each side)
    let padY: Int   // vertical padding   (each side)
}

/// Letterbox-resize a CGImage to yoloImgSize×yoloImgSize, preserving aspect ratio.
/// Padding is filled with the YOLO standard gray (114, 114, 114).
func letterbox(_ source: CGImage) -> LetterboxResult? {
    let origW  = Double(source.width)
    let origH  = Double(source.height)
    let scale  = min(Double(yoloImgSize) / origW, Double(yoloImgSize) / origH)
    let newW   = Int(origW * scale)
    let newH   = Int(origH * scale)
    let padX   = (yoloImgSize - newW) / 2
    let padY   = (yoloImgSize - newH) / 2

    guard let ctx = CGContext(
        data: nil, width: yoloImgSize, height: yoloImgSize,
        bitsPerComponent: 8, bytesPerRow: 0,
        space: CGColorSpaceCreateDeviceRGB(),
        bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue
    ) else { return nil }

    // Gray fill (YOLO standard: 114/255).
    ctx.setFillColor(CGColor(red: 114/255.0, green: 114/255.0, blue: 114/255.0, alpha: 1.0))
    ctx.fill(CGRect(x: 0, y: 0, width: yoloImgSize, height: yoloImgSize))

    // CGContext origin is bottom-left. Content rows [padY, padY+newH) from top
    // equals y=padY from the bottom when newH+2*padY = yoloImgSize (or near it).
    ctx.draw(source, in: CGRect(x: padX, y: padY, width: newW, height: newH))

    guard let boxed = ctx.makeImage() else { return nil }
    return LetterboxResult(image: boxed, newW: newW, newH: newH, padX: padX, padY: padY)
}

/// Convert the letterboxed CGImage to a CVPixelBuffer for MLModel input.
func makePixelBuffer(_ image: CGImage) -> CVPixelBuffer? {
    let attrs = [
        kCVPixelBufferCGImageCompatibilityKey: true,
        kCVPixelBufferCGBitmapContextCompatibilityKey: true,
    ] as CFDictionary
    var buf: CVPixelBuffer?
    guard CVPixelBufferCreate(kCFAllocatorDefault, image.width, image.height,
                              kCVPixelFormatType_32BGRA, attrs, &buf) == kCVReturnSuccess,
          let pixelBuf = buf else { return nil }

    CVPixelBufferLockBaseAddress(pixelBuf, [])
    defer { CVPixelBufferUnlockBaseAddress(pixelBuf, []) }

    guard let ctx = CGContext(
        data: CVPixelBufferGetBaseAddress(pixelBuf),
        width: image.width, height: image.height,
        bitsPerComponent: 8,
        bytesPerRow: CVPixelBufferGetBytesPerRow(pixelBuf),
        space: CGColorSpaceCreateDeviceRGB(),
        bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue | CGBitmapInfo.byteOrder32Little.rawValue
    ) else { return nil }

    ctx.draw(image, in: CGRect(x: 0, y: 0, width: image.width, height: image.height))
    return pixelBuf
}

// MARK: - YOLO CoreML inference

/// Run one image through the YOLO CoreML model. Returns predictions in original image coords.
func runYOLO(image: CGImage, model: MLModel) throws -> [Prediction] {
    guard let lb = letterbox(image), let pixelBuf = makePixelBuffer(lb.image) else {
        return []
    }

    let input = try MLDictionaryFeatureProvider(dictionary: [
        "image":               MLFeatureValue(pixelBuffer: pixelBuf),
        "iouThreshold":        MLFeatureValue(double: 0.45),
        "confidenceThreshold": MLFeatureValue(double: Double(confFloor)),
    ])
    let output = try model.prediction(from: input)

    guard let confArr  = output.featureValue(for: "confidence")?.multiArrayValue,
          let coordArr = output.featureValue(for: "coordinates")?.multiArrayValue else {
        return []
    }

    let n         = confArr.shape[0].intValue
    let nTotal    = confArr.shape[1].intValue
    let nCheck    = min(yoloClassNames.count, nTotal)  // first 5 columns are trained classes

    let cs0 = confArr.strides[0].intValue   // stride across detections
    let cs1 = confArr.strides[1].intValue   // stride across classes
    let xs0 = coordArr.strides[0].intValue  // stride across detections (for coords)

    let sz    = Double(yoloImgSize)
    let newWd = Double(lb.newW)
    let newHd = Double(lb.newH)
    let pxD   = Double(lb.padX)
    let pyD   = Double(lb.padY)

    var preds: [Prediction] = []
    for i in 0..<n {
        var bestConf: Float = 0
        var bestClass = 0
        for c in 0..<nCheck {
            let v = confArr[i * cs0 + c * cs1].floatValue
            if v > bestConf { bestConf = v; bestClass = c }
        }
        guard bestConf >= confFloor else { continue }

        // Raw coords: [cx, cy, w, h] normalized to the 640×640 letterboxed image.
        let cx640 = coordArr[i * xs0 + 0].doubleValue
        let cy640 = coordArr[i * xs0 + 1].doubleValue
        let w640  = coordArr[i * xs0 + 2].doubleValue
        let h640  = coordArr[i * xs0 + 3].doubleValue

        // Inverse-letterbox → original image normalized coords.
        let cxOrig = (cx640 * sz - pxD) / newWd
        let cyOrig = (cy640 * sz - pyD) / newHd
        let wOrig  = w640 * sz / newWd
        let hOrig  = h640 * sz / newHd

        preds.append(Prediction(
            label: yoloClassNames[bestClass],
            conf: bestConf,
            cx: cxOrig, cy: cyOrig, w: wOrig, h: hOrig
        ))
    }
    return preds
}

// MARK: - Greedy NMS (same-class, descending confidence)

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

// MARK: - AP computation (11-point interpolation, same as eval_map.swift)

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

// MARK: - Load YOLO CoreML model

print("Loading model: \(modelURL.lastPathComponent)")
let compiledURL = try MLModel.compileModel(at: modelURL)
let model = try MLModel(contentsOf: compiledURL)

// MARK: - Run inference on validation set

var classPredictions: [String: [(conf: Float, isTP: Bool)]] = [:]
var processed = 0
let startTime = Date()

let fm = FileManager.default
let imagePaths = try fm.contentsOfDirectory(at: valImagesDir, includingPropertiesForKeys: nil)
    .filter { $0.pathExtension == "png" }
    .sorted { $0.lastPathComponent < $1.lastPathComponent }

print("Running YOLO CoreML inference on \(imagePaths.count) images (single-pass, NMS baked in)...")

for imgURL in imagePaths {
    let filename = imgURL.lastPathComponent
    guard let gts = gtMap[filename], !gts.isEmpty else { continue }

    guard let src   = CGImageSourceCreateWithURL(imgURL as CFURL, nil),
          let cgImg = CGImageSourceCreateImageAtIndex(src, 0, nil) else { continue }

    let rawPreds = (try? runYOLO(image: cgImg, model: model)) ?? []
    let preds    = nms(rawPreds, iouThresh: nmsIoUThreshold)

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

    processed += 1
    if processed % 100 == 0 {
        let elapsed = Date().timeIntervalSince(startTime)
        let rate = Double(processed) / elapsed
        let remaining = Double(imagePaths.count - processed) / rate
        print("  \(processed)/\(imagePaths.count)  (\(String(format: "%.0f", remaining))s remaining)")
    }
}

// MARK: - Compute and print per-class AP

print()
print("── YOLO11n CoreML  mAP@0.5 (single-pass, letterbox, NMS@0.30) ──")
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
    print("  ~  DS-G5 PASS but DS-G6 FAIL (mAP \(String(format: "%.3f", mAP)) < 0.70)")
case (false, true, false):
    print("  ✗  DS-G5 FAIL — some class APs < 0.50, mAP \(String(format: "%.3f", mAP))")
default:
    print("  ✗  Below DS-G5 floor (mAP \(String(format: "%.3f", mAP)) < 0.50)")
}

// MARK: - Write eval_results_yolo_coreml.json

let results: [String: Any] = [
    "model":             "yolo11n_e100_coreml",
    "mAP50":             mAP,
    "iouThreshold":      iouMatchThreshold,
    "nmsThreshold":      nmsIoUThreshold,
    "confFloor":         Double(confFloor),
    "nValidationImages": processed,
    "perClass":          perClassResults,
    "evalDate":          ISO8601DateFormatter().string(from: Date()),
    "dsG5Pass":          allClassesPass,
    "dsG6Pass":          mAP >= 0.70,
]

let reportsDir = projectRoot.appending(path: "reports", directoryHint: .isDirectory)
try? FileManager.default.createDirectory(at: reportsDir, withIntermediateDirectories: true)
let jsonURL = reportsDir.appending(path: "eval_results_yolo_coreml.json")
let jsonData = try JSONSerialization.data(withJSONObject: results, options: [.prettyPrinted, .sortedKeys])
try jsonData.write(to: jsonURL)
print()
print("Results written to: \(jsonURL.path)")
