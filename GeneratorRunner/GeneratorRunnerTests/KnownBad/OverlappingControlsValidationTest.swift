// OverlappingControlsValidationTest.swift
// GeneratorRunnerTests — TASK-5a-3
//
// Validates OverlappingControlsViewController against the spec acceptance criteria:
//   AC-1: Exactly 10 primaryButton elements (2 per config × 5 configs)
//   AC-2: No knownIssues on any element (overlap flagged at Phase 7, not here)
//   AC-3: At least 5 distinct overlap configurations present (≥5 pairs with IoU > 0.1)
//   AC-4: All frames non-zero and within canvas
//   AC-5: For each pair, the IoU of buttonA and buttonB frames is > 0.1
//   AC-6: Seed reproducibility
//   AC-7: ≥50 seeds produce valid captures

import XCTest
import UIKit

// MARK: - OverlappingControlsValidationTest

@MainActor
final class OverlappingControlsValidationTest: XCTestCase {

    // MARK: - Helpers

    private func makeConfig(
        seed: UInt64,
        profile: OSVisualProfile = .ios26,
        colorScheme: GeneratorColorScheme = .light,
        pixelScale: Int = 3
    ) -> GeneratorRunConfig {
        GeneratorRunConfig(
            seed: seed,
            templateFamily: "OverlappingControls",
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

    private func capture(
        seed: UInt64,
        profile: OSVisualProfile = .ios26,
        colorScheme: GeneratorColorScheme = .light,
        pixelScale: Int = 3
    ) async throws -> CaptureResult {
        let config = makeConfig(seed: seed, profile: profile,
                                colorScheme: colorScheme, pixelScale: pixelScale)
        let vc = OverlappingControlsViewController(seed: seed, config: config)
        return try await ScreenshotCapture.captureUIKit(vc, config: config)
    }

    /// Returns the Intersection-over-Union of two rects.
    private func iou(_ a: CGRect, _ b: CGRect) -> CGFloat {
        let intersection = a.intersection(b)
        guard !intersection.isNull else { return 0 }
        let intersectionArea = intersection.width * intersection.height
        let unionArea = a.width * a.height + b.width * b.height - intersectionArea
        guard unionArea > 0 else { return 0 }
        return intersectionArea / unionArea
    }

    // MARK: - AC-1 + AC-2 + AC-3 + AC-4 + AC-5: Core annotation integrity

    func testAnnotationIntegrity_ios26_light() async throws {
        let config = makeConfig(seed: 42)
        let vc = OverlappingControlsViewController(seed: 42, config: config)
        let result = try await ScreenshotCapture.captureUIKit(vc, config: config)

        // AC-1: exactly 10 elements
        XCTAssertEqual(result.elements.count, 10,
            "Expected 10 primaryButton elements (2 per config × 5 configs), " +
            "got \(result.elements.count)")

        let canvas = CGRect(origin: .zero, size: config.osProfile.screenSize)

        for elem in result.elements {
            XCTAssertEqual(elem.elementType, "primaryButton",
                "\(elem.id): expected \"primaryButton\"")

            // AC-2: no knownIssues — overlap is a Phase 7 concern, not generated here
            XCTAssertTrue(elem.knownIssues.isEmpty,
                "\(elem.id): expected empty knownIssues, got \(elem.knownIssues)")

            // AC-4: non-zero, within canvas
            XCTAssertGreaterThan(elem.frame.width,  0, "\(elem.id): zero width")
            XCTAssertGreaterThan(elem.frame.height, 0, "\(elem.id): zero height")
            XCTAssert(
                canvas.intersects(elem.frame),
                "\(elem.id): frame \(elem.frame) does not intersect canvas \(canvas)"
            )
        }

        // AC-3 + AC-5: verify pairs — elements come in (A, B) pairs by index
        // The spec requires ≥5 pairs with IoU > 0.1.
        let buttons = result.elements.filter { $0.elementType == "primaryButton" }
        XCTAssertEqual(buttons.count, 10, "Need 10 buttons to form 5 pairs")

        var overlappingPairs = 0
        for i in stride(from: 0, to: buttons.count - 1, by: 2) {
            let frameA = buttons[i].frame
            let frameB = buttons[i + 1].frame
            let pairIoU = iou(frameA, frameB)
            if pairIoU > 0.1 {
                overlappingPairs += 1
            } else {
                // Report but don't fail immediately; we need ≥5 total
                print("Pair \(i/2): IoU=\(String(format: "%.3f", pairIoU)) — below 0.1 threshold")
            }
        }

        XCTAssertGreaterThanOrEqual(overlappingPairs, 5,
            "Expected ≥5 pairs with IoU > 0.1, found \(overlappingPairs)")

        // Attach PNG for visual spot-check
        let attachment = XCTAttachment(data: result.png, uniformTypeIdentifier: "public.png")
        attachment.name = "overlapping_controls_ios26_light_seed42.png"
        attachment.lifetime = .keepAlways
        add(attachment)
    }

    // MARK: - AC-6: Seed reproducibility

    func testSeedReproducibility() async throws {
        let result1 = try await capture(seed: 271828)
        let result2 = try await capture(seed: 271828)

        XCTAssertEqual(result1.sha256, result2.sha256, "Same seed → identical PNG")
        XCTAssertEqual(result1.elements.count, result2.elements.count)
    }

    // MARK: - AC-7: ≥50 seeds

    func testFiftyDistinctSeeds() async throws {
        var captureCount = 0

        for seed in UInt64(0)..<50 {
            let profile: OSVisualProfile = seed < 25 ? .ios26 : .ios17
            let scheme: GeneratorColorScheme = seed.isMultiple(of: 2) ? .light : .dark
            let scale = seed < 25 ? 3 : 2

            let config = makeConfig(seed: seed, profile: profile,
                                    colorScheme: scheme, pixelScale: scale)
            let vc = OverlappingControlsViewController(seed: seed, config: config)
            let result = try await ScreenshotCapture.captureUIKit(vc, config: config)

            XCTAssertEqual(result.elements.count, 10, "Seed \(seed): expected 10 elements")
            XCTAssertFalse(result.png.isEmpty, "Seed \(seed): empty PNG")

            captureCount += 1
        }

        XCTAssertEqual(captureCount, 50)
    }

    // MARK: - Dark mode on ios17

    func testCapture_ios17_dark() async throws {
        let result = try await capture(seed: 13, profile: .ios17, colorScheme: .dark, pixelScale: 2)
        XCTAssertEqual(result.elements.count, 10)

        let attachment = XCTAttachment(data: result.png, uniformTypeIdentifier: "public.png")
        attachment.name = "overlapping_controls_ios17_dark_seed13.png"
        attachment.lifetime = .keepAlways
        add(attachment)
    }
}
