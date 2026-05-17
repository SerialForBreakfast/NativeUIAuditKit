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

// MARK: - UIKitGeneratorValidationTest

@MainActor
final class UIKitGeneratorValidationTest: XCTestCase {

    // MARK: - Helpers

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
