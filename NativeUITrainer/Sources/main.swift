// main.swift
// NativeUITrainer
//
// CLI entry point for training the 5-class iOS object-detection model.
//
// Usage:
//   swift run NativeUITrainer \
//     --dataset <path-to-dataset-root> \
//     --output  <path-to-NativeUIAuditKitModels/Sources/NativeUIAuditKitModels>
//
// The tool:
//   1. Exports the training + validation splits to a Create ML annotatedFiles layout.
//   2. Calls MLObjectDetector.init() with objectPrint transfer-learning algorithm.
//   3. Writes the .mlpackage to <output>/NativeUIDetector_v1.mlpackage.
//   4. Writes training_config.json next to the .mlpackage.

import Foundation
import CreateML

// MARK: - Argument parsing

struct Args {
    let datasetDir: URL
    let outputDir:  URL

    static func parse() -> Args {
        var datasetPath: String?
        var outputPath:  String?

        var args = CommandLine.arguments.dropFirst()
        while !args.isEmpty {
            let flag = args.removeFirst()
            switch flag {
            case "--dataset": datasetPath = args.isEmpty ? nil : String(args.removeFirst())
            case "--output":  outputPath  = args.isEmpty ? nil : String(args.removeFirst())
            default: break
            }
        }

        guard let dp = datasetPath, let op = outputPath else {
            fputs("""
            Usage: NativeUITrainer --dataset <dataset-root> --output <models-dir>\n
            """, stderr)
            exit(1)
        }

        return Args(
            datasetDir: URL(filePath: dp),
            outputDir:  URL(filePath: op)
        )
    }
}

// MARK: - Main

let args = Args.parse()

let config = TrainingConfig(
    algorithm: "transferLearning",
    featureExtractor: "objectPrint_v1",          // MLObjectDetector uses objectPrint, not scenePrint
    maxIterations: TrainingConfig.default.maxIterations,
    batchSize: TrainingConfig.default.batchSize,
    trainingClasses: TrainingConfig.default.trainingClasses,
    subsamplingCapPerClass: TrainingConfig.default.subsamplingCapPerClass,
    datasetVersion: {
        let manifestURL = args.datasetDir.appending(path: "manifest.json")
        if let data = try? Data(contentsOf: manifestURL),
           let obj  = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
           let ver  = obj["datasetVersion"] as? String {
            return ver
        }
        return "unknown"
    }(),
    trainedAt: ISO8601DateFormatter().string(from: Date())
)

let targetClasses = Set(config.trainingClasses)
let cap            = config.subsamplingCapPerClass

// MARK: - Step 1: Export to Create ML annotatedFiles format

let exportRoot  = args.datasetDir.appending(path: "createml_export", directoryHint: .isDirectory)
let trainExport = exportRoot.appending(path: "train",      directoryHint: .isDirectory)
let valExport   = exportRoot.appending(path: "validation", directoryHint: .isDirectory)

print("── Step 1: Exporting to Create ML format ──────────────────────────────")
print("Dataset : \(args.datasetDir.path)")
print("Export  : \(exportRoot.path)")
print()

print("  [train]")
let trainResult = try CreateMLExporter.export(
    datasetDir: args.datasetDir,
    to: trainExport,
    targetClasses: targetClasses,
    split: "train",
    capPerClass: cap
)

print()
print("  [validation]")
let valResult = try CreateMLExporter.export(
    datasetDir: args.datasetDir,
    to: valExport,
    targetClasses: targetClasses,
    split: "validation",
    capPerClass: cap
)

// MARK: - Step 2: Build Create ML data sources

print()
print("── Step 2: Configuring Create ML data sources ─────────────────────────")

// Use directoryWithImages(at:annotationFile:):
//   - imagesDir contains hard-linked PNGs
//   - annotationFile is a single JSON with all image annotations in the format:
//       [{"imagefilename": "img.png", "annotation": [{"label": ..., "coordinates": {...}}]}]
// Coordinates are center-based, top-left origin, in pixels — exactly what CreateMLExporter writes.
let trainSource = MLObjectDetector.DataSource.directoryWithImages(
    at: trainResult.imagesDir,
    annotationFile: trainResult.annotationFile
)
let valSource = MLObjectDetector.DataSource.directoryWithImages(
    at: valResult.imagesDir,
    annotationFile: valResult.annotationFile
)

// MARK: - Step 3: Train

print()
print("── Step 3: Training (this takes a while) ──────────────────────────────")
print("  Algorithm        : transferLearning(objectPrint revision:1)")
print("  Max iterations   : \(config.maxIterations)")
print("  Batch size       : \(config.batchSize)")
print("  Classes          : \(config.trainingClasses.joined(separator: ", "))")
print()

// Annotation type: coordinates are NORMALIZED [0,1], top-left origin, center-anchored.
// CreateMLExporter computes: cx = vn.x + vn.w/2, cy = 1 - vn.y - vn.h/2 from
// boundsVisionNormalized (Vision bottom-left origin → Create ML top-left origin).
let annotationType = MLObjectDetector.AnnotationType
    .boundingBox(units: .normalized, origin: .topLeft, anchor: .center)

let parameters = MLObjectDetector.ModelParameters(
    validation: .dataSource(valSource),
    batchSize: config.batchSize,
    maxIterations: config.maxIterations,
    gridSize: CGSize(width: 13, height: 13),     // standard 13×13 YOLO grid
    algorithm: .transferLearning(.objectPrint(revision: 1))
)

let detector = try MLObjectDetector(
    trainingData: trainSource,
    parameters: parameters,
    annotationType: annotationType
)

// MARK: - Step 4: Evaluate on validation

print()
print("── Step 4: Validation metrics ─────────────────────────────────────────")
let valMetrics = detector.evaluation(on: valSource)
print("  Validation mAP@0.5  : \(String(format: "%.4f", valMetrics.meanAveragePrecision.IoU50))")
print("  Validation mAP@0.5:0.95: \(String(format: "%.4f", valMetrics.meanAveragePrecision.variedIoU))")
print()
for (cls, ap) in valMetrics.averagePrecision.IoU50.sorted(by: { $0.key < $1.key }) {
    print("    AP@0.5  \(cls): \(String(format: "%.4f", ap))")
}

// MARK: - Step 5: Write outputs

print()
print("── Step 5: Writing outputs ─────────────────────────────────────────────")

let fm = FileManager.default
try fm.createDirectory(at: args.outputDir, withIntermediateDirectories: true)

let mlpackageURL = args.outputDir.appending(
    path: "NativeUIDetector_v1.mlpackage",
    directoryHint: .isDirectory
)
let configURL = args.outputDir.appending(path: "training_config.json")

// Remove existing package (Create ML refuses to overwrite).
if fm.fileExists(atPath: mlpackageURL.path) {
    try fm.removeItem(at: mlpackageURL)
}

try detector.write(to: mlpackageURL)
print("  .mlpackage → \(mlpackageURL.path)")

try config.write(to: configURL)
print("  training_config.json → \(configURL.path)")

print()
print("Done. NativeUIDetector_v1 trained at \(config.trainedAt)")
print("  Training instance counts  : \(trainResult.classCounts)")
print("  Validation instance counts: \(valResult.classCounts)")
