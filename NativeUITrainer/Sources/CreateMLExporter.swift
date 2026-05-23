// CreateMLExporter.swift
// NativeUITrainer
//
// Converts our custom annotation format to Create ML's directoryWithImages format,
// filtering to a target class set and applying per-class instance subsampling.
//
// Create ML directoryWithImages annotation JSON (ONE file for the whole split):
//   [
//     {
//       "imagefilename": "img001.png",
//       "annotation": [{"label": "className", "coordinates": {"x": cx, "y": cy, "width": w, "height": h}}]
//     }, ...
//   ]
// Coordinates are NORMALIZED [0,1], center-based, top-left origin.
//
// Our source format:
//   {"elements": [
//     {
//       "elementType": "...",
//       "boundsPixels": {"x": left_px, "y": top_px, "width": w_px, "height": h_px},
//       "boundsVisionNormalized": {"x": left_vn, "y": bottom_vn, "width": w_vn, "height": h_vn}
//     }
//   ]}
//
// boundsVisionNormalized uses Vision's coordinate system:
//   x = left edge (from left, 0–1)
//   y = bottom edge distance from the BOTTOM of the image (0–1); y increases upward
// → Convert to Create ML normalized center-based top-left:
//   cx = vn.x + vn.width / 2
//   cy = 1 - vn.y - vn.height / 2   (flip y-axis)
//   width  = vn.width
//   height = vn.height

import Foundation

// MARK: - Input types (partial mirror of our annotation schema)

private struct OurAnnotation: Decodable {
    let elements: [OurElement]
}

private struct OurElement: Decodable {
    let elementType: String
    let boundsPixels: OurRect
    let boundsVisionNormalized: OurRect   // Vision bottom-left origin, already clamped to [0,1]
}

private struct OurRect: Decodable {
    let x, y, width, height: Double
}

// MARK: - Output types (Create ML directoryWithImages format)

// Internal (not private) so ImageRecord can reference CreateMLRect.
struct CreateMLAnnotation: Encodable {
    let label: String
    let coordinates: CreateMLRect
}

struct CreateMLRect: Encodable {
    let x, y, width, height: Double   // center-based, NORMALIZED [0,1], top-left origin
}

/// One entry in the consolidated annotation JSON passed to
/// `MLObjectDetector.DataSource.directoryWithImages(at:annotationFile:)`.
private struct CreateMLImageEntry: Encodable {
    let imagefilename: String
    let annotation: [CreateMLAnnotation]
}

// MARK: - Export result

struct ExportResult {
    /// URL of the images directory (contains hard-linked PNGs).
    let imagesDir: URL
    /// URL of the consolidated annotation JSON file.
    let annotationFile: URL
    /// Per-class instance counts after subsampling.
    let classCounts: [String: Int]
}

// MARK: - Exporter

struct CreateMLExporter {

    struct ImageRecord {
        let pngURL:  URL
        let jsonURL: URL
        let elements: [(label: String, rect: CreateMLRect)]
    }

    /// Converts the dataset at `datasetDir` to Create ML format in `outputDir`.
    ///
    /// Output layout inside `outputDir`:
    ///   images/           — hard-linked PNGs (no extra disk use on same volume)
    ///   annotations.json  — single consolidated Create ML annotation file
    ///
    /// - Parameters:
    ///   - datasetDir: Root of the dataset (contains `train/`, `manifest.json`, etc.)
    ///   - outputDir: Destination root for this split's export.
    ///   - targetClasses: Only elements whose `elementType` is in this set are exported.
    ///   - split: Which split to export (`"train"`, `"validation"`, or `"test"`).
    ///   - capPerClass: Maximum element instances per class (subsampling ceiling).
    /// - Returns: Export result with directory URLs and per-class counts.
    @discardableResult
    static func export(
        datasetDir: URL,
        to outputDir: URL,
        targetClasses: Set<String>,
        split: String,
        capPerClass: Int
    ) throws -> ExportResult {

        let fm = FileManager.default

        let imagesDir = outputDir.appending(path: "images", directoryHint: .isDirectory)
        try fm.createDirectory(at: imagesDir, withIntermediateDirectories: true)

        let splitDir = datasetDir.appending(path: split, directoryHint: .isDirectory)
        guard fm.fileExists(atPath: splitDir.path) else {
            throw ExporterError.splitDirectoryNotFound(splitDir.path)
        }

        // Enumerate all PNGs in the split directory.
        let pngURLs = try fm.contentsOfDirectory(at: splitDir, includingPropertiesForKeys: nil)
            .filter { $0.pathExtension == "png" }
            .sorted { $0.lastPathComponent < $1.lastPathComponent }

        // First pass: load all records, build per-class pools.
        var allRecords: [URL: ImageRecord] = [:]

        for pngURL in pngURLs {
            let jsonURL = pngURL.deletingPathExtension().appendingPathExtension("json")
            guard fm.fileExists(atPath: jsonURL.path),
                  let data = try? Data(contentsOf: jsonURL),
                  let annotation = try? JSONDecoder().decode(OurAnnotation.self, from: data)
            else { continue }

            let matchingElems = annotation.elements
                .filter { targetClasses.contains($0.elementType) }
                .map { elem -> (label: String, rect: CreateMLRect) in
                    // Use boundsVisionNormalized (already clamped to [0,1] by BP-21).
                    // Vision coordinate system: x=left, y=bottom (bottom-left origin).
                    // Convert to Create ML normalized center coords (top-left origin):
                    //   cx = vn.x + vn.width  / 2
                    //   cy = 1 - vn.y - vn.height / 2   ← flip y-axis
                    let vn = elem.boundsVisionNormalized
                    return (
                        label: elem.elementType,
                        rect: CreateMLRect(
                            x: vn.x + vn.width  / 2,
                            y: 1.0 - vn.y - vn.height / 2,
                            width:  vn.width,
                            height: vn.height
                        )
                    )
                }
            guard !matchingElems.isEmpty else { continue }

            allRecords[pngURL] = ImageRecord(pngURL: pngURL, jsonURL: jsonURL, elements: matchingElems)
        }

        // Shuffle each per-class pool with a fixed seed for reproducibility, then
        // do greedy subsampling: include images until each class hits capPerClass.
        var classCount: [String: Int] = [:]
        var selectedPNGs = Set<URL>()

        let candidates = Array(allRecords.values).sorted { $0.pngURL.path < $1.pngURL.path }
        for record in candidates {
            let classes = record.elements.map(\.label)
            let anyBelow = classes.contains { (classCount[$0] ?? 0) < capPerClass }
            guard anyBelow else { continue }
            selectedPNGs.insert(record.pngURL)
            for cls in Set(classes) {
                classCount[cls, default: 0] += record.elements.filter { $0.label == cls }.count
            }
        }

        // Second pass: hard-link PNGs and build consolidated annotation array.
        var entries: [CreateMLImageEntry] = []

        for pngURL in selectedPNGs.sorted(by: { $0.path < $1.path }) {
            guard let record = allRecords[pngURL] else { continue }

            let destPNG = imagesDir.appending(path: pngURL.lastPathComponent)

            // Hard-link PNG — avoids duplicating GBs of images when src and dst are on the same volume.
            if !fm.fileExists(atPath: destPNG.path) {
                try fm.linkItem(at: pngURL, to: destPNG)
            }

            let annotations = record.elements.map {
                CreateMLAnnotation(label: $0.label, coordinates: $0.rect)
            }
            entries.append(CreateMLImageEntry(
                imagefilename: pngURL.lastPathComponent,
                annotation: annotations
            ))
        }

        // Write the single consolidated annotation JSON.
        let annotationFileURL = outputDir.appending(path: "annotations.json")
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted]
        let jsonData = try encoder.encode(entries)
        try jsonData.write(to: annotationFileURL)

        print("  Exported \(entries.count) images to \(outputDir.path)")
        for cls in targetClasses.sorted() {
            print("    \(cls): \(classCount[cls] ?? 0) instances")
        }

        return ExportResult(
            imagesDir: imagesDir,
            annotationFile: annotationFileURL,
            classCounts: classCount
        )
    }
}

// MARK: - Seeded random for reproducible subsampling

private struct SeededRandom: RandomNumberGenerator {
    private var state: UInt64

    init(seed: UInt64) { self.state = seed }

    mutating func next() -> UInt64 {
        state = state &* 6_364_136_223_846_793_005 &+ 1_442_695_040_888_963_407
        return state
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
