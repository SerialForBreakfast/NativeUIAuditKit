// GenerateDatasetTests.swift
// GeneratorRunnerTests
//
// Hosted XCTest that generates the Phase 3e-1 dataset.
//
// Runs inside the iOS Simulator via `xcodebuild test`. Each test method generates
// 200 images for one template family and writes PNG + annotation JSON files to
// the app's Documents directory. The macOS NativeUIDatasetGenerator orchestrator
// locates the output directory via `xcrun simctl get_app_container` after the
// test run completes and copies the files to the dataset root.
//
// Output layout (inside Documents/dataset/):
//   train/img_NNNNNN.png
//   train/img_NNNNNN.json
//   validation/img_NNNNNN.png
//   validation/img_NNNNNN.json
//   test/img_NNNNNN.png
//   test/img_NNNNNN.json
//   manifest.json
//
// Split ratios: 80% train / 10% validation / 10% test (by imageIndex % 10).
//
// Concurrency: All capture work runs on @MainActor (UIKit requirement).
// The test methods are async and hop to @MainActor via ScreenshotCapture.
//
// Simulator state overrides in annotation metadata:
// The SimulatorStateOverride embedded in each config records 5 distinct time
// values across the sweep, satisfying TASK-3e-1 AC. The macOS orchestrator
// is responsible for actually setting the simulator status bar via
// `xcrun simctl status_bar` before each test run (see SimulatorStateManager).

import XCTest
import SwiftUI
import UIKit

// MARK: - GenerateDatasetTests

/// Generates all Phase 3e-1 training images inside the iOS Simulator.
///
/// Run order (alphabetical): Alert → LoginForm → SettingsList.
/// Each method generates 200 images; 600 total across the three templates.
///
/// **Threading:** Class is `@MainActor` — all SwiftUI rendering must occur on
/// the main thread. `async throws` test methods yield to the run loop between captures.
@MainActor
final class GenerateDatasetTests: XCTestCase {

    // MARK: - Fixtures

    /// Root output directory inside the simulator app's Documents container.
    private let datasetDir: URL = {
        FileManager.default
            .urls(for: .documentDirectory, in: .userDomainMask)[0]
            .appending(path: "dataset", directoryHint: .isDirectory)
    }()

    /// Five distinct simulator state overrides, rotated across the image sweep.
    /// Records different time/battery/cellular values in annotation metadata,
    /// satisfying the TASK-3e-1 AC for ≥5 distinct time values.
    private let simulatorStates: [SimulatorStateOverride] = [
        SimulatorStateOverride(
            time: "09:41", batteryLevel: 100, batteryState: "charging",
            cellularBars: 5, wifiBars: 3, cellularMode: "active", operatorName: ""
        ),
        SimulatorStateOverride(
            time: "12:30", batteryLevel: 75, batteryState: "discharging",
            cellularBars: 3, wifiBars: 3, cellularMode: "active", operatorName: ""
        ),
        SimulatorStateOverride(
            time: "18:05", batteryLevel: 50, batteryState: "discharging",
            cellularBars: 1, wifiBars: 1, cellularMode: "active", operatorName: ""
        ),
        SimulatorStateOverride(
            time: "22:15", batteryLevel: 25, batteryState: "discharging",
            cellularBars: 0, wifiBars: 0, cellularMode: "notSupported", operatorName: ""
        ),
        SimulatorStateOverride(
            time: "07:00", batteryLevel: 10, batteryState: "discharging",
            cellularBars: 5, wifiBars: 3, cellularMode: "active", operatorName: "AT&T"
        ),
    ]

    // MARK: - Set-up

    override func setUp() async throws {
        let fm = FileManager.default
        for split in ["train", "validation", "test"] {
            let dir = datasetDir.appending(path: split, directoryHint: .isDirectory)
            try fm.createDirectory(at: dir, withIntermediateDirectories: true)
        }
    }

    // MARK: - Test methods

    /// Generates 200 alert template images (seeds 2001–2200).
    /// Runs first alphabetically — initialises the manifest.
    func testGenerateAlertImages() async throws {
        try await generateImages(templateFamily: "Alert", count: 200, startSeed: 2001)
    }

    /// Generates 200 login-form template images (seeds 1001–1200).
    func testGenerateLoginFormImages() async throws {
        try await generateImages(templateFamily: "LoginForm", count: 200, startSeed: 1001)
    }

    /// Generates 200 settings-list template images (seeds 3001–3200).
    /// Runs last — final manifest write includes all 600 entries.
    func testGenerateSettingsListImages() async throws {
        try await generateImages(templateFamily: "SettingsList", count: 200, startSeed: 3001)
    }

    // MARK: - Core generation loop

    /// Generates `count` images for the given template family, appending to the shared manifest.
    ///
    /// - Parameters:
    ///   - templateFamily: `"LoginForm"`, `"SettingsList"`, or `"Alert"`.
    ///   - count: Number of images to generate.
    ///   - startSeed: First seed value; subsequent images use `startSeed + i`.
    private func generateImages(
        templateFamily: String,
        count: Int,
        startSeed: UInt64
    ) async throws {
        let manifestURL = datasetDir.appending(path: "manifest.json")
        var manifest = try DatasetManifest.load(from: manifestURL)

        for i in 0..<count {
            let seed = startSeed + UInt64(i)
            let state = simulatorStates[i % simulatorStates.count]
            let config = makeConfig(seed: seed, index: i, templateFamily: templateFamily, state: state)

            var corpus = ContentCorpus(seed: seed)
            let result = try await capture(templateFamily: templateFamily, seed: seed, config: config, corpus: &corpus)

            let imageIndex = manifest.imageCount + 1
            let split = splitFor(imageIndex: imageIndex)
            let baseName = String(format: "img_%06d", imageIndex)
            let pngName  = baseName + ".png"
            let jsonName = baseName + ".json"

            let splitDir = datasetDir.appending(path: split.rawValue, directoryHint: .isDirectory)
            try result.png.write(to: splitDir.appending(path: pngName))
            try AnnotationWriter.write(
                result: result,
                config: config,
                imageFileName: pngName,
                templateFamily: templateFamily,
                generatorVersion: "0.1.0",
                to: splitDir.appending(path: jsonName)
            )

            let entry = ManifestEntry(
                fileName: "\(split.rawValue)/\(pngName)",
                split: split,
                sha256: result.sha256,
                templateFamily: templateFamily,
                generatorSeed: seed,
                simulatorState: state,
                isolationTemplate: config.isolationTemplate,
                lowDensity: config.lowDensity,
                deviceName: config.deviceName,
                pixelScale: config.pixelScale
            )
            manifest.append(entry, elementTypes: result.elements.map(\.elementType))
        }

        try manifest.save(to: manifestURL)
    }

    // MARK: - Capture dispatch

    /// Calls the correct template's `ScreenshotCapture.capture` for the given family.
    ///
    /// - Parameters:
    ///   - templateFamily: Template to render.
    ///   - seed: Deterministic seed for the config factory.
    ///   - config: `GeneratorRunConfig` passed to `ScreenshotCapture.capture`.
    ///   - corpus: Seeded text corpus (mutated by the factory call).
    /// - Returns: `CaptureResult` with PNG, SHA-256, and element frames.
    /// - Throws: `GenerateDatasetError.unknownTemplateFamily` for unrecognised families.
    private func capture(
        templateFamily: String,
        seed: UInt64,
        config: GeneratorRunConfig,
        corpus: inout ContentCorpus
    ) async throws -> CaptureResult {
        switch templateFamily {
        case "LoginForm":
            let formConfig = LoginFormConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(LoginFormTemplate(config: formConfig), config: config)
        case "SettingsList":
            let listConfig = SettingsListConfig.make(seed: seed, corpus: &corpus, hasHomeIndicator: config.osProfile.hasHomeIndicator)
            return try await ScreenshotCapture.capture(SettingsListTemplate(config: listConfig), config: config)
        case "Alert":
            let alertConfig = AlertConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(AlertTemplate(config: alertConfig), config: config)
        default:
            throw GenerateDatasetError.unknownTemplateFamily(templateFamily)
        }
    }

    // MARK: - Config factory

    /// Builds a `GeneratorRunConfig` for one image, varying device, color scheme,
    /// DynamicType, and simulator state based on `index` and `seed`.
    private func makeConfig(
        seed: UInt64,
        index: Int,
        templateFamily: String,
        state: SimulatorStateOverride
    ) -> GeneratorRunConfig {
        // Alternate between a high-DPI iPhone (@3x) and a compact iPhone (@2x).
        let highDPI = index % 2 == 0
        let osProfile: OSVisualProfile = highDPI ? .ios26 : .ios17
        let deviceName = highDPI ? "iPhone 17 Pro" : "iPhone SE (3rd generation)"
        let pixelScale = highDPI ? 3 : 2

        return GeneratorRunConfig(
            seed: seed,
            templateFamily: templateFamily,
            osProfile: osProfile,
            simulatorOverride: state,
            colorScheme: index % 2 == 0 ? .dark : .light,
            dynamicTypeSize: dynamicTypeSize(for: index),
            deviceName: deviceName,
            pixelScale: pixelScale,
            locale: "en_US",
            layoutDirection: .ltr,
            accessibilityFlags: .default
        )
    }

    // MARK: - Helpers

    /// Assigns a `DatasetSplit` based on a 10-bucket rotation: 80% train, 10% validation, 10% test.
    private func splitFor(imageIndex: Int) -> DatasetSplit {
        switch imageIndex % 10 {
        case 0:         return .test
        case 9:         return .validation
        default:        return .train
        }
    }

    /// Cycles through 6 `GeneratorDynamicTypeSize` values based on the image index.
    private func dynamicTypeSize(for index: Int) -> GeneratorDynamicTypeSize {
        let sizes: [GeneratorDynamicTypeSize] = [
            .medium, .large, .xLarge,
            .accessibilityMedium, .xxLarge, .small
        ]
        return sizes[index % sizes.count]
    }
}

// MARK: - GenerateDatasetError

/// Errors produced by `GenerateDatasetTests`.
enum GenerateDatasetError: Error, CustomStringConvertible {
    case unknownTemplateFamily(String)

    var description: String {
        switch self {
        case .unknownTemplateFamily(let family):
            return "Unknown template family '\(family)'. Expected: LoginForm, SettingsList, Alert."
        }
    }
}
