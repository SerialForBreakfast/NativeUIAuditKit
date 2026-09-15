#!/usr/bin/env swift
// tvos_detect.swift
// NativeUIAuditKit — tvOS Offline Detection CLI for TVTestRig
//
// Standalone offline CLI for detecting native Apple TV UI elements,
// performing OCR text recognition, and authoritatively determining the focused element.
//
// Usage:
//   swift scripts/tvos_detect.swift --image /path/to/screenshot.png [--output /path/to/result.json] [--pretty]

import Foundation
import CoreGraphics
import ImageIO
import Vision

// MARK: - CLI Argument Parsing

struct CLIArgs {
    var imagePath: String?
    var outputPath: String?
    var minConfidence: Double = 0.40
    var prettyPrint: Bool = true
}

func parseArguments() -> CLIArgs {
    var args = CLIArgs()
    let raw = CommandLine.arguments

    var i = 1
    while i < raw.count {
        switch raw[i] {
        case "--image", "-i":
            if i + 1 < raw.count { args.imagePath = raw[i + 1]; i += 1 }
        case "--output", "-o":
            if i + 1 < raw.count { args.outputPath = raw[i + 1]; i += 1 }
        case "--min-conf":
            if i + 1 < raw.count, let val = Double(raw[i + 1]) { args.minConfidence = val; i += 1 }
        case "--pretty":
            args.prettyPrint = true
        case "--compact":
            args.prettyPrint = false
        case "--help", "-h":
            print("""
            tvos_detect — Offline tvOS UI Detection CLI for TVTestRig

            Usage:
              swift scripts/tvos_detect.swift --image <path.png> [options]

            Options:
              --image, -i <path>       Path to tvOS screenshot PNG (1920x1080 or 3840x2160)
              --output, -o <path>      Output JSON file path (defaults to stdout if omitted)
              --min-conf <float>       Minimum detection confidence threshold (default: 0.40)
              --compact                Output minified JSON
              --help, -h               Show this help message
            """)
            exit(0)
        default:
            if args.imagePath == nil && !raw[i].hasPrefix("-") {
                args.imagePath = raw[i]
            }
        }
        i += 1
    }
    return args
}

// MARK: - Models

struct DetectionRect: Codable, Sendable {
    let x: Double
    let y: Double
    let width: Double
    let height: Double
}

struct ElementState: Codable, Sendable {
    var isEnabled: Bool = true
    var isSelected: Bool = false
    var isFocused: Bool? = nil
}

struct ElementObservation: Codable, Sendable {
    let id: String
    let elementType: String
    let boundingBox: DetectionRect        // Vision normalized [0,1], bottom-left origin
    let boundingBoxPixels: DetectionRect  // Pixel rect, top-left origin
    let confidence: Double
    let visibleText: String?
    let state: ElementState
}

struct DetectionOutput: Codable, Sendable {
    let imageWidth: Int
    let imageHeight: Int
    let focusedElementId: String?
    let totalElements: Int
    let elements: [ElementObservation]
}

// MARK: - OCR Text Extraction

func extractOCRRegions(from cgImage: CGImage) -> [(text: String, rect: CGRect, conf: Float)] {
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = true

    let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
    do {
        try handler.perform([request])
    } catch {
        fputs("WARNING: OCR failed: \(error.localizedDescription)\n", stderr)
        return []
    }

    guard let results = request.results else { return [] }
    let w = Double(cgImage.width)
    let h = Double(cgImage.height)

    return results.compactMap { obs in
        guard let candidate = obs.topCandidates(1).first else { return nil }
        let box = obs.boundingBox
        // Convert Vision normalized box (bottom-left origin) to pixel rect (top-left origin)
        let pxX = box.minX * w
        let pxY = (1.0 - box.minY - box.height) * h
        let pxW = box.width * w
        let pxH = box.height * h
        let pixelRect = CGRect(x: pxX, y: pxY, width: pxW, height: pxH)
        return (text: candidate.string, rect: pixelRect, conf: candidate.confidence)
    }
}

// MARK: - Pixel Luminance / Focus Analyzer

func evaluateElementLuminance(cgImage: CGImage, pixelRect: CGRect) -> Double {
    let w = cgImage.width
    let h = cgImage.height

    let cropRect = pixelRect.intersection(CGRect(x: 0, y: 0, width: w, height: h))
    guard cropRect.width >= 4, cropRect.height >= 4,
          let cropped = cgImage.cropping(to: cropRect) else {
        return 0.0
    }

    let cw = cropped.width
    let ch = cropped.height
    let bytesPerPixel = 4
    let bytesPerRow = cw * bytesPerPixel
    var rawData = [UInt8](repeating: 0, count: ch * bytesPerRow)

    let colorSpace = CGColorSpaceCreateDeviceRGB()
    guard let ctx = CGContext(
        data: &rawData,
        width: cw,
        height: ch,
        bitsPerComponent: 8,
        bytesPerRow: bytesPerRow,
        space: colorSpace,
        bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
    ) else { return 0.0 }

    ctx.draw(cropped, in: CGRect(x: 0, y: 0, width: cw, height: ch))

    // Sample pixels across the crop to compute mean luminance
    var totalLuminance = 0.0
    var count = 0

    // Sample interior (inset 15% to avoid borders)
    let minX = Int(Double(cw) * 0.15)
    let maxX = Int(Double(cw) * 0.85)
    let minY = Int(Double(ch) * 0.15)
    let maxY = Int(Double(ch) * 0.85)

    let step = max(1, (maxX - minX) / 20)

    for y in stride(from: minY, to: maxY, by: max(1, step)) {
        for x in stride(from: minX, to: maxX, by: max(1, step)) {
            let offset = (y * bytesPerRow) + (x * bytesPerPixel)
            if offset + 3 < rawData.count {
                let r = Double(rawData[offset]) / 255.0
                let g = Double(rawData[offset + 1]) / 255.0
                let b = Double(rawData[offset + 2]) / 255.0
                let lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
                totalLuminance += lum
                count += 1
            }
        }
    }

    return count > 0 ? (totalLuminance / Double(count)) : 0.0
}

// MARK: - Main Pipeline

func run() -> Int32 {
    let args = parseArguments()

    guard let imgPath = args.imagePath else {
        fputs("ERROR: No input image specified. Use --image <path.png>\n", stderr)
        return 1
    }

    let url = URL(fileURLWithPath: imgPath)
    guard let src = CGImageSourceCreateWithURL(url as CFURL, nil),
          let cgImage = CGImageSourceCreateImageAtIndex(src, 0, nil) else {
        fputs("ERROR: Could not load image from \(imgPath)\n", stderr)
        return 1
    }

    let width = cgImage.width
    let height = cgImage.height

    fputs("Processing tvOS screenshot: \(width)x\(height) [\(url.lastPathComponent)]\n", stderr)

    // 1. Extract OCR text
    let ocrResults = extractOCRRegions(from: cgImage)
    fputs("Extracted \(ocrResults.count) OCR text regions\n", stderr)

    // 2. Detect candidate UI elements
    // Form candidates from OCR regions and layout clusters
    var candidateElements: [(
        id: String,
        type: String,
        pixelRect: CGRect,
        text: String?,
        confidence: Double,
        luminance: Double
    )] = []

    for (i, ocr) in ocrResults.enumerated() {
        let r = ocr.rect
        // Infer element type from geometry and position
        var elemType = "label"
        if r.minY < Double(height) * 0.15 {
            elemType = "tabBar"
        } else if r.width > 400 && r.height < 100 {
            elemType = "listRow"
        } else if r.width >= 120 && r.width <= 400 && r.height >= 80 {
            elemType = "collectionItem"
        } else if r.height >= 44 && r.height <= 90 {
            elemType = "primaryButton"
        }

        // Measure crop luminance
        let lum = evaluateElementLuminance(cgImage: cgImage, pixelRect: r)

        candidateElements.append((
            id: "\(elemType)_\(i)",
            type: elemType,
            pixelRect: r,
            text: ocr.text,
            confidence: Double(ocr.conf),
            luminance: lum
        ))
    }

    // 3. Focus Evaluation:
    // In tvOS, the focused element has a distinctive solid white/high-contrast background (luminance > 0.70).
    // Find candidate with highest luminance among interactive controls.
    let interactiveCandidates = candidateElements.filter {
        $0.type == "listRow" || $0.type == "collectionItem" || $0.type == "primaryButton" || $0.type == "tabBar"
    }

    let focusWinner = interactiveCandidates
        .filter { $0.luminance > 0.60 }
        .max { $0.luminance < $1.luminance }

    var observations: [ElementObservation] = []

    for cand in candidateElements {
        let isFocused = (focusWinner != nil && cand.id == focusWinner!.id)

        // Vision normalized rect: bottom-left origin, [0,1] range
        let vnX = cand.pixelRect.minX / Double(width)
        let vnY = 1.0 - (cand.pixelRect.minY + cand.pixelRect.height) / Double(height)
        let vnW = cand.pixelRect.width / Double(width)
        let vnH = cand.pixelRect.height / Double(height)

        let obs = ElementObservation(
            id: cand.id,
            elementType: cand.type,
            boundingBox: DetectionRect(x: vnX, y: vnY, width: vnW, height: vnH),
            boundingBoxPixels: DetectionRect(
                x: cand.pixelRect.minX,
                y: cand.pixelRect.minY,
                width: cand.pixelRect.width,
                height: cand.pixelRect.height
            ),
            confidence: cand.confidence,
            visibleText: cand.text,
            state: ElementState(
                isEnabled: true,
                isSelected: false,
                isFocused: isFocused ? true : false
            )
        )
        observations.append(obs)
    }

    let output = DetectionOutput(
        imageWidth: width,
        imageHeight: height,
        focusedElementId: focusWinner?.id,
        totalElements: observations.count,
        elements: observations
    )

    // Encode JSON
    let encoder = JSONEncoder()
    if args.prettyPrint {
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
    }

    guard let jsonData = try? encoder.encode(output),
          let jsonStr = String(data: jsonData, encoding: .utf8) else {
        fputs("ERROR: Failed to serialize output JSON\n", stderr)
        return 1
    }

    // Output
    if let outPath = args.outputPath {
        let outURL = URL(fileURLWithPath: outPath)
        do {
            try jsonData.write(to: outURL, options: .atomic)
            fputs("Saved observations to: \(outPath)\n", stderr)
        } catch {
            fputs("ERROR: Could not write output to \(outPath): \(error.localizedDescription)\n", stderr)
            return 1
        }
    } else {
        print(jsonStr)
    }

    // Print summary to stderr
    fputs("\n--- tvOS Detection Summary ---\n", stderr)
    if let foc = focusWinner {
        fputs(" [FOCUSED] \(foc.type) [\(foc.id)] at \(Int(foc.pixelRect.minX)),\(Int(foc.pixelRect.minY)) (\(Int(foc.pixelRect.width))x\(Int(foc.pixelRect.height))) | Text: \"\(foc.text ?? "")\"\n", stderr)
    } else {
        fputs(" [FOCUS] No clear focused element detected (all luminance <= 0.60)\n", stderr)
    }
    fputs(" Total elements detected: \(observations.count)\n", stderr)
    fputs("------------------------------\n", stderr)

    return 0
}

exit(run())
