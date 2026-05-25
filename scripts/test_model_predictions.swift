// test_model_predictions.swift
// NativeUIAuditKit/scripts
//
// Spot-checks the trained model on one or two validation images using the full
// 3-pass pipeline (full-image + SAHI tiles + horizontal strips).
//
// Run after every training run before full eval_map.swift evaluation:
//   1. Confirm alert IoU > 0.9 on the alert image (sanity check)
//   2. Check whether navigationBar/textField detections appear on img_000809
//
// Usage (from project root):
//   swift scripts/test_model_predictions.swift
//   swift scripts/test_model_predictions.swift path/to/image.png
//
// Key ground truths (Create ML normalized, top-left origin):
//   img_000409: alert cx=0.500 cy=0.488 w=0.690 h=0.254
//   img_000809: navigationBar cx=0.500 cy=0.104 w=1.000 h=0.063

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

let datasetImagesDir = URL(filePath: "/Users/josephmccraw/Library/Developer/CoreSimulator/Devices/812EDC32-DB8D-49D6-B130-2279180CCDEB/data/Containers/Data/Application/E0711EF5-B600-47B2-A7B8-D5BA63DE1D83/Documents/dataset/createml_export/validation/images")

// Default: run both the alert image and the navigationBar image
let alertImageURL  = datasetImagesDir.appending(path: "img_000409.png")
let navBarImageURL = datasetImagesDir.appending(path: "img_000809.png")

// MARK: - Helpers

func cropCGImage(source: CGImage, x: Int, y: Int, width: Int, height: Int) -> CGImage? {
    guard let ctx = CGContext(
        data: nil, width: width, height: height,
        bitsPerComponent: 8, bytesPerRow: 0,
        space: CGColorSpaceCreateDeviceRGB(),
        bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue
    ) else { return nil }
    ctx.draw(source, in: CGRect(x: -x, y: -(source.height - y - height), width: source.width, height: source.height))
    return ctx.makeImage()
}

func upscale(_ image: CGImage, factor: Int) -> CGImage? {
    guard let ctx = CGContext(
        data: nil, width: image.width * factor, height: image.height * factor,
        bitsPerComponent: 8, bytesPerRow: 0,
        space: CGColorSpaceCreateDeviceRGB(),
        bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue
    ) else { return nil }
    ctx.interpolationQuality = .none
    ctx.draw(image, in: CGRect(x: 0, y: 0, width: image.width * factor, height: image.height * factor))
    return ctx.makeImage()
}

struct Det {
    let pass: String
    let label: String
    let conf: Float
    let cx, cy, w, h: Double  // Create ML top-left normalized
}

func runReq(on image: CGImage, model: VNCoreMLModel) throws -> [VNRecognizedObjectObservation] {
    let req = VNCoreMLRequest(model: model)
    req.imageCropAndScaleOption = .scaleFill   // BP-25
    try VNImageRequestHandler(cgImage: image, options: [:]).perform([req])
    return req.results as? [VNRecognizedObjectObservation] ?? []
}

func iou(_ ax: Double, _ ay: Double, _ aw: Double, _ ah: Double,
         _ bx: Double, _ by: Double, _ bw: Double, _ bh: Double) -> Double {
    let ix = max(0, min(ax+aw/2, bx+bw/2) - max(ax-aw/2, bx-bw/2))
    let iy = max(0, min(ay+ah/2, by+bh/2) - max(ay-ah/2, by-bh/2))
    let inter = ix * iy
    let union = aw*ah + bw*bh - inter
    return union > 0 ? inter/union : 0
}

func threePassInference(image: CGImage, model: VNCoreMLModel) throws -> [Det] {
    var dets: [Det] = []

    // Pass 1 — full image
    for obs in try runReq(on: image, model: model) {
        let b = obs.boundingBox
        dets.append(Det(pass: "full", label: obs.labels.first?.identifier ?? "?",
                        conf: obs.confidence,
                        cx: Double(b.midX), cy: 1.0 - Double(b.midY),
                        w: Double(b.width), h: Double(b.height)))
    }

    // Pass 2 — SAHI tiles
    if let up = upscale(image, factor: 2) {
        let W = up.width, H = up.height
        let tileSize = 640, stride = 480
        var ty = 0
        while ty < H {
            let tH = min(tileSize, H - ty); var tx = 0
            while tx < W {
                let tW = min(tileSize, W - tx)
                if let tile = cropCGImage(source: up, x: tx, y: ty, width: tW, height: tH) {
                    for obs in try runReq(on: tile, model: model) {
                        let b = obs.boundingBox
                        let tileCX = Double(b.midX); let tileCY = 1.0 - Double(b.midY)
                        let xFrac = Double(tx)/Double(W); let yFrac = Double(ty)/Double(H)
                        let wFrac = Double(tW)/Double(W); let hFrac = Double(tH)/Double(H)
                        dets.append(Det(pass: "sahi", label: obs.labels.first?.identifier ?? "?",
                                        conf: obs.confidence,
                                        cx: xFrac + tileCX*wFrac, cy: yFrac + tileCY*hFrac,
                                        w: Double(b.width)*wFrac, h: Double(b.height)*hFrac))
                    }
                }
                tx += stride
            }
            ty += stride
        }
    }

    // Pass 3 — horizontal strips (navigationBar / textField)
    let imageH = image.height, imageW = image.width
    let stripH = max(1, Int(Double(imageH) * 0.22))
    let stride  = max(1, stripH / 2)
    var y = 0
    while y + stripH <= imageH {
        if let strip = cropCGImage(source: image, x: 0, y: y, width: imageW, height: stripH) {
            for obs in try runReq(on: strip, model: model) {
                let b = obs.boundingBox
                let stripTopVision    = 1.0 - Double(y + stripH) / Double(imageH)
                let stripHeightVision = Double(stripH) / Double(imageH)
                let fullVisionMidY    = stripTopVision + Double(b.midY) * stripHeightVision
                let fullH             = Double(b.height) * stripHeightVision
                dets.append(Det(pass: "strip", label: obs.labels.first?.identifier ?? "?",
                                conf: obs.confidence,
                                cx: Double(b.midX), cy: 1.0 - fullVisionMidY,
                                w: Double(b.width), h: fullH))
            }
        }
        y += stride
    }

    // NMS — same-class, greedy
    let sorted = dets.sorted { $0.conf > $1.conf }
    var kept: [Det] = []; var suppressed = Set<Int>()
    for (i, a) in sorted.enumerated() {
        if suppressed.contains(i) { continue }; kept.append(a)
        for (j, b) in sorted.enumerated() where j > i {
            if suppressed.contains(j) || a.label != b.label { continue }
            if iou(a.cx, a.cy, a.w, a.h, b.cx, b.cy, b.w, b.h) > 0.45 { suppressed.insert(j) }
        }
    }
    return kept
}

func printResults(dets: [Det], imageName: String, groundTruths: [(label: String, cx: Double, cy: Double, w: Double, h: Double)]) {
    print("── \(imageName) ─────────────────────────────────────────────────────")
    print("Detections: \(dets.count)")
    print()
    for gt in groundTruths {
        print("  GT \(gt.label.padding(toLength: 18, withPad: " ", startingAt: 0)): cx=\(String(format:"%.3f",gt.cx)) cy=\(String(format:"%.3f",gt.cy)) w=\(String(format:"%.3f",gt.w)) h=\(String(format:"%.3f",gt.h))")
    }
    print()
    if dets.isEmpty {
        print("  ⚠︎  No detections. If this is a known class, check strip/SAHI passes.")
    }
    for d in dets.prefix(10) {
        // Compute best IoU against any GT of matching class
        let bestIoU = groundTruths
            .filter { $0.label == d.label }
            .map { iou(d.cx, d.cy, d.w, d.h, $0.cx, $0.cy, $0.w, $0.h) }
            .max() ?? 0
        let iouStr = bestIoU > 0 ? "IoU=\(String(format:"%.3f",bestIoU))\(bestIoU >= 0.5 ? " ✓" : " ✗")" : ""
        print("  [\(d.pass.padding(toLength: 5, withPad: " ", startingAt: 0))] \(d.label.padding(toLength: 18, withPad: " ", startingAt: 0)) conf=\(String(format:"%.4f",d.conf))  cx=\(String(format:"%.3f",d.cx)) cy=\(String(format:"%.3f",d.cy)) w=\(String(format:"%.3f",d.w)) h=\(String(format:"%.3f",d.h))  \(iouStr)")
    }
    print()
}

// MARK: - Main

print("Model: \(modelURL.lastPathComponent)")
let compiledURL = try MLModel.compileModel(at: modelURL)
let model       = try MLModel(contentsOf: compiledURL)
let vnModel     = try VNCoreMLModel(for: model)
print("Model loaded ✓")
print()

// Determine which image(s) to run
let args = CommandLine.arguments.dropFirst()
let imagesToRun: [(url: URL, name: String, gts: [(label: String, cx: Double, cy: Double, w: Double, h: Double)])]

if let path = args.first {
    imagesToRun = [(
        url: URL(filePath: path),
        name: URL(filePath: path).lastPathComponent,
        gts: []
    )]
} else {
    imagesToRun = [
        (url: alertImageURL,  name: "img_000409 (alert)",
         gts: [("alert", 0.500, 0.488, 0.690, 0.254)]),
        (url: navBarImageURL, name: "img_000809 (navigationBar)",
         gts: [("navigationBar", 0.500, 0.104, 1.000, 0.063)]),
    ]
}

for item in imagesToRun {
    guard let src   = CGImageSourceCreateWithURL(item.url as CFURL, nil),
          let cgImg = CGImageSourceCreateImageAtIndex(src, 0, nil) else {
        print("⚠︎ Could not load \(item.url.path)")
        continue
    }
    let dets = try threePassInference(image: cgImg, model: vnModel)
    printResults(dets: dets, imageName: item.name, groundTruths: item.gts)
}

print("Done. Expected: alert IoU > 0.9 | navigationBar any detection with conf > 0.1")
