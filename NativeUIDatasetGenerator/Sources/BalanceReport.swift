// BalanceReport.swift
// NativeUIDatasetGenerator
//
// Generates a Markdown dataset health report from a DatasetManifest.
// Flags classes below a minimum instance floor and reports the imbalance ratio.
//
// Concurrency: All methods are pure and synchronous — safe to call from any context.

import Foundation

// MARK: - BalanceReport

/// Produces a human-readable Markdown table from a `DatasetManifest`,
/// highlighting under-represented classes and the overall imbalance ratio.
public enum BalanceReport {

    /// Minimum instance count below which a class is considered under-represented.
    public static let defaultFloor = 100

    /// Maximum imbalance ratio (max/min) that triggers a warning header.
    public static let imbalanceWarningThreshold = 5.0

    // MARK: - Public API

    /// Generate a Markdown balance report from the provided manifest.
    ///
    /// - Parameters:
    ///   - manifest: The `DatasetManifest` to analyse.
    ///   - floor: Minimum instance count required per class (default: 100).
    /// - Returns: A Markdown string suitable for writing to `reports/dataset_balance.md`.
    public static func generate(from manifest: DatasetManifest, floor: Int = defaultFloor) -> String {
        var lines: [String] = []

        lines.append("# Dataset Balance Report")
        lines.append("")
        lines.append("Generated: \(ISO8601DateFormatter().string(from: Date()))")
        lines.append("Total images: \(manifest.imageCount)")
        lines.append("")

        // Overall imbalance ratio
        if let ratio = manifest.imbalanceRatio {
            let flag = ratio > imbalanceWarningThreshold ? " ⚠️" : ""
            lines.append("**Imbalance ratio (max/min):** \(String(format: "%.1f", ratio))\(flag)")
        } else {
            lines.append("**Imbalance ratio:** n/a (fewer than 2 classes observed)")
        }
        lines.append("")

        let underrep = manifest.underrepresented(floor: floor)
        if underrep.isEmpty {
            lines.append("All classes meet the minimum instance floor of \(floor).")
        } else {
            lines.append("**Under-represented classes (< \(floor) instances):** \(underrep.count)")
        }
        lines.append("")

        // Per-class table
        lines.append("## Per-Class Instance Counts")
        lines.append("")
        lines.append("| Class | Instances | Status |")
        lines.append("|---|---|---|")

        let allClasses = manifest.classDistribution.keys.sorted()
        for cls in allClasses {
            let count = manifest.classDistribution[cls] ?? 0
            let status: String
            if count == 0 {
                status = "⚠️ MISSING"
            } else if count < floor {
                status = "⚠️ LOW"
            } else {
                status = "OK"
            }
            lines.append("| `\(cls)` | \(count) | \(status) |")
        }

        lines.append("")
        lines.append("*Floor = \(floor) instances per class*")

        return lines.joined(separator: "\n")
    }

    /// Write the balance report to a file.
    ///
    /// - Parameters:
    ///   - manifest: Source manifest.
    ///   - url: Destination URL (parent directory must exist).
    ///   - floor: Minimum instance floor (default: 100).
    /// - Throws: File system errors.
    public static func write(
        from manifest: DatasetManifest,
        to url: URL,
        floor: Int = defaultFloor
    ) throws {
        let content = generate(from: manifest, floor: floor)
        try content.write(to: url, atomically: true, encoding: .utf8)
    }
}
