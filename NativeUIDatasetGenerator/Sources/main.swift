// main.swift
// NativeUIDatasetGenerator — macOS orchestration entry point
//
// Concurrency: Pipeline runs inside a Task launched from the synchronous
// top-level context, gated by a DispatchSemaphore so the process waits for
// completion before exiting. All shell commands are blocking (Process.waitUntilExit).

import CryptoKit
// Drives the full dataset generation pipeline:
//   1. Boot the target iOS Simulator (if not already booted)
//   2. Build and install GeneratorRunner.app onto the simulator
//   3. Apply a simulator status bar override via xcrun simctl status_bar
//   4. Run xcodebuild test against the GeneratorRunnerTests scheme
//   5. Locate the app data container on disk
//   6. Copy all PNGs and annotation JSON files to the output directory
//   7. Print a summary and balance report
//
// Usage:
//   swift run NativeUIDatasetGenerator \
//     --device-udid <UUID> \
//     --output /path/to/NativeUIAuditKit-Dataset \
//     [--project /path/to/GeneratorRunner.xcodeproj]
//
// Prerequisites:
//   - Xcode command-line tools installed
//   - iPhone Simulator for the specified UDID available in `xcrun simctl list`
//   - GeneratorRunner.xcodeproj built at least once (DerivedData populated)

import Foundation

// MARK: - Entry point

// Parse CLI arguments.
var deviceUDID: String?
var outputDir: String?
var projectPath: String = {
    // Default: look for GeneratorRunner.xcodeproj relative to the package root.
    let here = URL(fileURLWithPath: #file)
    let packageRoot = here
        .deletingLastPathComponent() // Sources/
        .deletingLastPathComponent() // NativeUIDatasetGenerator/
        .deletingLastPathComponent() // (package root)
    return packageRoot
        .appending(path: "GeneratorRunner/GeneratorRunner.xcodeproj")
        .path
}()

var args = CommandLine.arguments.dropFirst()
while !args.isEmpty {
    let arg = args.removeFirst()
    switch arg {
    case "--device-udid":
        deviceUDID = args.removeFirst()
    case "--output":
        outputDir = args.removeFirst()
    case "--project":
        projectPath = args.removeFirst()
    case "--help", "-h":
        printUsage()
        exit(0)
    default:
        fputs("Unknown argument: \(arg)\n", stderr)
        printUsage()
        exit(1)
    }
}

guard let udid = deviceUDID, let outDir = outputDir else {
    fputs("Error: --device-udid and --output are required.\n", stderr)
    printUsage()
    exit(1)
}

// Run the pipeline (top-level async context via a DispatchSemaphore).
let sema = DispatchSemaphore(value: 0)
var exitCode: Int32 = 0

Task {
    do {
        try await runPipeline(deviceUDID: udid, outputDir: outDir, projectPath: projectPath)
    } catch {
        fputs("Pipeline failed: \(error)\n", stderr)
        exitCode = 1
    }
    sema.signal()
}

sema.wait()
exit(exitCode)

// MARK: - Pipeline

/// Main orchestration pipeline.
///
/// - Parameters:
///   - deviceUDID: The simulator device UDID (from `xcrun simctl list devices`).
///   - outputDir: Destination directory for the dataset (will be created if absent).
///   - projectPath: Absolute path to `GeneratorRunner.xcodeproj`.
func runPipeline(deviceUDID: String, outputDir: String, projectPath: String) async throws {
    let fm = FileManager.default

    // 1. Boot simulator if needed.
    print("[1/6] Booting simulator \(deviceUDID)…")
    try shell("xcrun", "simctl", "boot", deviceUDID) // no-op if already booted

    // 2. Build and install.
    print("[2/6] Building and installing GeneratorRunner…")
    try shell(
        "xcodebuild",
        "-project", projectPath,
        "-scheme", "GeneratorRunner",
        "-destination", "platform=iOS Simulator,id=\(deviceUDID)",
        "-configuration", "Debug",
        "build",
        "DSTROOT=/tmp/GeneratorRunnerInstall"
    )
    let derivedDataDir = try derivedDataPath(for: projectPath)
    let appPath = try findApp(named: "GeneratorRunner.app", in: derivedDataDir)
    try shell("xcrun", "simctl", "install", deviceUDID, appPath)

    // 3. Apply status bar override (time, battery, signal).
    print("[3/6] Applying status bar override…")
    try shell(
        "xcrun", "simctl", "status_bar", deviceUDID, "override",
        "--time", "09:41",
        "--batteryLevel", "100",
        "--batteryState", "charging",
        "--cellularBars", "5",
        "--wifiBars", "3"
    )

    // 4. Run generation tests.
    print("[4/6] Running GeneratorRunnerTests (this takes several minutes)…")
    try shell(
        "xcodebuild",
        "test",
        "-project", projectPath,
        "-scheme", "GeneratorRunnerTests",
        "-destination", "platform=iOS Simulator,id=\(deviceUDID)",
        "-configuration", "Debug"
    )

    // 5. Locate output in simulator container.
    print("[5/6] Locating dataset output in simulator container…")
    let containerPath = try shellOutput(
        "xcrun", "simctl", "get_app_container",
        deviceUDID, "com.nativeuiauditkit.generatorrunner", "data"
    ).trimmingCharacters(in: .whitespacesAndNewlines)

    let sourceDatasetDir = URL(fileURLWithPath: containerPath)
        .appending(path: "Documents/dataset", directoryHint: .isDirectory)

    guard fm.fileExists(atPath: sourceDatasetDir.path) else {
        throw OrchestratorError.datasetDirectoryNotFound(sourceDatasetDir.path)
    }

    // 6. Copy to output directory.
    print("[6/6] Copying dataset to \(outputDir)…")
    let destDir = URL(fileURLWithPath: outputDir)
    try fm.createDirectory(at: destDir, withIntermediateDirectories: true)
    try copyDataset(from: sourceDatasetDir, to: destDir)

    // Reset status bar.
    try shell("xcrun", "simctl", "status_bar", deviceUDID, "clear")

    // Print summary.
    printSummary(datasetDir: destDir)
}

// MARK: - File copy

/// Recursively copies the dataset directory from the simulator container to `destination`.
/// Overwrites existing files with the same name (atomic write).
func copyDataset(from source: URL, to destination: URL) throws {
    let fm = FileManager.default
    let enumerator = fm.enumerator(
        at: source,
        includingPropertiesForKeys: [.isRegularFileKey],
        options: [.skipsHiddenFiles]
    )!

    var copied = 0
    for case let fileURL as URL in enumerator {
        let relative = fileURL.path.replacingOccurrences(of: source.path + "/", with: "")
        let destURL  = destination.appending(path: relative)
        try fm.createDirectory(
            at: destURL.deletingLastPathComponent(),
            withIntermediateDirectories: true
        )
        if fm.fileExists(atPath: destURL.path) {
            try fm.removeItem(at: destURL)
        }
        try fm.copyItem(at: fileURL, to: destURL)
        copied += 1
    }
    print("  Copied \(copied) files.")
}

// MARK: - Summary

/// Loads the manifest and prints image counts and balance metrics.
func printSummary(datasetDir: URL) {
    let manifestURL = datasetDir.appending(path: "manifest.json")
    guard let manifest = try? DatasetManifest.load(from: manifestURL) else {
        print("Summary: manifest.json not found at \(manifestURL.path)")
        return
    }

    let trainCount = manifest.entries.filter { $0.split == .train }.count
    let valCount   = manifest.entries.filter { $0.split == .validation }.count
    let testCount  = manifest.entries.filter { $0.split == .test }.count

    print("\nDataset summary")
    print("  Total images : \(manifest.imageCount)")
    print("  Train        : \(trainCount)")
    print("  Validation   : \(valCount)")
    print("  Test         : \(testCount)")

    if let ratio = manifest.imbalanceRatio {
        print(String(format: "  Imbalance    : %.1f×", ratio))
    }

    let underrep = manifest.underrepresented(floor: 10)
    if !underrep.isEmpty {
        print("  Under-represented classes (<10 samples): \(underrep.joined(separator: ", "))")
    }

    // Verify SHA integrity: every entry's sha256 must match its PNG on disk.
    var mismatches = 0
    for entry in manifest.entries {
        let pngURL = datasetDir.appending(path: entry.fileName)
        if let data = try? Data(contentsOf: pngURL) {
            let hash = SHA256.hash(data: data)
            let hex  = hash.map { String(format: "%02x", $0) }.joined()
            if hex != entry.sha256 { mismatches += 1 }
        } else {
            mismatches += 1
        }
    }
    let rate = manifest.imageCount > 0
        ? Double(manifest.imageCount - mismatches) / Double(manifest.imageCount)
        : 0.0
    print(String(format: "  SHA match    : %.1f%% (%d/%d)", rate * 100, manifest.imageCount - mismatches, manifest.imageCount))
    if mismatches > 0 {
        print("  WARNING: \(mismatches) SHA mismatches — re-run generation for affected images.")
    }
}

// MARK: - Shell helpers

/// Runs a shell command, throwing `OrchestratorError.commandFailed` on non-zero exit.
@discardableResult
func shell(_ args: String...) throws -> Int32 {
    let process = Process()
    process.executableURL = URL(fileURLWithPath: "/usr/bin/env")
    process.arguments = args
    try process.run()
    process.waitUntilExit()
    let status = process.terminationStatus
    if status != 0 {
        throw OrchestratorError.commandFailed(args, status)
    }
    return status
}

/// Runs a shell command and returns its stdout as a String.
func shellOutput(_ args: String...) throws -> String {
    let process = Process()
    let pipe    = Pipe()
    process.executableURL = URL(fileURLWithPath: "/usr/bin/env")
    process.arguments = args
    process.standardOutput = pipe
    try process.run()
    process.waitUntilExit()
    if process.terminationStatus != 0 {
        throw OrchestratorError.commandFailed(args, process.terminationStatus)
    }
    let data = pipe.fileHandleForReading.readDataToEndOfFile()
    return String(decoding: data, as: UTF8.self)
}

/// Locates the DerivedData directory for the given project using `xcodebuild -showBuildSettings`.
func derivedDataPath(for projectPath: String) throws -> String {
    let output = try shellOutput(
        "xcodebuild",
        "-project", projectPath,
        "-scheme", "GeneratorRunner",
        "-showBuildSettings"
    )
    for line in output.components(separatedBy: "\n") {
        let trimmed = line.trimmingCharacters(in: .whitespaces)
        if trimmed.hasPrefix("BUILT_PRODUCTS_DIR") {
            let parts = trimmed.components(separatedBy: " = ")
            if parts.count == 2 { return parts[1].trimmingCharacters(in: .whitespaces) }
        }
    }
    throw OrchestratorError.derivedDataNotFound(projectPath)
}

/// Searches for `appName` in `directory` and returns its path.
func findApp(named appName: String, in directory: String) throws -> String {
    let fm = FileManager.default
    guard let enumerator = fm.enumerator(atPath: directory) else {
        throw OrchestratorError.appBundleNotFound(appName, directory)
    }
    for case let path as String in enumerator where path.hasSuffix(appName) {
        return (directory as NSString).appendingPathComponent(path)
    }
    throw OrchestratorError.appBundleNotFound(appName, directory)
}

// MARK: - Errors

enum OrchestratorError: Error, CustomStringConvertible {
    case commandFailed([String], Int32)
    case datasetDirectoryNotFound(String)
    case appBundleNotFound(String, String)
    case derivedDataNotFound(String)

    var description: String {
        switch self {
        case .commandFailed(let args, let code):
            return "\(args.joined(separator: " ")) exited \(code)"
        case .datasetDirectoryNotFound(let path):
            return "Dataset directory not found after test run: \(path)"
        case .appBundleNotFound(let name, let dir):
            return "Could not locate \(name) in \(dir)"
        case .derivedDataNotFound(let project):
            return "BUILT_PRODUCTS_DIR not found in xcodebuild settings for \(project)"
        }
    }
}

// MARK: - Usage

func printUsage() {
    print("""
    NativeUIDatasetGenerator v0.1.0

    Generates annotated iOS UI screenshots for training NativeUIAuditKit models.

    USAGE:
      swift run NativeUIDatasetGenerator \\
        --device-udid <UUID> \\
        --output /path/to/NativeUIAuditKit-Dataset \\
        [--project /path/to/GeneratorRunner.xcodeproj]

    OPTIONS:
      --device-udid   iOS Simulator UDID (from `xcrun simctl list devices available`)
      --output        Destination directory for the dataset
      --project       Path to GeneratorRunner.xcodeproj (default: auto-detected)
      --help          Show this message

    EXAMPLES:
      # List available simulators:
      xcrun simctl list devices available | grep iPhone

      # Run on iPhone 17 Pro simulator:
      swift run NativeUIDatasetGenerator \\
        --device-udid AE2A4F09-CCE3-43C4-B96F-4E03CDCB4107 \\
        --output ~/NativeUIAuditKit-Dataset
    """)
}
