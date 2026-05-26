// diagnose_fp_passes.swift
// NativeUIAuditKit/scripts
//
// Diagnostic: for a sample of validation images, reports which inference pass
// (full-image, SAHI, or strip) is generating false positive navBar predictions,
// and at which strip indices they appear.
//
// This helps distinguish between:
//   A) Strip pass firing in wrong strips (bottom-of-image strips predicting navBar)
//   B) SAHI tiles producing many remapped FP predictions
//   C) Full-image pass generating FPs
//
// Usage (from project root):
//   swift scripts/diagnose_fp_passes.swift

import Foundation
import CoreML
import Vision
import CoreGraphics
import ImageIO

let projectRoot = URL(filePath: #filePath)
    .deletingLastPathComponent()
    .deletingLastPathComponent()

let modelURL = projectRoot
    .appending(path: "NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/NativeUIDetector_v1.mlpackage.mlmodel")

let valImagesDir = URL(filePath: "/Users/josephmccraw/Library/Developer/CoreSimulator/Devices/812EDC32-DB8D-49D6-B130-2279180CCDEB/data/Containers/Data/Application/E0711EF5-B600-47B2-A7B8-D5BA63DE1D83/Documents/dataset/createml_export/validation/images")

let confThreshold: Float = 0.10
let targetClass = "navigationBar"
let sampleCount = 10

// MARK: - Load model

print("Loading model...")
let compiledURL = try MLModel.compileModel(at: modelURL)
let model = try VNCoreMLModel(for: MLModel(contentsOf: compiledURL))
print("Model loaded ✓\n")

// MARK: - Sample images

let allImages = (try? FileManager.default.contentsOfDirectory(at: valImagesDir, includingPropertiesForKeys: nil)
    .filter { ["png","jpg","jpeg"].contains($0.pathExtension.lowercased()) }
    .sorted { $0.lastPathComponent < $1.lastPathComponent }) ?? []

let sample = Array(allImages.prefix(sampleCount))
print("Analyzing \(sample.count) images for \(targetClass) FP sources\n")
print(String(repeating: "─", count: 70))

// MARK: - Per-image analysis

struct PassResult {
    var fullPreds: Int = 0
    var sahiPreds: Int = 0
    var stripPreds: [(idx: Int, yFraction: Double, conf: Float)] = []
}

for imgURL in sample {
    guard let src = CGImageSourceCreateWithURL(imgURL as CFURL, nil),
          let cg  = CGImageSourceCreateImageAtIndex(src, 0, nil) else {
        print("⚠ Could not load \(imgURL.lastPathComponent)")
        continue
    }

    var result = PassResult()

    // Pass 1 — full image
    let req1 = VNCoreMLRequest(model: model)
    req1.imageCropAndScaleOption = .scaleFill
    try VNImageRequestHandler(cgImage: cg, options: [:]).perform([req1])
    result.fullPreds = (req1.results as? [VNRecognizedObjectObservation] ?? [])
        .filter { $0.confidence >= confThreshold && $0.labels.first?.identifier == targetClass }
        .count

    // Pass 2 — SAHI tiles
    if let up = { () -> CGImage? in
        guard let ctx = CGContext(data: nil, width: cg.width*2, height: cg.height*2,
                                  bitsPerComponent: 8, bytesPerRow: 0,
                                  space: CGColorSpaceCreateDeviceRGB(),
                                  bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue) else { return nil }
        ctx.interpolationQuality = .none
        ctx.draw(cg, in: CGRect(x:0, y:0, width: cg.width*2, height: cg.height*2))
        return ctx.makeImage()
    }() {
        let W = up.width, H = up.height, tileSize = 640, stride = 480
        var ty = 0
        while ty < H {
            let tH = min(tileSize, H - ty); var tx = 0
            while tx < W {
                let tW = min(tileSize, W - tx)
                if let tile: CGImage = {
                    guard let ctx = CGContext(data: nil, width: tW, height: tH,
                                              bitsPerComponent: 8, bytesPerRow: 0,
                                              space: CGColorSpaceCreateDeviceRGB(),
                                              bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue) else { return nil }
                    ctx.draw(up, in: CGRect(x: -tx, y: -(H - ty - tH), width: W, height: H))
                    return ctx.makeImage()
                }() {
                    let req2 = VNCoreMLRequest(model: model)
                    req2.imageCropAndScaleOption = .scaleFill
                    try VNImageRequestHandler(cgImage: tile, options: [:]).perform([req2])
                    let n = (req2.results as? [VNRecognizedObjectObservation] ?? [])
                        .filter { $0.confidence >= confThreshold && $0.labels.first?.identifier == targetClass }
                        .count
                    result.sahiPreds += n
                }
                tx += stride
            }
            ty += stride
        }
    }

    // Pass 3 — strips
    let imgH = cg.height, imgW = cg.width
    let stripH = max(1, Int(Double(imgH) * 0.22))
    let strideH = max(1, stripH / 2)
    var y = 0, stripIdx = 0
    while y + stripH <= imgH {
        if let strip: CGImage = {
            guard let ctx = CGContext(data: nil, width: imgW, height: stripH,
                                      bitsPerComponent: 8, bytesPerRow: 0,
                                      space: CGColorSpaceCreateDeviceRGB(),
                                      bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue) else { return nil }
            ctx.draw(cg, in: CGRect(x: 0, y: -(cg.height - y - stripH), width: imgW, height: imgH))
            return ctx.makeImage()
        }() {
            let req3 = VNCoreMLRequest(model: model)
            req3.imageCropAndScaleOption = .scaleFill
            try VNImageRequestHandler(cgImage: strip, options: [:]).perform([req3])
            let preds = (req3.results as? [VNRecognizedObjectObservation] ?? [])
                .filter { $0.confidence >= confThreshold && $0.labels.first?.identifier == targetClass }
            for p in preds {
                let yFrac = Double(y) / Double(imgH)  // how far down the image this strip starts (0=top, 1=bottom)
                result.stripPreds.append((idx: stripIdx, yFraction: yFrac, conf: p.confidence))
            }
        }
        y += strideH
        stripIdx += 1
    }

    // Print summary
    let totalStrip = result.stripPreds.count
    let topStrips  = result.stripPreds.filter { $0.yFraction < 0.20 }.count  // top 20% of image
    let botStrips  = result.stripPreds.filter { $0.yFraction >= 0.20 }.count // rest
    print("\n\(imgURL.lastPathComponent)  (\(cg.width)×\(cg.height))")
    print("  full=\(result.fullPreds)  sahi=\(result.sahiPreds)  strip=\(totalStrip)")
    print("  strip breakdown: top-of-image=\(topStrips)  mid/bottom=\(botStrips)")
    if !result.stripPreds.isEmpty {
        for sp in result.stripPreds.prefix(5) {
            print(String(format: "    strip[%02d] yStart=%.2f conf=%.3f", sp.idx, sp.yFraction, sp.conf))
        }
        if result.stripPreds.count > 5 { print("    ... +\(result.stripPreds.count - 5) more") }
    }
}

print("\n" + String(repeating: "─", count: 70))
print("Key: yStart=0.0 = top of image, yStart=0.8 = bottom strip")
print("A navBar should only be in strips with yStart < 0.15")
print("FPs at yStart >= 0.20 confirm model fires in wrong strips")
