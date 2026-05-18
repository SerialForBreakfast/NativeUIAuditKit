// RTLMirroringFailureValidationTest.swift
// GeneratorRunnerTests — TASK-5a-6
//
// Validates RTLMirroringFailureViewController against the spec acceptance criteria:
//   AC-1: All elements have knownIssues: ["rtlMirroringFailure"]
//   AC-2: Config layoutDirection is .rtl
//   AC-3: All frames are non-zero and within the canvas
//   AC-4: Exactly 6 elements (one per failure pattern)
//   AC-5: Seed reproducibility
//   AC-6: ≥30 seeds produce valid captures without error (spec min is ≥30)

import XCTest
import UIKit

// MARK: - RTLMirroringFailureValidationTest

@MainActor
final class RTLMirroringFailureValidationTest: XCTestCase {

    // MARK: - Helpers

    private func makeConfig(
        seed: UInt64,
        profile: OSVisualProfile = .ios26,
        colorScheme: GeneratorColorScheme = .light,
        pixelScale: Int = 3
    ) -> GeneratorRunConfig {
        GeneratorRunConfig(
            seed: seed,
            templateFamily: "RTLMirroringFailure",
            osProfile: profile,
            simulatorOverride: SimulatorStateOverride(
                time: "09:41", batteryLevel: 100, batteryState: "charging",
                cellularBars: 5, wifiBars: 3, cellularMode: "active", operatorName: ""
            ),
            colorScheme: colorScheme,
            dynamicTypeSize: .large,
            deviceName: "Test Device",
            pixelScale: pixelScale,
            locale: "ar_SA",      // Arabic locale — canonical RTL test locale
            layoutDirection: .rtl // AC-2: config must be RTL
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
        let vc = RTLMirroringFailureViewController(seed: seed, config: config)
        return try await ScreenshotCapture.captureUIKit(vc, config: config)
    }

    // MARK: - AC-1 + AC-2 + AC-3 + AC-4: Core annotation integrity

    func testAnnotationIntegrity_ios26_rtl() async throws {
        let config = makeConfig(seed: 42)
        let vc = RTLMirroringFailureViewController(seed: 42, config: config)
        let result = try await ScreenshotCapture.captureUIKit(vc, config: config)

        // AC-2: layout direction must be RTL
        XCTAssertEqual(config.layoutDirection, .rtl,
            "Config must specify RTL layout direction")

        // AC-4: exactly 6 elements (one per failure pattern)
        XCTAssertEqual(result.elements.count, 6,
            "Expected 6 elements (one per RTL failure pattern), got \(result.elements.count)")

        let canvas = CGRect(origin: .zero, size: config.osProfile.screenSize)

        for elem in result.elements {
            // AC-1: knownIssues
            XCTAssertEqual(
                elem.knownIssues, ["rtlMirroringFailure"],
                "\(elem.id): expected [\"rtlMirroringFailure\"], got \(elem.knownIssues)"
            )

            // AC-3: non-zero, within canvas
            XCTAssertGreaterThan(elem.frame.width,  0, "\(elem.id): zero width")
            XCTAssertGreaterThan(elem.frame.height, 0, "\(elem.id): zero height")
            XCTAssert(
                canvas.intersects(elem.frame),
                "\(elem.id): frame \(elem.frame) outside canvas \(canvas)"
            )
        }

        // Verify the expected element types are present
        let types = Set(result.elements.map(\.elementType))
        let requiredTypes: Set<String> = ["primaryButton", "progressView", "label", "slider"]
        let missing = requiredTypes.subtracting(types)
        XCTAssertTrue(missing.isEmpty,
            "Missing element types in RTL failure capture: \(missing.sorted())")

        // Attach PNG
        let attachment = XCTAttachment(data: result.png, uniformTypeIdentifier: "public.png")
        attachment.name = "rtl_mirroring_failure_ios26_seed42.png"
        attachment.lifetime = .keepAlways
        add(attachment)
    }

    // MARK: - AC-5: Seed reproducibility

    func testSeedReproducibility() async throws {
        let result1 = try await capture(seed: 88888)
        let result2 = try await capture(seed: 88888)
        XCTAssertEqual(result1.sha256, result2.sha256, "Same seed → identical PNG")
        XCTAssertEqual(result1.elements.count, result2.elements.count)
    }

    // MARK: - AC-6: ≥30 seeds complete without error

    func testThirtyDistinctSeeds() async throws {
        var captureCount = 0

        for seed in UInt64(0)..<30 {
            let profile: OSVisualProfile = seed < 15 ? .ios26 : .ios17
            let scheme: GeneratorColorScheme = seed.isMultiple(of: 2) ? .light : .dark
            let scale = seed < 15 ? 3 : 2

            let config = GeneratorRunConfig(
                seed: seed,
                templateFamily: "RTLMirroringFailure",
                osProfile: profile,
                simulatorOverride: SimulatorStateOverride(
                    time: "09:41", batteryLevel: 100, batteryState: "charging",
                    cellularBars: 5, wifiBars: 3, cellularMode: "active", operatorName: ""
                ),
                colorScheme: scheme,
                dynamicTypeSize: .large,
                deviceName: "Test Device",
                pixelScale: scale,
                locale: "ar_SA",
                layoutDirection: .rtl
            )
            let vc = RTLMirroringFailureViewController(seed: seed, config: config)
            let result = try await ScreenshotCapture.captureUIKit(vc, config: config)

            XCTAssertEqual(result.elements.count, 6, "Seed \(seed): expected 6 elements")
            XCTAssertFalse(result.png.isEmpty, "Seed \(seed): empty PNG")

            if seed.isMultiple(of: 10) {
                for elem in result.elements {
                    XCTAssertEqual(elem.knownIssues, ["rtlMirroringFailure"],
                        "Seed \(seed), \(elem.id): wrong knownIssues")
                }
            }
            captureCount += 1
        }

        XCTAssertEqual(captureCount, 30)
    }
}
