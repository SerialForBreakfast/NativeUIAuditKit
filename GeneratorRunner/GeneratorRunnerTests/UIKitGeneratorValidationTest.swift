// UIKitGeneratorValidationTest.swift
// GeneratorRunnerTests
//
// TASK-4-2: Validates UIKitGeneratorViewController against the spec acceptance criteria.
//
// AC checklist:
//   AC-1: ≥8 distinct element types in annotation output
//   AC-2: All exported frames are non-zero and intersect the canvas
//   AC-3: listRow frames at ≥2 distinct y-positions (mid-table, not just row 0)
//   AC-4: No UIButton with isHidden = true appears in annotation output
//   AC-5: Dark-mode capture on @2x (ios17) profile produces 750×1334px PNG
//   AC-6: Seed-reproducibility: same seed → same sha256 PNG
//
// Each test method attaches the captured PNG for visual inspection via xcresulttool.

import XCTest
import UIKit
import CryptoKit
import SwiftUI

// MARK: - UIKitGeneratorValidationTest

/// Opt-in only: select this test explicitly after runtime/storage authority is granted.
/// Never uses the legacy dataset tree, orchestrator install path or frozen recipes.
@MainActor
final class VisualProbeBatchTest: XCTestCase {
    func testExplicitVisualProbeBatch() async throws {
        let env = ProcessInfo.processInfo.environment
        guard env["NUA_PROBE_EXECUTION"] == "approved-development-probe" else {
            throw XCTSkip("Native probe capture requires separately approved execution scope")
        }
        let target = try XCTUnwrap(env["NUA_PROBE_SIMULATOR_UUID"])
        XCTAssertEqual(env["SIMULATOR_UDID"], target)
        guard UUID(uuidString: target) != nil, env["SIMULATOR_UDID"] == target else {
            throw VisualProbeCatalog.ValidationError.invalidSelection
        }
        let path = try XCTUnwrap(env["NUA_PROBE_CATALOG"])
        let input = URL(fileURLWithPath: path)
        guard input.resolvingSymlinksInPath().standardizedFileURL == input.standardizedFileURL else {
            throw VisualProbeCatalog.ValidationError.changedCatalog
        }
        let attributes = try input.resourceValues(forKeys: [.isRegularFileKey, .isSymbolicLinkKey, .fileSizeKey])
        guard attributes.isRegularFile == true, attributes.isSymbolicLink != true,
              let size = attributes.fileSize, size <= 1_048_576 else {
            throw VisualProbeCatalog.ValidationError.changedCatalog
        }
        let bytes = try Data(contentsOf: input)
        let digest = SHA256.hash(data: bytes).map { String(format: "%02x", $0) }.joined()
        guard digest == env["NUA_PROBE_CATALOG_SHA256"] else {
            throw VisualProbeCatalog.ValidationError.changedCatalog
        }
        let catalog = try VisualProbeCatalog.decodeFrozen(bytes)
        let selection = try XCTUnwrap(env["NUA_PROBE_CASE_IDS_JSON"]?.data(using: .utf8))
        let rows = try catalog.validatedBatch(ids: JSONDecoder().decode([String].self, from: selection))
        let outputName = try XCTUnwrap(env["NUA_PROBE_OUTPUT_NAME"])
        guard outputName.range(of: "^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$", options: .regularExpression) != nil else {
            throw VisualProbeCatalog.ValidationError.invalidSelection
        }
        let fm = FileManager.default
        let parent = fm.urls(for: .documentDirectory, in: .userDomainMask)[0].appendingPathComponent("visual-probes")
        let output = parent.appendingPathComponent(outputName)
        guard !fm.fileExists(atPath: output.path) else {
            throw CocoaError(.fileWriteFileExists)
        }
        try fm.createDirectory(at: parent, withIntermediateDirectories: true)
        try fm.createDirectory(at: output, withIntermediateDirectories: false)
        try bytes.write(to: output.appendingPathComponent("catalog.json"), options: .withoutOverwriting)
        var members: [[String: Any]] = []
        let started = ProcessInfo.processInfo.systemUptime
        do {
            for (index, row) in rows.enumerated() {
                guard ProcessInfo.processInfo.systemUptime - started < 120 else { throw CocoaError(.userCancelled) }
                let config = row.config
                let result: CaptureResult
                switch config.templateFamily {
                case "UIKitControls":
                    result = try await ScreenshotCapture.captureUIKit(UIKitControlsViewController(seed: config.seed, config: config), config: config)
                case "DynamicTypeOverflow":
                    result = try await ScreenshotCapture.captureUIKit(DynamicTypeOverflowViewController(seed: config.seed, config: config), config: config)
                case "ChromeCoverage":
                    var corpus = ContentCorpus(seed: config.seed)
                    let chrome = ChromeCoverageConfig.make(seed: config.seed, corpus: &corpus,
                        status: config.simulatorOverride,
                        effectiveColorScheme: config.colorScheme == .dark ? .dark : .light)
                    result = try await ScreenshotCapture.capture(ChromeCoverageTemplate(config: chrome), config: config)
                default: throw VisualProbeCatalog.ValidationError.changedCatalog
                }
                guard ProcessInfo.processInfo.systemUptime - started < 120 else { throw CocoaError(.userCancelled) }
                let image = try XCTUnwrap(UIImage(data: result.png)?.cgImage)
                guard image.width == Int(result.pixelSize.width), image.height == Int(result.pixelSize.height),
                      !result.elements.isEmpty else { throw ScreenshotCaptureError.pngRenderingFailed }
                let actualHash = SHA256.hash(data: result.png).map { String(format: "%02x", $0) }.joined()
                guard actualHash == result.sha256 else { throw ScreenshotCaptureError.pngRenderingFailed }
                let base = String(format: "probe-%03d", index)
                let imageURL = output.appendingPathComponent(base + ".png")
                let annotationURL = output.appendingPathComponent(base + ".json")
                try result.png.write(to: imageURL, options: .withoutOverwriting)
                try AnnotationWriter.write(result: result, config: config, imageFileName: base + ".png",
                    templateFamily: config.templateFamily, generatorVersion: "visual-probe-1",
                    to: annotationURL, schema: .measuredState)
                let annotation = try Data(contentsOf: annotationURL)
                guard try Data(contentsOf: imageURL) == result.png else { throw ScreenshotCaptureError.pngRenderingFailed }
                let sidecar = try JSONDecoder().decode(AnnotationJSON.self, from: annotation)
                guard sidecar.schemaVersion == "1.2", sidecar.imageSHA256 == actualHash,
                      sidecar.elements.count == result.elements.count else {
                    throw VisualProbeCatalog.ValidationError.changedCatalog
                }
                members.append(["id": row.id, "group": row.group, "image": base + ".png",
                    "annotation": base + ".json", "imageSHA256": actualHash,
                    "annotationSHA256": SHA256.hash(data: annotation).map { String(format: "%02x", $0) }.joined()])
            }
            let receipt: [String: Any] = ["version": "visual-probe-capture-v1",
                "completion": "captured_pending_visual_review", "trainingEligible": false,
                "partition": "development", "catalogSHA256": digest, "simulatorUUID": target,
                "runtimeOS": UIDevice.current.systemVersion, "expectedCount": rows.count,
                "actualCount": members.count, "members": members,
                "unsupportedIntersections": catalog.unsupportedIntersections]
            try JSONSerialization.data(withJSONObject: receipt, options: [.sortedKeys, .prettyPrinted])
                .write(to: output.appendingPathComponent("capture.json"), options: .withoutOverwriting)
        } catch {
            let failure: [String: Any] = ["completion": "partial", "expectedCount": rows.count,
                "actualCount": members.count, "members": members, "error": String(describing: error)]
            try? JSONSerialization.data(withJSONObject: failure, options: [.sortedKeys, .prettyPrinted])
                .write(to: output.appendingPathComponent("failure.json"), options: .withoutOverwriting)
            throw error
        }
    }
}

@MainActor
final class UIKitGeneratorValidationTest: XCTestCase {

    // MARK: - Helpers

    func testMeasuredControlStateDoesNotInventLabelState() async throws {
        final class StateViewController: UIViewController, UIKitAnnotatable {
            let button = UIButton(type: .system)
            let label = UILabel()
            override func viewDidLoad() {
                super.viewDidLoad()
                button.frame = CGRect(x: 20, y: 100, width: 200, height: 60)
                button.setTitle("Selected disabled", for: .normal)
                button.isEnabled = false
                button.isSelected = true
                label.frame = CGRect(x: 20, y: 180, width: 200, height: 40)
                label.text = "Unknown state"
                view.addSubview(button)
                view.addSubview(label)
            }
            var annotatedViews: [UIKitAnnotatedView] {
                [UIKitAnnotatedView(id: "primaryButton_state", elementType: "primaryButton", view: button),
                 UIKitAnnotatedView(id: "label_state", elementType: "label", view: label)]
            }
        }
        let config = makeConfig(seed: 1, profile: .ios17, colorScheme: .light, pixelScale: 2)
        let captured = try await ScreenshotCapture.captureUIKit(StateViewController(), config: config)
        let button = try XCTUnwrap(captured.elements.first { $0.id == "primaryButton_state" })
        let label = try XCTUnwrap(captured.elements.first { $0.id == "label_state" })
        XCTAssertEqual(button.isEnabled, false)
        XCTAssertEqual(button.isSelected, true)
        XCTAssertNil(label.isEnabled)
        XCTAssertNil(label.isSelected)
    }

    private func makeConfig(
        seed: UInt64,
        profile: OSVisualProfile,
        colorScheme: GeneratorColorScheme,
        pixelScale: Int
    ) -> GeneratorRunConfig {
        GeneratorRunConfig(
            seed: seed,
            templateFamily: "UIKitGenerator",
            osProfile: profile,
            simulatorOverride: SimulatorStateOverride(
                time: "09:41", batteryLevel: 100, batteryState: "charging",
                cellularBars: 5, wifiBars: 3, cellularMode: "active", operatorName: ""
            ),
            colorScheme: colorScheme,
            dynamicTypeSize: .large,
            deviceName: "Test Device",
            pixelScale: pixelScale,
            locale: "en_US",
            layoutDirection: .ltr
        )
    }

    private func capture(seed: UInt64, profile: OSVisualProfile, colorScheme: GeneratorColorScheme, pixelScale: Int) async throws -> CaptureResult {
        let config = makeConfig(seed: seed, profile: profile, colorScheme: colorScheme, pixelScale: pixelScale)
        let vc = UIKitGeneratorViewController(seed: seed, config: config)
        return try await ScreenshotCapture.captureUIKit(vc, config: config)
    }

    // MARK: - AC-1 + AC-2 + AC-3 + AC-4: Core annotation integrity (light mode, @3x)

    func testAnnotationIntegrity_ios26_light() async throws {
        let config = makeConfig(seed: 42, profile: .ios26, colorScheme: .light, pixelScale: 3)
        let vc = UIKitGeneratorViewController(seed: 42, config: config)
        let result = try await ScreenshotCapture.captureUIKit(vc, config: config)

        // AC-1: ≥8 distinct element types
        let elementTypes = Set(result.elements.map(\.elementType))
        XCTAssertGreaterThanOrEqual(
            elementTypes.count, 8,
            "Expected ≥8 element types, got \(elementTypes.count): \(elementTypes.sorted())"
        )

        // AC-2: All frames are non-zero and intersect canvas
        let canvas = CGRect(origin: .zero, size: config.osProfile.screenSize)
        for elem in result.elements {
            XCTAssertGreaterThan(elem.frame.width,  0, "\(elem.id): zero width")
            XCTAssertGreaterThan(elem.frame.height, 0, "\(elem.id): zero height")
            XCTAssert(
                canvas.intersects(elem.frame),
                "\(elem.id): frame \(elem.frame) doesn't intersect canvas \(canvas)"
            )
        }

        // AC-3: listRow annotations span ≥2 distinct y-positions (mid-table rows present)
        let listRows = result.elements
            .filter { $0.elementType == "listRow" }
            .sorted { $0.frame.minY < $1.frame.minY }
        XCTAssertGreaterThanOrEqual(listRows.count, 2, "Expected ≥2 listRow elements")
        if listRows.count >= 2 {
            let yDelta = listRows[1].frame.minY - listRows[0].frame.minY
            XCTAssertGreaterThan(yDelta, 10,
                "Row 0 and row 1 should be at different y (Δ=\(yDelta)pt)")
        }

        // AC-4: No hidden UIButton in output (hiddenButton must not appear)
        let buttonTypes: Set<String> = ["primaryButton", "secondaryButton", "menuButton"]
        let buttonAnnotations = result.elements.filter { buttonTypes.contains($0.elementType) }
        // All reported buttons must have non-hidden frames (canvas-visible)
        for btn in buttonAnnotations {
            XCTAssert(canvas.intersects(btn.frame), "Button \(btn.id) outside canvas — should have been filtered")
        }
        // Verify the hidden button is not in the output (there's no element with a frame
        // matching the hidden button's position at navBarMaxY+50)
        let hiddenButtonCandidates = result.elements.filter {
            $0.elementType == "primaryButton" &&
            abs($0.frame.minY - (config.osProfile.safeAreaTopInset + 44 + 50)) < 5
        }
        XCTAssertTrue(hiddenButtonCandidates.isEmpty,
            "Hidden button at y≈\(config.osProfile.safeAreaTopInset + 44 + 50) found in output — should be excluded")

        // Attach PNG for visual inspection
        let attachment = XCTAttachment(data: result.png, uniformTypeIdentifier: "public.png")
        attachment.name = "uitkit_generator_ios26_light.png"
        attachment.lifetime = .keepAlways
        add(attachment)
    }

    // MARK: - AC-5: Dark mode + @2x pixel dimensions

    func testCapture_ios17_dark() async throws {
        let result = try await capture(seed: 99, profile: .ios17, colorScheme: .dark, pixelScale: 2)

        // AC-5: ios17 @2x → 750×1334px
        XCTAssertEqual(result.scale, 2)
        XCTAssertEqual(result.pixelSize.width,  750,  accuracy: 2, "Expected 750px wide")
        XCTAssertEqual(result.pixelSize.height, 1334, accuracy: 2, "Expected 1334px tall")
        XCTAssertEqual(result.pointSize.width,  375,  accuracy: 1, "Expected 375pt wide")
        XCTAssertEqual(result.pointSize.height, 667,  accuracy: 1, "Expected 667pt tall")

        // Should still have ≥8 element types on the smaller canvas
        let elementTypes = Set(result.elements.map(\.elementType))
        XCTAssertGreaterThanOrEqual(elementTypes.count, 8,
            "ios17 canvas: expected ≥8 types, got \(elementTypes.count): \(elementTypes.sorted())")

        let attachment = XCTAttachment(data: result.png, uniformTypeIdentifier: "public.png")
        attachment.name = "uitkit_generator_ios17_dark.png"
        attachment.lifetime = .keepAlways
        add(attachment)
    }

    // MARK: - AC-6: Seed reproducibility — same seed → same sha256

    func testSeedReproducibility() async throws {
        let result1 = try await capture(seed: 777, profile: .ios26, colorScheme: .light, pixelScale: 3)
        let result2 = try await capture(seed: 777, profile: .ios26, colorScheme: .light, pixelScale: 3)

        XCTAssertEqual(result1.sha256, result2.sha256,
            "Same seed should produce identical PNG (byte-for-byte match)")
        XCTAssertEqual(result1.elements.count, result2.elements.count,
            "Same seed should produce identical element count")
    }

    // MARK: - Element type coverage audit

    func testElementTypeCoverage() async throws {
        let result = try await capture(seed: 42, profile: .ios26, colorScheme: .light, pixelScale: 3)

        let types = Set(result.elements.map(\.elementType))

        // These must ALL be present in a full-canvas ios26 capture
        let required: Set<String> = [
            "navigationBar", "tabBar", "tabBarItem",
            "label", "textField",
            "toggle", "slider", "segmentedControl",
            "primaryButton", "secondaryButton", "menuButton",
            "activityIndicator", "progressView", "pageControl",
            "imageView", "listRow",
        ]

        let missing = required.subtracting(types)
        XCTAssertTrue(missing.isEmpty,
            "Missing element types in ios26 capture: \(missing.sorted())")
    }

    // MARK: - listRow cell-style diversity (4 styles → 4 annotations with distinct y positions)

    func testListRowFourStylesPresent() async throws {
        let result = try await capture(seed: 42, profile: .ios26, colorScheme: .light, pixelScale: 3)

        let listRows = result.elements
            .filter { $0.elementType == "listRow" }
            .sorted { $0.frame.minY < $1.frame.minY }

        XCTAssertEqual(listRows.count, 4, "Expected 4 listRow annotations (one per UITableViewCell style)")

        // Each row must be below the previous one by ≥ 30pt
        for i in 1..<listRows.count {
            let delta = listRows[i].frame.minY - listRows[i - 1].frame.minY
            XCTAssertGreaterThan(delta, 30,
                "listRow_\(i) is not below listRow_\(i-1) by ≥30pt (Δ=\(delta))")
        }
    }
}
