// DynamicTypeOverflowValidationTest.swift
// GeneratorRunnerTests — TASK-5a-5
//
// Validates DynamicTypeOverflowViewController against the spec acceptance criteria:
//   AC-1: All elements have knownIssues: ["dynamicTypeOverflow"]
//   AC-2: All frames are non-zero and within the canvas
//   AC-3: Config uses dynamicTypeSize: accessibilityExtraExtraExtraLarge
//   AC-4: For each annotated container, the label inside it has an intrinsic content
//         height > the container height (proving overflow would occur at natural size)
//   AC-5: Seed reproducibility
//   AC-6: ≥50 seeds produce valid captures without error

import XCTest
import UIKit

// MARK: - DynamicTypeOverflowValidationTest

@MainActor
final class DynamicTypeOverflowValidationTest: XCTestCase {

    // MARK: - Helpers

    private func makeConfig(
        seed: UInt64,
        profile: OSVisualProfile = .ios26,
        colorScheme: GeneratorColorScheme = .light,
        pixelScale: Int = 3
    ) -> GeneratorRunConfig {
        GeneratorRunConfig(
            seed: seed,
            templateFamily: "DynamicTypeOverflow",
            osProfile: profile,
            simulatorOverride: SimulatorStateOverride(
                time: "09:41", batteryLevel: 100, batteryState: "charging",
                cellularBars: 5, wifiBars: 3, cellularMode: "active", operatorName: ""
            ),
            colorScheme: colorScheme,
            // AC-3: must use the largest accessibility size
            dynamicTypeSize: .accessibilityExtraExtraExtraLarge,
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
        let vc = DynamicTypeOverflowViewController(seed: seed, config: config)
        return try await ScreenshotCapture.captureUIKit(vc, config: config)
    }

    // MARK: - AC-1 + AC-2 + AC-3: Core annotation integrity

    func testAnnotationIntegrity_ios26_axxxl() async throws {
        let config = makeConfig(seed: 42)
        let vc = DynamicTypeOverflowViewController(seed: 42, config: config)
        let result = try await ScreenshotCapture.captureUIKit(vc, config: config)

        XCTAssertFalse(result.elements.isEmpty, "Expected ≥1 element")

        // AC-3: config uses AXXXL
        XCTAssertEqual(config.dynamicTypeSize, .accessibilityExtraExtraExtraLarge,
            "Config must use accessibilityExtraExtraExtraLarge")

        let canvas = CGRect(origin: .zero, size: config.osProfile.screenSize)

        for elem in result.elements {
            XCTAssertEqual(elem.elementType, "label",
                "\(elem.id): expected \"label\", got \"\(elem.elementType)\"")

            // AC-1
            XCTAssertEqual(elem.knownIssues, ["dynamicTypeOverflow"],
                "\(elem.id): expected [\"dynamicTypeOverflow\"], got \(elem.knownIssues)")

            // AC-2
            XCTAssertGreaterThan(elem.frame.width,  0, "\(elem.id): zero width")
            XCTAssertGreaterThan(elem.frame.height, 0, "\(elem.id): zero height")
            XCTAssert(
                canvas.intersects(elem.frame),
                "\(elem.id): frame \(elem.frame) outside canvas \(canvas)"
            )
        }

        // 4–6 rows
        XCTAssertGreaterThanOrEqual(result.elements.count, 4)
        XCTAssertLessThanOrEqual(result.elements.count,   6)

        // Attach PNG
        let attachment = XCTAttachment(data: result.png, uniformTypeIdentifier: "public.png")
        attachment.name = "dt_overflow_ios26_axxxl_seed42.png"
        attachment.lifetime = .keepAlways
        add(attachment)
    }

    // MARK: - AC-4: Label intrinsic height > container height (overflow is real)

    func testLabelOverflowsContainer() async throws {
        let config = makeConfig(seed: 42)
        let vc = DynamicTypeOverflowViewController(seed: 42, config: config)
        _ = try await ScreenshotCapture.captureUIKit(vc, config: config)

        for annotatedView in vc.annotatedViews {
            guard let containerView = annotatedView.view else {
                XCTFail("\(annotatedView.id): container view was deallocated")
                continue
            }

            // The UILabel is the first subview of the container
            guard let label = containerView.subviews.first as? UILabel else {
                XCTFail("\(annotatedView.id): no UILabel subview found")
                continue
            }

            let containerH = containerView.bounds.height
            let intrinsicH  = label.intrinsicContentSize.height

            XCTAssertGreaterThan(
                intrinsicH, containerH,
                "\(annotatedView.id): label intrinsic height \(intrinsicH)pt should " +
                "exceed container height \(containerH)pt — overflow not demonstrated"
            )
        }
    }

    // MARK: - AC-5: Seed reproducibility

    func testSeedReproducibility() async throws {
        let result1 = try await capture(seed: 55555)
        let result2 = try await capture(seed: 55555)
        XCTAssertEqual(result1.sha256, result2.sha256, "Same seed → identical PNG")
        XCTAssertEqual(result1.elements.count, result2.elements.count)
    }

    // MARK: - AC-6: ≥50 seeds

    func testFiftyDistinctSeeds() async throws {
        var captureCount = 0

        for seed in UInt64(0)..<50 {
            let profile: OSVisualProfile = seed < 25 ? .ios26 : .ios17
            let scheme: GeneratorColorScheme = seed.isMultiple(of: 2) ? .light : .dark
            let scale = seed < 25 ? 3 : 2

            let config = GeneratorRunConfig(
                seed: seed,
                templateFamily: "DynamicTypeOverflow",
                osProfile: profile,
                simulatorOverride: SimulatorStateOverride(
                    time: "09:41", batteryLevel: 100, batteryState: "charging",
                    cellularBars: 5, wifiBars: 3, cellularMode: "active", operatorName: ""
                ),
                colorScheme: scheme,
                dynamicTypeSize: .accessibilityExtraExtraExtraLarge,
                deviceName: "Test Device",
                pixelScale: scale,
                locale: "en_US",
                layoutDirection: .ltr
            )
            let vc = DynamicTypeOverflowViewController(seed: seed, config: config)
            let result = try await ScreenshotCapture.captureUIKit(vc, config: config)

            XCTAssertFalse(result.elements.isEmpty, "Seed \(seed): zero elements")
            XCTAssertFalse(result.png.isEmpty, "Seed \(seed): empty PNG")

            if seed.isMultiple(of: 10) {
                for elem in result.elements {
                    XCTAssertEqual(elem.knownIssues, ["dynamicTypeOverflow"],
                        "Seed \(seed), \(elem.id): wrong knownIssues")
                }
            }
            captureCount += 1
        }

        XCTAssertEqual(captureCount, 50)
    }
}
