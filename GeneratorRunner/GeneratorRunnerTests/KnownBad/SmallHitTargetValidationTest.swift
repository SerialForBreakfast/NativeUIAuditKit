// SmallHitTargetValidationTest.swift
// GeneratorRunnerTests — TASK-5a-4
//
// Validates SmallHitTargetViewController against the spec acceptance criteria:
//   AC-1: All elements have knownIssues: ["tappableTargetTooSmall"]
//   AC-2: Every annotated frame has width < 44 OR height < 44 (verifiable from boundsPoints)
//   AC-3: All four canonical sizes (20×20, 30×30, 32×44, 44×20) are present in every capture
//   AC-4: All frames are non-zero and within the canvas
//   AC-5: Seed reproducibility
//   AC-6: ≥50 distinct seeds produce valid captures without error

import XCTest
import UIKit

// MARK: - SmallHitTargetValidationTest

@MainActor
final class SmallHitTargetValidationTest: XCTestCase {

    // MARK: - Helpers

    private func makeConfig(
        seed: UInt64,
        profile: OSVisualProfile = .ios26,
        colorScheme: GeneratorColorScheme = .light,
        pixelScale: Int = 3
    ) -> GeneratorRunConfig {
        GeneratorRunConfig(
            seed: seed,
            templateFamily: "SmallHitTarget",
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
        let vc = SmallHitTargetViewController(seed: seed, config: config)
        return try await ScreenshotCapture.captureUIKit(vc, config: config)
    }

    // MARK: - AC-1 + AC-2 + AC-3 + AC-4: Core annotation integrity

    func testAnnotationIntegrity_ios26_light() async throws {
        let config = makeConfig(seed: 42)
        let vc = SmallHitTargetViewController(seed: 42, config: config)
        let result = try await ScreenshotCapture.captureUIKit(vc, config: config)

        // AC-3: Exactly 4 elements (one per canonical size)
        XCTAssertEqual(result.elements.count, 4,
            "Expected exactly 4 button annotations (one per canonical spec size), " +
            "got \(result.elements.count)")

        let canvas = CGRect(origin: .zero, size: config.osProfile.screenSize)

        for elem in result.elements {
            // Element type
            XCTAssertEqual(elem.elementType, "primaryButton",
                "\(elem.id): expected \"primaryButton\", got \"\(elem.elementType)\"")

            // AC-1: knownIssues
            XCTAssertEqual(elem.knownIssues, ["tappableTargetTooSmall"],
                "\(elem.id): expected [\"tappableTargetTooSmall\"], got \(elem.knownIssues)")

            // AC-2: at least one dimension is < 44pt (this is the invariant from the spec)
            let failsWidth  = elem.frame.width  < 44
            let failsHeight = elem.frame.height < 44
            XCTAssertTrue(
                failsWidth || failsHeight,
                "\(elem.id): frame \(elem.frame) — neither dimension is below 44pt; " +
                "should not carry tappableTargetTooSmall"
            )

            // AC-4: non-zero, within canvas
            XCTAssertGreaterThan(elem.frame.width,  0, "\(elem.id): zero width")
            XCTAssertGreaterThan(elem.frame.height, 0, "\(elem.id): zero height")
            XCTAssert(
                canvas.intersects(elem.frame),
                "\(elem.id): frame \(elem.frame) does not intersect canvas \(canvas)"
            )
        }

        // AC-3: Verify the four canonical sizes are all present (within 1pt tolerance)
        let canonicalSizes: [(CGFloat, CGFloat)] = [(20, 20), (30, 30), (32, 44), (44, 20)]
        for (w, h) in canonicalSizes {
            let match = result.elements.first {
                abs($0.frame.width  - w) < 1.5 &&
                abs($0.frame.height - h) < 1.5
            }
            XCTAssertNotNil(match,
                "Expected a \(Int(w))×\(Int(h))pt button in the annotation output, " +
                "found sizes: \(result.elements.map { "\(Int($0.frame.width))×\(Int($0.frame.height))" })")
        }

        // Attach PNG for visual inspection
        let attachment = XCTAttachment(data: result.png, uniformTypeIdentifier: "public.png")
        attachment.name = "small_hit_target_ios26_light_seed42.png"
        attachment.lifetime = .keepAlways
        add(attachment)
    }

    // MARK: - AC-5: Seed reproducibility

    func testSeedReproducibility() async throws {
        let result1 = try await capture(seed: 314159)
        let result2 = try await capture(seed: 314159)

        XCTAssertEqual(result1.sha256, result2.sha256,
            "Same seed should produce identical PNG")
        XCTAssertEqual(result1.elements.count, result2.elements.count,
            "Same seed should produce identical element count")
    }

    // MARK: - AC-6: ≥50 seeds — all complete without error, knownIssues always set

    func testFiftyDistinctSeeds() async throws {
        var captureCount = 0

        for seed in UInt64(0)..<50 {
            let profile: OSVisualProfile = seed < 25 ? .ios26 : .ios17
            let scheme: GeneratorColorScheme = seed.isMultiple(of: 2) ? .light : .dark
            let scale = seed < 25 ? 3 : 2

            let config = makeConfig(seed: seed, profile: profile,
                                    colorScheme: scheme, pixelScale: scale)
            let vc = SmallHitTargetViewController(seed: seed, config: config)
            let result = try await ScreenshotCapture.captureUIKit(vc, config: config)

            XCTAssertEqual(result.elements.count, 4, "Seed \(seed): expected 4 elements")
            XCTAssertFalse(result.png.isEmpty, "Seed \(seed): empty PNG")

            for elem in result.elements {
                XCTAssertEqual(elem.knownIssues, ["tappableTargetTooSmall"],
                    "Seed \(seed), \(elem.id): wrong knownIssues")
                let failsW = elem.frame.width  < 44
                let failsH = elem.frame.height < 44
                XCTAssertTrue(failsW || failsH,
                    "Seed \(seed), \(elem.id): no dimension below 44pt")
            }

            captureCount += 1
        }

        XCTAssertEqual(captureCount, 50, "Expected exactly 50 successful captures")
    }

    // MARK: - Dark mode on ios17

    func testCapture_ios17_dark() async throws {
        let result = try await capture(seed: 7, profile: .ios17, colorScheme: .dark, pixelScale: 2)

        XCTAssertEqual(result.elements.count, 4, "ios17 dark: expected 4 elements")
        XCTAssertEqual(result.scale, 2)

        let attachment = XCTAttachment(data: result.png, uniformTypeIdentifier: "public.png")
        attachment.name = "small_hit_target_ios17_dark_seed7.png"
        attachment.lifetime = .keepAlways
        add(attachment)
    }
}
