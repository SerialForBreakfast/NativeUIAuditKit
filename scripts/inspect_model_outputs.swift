// inspect_model_outputs.swift
// NativeUIAuditKit/scripts
//
// Bypasses VNCoreMLRequest and calls MLModel.prediction() directly to see raw
// output tensor names, shapes, and top values. Used to diagnose why navigationBar
// and textField produce zero VNCoreMLRequest detections.
//
// Usage (from project root):
//   swift scripts/inspect_model_outputs.swift [path/to/image.png]

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

let defaultImage = URL(filePath: "/Users/josephmccraw/Library/Developer/CoreSimulator/Devices/812EDC32-DB8D-49D6-B130-2279180CCDEB/data/Containers/Data/Application/E0711EF5-B600-47B2-A7B8-D5BA63DE1D83/Documents/dataset/createml_export/validation/images/img_000809.png")

let imgURL: URL = CommandLine.arguments.count > 1
    ? URL(filePath: CommandLine.arguments[1]) : defaultImage

// MARK: - Load model

let compiledURL = try MLModel.compileModel(at: modelURL)
let model = try MLModel(contentsOf: compiledURL)

print("=== Model Description ===")
let desc = model.modelDescription
print("Input features:")
for f in desc.inputDescriptionsByName {
    print("  \(f.key): \(f.value)")
}
print("Output features:")
for f in desc.outputDescriptionsByName {
    print("  \(f.key): \(f.value)")
}
print()

// MARK: - Resize image to model input size (299×299)

guard let src = CGImageSourceCreateWithURL(imgURL as CFURL, nil),
      let cgImg = CGImageSourceCreateImageAtIndex(src, 0, nil) else {
    fputs("Failed to load image\n", stderr); exit(1)
}
print("Original image: \(cgImg.width)×\(cgImg.height)")

// Scale fill: stretch to 299×299 (match training preprocessing per BP-25)
let inputSize = 299
let ctx = CGContext(
    data: nil, width: inputSize, height: inputSize,
    bitsPerComponent: 8, bytesPerRow: inputSize * 4,
    space: CGColorSpaceCreateDeviceRGB(),
    bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue
)!
ctx.draw(cgImg, in: CGRect(x: 0, y: 0, width: inputSize, height: inputSize))
let resized = ctx.makeImage()!
print("Resized to: \(resized.width)×\(resized.height)")

// MARK: - Make prediction using CVPixelBuffer

var pixelBuffer: CVPixelBuffer?
CVPixelBufferCreate(nil, inputSize, inputSize, kCVPixelFormatType_32ARGB, nil, &pixelBuffer)
CVPixelBufferLockBaseAddress(pixelBuffer!, [])
let pbCtx = CGContext(
    data: CVPixelBufferGetBaseAddress(pixelBuffer!),
    width: inputSize, height: inputSize,
    bitsPerComponent: 8,
    bytesPerRow: CVPixelBufferGetBytesPerRow(pixelBuffer!),
    space: CGColorSpaceCreateDeviceRGB(),
    bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue
)!
pbCtx.draw(resized, in: CGRect(x: 0, y: 0, width: inputSize, height: inputSize))
CVPixelBufferUnlockBaseAddress(pixelBuffer!, [])

// Override internal NMS thresholds so we see ALL detections
let input = try MLDictionaryFeatureProvider(dictionary: [
    "image": pixelBuffer!,
    "confidenceThreshold": MLFeatureValue(double: 0.0),
    "iouThreshold": MLFeatureValue(double: 1.0)   // suppress NMS suppression
])
let output = try model.prediction(from: input)

print()
print("=== Raw Output Values ===")
for key in output.featureNames.sorted() {
    let val = output.featureValue(for: key)
    if let mla = val?.multiArrayValue {
        print("\(key): shape=\(mla.shape)  dtype=\(mla.dataType.rawValue)")
        // Print first 20 values
        let count = min(mla.count, 20)
        var vals: [String] = []
        for i in 0..<count {
            vals.append(String(format: "%.4f", mla[i].doubleValue))
        }
        print("  first \(count) values: [\(vals.joined(separator: ", "))]")
        // Print max value and its index
        var maxVal = Double.leastNormalMagnitude
        var maxIdx = 0
        for i in 0..<mla.count {
            let v = mla[i].doubleValue
            if v > maxVal { maxVal = v; maxIdx = i }
        }
        print("  max: \(String(format: "%.4f", maxVal)) at index \(maxIdx)")
    } else if let str = val?.stringValue {
        print("\(key): \"\(str)\"")
    } else if let dbl = val?.doubleValue {
        print("\(key): \(dbl)")
    } else {
        print("\(key): \(val as Any)")
    }
}
