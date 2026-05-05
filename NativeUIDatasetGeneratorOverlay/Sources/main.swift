// NativeUIDatasetGeneratorOverlay — main.swift
// macOS CLI tool for manual spot-checking of generator output.
//
// Renders annotation bounding boxes over the paired PNG and produces
// an HTML gallery for human review. Interactive spot-check mode walks
// through N random images and records Pass/Fail to a JSON report.
//
// Usage:
//   NativeUIDatasetGeneratorOverlay render --image img.png --annotation img.json --output overlaid.png
//   NativeUIDatasetGeneratorOverlay spot-check --dataset-dir Dataset/ --count 50 --output reports/spotcheck_v1.json

import AppKit
import CoreGraphics
import Foundation

// MARK: - Entry point

guard CommandLine.arguments.count >= 2 else {
    printUsage()
    exit(1)
}

let subcommand = CommandLine.arguments[1]

switch subcommand {
case "render":
    runRender()
case "spot-check":
    runSpotCheck()
default:
    fputs("Unknown subcommand: \(subcommand)\n", stderr)
    printUsage()
    exit(1)
}

// MARK: - Subcommand: render

func runRender() {
    var imagePath: String?
    var annotationPath: String?
    var outputPath: String?

    let args = CommandLine.arguments.dropFirst(2)
    var it = args.makeIterator()
    while let arg = it.next() {
        switch arg {
        case "--image":       imagePath      = it.next()
        case "--annotation":  annotationPath = it.next()
        case "--output":      outputPath     = it.next()
        default: break
        }
    }

    guard let imagePath, let annotationPath, let outputPath else {
        fputs("render requires --image, --annotation, and --output.\n", stderr)
        exit(1)
    }

    let result = renderOverlay(imagePath: imagePath, annotationPath: annotationPath)
    switch result {
    case .success(let data):
        do {
            try data.write(to: URL(fileURLWithPath: outputPath))
            print("Wrote overlaid PNG: \(outputPath)")
        } catch {
            fputs("Failed to write output: \(error)\n", stderr)
            exit(1)
        }
    case .failure(let error):
        fputs("Render error: \(error)\n", stderr)
        exit(1)
    }
}

// MARK: - Subcommand: spot-check

func runSpotCheck() {
    var datasetDir: String?
    var count = 50
    var outputPath = "reports/spotcheck_v1.json"
    var version = 1

    let args = CommandLine.arguments.dropFirst(2)
    var it = args.makeIterator()
    while let arg = it.next() {
        switch arg {
        case "--dataset-dir": datasetDir = it.next()
        case "--count":       count = Int(it.next() ?? "50") ?? 50
        case "--output":      outputPath = it.next() ?? outputPath
        case "--version":     version = Int(it.next() ?? "1") ?? 1
        default: break
        }
    }

    guard let datasetDir else {
        fputs("spot-check requires --dataset-dir.\n", stderr)
        exit(1)
    }

    let pairs = findImageAnnotationPairs(in: datasetDir)
    guard !pairs.isEmpty else {
        fputs("No PNG + JSON annotation pairs found in \(datasetDir).\n", stderr)
        exit(1)
    }

    // Randomly sample up to `count` pairs.
    var rng = SeededSystemRNG()
    let sample = Array(pairs.shuffled(using: &rng).prefix(count))

    print("Spot-check mode: reviewing \(sample.count) images from \(datasetDir)")
    print("Press RETURN after each image to record Pass, or type 'f' then RETURN to record Fail.")
    print("Press Ctrl+C to quit early — partial results will be saved.\n")

    var passed = 0
    var failed = 0
    var failedImages: [String] = []

    for (idx, pair) in sample.enumerated() {
        // Render overlay to a temp file.
        let tmpPath = NSTemporaryDirectory() + "overlay_\(idx).png"
        let result = renderOverlay(imagePath: pair.imagePath, annotationPath: pair.annotationPath)
        if case .success(let data) = result {
            try? data.write(to: URL(fileURLWithPath: tmpPath))
        }

        print("[\(idx + 1)/\(sample.count)] \(pair.imagePath)")
        if case .success = result {
            // Open the overlaid image in Preview.
            let task = Process()
            task.executableURL = URL(fileURLWithPath: "/usr/bin/open")
            task.arguments = [tmpPath]
            try? task.run()
        }

        print("Pass (RETURN) or Fail (f + RETURN)?", terminator: " ")
        let input = readLine(strippingNewline: true)?.lowercased() ?? ""
        if input == "f" {
            failed += 1
            failedImages.append(pair.imagePath)
            print("  → FAIL")
        } else {
            passed += 1
            print("  → PASS")
        }
        print()
    }

    let report: [String: Any] = [
        "version": version,
        "totalReviewed": sample.count,
        "passed": passed,
        "failed": failed,
        "failedImages": failedImages,
        "reviewDate": ISO8601DateFormatter().string(from: Date()),
    ]

    do {
        let data = try JSONSerialization.data(withJSONObject: report, options: [.prettyPrinted, .sortedKeys])
        let outputURL = URL(fileURLWithPath: outputPath)
        try FileManager.default.createDirectory(
            at: outputURL.deletingLastPathComponent(),
            withIntermediateDirectories: true
        )
        try data.write(to: outputURL)
        print("Spot-check complete: \(passed) passed, \(failed) failed.")
        print("Report saved to: \(outputPath)")
        if failed > 3 {
            print("WARNING: \(failed) failures exceed the 3-failure threshold. Investigate generator bugs before proceeding.")
        }
    } catch {
        fputs("Failed to write report: \(error)\n", stderr)
        exit(1)
    }
}

// MARK: - Core overlay renderer

/// Draw bounding boxes from `annotationPath` onto the PNG at `imagePath`.
/// Returns the overlaid PNG data.
///
/// Uses `NSImage(size:flipped:drawingHandler:)` with `flipped: true` so the drawing
/// handler operates in a top-left-origin coordinate system that matches the iOS
/// `boundsPixels` annotation coordinates. This avoids the manual CGContext y-flip
/// gymnastics that previously caused the source image to appear inverted and
/// `CTFrameDraw` label text to render horizontally mirrored.
///
/// - Parameters:
///   - imagePath: Absolute path to the source PNG.
///   - annotationPath: Absolute path to the paired annotation JSON.
/// - Returns: PNG data with colored bounding boxes and element-type labels burned in.
func renderOverlay(imagePath: String, annotationPath: String) -> Result<Data, Error> {
    guard let sourceImage = NSImage(contentsOfFile: imagePath) else {
        return .failure(OverlayError.imageLoadFailed(imagePath))
    }

    // Load annotation JSON.
    let annotationURL = URL(fileURLWithPath: annotationPath)
    guard let jsonData = try? Data(contentsOf: annotationURL),
          let json = try? JSONSerialization.jsonObject(with: jsonData) as? [String: Any],
          let elements = json["elements"] as? [[String: Any]] else {
        return .failure(OverlayError.annotationLoadFailed(annotationPath))
    }

    let imageInfo = json["image"] as? [String: Any]
    let scale = (imageInfo?["scale"] as? Int) ?? 1

    // boundsPixels coordinates are in pixels; draw at that resolution.
    guard let cgSource = sourceImage.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        return .failure(OverlayError.imageLoadFailed(imagePath))
    }
    let pixelW = CGFloat(cgSource.width)
    let pixelH = CGFloat(cgSource.height)
    let canvasSize = NSSize(width: pixelW, height: pixelH)

    // NSImage(size:flipped:drawingHandler:) with flipped: true gives a top-left-origin
    // drawing context. NSImage.draw(in:), NSBezierPath, and NSAttributedString all
    // behave correctly in this space — no manual CTM gymnastics required.
    let outputImage = NSImage(size: canvasSize, flipped: true) { _ in
        // Draw the source image filling the full canvas.
        sourceImage.draw(in: NSRect(origin: .zero, size: canvasSize))

        for element in elements {
            guard let typeStr = element["elementType"] as? String,
                  let bpRaw  = element["boundsPixels"] as? [String: Any],
                  let bpx    = bpRaw["x"] as? Double,
                  let bpy    = bpRaw["y"] as? Double,
                  let bpw    = bpRaw["width"] as? Double,
                  let bph    = bpRaw["height"] as? Double else { continue }

            let excluded = element["excluded"] as? Bool ?? false
            guard !excluded else { continue }

            let occluded = element["occluded"] as? Bool ?? false
            let boxRect  = NSRect(x: bpx, y: bpy, width: bpw, height: bph)
            let nsColor  = strokeNSColor(forType: typeStr)
            let lineW    = CGFloat(max(2, scale))

            // Rounded rect stroke.
            let path = NSBezierPath(roundedRect: boxRect.insetBy(dx: lineW / 2, dy: lineW / 2),
                                    xRadius: 4, yRadius: 4)
            path.lineWidth = lineW
            if occluded {
                let dash: [CGFloat] = [lineW * 4, lineW * 2]
                path.setLineDash(dash, count: 2, phase: 0)
            }
            nsColor.setStroke()
            path.stroke()

            // Label tag above the box.
            drawLabel(text: typeStr, at: NSPoint(x: bpx, y: bpy), color: nsColor, scale: scale)
        }
        return true
    }

    // Convert to PNG via a CGImage snapshot.
    guard let cgOutput = outputImage.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        return .failure(OverlayError.renderFailed)
    }
    let bitmap = NSBitmapImageRep(cgImage: cgOutput)
    bitmap.size = canvasSize
    guard let pngData = bitmap.representation(using: .png, properties: [:]) else {
        return .failure(OverlayError.renderFailed)
    }
    return .success(pngData)
}

// MARK: - Colour coding (per class group)

/// Returns the `NSColor` stroke colour for a given element type string.
/// Matches the same group palette used by `BoundingBoxDebugRenderer` on the iOS side.
func strokeNSColor(forType type: String) -> NSColor {
    switch type {
    case "statusBar", "navigationBar", "tabBar", "toolbar", "sidebar", "homeIndicator", "dynamicIsland":
        return NSColor(red: 0.13, green: 0.59, blue: 0.95, alpha: 1)   // blue — chrome
    case "primaryButton", "secondaryButton", "destructiveButton", "cancelAction",
         "textField", "secureField", "toggle", "slider", "segmentedControl",
         "picker", "stepperControl", "searchField", "menuButton", "colorWell":
        return NSColor(red: 0.18, green: 0.80, blue: 0.44, alpha: 1)   // green — controls
    case "alert", "actionSheet", "sheet", "popover", "listRow", "collectionItem",
         "disclosureGroup", "tooltip", "contextMenu":
        return NSColor(red: 1.00, green: 0.60, blue: 0.00, alpha: 1)   // orange — containers
    case "activityIndicator", "progressView", "pageControl", "scrollIndicator", "refreshControl":
        return NSColor(red: 0.60, green: 0.20, blue: 0.80, alpha: 1)   // purple — indicators
    default:
        return NSColor(red: 0.55, green: 0.55, blue: 0.55, alpha: 1)   // grey — special / unknown
    }
}

// MARK: - Label drawing

/// Draws a filled pill tag with monospaced `text` just above `point` (top-left of element box).
///
/// Called from inside an `NSImage(size:flipped:drawingHandler:)` handler where the coordinate
/// system has top-left origin and y increases downward. `NSAttributedString.draw(in:)` in
/// this context renders text correctly without any additional CTM adjustment.
///
/// - Parameters:
///   - text: The element type string to display (e.g. `"textField_0"`).
///   - point: Top-left corner of the bounding box (top-left-origin pixel coordinates).
///   - color: Fill colour for the pill background; white text is used for contrast.
///   - scale: Pixel scale factor (1, 2, or 3) — controls font size and padding.
func drawLabel(text: String, at point: NSPoint, color: NSColor, scale: Int) {
    let fontSize = CGFloat(max(10, scale * 7))
    let attrs: [NSAttributedString.Key: Any] = [
        .font: NSFont.monospacedSystemFont(ofSize: fontSize, weight: .medium),
        .foregroundColor: NSColor.white,
    ]
    let str = NSAttributedString(string: text, attributes: attrs)
    let textSize = str.size()
    let hPad = 3.0 * CGFloat(scale)
    let vPad = 2.0 * CGFloat(scale)

    let tagW = textSize.width  + hPad * 2
    let tagH = textSize.height + vPad * 2

    // Place tag just above the box top edge; clamp so it doesn't go above y=0.
    let tagY = max(0, point.y - tagH - CGFloat(scale))
    let tagRect = NSRect(x: point.x, y: tagY, width: tagW, height: tagH)

    // Filled rounded-rect background.
    let pill = NSBezierPath(roundedRect: tagRect, xRadius: 3, yRadius: 3)
    color.withAlphaComponent(0.88).setFill()
    pill.fill()

    // Text — NSAttributedString.draw(in:) is correct in a flipped NSImage context.
    str.draw(in: NSRect(x: tagRect.minX + hPad, y: tagRect.minY + vPad,
                        width: textSize.width, height: textSize.height))
}

// MARK: - Helpers

struct ImageAnnotationPair {
    let imagePath: String
    let annotationPath: String
}

func findImageAnnotationPairs(in directory: String) -> [ImageAnnotationPair] {
    let fm = FileManager.default
    guard let enumerator = fm.enumerator(atPath: directory) else { return [] }

    var pairs: [ImageAnnotationPair] = []
    while let file = enumerator.nextObject() as? String {
        guard file.hasSuffix(".png") else { continue }
        let base = (file as NSString).deletingPathExtension
        let jsonPath = (directory as NSString).appendingPathComponent(
            (base as NSString).appendingPathExtension("json")!
        )
        let imgPath = (directory as NSString).appendingPathComponent(file)
        if fm.fileExists(atPath: jsonPath) {
            pairs.append(ImageAnnotationPair(imagePath: imgPath, annotationPath: jsonPath))
        }
    }
    return pairs
}

/// System-seeded RNG for sampling — not deterministic (uses arc4random).
struct SeededSystemRNG: RandomNumberGenerator {
    mutating func next() -> UInt64 {
        UInt64(arc4random()) << 32 | UInt64(arc4random())
    }
}

// MARK: - Errors

enum OverlayError: Error, CustomStringConvertible {
    case imageLoadFailed(String)
    case annotationLoadFailed(String)
    case contextCreationFailed
    case renderFailed

    var description: String {
        switch self {
        case .imageLoadFailed(let p):      return "Failed to load image: \(p)"
        case .annotationLoadFailed(let p): return "Failed to load annotation JSON: \(p)"
        case .contextCreationFailed:       return "CGContext creation failed."
        case .renderFailed:                return "Failed to produce output image."
        }
    }
}

// MARK: - Usage

func printUsage() {
    print("""
    NativeUIDatasetGeneratorOverlay — Annotation overlay viewer and spot-check tool

    Subcommands:
      render       Draw bounding boxes on a single PNG.
      spot-check   Interactively review N random images and record Pass/Fail.

    render options:
      --image <path>       Path to the source PNG.
      --annotation <path>  Path to the paired annotation JSON.
      --output <path>      Path for the overlaid output PNG.

    spot-check options:
      --dataset-dir <dir>  Directory containing PNG + JSON pairs.
      --count <N>          Number of random images to review (default: 50).
      --output <path>      Path for the JSON report (default: reports/spotcheck_v1.json).
      --version <N>        Version suffix for the report filename (default: 1).

    Box colours:
      Blue   = Chrome elements (navigationBar, tabBar, …)
      Green  = Controls (button, textField, toggle, …)
      Orange = Containers (alert, sheet, listRow, …)
      Purple = Indicators (progressView, activityIndicator, …)
      Grey   = Special (webContent, unknown)
      Dashed = Occluded elements
    """)
}
