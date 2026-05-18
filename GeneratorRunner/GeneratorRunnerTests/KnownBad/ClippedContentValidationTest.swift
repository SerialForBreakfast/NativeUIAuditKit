// ClippedContentValidationTest.swift
// GeneratorRunnerTests — TASK-5a-2
//
// Validates ClippedContentViewController against the spec acceptance criteria:
//   AC-1: Every element has knownIssues: ["clippedElement"]
//   AC-2: All annotated frames (containers) are non-zero and within the canvas
//   AC-3: Each annotated container frame is strictly smaller than the child
//         imageView frame in at least one dimension (proves clipping is real)
//   AC-4: Seed reproducibility — same seed → identical sha256 PNG
//   AC-5: ≥50 distinct seeds produce valid captures without error
//   AC-6: elementType is "imageView" for every annotated element

import XCTest
import UIKit

// MARK: - ClippedContentValidationTest

@MainActor
final class ClippedContentValidationTest: XCTestCase {

    // MARK: - Helpers

    private func makeConfig(
        seed: UInt64,
        profile: OSVisualProfile = .ios26,
        colorScheme: GeneratorColorScheme = .light,
        pixelScale: Int = 3
    ) -> GeneratorRunConfig {
        GeneratorRunConfig(
            seed: seed,
            templateFamily: "ClippedContent",
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
        let vc = ClippedContentViewController(seed: seed, config: config)
        return try await ScreenshotCapture.captureUIKit(vc, config: config)
    }

    // MARK: - AC-1 + AC-2 + AC-6: knownIssues, elementType, and frame integrity

    func testAnnotationIntegrity_ios26_light() async throws {
        let config = makeConfig(seed: 42)
        let vc = ClippedContentViewController(seed: 42, config: config)
        let result = try await ScreenshotCapture.captureUIKit(vc, config: config)

        XCTAssertFalse(result.elements.isEmpty, "Expected ≥1 annotated element")

        let canvas = CGRect(origin: .zero, size: config.osProfile.screenSize)

        for elem in result.elements {
            // AC-6: element type must be "imageView"
            XCTAssertEqual(
                elem.elementType, "imageView",
                "\(elem.id): expected elementType \"imageView\", got \"\(elem.elementType)\""
            )

            // AC-1: every element must have knownIssues: ["clippedElement"]
            XCTAssertEqual(
                elem.knownIssues, ["clippedElement"],
                "\(elem.id): expected knownIssues [\"clippedElement\"], got \(elem.knownIssues)"
            )

            // AC-2: non-zero frame, within canvas
            XCTAssertGreaterThan(elem.frame.width,  0, "\(elem.id): zero width")
            XCTAssertGreaterThan(elem.frame.height, 0, "\(elem.id): zero height")
            XCTAssert(
                canvas.intersects(elem.frame),
                "\(elem.id): frame \(elem.frame) does not intersect canvas \(canvas)"
            )
        }

        // Spec: 4–6 rows
        XCTAssertGreaterThanOrEqual(result.elements.count, 4, "Expected ≥4 clipped rows")
        XCTAssertLessThanOrEqual(result.elements.count,   6, "Expected ≤6 clipped rows")

        // Attach PNG for visual inspection
        let attachment = XCTAttachment(data: result.png, uniformTypeIdentifier: "public.png")
        attachment.name = "clipped_content_ios26_light_seed42.png"
        attachment.lifetime = .keepAlways
        add(attachment)
    }

    // MARK: - AC-3: Each annotated container is smaller than its child in ≥1 axis

    func testChildOverflowsContainer() async throws {
        let config = makeConfig(seed: 42)
        let vc = ClippedContentViewController(seed: 42, config: config)

        // Trigger layout so frames are stable before we inspect the view hierarchy
        let result = try await ScreenshotCapture.captureUIKit(vc, config: config)

        XCTAssertFalse(result.elements.isEmpty, "No elements to check")

        // Walk the VC's annotated rows: for each container, verify its child imageView
        // has at least one dimension strictly larger than the container.
        for annotatedView in vc.annotatedViews {
            guard let containerView = annotatedView.view else {
                XCTFail("\(annotatedView.id): view was deallocated before inspection")
                continue
            }

            // The child imageView is the only subview of the container
            guard let childImageView = containerView.subviews.first else {
                XCTFail("\(annotatedView.id): container has no subviews — child not added")
                continue
            }

            let containerSize = containerView.bounds.size
            let childSize = childImageView.frame.size

            let overflowsWidth  = childSize.width  > containerSize.width  + 1
            let overflowsHeight = childSize.height > containerSize.height + 1

            XCTAssertTrue(
                overflowsWidth || overflowsHeight,
                "\(annotatedView.id): child (\(childSize)) should exceed container " +
                "(\(containerSize)) in at least one axis — clipping not demonstrated"
            )
        }

        _ = result  // suppress unused warning
    }

    // MARK: - AC-4: Seed reproducibility

    func testSeedReproducibility() async throws {
        let result1 = try await capture(seed: 99999)
        let result2 = try await capture(seed: 99999)

        XCTAssertEqual(result1.sha256, result2.sha256,
            "Same seed should produce identical PNG (byte-for-byte)")
        XCTAssertEqual(result1.elements.count, result2.elements.count,
            "Same seed should produce identical element count")
    }

    // MARK: - AC-5: ≥50 seeds complete without error

    func testFiftyDistinctSeeds() async throws {
        var captureCount = 0

        for seed in UInt64(0)..<50 {
            let profile: OSVisualProfile = seed < 25 ? .ios26 : .ios17
            let scheme: GeneratorColorScheme = seed.isMultiple(of: 2) ? .light : .dark
            let scale = seed < 25 ? 3 : 2

            let config = makeConfig(seed: seed, profile: profile,
                                    colorScheme: scheme, pixelScale: scale)
            let vc = ClippedContentViewController(seed: seed, config: config)
            let result = try await ScreenshotCapture.captureUIKit(vc, config: config)

            XCTAssertFalse(result.elements.isEmpty, "Seed \(seed): zero elements")
            XCTAssertFalse(result.png.isEmpty,      "Seed \(seed): empty PNG")

            // Spot-check knownIssues on every 10th seed
            if seed.isMultiple(of: 10) {
                for elem in result.elements {
                    XCTAssertEqual(elem.knownIssues, ["clippedElement"],
                        "Seed \(seed), \(elem.id): wrong knownIssues")
                }
            }

            captureCount += 1
        }

        XCTAssertEqual(captureCount, 50, "Expected exactly 50 successful captures")
    }

    // MARK: - Dark mode on ios17

    func testCapture_ios17_dark() async throws {
        let result = try await capture(seed: 7, profile: .ios17, colorScheme: .dark, pixelScale: 2)

        XCTAssertFalse(result.elements.isEmpty, "ios17 dark: zero elements")
        XCTAssertEqual(result.scale, 2)
        XCTAssertEqual(result.pixelSize.width,  750,  accuracy: 2, "Expected 750px wide")
        XCTAssertEqual(result.pixelSize.height, 1334, accuracy: 2, "Expected 1334px tall")

        let attachment = XCTAttachment(data: result.png, uniformTypeIdentifier: "public.png")
        attachment.name = "clipped_content_ios17_dark_seed7.png"
        attachment.lifetime = .keepAlways
        add(attachment)
    }
}
