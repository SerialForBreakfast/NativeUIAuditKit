#!/usr/bin/env swift
// derive_frame_similarity_threshold.swift
// NativeUIAuditKit/scripts
//
// Empirical support for FrameSimilarity's threshold (TASK-PERCEP-01 — never bake a guessed
// constant into the library). Computes pairwise Vision feature-print distances across a
// directory of screenshots and reports the distribution, so a caller can pick a threshold from
// real numbers instead of intuition.
//
// KNOWN LIMITATION: every image in a plain screenshot directory is a *different scene* — this
// only characterizes the "different screen" distance floor, not the "same screen, something
// small changed (e.g. focus moved)" distribution TASK-PERCEP-01's cache is actually meant to
// gate. That second distribution needs paired same-recipe frames (e.g. TVTestRig fixture-batch
// unfocused/focused pairs) — not available yet as real data (see Tasks.md TASK-6a-10). Treat
// any threshold derived from this script alone as a coarse upper bound, not a validated cutoff.
//
// Usage:
//   swift scripts/derive_frame_similarity_threshold.swift [--input <dir>]
//
// Output:
//   reports/frame_similarity_threshold_derivation.json

import Foundation
import CoreGraphics
import ImageIO
import Vision

let projectRoot = URL(filePath: #filePath).deletingLastPathComponent().deletingLastPathComponent()

var inputDir = projectRoot.appending(path: "dataset/tvos_fixture_captures")
let args = CommandLine.arguments
if let idx = args.firstIndex(of: "--input"), idx + 1 < args.count {
    inputDir = URL(filePath: args[idx + 1])
}

func loadImage(_ url: URL) -> CGImage? {
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil) else { return nil }
    return CGImageSourceCreateImageAtIndex(source, 0, nil)
}

func featurePrint(for image: CGImage) throws -> VNFeaturePrintObservation {
    let request = VNGenerateImageFeaturePrintRequest()
    let handler = VNImageRequestHandler(cgImage: image, options: [:])
    try handler.perform([request])
    guard let observation = request.results?.first as? VNFeaturePrintObservation else {
        throw NSError(domain: "derive_frame_similarity_threshold", code: 1, userInfo: [NSLocalizedDescriptionKey: "no feature print"])
    }
    return observation
}

guard let entries = try? FileManager.default.contentsOfDirectory(at: inputDir, includingPropertiesForKeys: nil) else {
    print("Input directory does not exist or is unreadable: \(inputDir.path)")
    exit(1)
}
let pngURLs = entries.filter { $0.pathExtension.lowercased() == "png" }.sorted { $0.path < $1.path }
guard pngURLs.count >= 2 else {
    print("Need at least 2 PNGs under \(inputDir.path); found \(pngURLs.count)")
    exit(1)
}

print("Computing feature prints for \(pngURLs.count) images from \(inputDir.path) ...")
var prints: [(name: String, print: VNFeaturePrintObservation)] = []
for url in pngURLs {
    guard let image = loadImage(url) else {
        print("  skip (unreadable): \(url.lastPathComponent)")
        continue
    }
    do {
        let fp = try featurePrint(for: image)
        prints.append((url.lastPathComponent, fp))
    } catch {
        print("  skip (no feature print): \(url.lastPathComponent) — \(error)")
    }
}

guard prints.count >= 2 else {
    print("Fewer than 2 usable feature prints; aborting.")
    exit(1)
}

// Same-image self-distance, as a sanity floor (should be ~0 for every image).
var selfDistances: [Float] = []
for entry in prints {
    var d: Float = 0
    try? entry.print.computeDistance(&d, to: entry.print)
    selfDistances.append(d)
}

// Cross-image ("different scene") distances — every unordered pair, once.
var crossDistances: [(a: String, b: String, distance: Float)] = []
for i in 0..<prints.count {
    for j in (i + 1)..<prints.count {
        var d: Float = 0
        do {
            try prints[i].print.computeDistance(&d, to: prints[j].print)
            crossDistances.append((prints[i].name, prints[j].name, d))
        } catch {
            // Skip pairs Vision can't score rather than aborting the whole run.
        }
    }
}

func stats(_ values: [Float]) -> (min: Float, max: Float, mean: Float, median: Float) {
    let sorted = values.sorted()
    let mean = values.reduce(0, +) / Float(values.count)
    let median = sorted[sorted.count / 2]
    return (sorted.first ?? 0, sorted.last ?? 0, mean, median)
}

let selfStats = stats(selfDistances)
let crossValues = crossDistances.map(\.distance)
let crossStats = stats(crossValues)
let closestCrossPair = crossDistances.min(by: { $0.distance < $1.distance })

print("\nSelf-distance (identical image vs. itself), n=\(selfDistances.count):")
print("  min=\(selfStats.min) max=\(selfStats.max) mean=\(selfStats.mean) median=\(selfStats.median)")
print("\nCross-scene distance (different screenshots), n=\(crossValues.count):")
print("  min=\(crossStats.min) max=\(crossStats.max) mean=\(crossStats.mean) median=\(crossStats.median)")
if let closest = closestCrossPair {
    print("  closest pair: \(closest.a) <-> \(closest.b) = \(closest.distance)")
}
print("""

Coarse upper bound for a same-screen threshold: below the closest observed cross-scene
distance (\(closestCrossPair?.distance ?? -1)). This is NOT a validated cutoff — it only proves
the threshold must stay under this to avoid collapsing two different screens together. It says
nothing about how large a real focus-only change measures, because no same-scene/changed-focus
pairs exist in this corpus. Re-run against TVTestRig fixture-batch unfocused/focused pairs once
real ones exist, and derive the actual threshold from that distribution instead.
""")

struct Report: Codable {
    let inputDirectory: String
    let imageCount: Int
    let selfDistanceMin: Float
    let selfDistanceMax: Float
    let selfDistanceMean: Float
    let crossSceneDistanceMin: Float
    let crossSceneDistanceMax: Float
    let crossSceneDistanceMean: Float
    let crossSceneDistanceMedian: Float
    let closestCrossScenePair: [String]
    let closestCrossSceneDistance: Float
    let note: String
}

let report = Report(
    inputDirectory: inputDir.path,
    imageCount: prints.count,
    selfDistanceMin: selfStats.min,
    selfDistanceMax: selfStats.max,
    selfDistanceMean: selfStats.mean,
    crossSceneDistanceMin: crossStats.min,
    crossSceneDistanceMax: crossStats.max,
    crossSceneDistanceMean: crossStats.mean,
    crossSceneDistanceMedian: crossStats.median,
    closestCrossScenePair: closestCrossPair.map { [$0.a, $0.b] } ?? [],
    closestCrossSceneDistance: closestCrossPair?.distance ?? -1,
    note: "Cross-scene stats only — no same-scene/changed-focus pairs available yet. Do not treat closestCrossSceneDistance as a validated threshold."
)

let reportsDir = projectRoot.appending(path: "reports")
try? FileManager.default.createDirectory(at: reportsDir, withIntermediateDirectories: true)
let encoder = JSONEncoder()
encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
let data = try encoder.encode(report)
let outputURL = reportsDir.appending(path: "frame_similarity_threshold_derivation.json")
try data.write(to: outputURL)
print("\nWrote \(outputURL.path)")
