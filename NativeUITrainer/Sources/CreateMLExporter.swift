// CreateMLExporter.swift
// NativeUITrainer
//
// Converts our custom annotation format to Create ML's directoryWithImages format.
//
// ## Two export modes
//
// **Full-image mode** (stripFraction == 0):
//   Each source PNG is hard-linked into images/ and its annotations are written as-is.
//   Good for large, object-like elements (alert, toggle) but fails for full-width thin
//   elements (navigationBar, textField) due to YOLO anchor-assignment failure at 16:1
//   aspect ratio. See BP-26.
//
// **Strip mode** (stripFraction > 0, e.g. 0.22):
//   Each source PNG is ALSO sliced into overlapping horizontal strips of height
//   (stripFraction × imageHeight), stride (stripFraction/2 × imageHeight).
//   In a 22%-tall strip, navigationBar goes from 16:1 → 3.5:1 and textField from
//   21:1 → 2.9:1 — within the objectPrint anchor-assignment range.
//   The original full images are still included alongside the strips, so large
//   elements (alert) also remain well-represented.
//
// ## Output layout (same in both modes)
//   <outputDir>/images/           — PNGs (hard-linked originals + written strip crops)
//   <outputDir>/annotations.json  — single consolidated Create ML annotation file
//
// ## Coordinate systems
//   Source annotations use boundsVisionNormalized (Vision bottom-left origin).
//   Exported annotations use Create ML normalized (top-left origin, center-anchored):
//     cx = vn.x + vn.width  / 2
//     cy = 1.0 - vn.y - vn.height / 2   ← y-axis flip
//   Strip annotations further remap cy and h into strip-local normalized space:
//     scaleY    = imageHeight / stripHeight
//     cy_strip  = (cy_full - stripTopNorm) * scaleY
//     h_strip   = h_full * scaleY

import CoreGraphics
import Foundation
import ImageIO

// MARK: - Source annotation types

private struct OurAnnotation: Decodable {
    let elements: [OurElement]
}

private struct OurElement: Decodable {
    let elementType: String
    let boundsPixels: OurRect
    let boundsVisionNormalized: OurRect
}

private struct OurRect: Decodable {
    let x, y, width, height: Double
}

// MARK: - Create ML output types

struct CreateMLAnnotation: Encodable {
    let label: String
    let coordinates: CreateMLRect
}

struct CreateMLRect: Encodable {
    let x, y, width, height: Double
}

private struct CreateMLImageEntry: Encodable {
    let imagefilename: String
    let annotation: [CreateMLAnnotation]
}

// MARK: - Export result

struct ExportResult {
    let imagesDir: URL
    let annotationFile: URL
    let classCounts: [String: Int]
}

// MARK: - Internal record

private struct ImageRecord {
    let pngURL: URL
    /// Annotations in Create ML normalized coords (top-left origin, center-anchored).
    let elements: [(label: String, cx: Double, cy: Double, w: Double, h: Double)]
}

// MARK: - Exporter

struct CreateMLExporter {

    /// Exports the dataset split at `datasetDir/<split>/` to `outputDir`.
    ///
    /// When `stripFraction > 0`, each image generates:
    ///   - one full-image entry (unchanged)
    ///   - N overlapping horizontal-strip entries, stride = stripFraction/2
    ///
    /// Strip naming: `<basename>_s<index:02d>.png`
    @discardableResult
    static func export(
        datasetDir: URL,
        to outputDir: URL,
        targetClasses: Set<String>,
        split: String,
        capPerClass: Int,
        stripFraction: Double = 0.0
    ) throws -> ExportResult {

        let fm = FileManager.default
        let imagesDir = outputDir.appending(path: "images", directoryHint: .isDirectory)
        try fm.createDirectory(at: imagesDir, withIntermediateDirectories: true)

        let splitDir = datasetDir.appending(path: split, directoryHint: .isDirectory)
        guard fm.fileExists(atPath: splitDir.path) else {
            throw ExporterError.splitDirectoryNotFound(splitDir.path)
        }

        // Enumerate source PNGs
        let pngURLs = try fm.contentsOfDirectory(at: splitDir, includingPropertiesForKeys: nil)
            .filter { $0.pathExtension == "png" }
            .sorted { $0.lastPathComponent < $1.lastPathComponent }

        // MARK: Pass 1 — load all source records in Create ML normalized coords

        var allRecords: [ImageRecord] = []

        for pngURL in pngURLs {
            let jsonURL = pngURL.deletingPathExtension().appendingPathExtension("json")
            guard fm.fileExists(atPath: jsonURL.path),
                  let data = try? Data(contentsOf: jsonURL),
                  let ann  = try? JSONDecoder().decode(OurAnnotation.self, from: data)
            else { continue }

            let elems = ann.elements
                .filter { targetClasses.contains($0.elementType) }
                .map { elem -> (label: String, cx: Double, cy: Double, w: Double, h: Double) in
                    let vn = elem.boundsVisionNormalized
                    return (
                        label: elem.elementType,
                        cx: vn.x + vn.width  / 2,
                        cy: 1.0 - vn.y - vn.height / 2,
                        w:  vn.width,
                        h:  vn.height
                    )
                }
            guard !elems.isEmpty else { continue }
            allRecords.append(ImageRecord(pngURL: pngURL, elements: elems))
        }

        // MARK: Pass 2 — greedy subsampling on full-image records

        var classCount: [String: Int] = [:]
        var selectedPNGs = Set<URL>()
        let candidates = allRecords.sorted { $0.pngURL.path < $1.pngURL.path }

        for record in candidates {
            let classes = record.elements.map(\.label)
            let anyBelow = classes.contains { (classCount[$0] ?? 0) < capPerClass }
            guard anyBelow else { continue }
            selectedPNGs.insert(record.pngURL)
            for cls in Set(classes) {
                classCount[cls, default: 0] += record.elements.filter { $0.label == cls }.count
            }
        }

        // MARK: Pass 3 — build export entries (full images + optional strips)

        var entries: [CreateMLImageEntry] = []

        for pngURL in selectedPNGs.sorted(by: { $0.path < $1.path }) {
            guard let record = allRecords.first(where: { $0.pngURL == pngURL }) else { continue }

            // --- Full-image entry ---

            let destPNG = imagesDir.appending(path: pngURL.lastPathComponent)
            if !fm.fileExists(atPath: destPNG.path) {
                try fm.linkItem(at: pngURL, to: destPNG)
            }

            entries.append(CreateMLImageEntry(
                imagefilename: pngURL.lastPathComponent,
                annotation: record.elements.map {
                    CreateMLAnnotation(label: $0.label,
                                       coordinates: CreateMLRect(x: $0.cx, y: $0.cy,
                                                                 width: $0.w, height: $0.h))
                }
            ))

            // --- Strip entries ---

            guard stripFraction > 0 else { continue }

            // Load source CGImage (needed for dimensions + cropping)
            guard let imageSource = CGImageSourceCreateWithURL(pngURL as CFURL, nil),
                  let cgImage = CGImageSourceCreateImageAtIndex(imageSource, 0, nil)
            else { continue }

            let imageWidth  = cgImage.width
            let imageHeight = cgImage.height
            let stripH = max(1, Int(Double(imageHeight) * stripFraction))
            let stride  = max(1, stripH / 2)

            var stripIndex = 0
            var stripY = 0
            while stripY + stripH <= imageHeight {
                defer { stripY += stride; stripIndex += 1 }

                let yTopNorm    = Double(stripY)            / Double(imageHeight)
                let yBottomNorm = Double(stripY + stripH)   / Double(imageHeight)
                let scaleY      = Double(imageHeight)       / Double(stripH)

                // Filter: keep elements whose center falls within the strip
                let stripElems = record.elements.compactMap {
                    elem -> (label: String, cx: Double, cy: Double, w: Double, h: Double)? in
                    guard elem.cy >= yTopNorm && elem.cy <= yBottomNorm else { return nil }
                    // Remap to strip-local normalized coords (top-left, center-anchored)
                    let cy_s = (elem.cy - yTopNorm) * scaleY
                    let h_s  = elem.h * scaleY
                    // Clamp to [0,1] in case the element overflows the strip edge
                    let cy_clamped = max(0.0, min(1.0, cy_s))
                    let h_clamped  = max(0.0, min(1.0, h_s))
                    guard h_clamped > 0.01 else { return nil }   // discard near-invisible boxes
                    return (label: elem.label, cx: elem.cx, cy: cy_clamped,
                            w: elem.w, h: h_clamped)
                }
                guard !stripElems.isEmpty else { continue }

                // Crop CGImage to strip using a CGContext
                // CGContext uses bottom-left origin. To show source rows [stripY, stripY+stripH):
                //   draw full source at y = -(imageHeight - stripY - stripH)
                guard let stripCtx = CGContext(
                    data: nil,
                    width: imageWidth, height: stripH,
                    bitsPerComponent: 8, bytesPerRow: 0,
                    space: CGColorSpaceCreateDeviceRGB(),
                    bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue
                ) else { continue }

                let drawY = -(imageHeight - stripY - stripH)
                stripCtx.draw(cgImage,
                               in: CGRect(x: 0, y: drawY,
                                          width: imageWidth, height: imageHeight))
                guard let stripImage = stripCtx.makeImage() else { continue }

                // Write strip PNG
                let baseName    = pngURL.deletingPathExtension().lastPathComponent
                let stripName   = "\(baseName)_s\(String(format: "%02d", stripIndex)).png"
                let stripDestURL = imagesDir.appending(path: stripName)

                guard let dest = CGImageDestinationCreateWithURL(
                    stripDestURL as CFURL, "public.png" as CFString, 1, nil
                ) else { continue }
                CGImageDestinationAddImage(dest, stripImage, nil)
                guard CGImageDestinationFinalize(dest) else { continue }

                entries.append(CreateMLImageEntry(
                    imagefilename: stripName,
                    annotation: stripElems.map {
                        CreateMLAnnotation(label: $0.label,
                                           coordinates: CreateMLRect(x: $0.cx, y: $0.cy,
                                                                     width: $0.w, height: $0.h))
                    }
                ))
            }
        }

        // MARK: Write consolidated annotation JSON

        let annotationFileURL = outputDir.appending(path: "annotations.json")
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted]
        let jsonData = try encoder.encode(entries)
        try jsonData.write(to: annotationFileURL)

        let fullImageCount = selectedPNGs.count
        let stripCount     = entries.count - fullImageCount
        print("  Exported \(entries.count) images to \(outputDir.path)")
        print("    (\(fullImageCount) full images + \(stripCount) strips)")
        for cls in targetClasses.sorted() {
            print("    \(cls): \(classCount[cls] ?? 0) instances (full-image count)")
        }

        return ExportResult(
            imagesDir: imagesDir,
            annotationFile: annotationFileURL,
            classCounts: classCount
        )
    }
}

// MARK: - Errors

enum ExporterError: Error, CustomStringConvertible {
    case splitDirectoryNotFound(String)

    var description: String {
        switch self {
        case .splitDirectoryNotFound(let p): return "Split directory not found: \(p)"
        }
    }
}
