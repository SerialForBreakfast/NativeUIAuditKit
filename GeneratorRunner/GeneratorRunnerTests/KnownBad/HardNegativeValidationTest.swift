// HardNegativeValidationTest.swift
// GeneratorRunnerTests — TASK-5a-9
//
// Validates HardNegativeViewController (both active types) against the spec:
//
//   Type 1 — Loading overlay:    elements: [] (zero annotations)
//   Type 3 — Decorative fill:    elements: [] (zero annotations)
//
//   ≥30 images per active type (≥60 total) per spec.

import XCTest
import UIKit

// MARK: - HardNegativeValidationTest

@MainActor
final class HardNegativeValidationTest: XCTestCase {

    // MARK: - Helpers

    private func makeConfig(
        seed: UInt64,
        type: HardNegativeType,
        profile: OSVisualProfile = .ios26,
        colorScheme: GeneratorColorScheme = .light,
        pixelScale: Int = 3
    ) -> GeneratorRunConfig {
        GeneratorRunConfig(
            seed: seed,
            templateFamily: "HardNegative_\(type.rawValue)",
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
        type: HardNegativeType,
        seed: UInt64,
        profile: OSVisualProfile = .ios26,
        colorScheme: GeneratorColorScheme = .light,
        pixelScale: Int = 3
    ) async throws -> CaptureResult {
        let config = makeConfig(seed: seed, type: type, profile: profile,
                                colorScheme: colorScheme, pixelScale: pixelScale)
        let vc = HardNegativeViewController(type: type, seed: seed, config: config)
        return try await ScreenshotCapture.captureUIKit(vc, config: config)
    }

    // MARK: - Type 1: Loading overlay → elements: []

    func testOnlyNativeHardNegativeTypesRemainActive() {
        XCTAssertEqual(HardNegativeType.allCases.map(\.rawValue), [1, 3])
    }

    func testLoadingOverlay_hasNoAnnotations() async throws {
        let result = try await capture(type: .loadingOverlay, seed: 42)

        XCTAssertTrue(result.elements.isEmpty,
            "Loading overlay must have zero annotations, got: " +
            result.elements.map(\.elementType).joined(separator: ", "))
        XCTAssertFalse(result.png.isEmpty, "Empty PNG")

        let attachment = XCTAttachment(data: result.png, uniformTypeIdentifier: "public.png")
        attachment.name = "hard_negative_loading_ios26_seed42.png"
        attachment.lifetime = .keepAlways
        add(attachment)
    }

    func testLoadingOverlay_thirtySeeds() async throws {
        var count = 0
        for seed in UInt64(0)..<30 {
            let result = try await capture(type: .loadingOverlay, seed: seed)
            XCTAssertTrue(result.elements.isEmpty, "Seed \(seed): expected no annotations")
            XCTAssertFalse(result.png.isEmpty, "Seed \(seed): empty PNG")
            count += 1
        }
        XCTAssertEqual(count, 30)
    }

    // MARK: - Type 3: Decorative fill → elements: []

    func testDecorativeFill_hasNoAnnotations() async throws {
        let result = try await capture(type: .decorativeFill, seed: 42)

        XCTAssertTrue(result.elements.isEmpty,
            "Decorative fill must have zero annotations, got: " +
            result.elements.map(\.elementType).joined(separator: ", "))
        XCTAssertFalse(result.png.isEmpty, "Empty PNG")

        let attachment = XCTAttachment(data: result.png, uniformTypeIdentifier: "public.png")
        attachment.name = "hard_negative_decorative_ios26_seed42.png"
        attachment.lifetime = .keepAlways
        add(attachment)
    }

    func testDecorativeFill_thirtySeeds() async throws {
        var count = 0
        for seed in UInt64(0)..<30 {
            let result = try await capture(type: .decorativeFill, seed: seed)
            XCTAssertTrue(result.elements.isEmpty, "Seed \(seed): expected no annotations")
            XCTAssertFalse(result.png.isEmpty, "Seed \(seed): empty PNG")
            count += 1
        }
        XCTAssertEqual(count, 30)
    }

    // MARK: - Seed reproducibility (one type per check)

    func testSeedReproducibility_loadingOverlay() async throws {
        let r1 = try await capture(type: .loadingOverlay, seed: 9999)
        let r2 = try await capture(type: .loadingOverlay, seed: 9999)
        XCTAssertEqual(r1.sha256, r2.sha256, "Loading overlay: same seed → identical PNG")
    }

    func testSeedReproducibility_decorativeFill() async throws {
        let r1 = try await capture(type: .decorativeFill, seed: 8888)
        let r2 = try await capture(type: .decorativeFill, seed: 8888)
        XCTAssertEqual(r1.sha256, r2.sha256, "Decorative fill: same seed → identical PNG")
    }
}
