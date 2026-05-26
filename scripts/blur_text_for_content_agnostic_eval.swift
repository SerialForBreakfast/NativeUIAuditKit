// blur_text_for_content_agnostic_eval.swift
// NativeUIAuditKit/scripts
//
// TASK-6-5 AC: Content-agnostic test.
//
// Blurs all text regions in validation images using VNRecognizeTextRequest.
// The blurred images are then re-evaluated with eval_map.swift to confirm
// that model accuracy for non-text-dependent classes (navigationBar, tabBar,
// toggle, alert) does not drop >10 AP points — which would indicate the
// model is reading text content as a proxy feature rather than learning
// element shape and position.
//
// Usage (from project root):
//   swift scripts/blur_text_for_content_agnostic_eval.swift
//
// Output:
//   reports/blurred_eval_images/  — blurred PNG copies of validation images
//
// Then run eval_map.swift against the blurred images:
//   # Edit eval_map.swift valImagesDir to point to reports/blurred_eval_images/
//   # OR pass as arg once eval_map.swift gains an --images flag
//
// Baseline mAP comes from the standard eval_map.swift run (reports/eval_results.json).
// If baseline mAP - blurred mAP > 10pp for any of {navigationBar, toggle, alert},
// the model is reading text as a layout proxy — add more structural variety to
// those classes' training templates.

import Foundation
import Vision
import CoreGraphics
import CoreImage
import ImageIO

// MARK: - Config

let projectRoot = URL(filePath: #filePath)
    .deletingLastPathComponent()   // scripts/
    .deletingLastPathComponent()   // project root

let valImagesDir = URL(filePath: "/Users/josephmccraw/Library/Developer/CoreSimulator/Devices/812EDC32-DB8D-49D6-B130-2279180CCDEB/data/Containers/Data/Application/E0711EF5-B600-47B2-A7B8-D5BA63DE1D83/Documents/dataset/createml_export/validation/images")

/// Number of images to blur. TASK-6-5 requires 200.
let imageLimit = 200

/// CIGaussianBlur radius applied to each text observation bounding box.
let blurRadius: Double = 18.0

let outputDir = projectRoot.appending(path: "reports/blurred_eval_images", directoryHint: .isDirectory)

// MARK: - Setup

let fm = FileManager.default
try fm.createDirectory(at: outputDir, withIntermediateDirectories: true)

let allImages = try fm.contentsOfDirectory(at: valImagesDir, includingPropertiesForKeys: nil)
    .filter { $0.pathExtension == "png" }
    .sorted { $0.lastPathComponent < $1.lastPathComponent }

let imagesToProcess = Array(allImages.prefix(imageLimit))
print("Blurring text in \(imagesToProcess.count) validation images → \(outputDir.path)")
print()

// MARK: - Blur one image

/// Detects text regions in `image` using VNRecognizeTextRequest, then
/// applies a Gaussian blur to each bounding box, returning the blurred CGImage.
func blurTextRegions(in cgImage: CGImage) throws -> CGImage {

    // 1. Run text recognition to find text bounding boxes
    var textBoxes: [CGRect] = []
    let textRequest = VNRecognizeTextRequest { request, _ in
        guard let results = request.results as? [VNRecognizedTextObservation] else { return }
        for obs in results {
            // Vision coords: bottom-left origin, normalized [0,1]
            // Convert to pixel coords for drawing
            let b = obs.boundingBox
            let px = CGRect(
                x:      b.minX * Double(cgImage.width),
                y:      b.minY * Double(cgImage.height),   // still bottom-left here
                width:  b.width  * Double(cgImage.width),
                height: b.height * Double(cgImage.height)
            )
            textBoxes.append(px)
        }
    }
    textRequest.recognitionLevel = .fast   // speed over accuracy — we just need box locations
    textRequest.usesLanguageCorrection = false
    try VNImageRequestHandler(cgImage: cgImage, options: [:]).perform([textRequest])

    guard !textBoxes.isEmpty else { return cgImage }   // no text found — return original

    // 2. Apply blur to each text region using Core Image
    let ciImage   = CIImage(cgImage: cgImage)
    let imgHeight = Double(cgImage.height)

    // Build an accumulated blurred image by masking each text region
    var output = ciImage

    for box in textBoxes {
        // Core Image uses bottom-left origin (same as Vision), so no y flip needed.
        // Expand box by 4px to cover antialiased text edges.
        let expanded = box.insetBy(dx: -4, dy: -4)
            .intersection(CGRect(x: 0, y: 0, width: Double(cgImage.width), height: imgHeight))

        // Crop the text region from the current image
        guard let cropped = output.cropped(to: expanded)
                                   .applyingFilter("CIGaussianBlur", parameters: ["inputRadius": blurRadius])
                                   .composited(over: output) as CIImage? else { continue }
        // composited(over:) puts the blurred crop on top of the full image
        // Crop back to the full image extent to avoid the blur expanding the image bounds
        output = cropped.cropped(to: CGRect(x: 0, y: 0, width: Double(cgImage.width), height: imgHeight))
    }

    // 3. Render back to CGImage
    let context = CIContext(options: [.useSoftwareRenderer: false])
    guard let result = context.createCGImage(output, from: CGRect(x: 0, y: 0, width: cgImage.width, height: cgImage.height)) else {
        return cgImage   // fallback to original if rendering fails
    }
    return result
}

// MARK: - Process all images

var processed = 0
var textFound = 0
let startTime = Date()

for imgURL in imagesToProcess {
    guard let src   = CGImageSourceCreateWithURL(imgURL as CFURL, nil),
          let cgImg = CGImageSourceCreateImageAtIndex(src, 0, nil) else {
        print("  ⚠︎ Could not load \(imgURL.lastPathComponent)")
        continue
    }

    let blurred = (try? blurTextRegions(in: cgImg)) ?? cgImg

    // Write output PNG
    let outURL  = outputDir.appending(path: imgURL.lastPathComponent)
    guard let dest = CGImageDestinationCreateWithURL(outURL as CFURL, "public.png" as CFString, 1, nil) else {
        print("  ⚠︎ Could not create destination for \(imgURL.lastPathComponent)")
        continue
    }
    CGImageDestinationAddImage(dest, blurred, nil)
    CGImageDestinationFinalize(dest)

    processed += 1
    if processed % 50 == 0 {
        let elapsed = Date().timeIntervalSince(startTime)
        print("  \(processed)/\(imagesToProcess.count)  (\(String(format: "%.0f", elapsed))s elapsed)")
    }
}

let elapsed = Date().timeIntervalSince(startTime)
print()
print("Done. \(processed) images written in \(String(format: "%.1f", elapsed))s")
print()
print("Next steps:")
print("  1. Edit scripts/eval_map.swift: change valImagesDir to point to reports/blurred_eval_images/")
print("  2. swift scripts/eval_map.swift  →  compare per-class AP to reports/eval_results.json baseline")
print("  3. If any of {navigationBar, toggle, alert} drops >10pp: model reads text as a layout proxy.")
print("     Fix: add more structural variety to those classes' training templates, then retrain.")
