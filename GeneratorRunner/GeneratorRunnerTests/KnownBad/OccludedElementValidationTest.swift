// OccludedElementValidationTest.swift
// GeneratorRunnerTests — TASK-5a-8
//
// Validates OccludedElementViewController against the spec acceptance criteria:
//   AC-1: Sheet is annotated as `sheet`
//   AC-2: Fully covered buttons (>80% covered) are excluded from annotatedViews
//   AC-3: Partially covered buttons (20–80% visible) ARE in annotatedViews
//   AC-4: Fully visible buttons are annotated with no knownIssues
//   AC-5: All annotated frames non-zero
//   AC-6: Seed reproducibility
//   AC-7: ≥50 seeds produce valid captures

import XCTest
import UIKit

// MARK: - OccludedElementValidationTest

@MainActor
final class OccludedElementValidationTest: XCTestCase {

    // MARK: - Helpers

    private func makeConfig(
        seed: UInt64,
        profile: OSVisualProfile = .ios26,
        colorScheme: GeneratorColorScheme = .light,
        pixelScale: Int = 3
    ) -> GeneratorRunConfig {
        GeneratorRunConfig(
            seed: seed,
            templateFamily: "OccludedElement",
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

    // MARK: - AC-1 + AC-2 + AC-3 + AC-4 + AC-5: Annotation integrity

    func testAnnotationIntegrity_ios26_light() async throws {
        let config = makeConfig(seed: 42)
        let vc = OccludedElementViewController(seed: 42, config: config)
        let result = try await ScreenshotCapture.captureUIKit(vc, config: config)

        // AC-1: Sheet must be present
        let sheetElements = result.elements.filter { $0.elementType == "sheet" }
        XCTAssertEqual(sheetElements.count, 1, "Expected exactly 1 sheet annotation")

        // AC-4: All knownIssues should be empty (no knownIssues on occluded elements)
        for elem in result.elements {
            XCTAssertTrue(elem.knownIssues.isEmpty,
                "\(elem.id): expected empty knownIssues, got \(elem.knownIssues)")
        }

        // AC-5: All frames non-zero
        for elem in result.elements {
            XCTAssertGreaterThan(elem.frame.width,  0, "\(elem.id): zero width")
            XCTAssertGreaterThan(elem.frame.height, 0, "\(elem.id): zero height")
        }

        // Total buttons in annotatedViews <= total rows (4 buttons, only some annotated)
        let buttonElements = result.elements.filter { $0.elementType == "primaryButton" }
        XCTAssertGreaterThanOrEqual(buttonElements.count, 1,
            "Expected ≥1 button (at least one fully visible)")
        XCTAssertLessThanOrEqual(buttonElements.count, 3,
            "Expected ≤3 buttons (fully covered rows excluded)")

        // Attach PNG
        let attachment = XCTAttachment(data: result.png, uniformTypeIdentifier: "public.png")
        attachment.name = "occluded_element_ios26_light_seed42.png"
        attachment.lifetime = .keepAlways
        add(attachment)
    }

    // MARK: - AC-6: Seed reproducibility

    func testSeedReproducibility() async throws {
        let config1 = makeConfig(seed: 77777)
        let vc1 = OccludedElementViewController(seed: 77777, config: config1)
        let r1 = try await ScreenshotCapture.captureUIKit(vc1, config: config1)

        let config2 = makeConfig(seed: 77777)
        let vc2 = OccludedElementViewController(seed: 77777, config: config2)
        let r2 = try await ScreenshotCapture.captureUIKit(vc2, config: config2)

        XCTAssertEqual(r1.sha256, r2.sha256, "Same seed → identical PNG")
        XCTAssertEqual(r1.elements.count, r2.elements.count)
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
            let vc = OccludedElementViewController(seed: seed, config: config)
            let result = try await ScreenshotCapture.captureUIKit(vc, config: config)

            XCTAssertFalse(result.png.isEmpty, "Seed \(seed): empty PNG")
            // Sheet must always be present
            let hasSheet = result.elements.contains { $0.elementType == "sheet" }
            XCTAssertTrue(hasSheet, "Seed \(seed): no sheet element")
            captureCount += 1
        }

        XCTAssertEqual(captureCount, 50)
    }
}
