// export_yolo_gt.swift
// NativeUIAuditKit/scripts
//
// Exports YOLO-format ground-truth .txt files from the consolidated
// createml_export validation annotations.json so that confusion_matrix.py
// can be run against the eval_map.swift prediction outputs.
//
// YOLO format per line: class_id cx cy w h  (top-left normalized, no confidence)
//
// Class IDs are assigned alphabetically from the 5 training classes,
// matching the scheme eval_map.swift uses for prediction files:
//   0 alert
//   1 navigationBar
//   2 primaryButton
//   3 textField
//   4 toggle
//
// Usage (from project root):
//   swift scripts/export_yolo_gt.swift
//
// Output:
//   reports/yolo_gt/   — one .txt file per validation image (matching prediction filenames)
//   reports/yolo_gt/classes.txt — class index file
//
// After running eval_map.swift with WRITE_YOLO_PREDS=1:
//   python scripts/confusion_matrix.py \
//     --gt-dir   reports/yolo_gt \
//     --pred-dir reports/yolo_preds \
//     --version  1

import Foundation
import CoreGraphics

// MARK: - Config

let projectRoot = URL(filePath: #filePath)
    .deletingLastPathComponent()   // scripts/
    .deletingLastPathComponent()   // project root

let valAnnotationURL = URL(filePath: "/Users/josephmccraw/Library/Developer/CoreSimulator/Devices/812EDC32-DB8D-49D6-B130-2279180CCDEB/data/Containers/Data/Application/E0711EF5-B600-47B2-A7B8-D5BA63DE1D83/Documents/dataset/createml_export/validation/annotations.json")

/// The 5 training classes, sorted alphabetically — must match eval_map.swift class ordering.
let classNames = ["alert", "navigationBar", "primaryButton", "textField", "toggle"]
let classToID  = Dictionary(uniqueKeysWithValues: classNames.enumerated().map { ($0.element, $0.offset) })

let outputDir = projectRoot.appending(path: "reports/yolo_gt", directoryHint: .isDirectory)

// MARK: - Types

struct AnnEntry: Decodable {
    let imagefilename: String
    let annotation: [AnnBox]
    struct AnnBox: Decodable {
        let label: String
        let coordinates: Coords
        struct Coords: Decodable { let x, y, width, height: Double }
    }
}

// MARK: - Main

try FileManager.default.createDirectory(at: outputDir, withIntermediateDirectories: true)

// Write classes.txt
let classesContent = classNames.enumerated().map { "\($0.offset) \($0.element)" }.joined(separator: "\n")
try (classesContent + "\n").write(to: outputDir.appending(path: "classes.txt"), atomically: true, encoding: .utf8)

// Load consolidated annotation
let data    = try Data(contentsOf: valAnnotationURL)
let entries = try JSONDecoder().decode([AnnEntry].self, from: data)
print("Loaded \(entries.count) validation entries")

var written = 0
var skipped = 0

for entry in entries {
    // Coordinates in annotations.json are already Create ML top-left normalized (cx, cy, w, h)
    let lines = entry.annotation.compactMap { box -> String? in
        guard let id = classToID[box.label] else { return nil }
        let c = box.coordinates
        // annotations.json cx/cy are already top-left normalized — write directly
        return "\(id) \(c.x) \(c.y) \(c.width) \(c.height)"
    }

    let stem    = (entry.imagefilename as NSString).deletingPathExtension
    let outURL  = outputDir.appending(path: "\(stem).txt")

    if lines.isEmpty {
        // Write empty file so the confusion matrix knows this image had no target-class GT
        try "".write(to: outURL, atomically: true, encoding: .utf8)
        skipped += 1
    } else {
        try (lines.joined(separator: "\n") + "\n").write(to: outURL, atomically: true, encoding: .utf8)
        written += 1
    }
}

print("GT files written: \(written) with annotations, \(skipped) empty (no target-class elements)")
print("Output: \(outputDir.path)")
print()
print("Run confusion matrix:")
print("  WRITE_YOLO_PREDS=1 swift scripts/eval_map.swift    # writes reports/yolo_preds/")
print("  swift scripts/export_yolo_gt.swift                 # writes reports/yolo_gt/ (this script)")
print("  python scripts/confusion_matrix.py \\")
print("    --gt-dir   reports/yolo_gt \\")
print("    --pred-dir reports/yolo_preds \\")
print("    --version  1")
