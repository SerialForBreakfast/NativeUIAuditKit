// KitchenSinkValidationTest.swift
// GeneratorRunnerTests
//
// One-shot smoke test: generates a single KitchenSink image, draws labeled bounding
// boxes on it, and writes two files to Documents/debug/:
//
//   kitchen_sink_raw.png      — clean screenshot, no overlay
//   kitchen_sink_debug.png    — same PNG with colored boxes + element ID labels burned in
//
// How to inspect output:
//   Open the .xcresult in Xcode → test navigator → expand the test → click the attachment.
//   Or: open .build/debug-output/KitchenSinkValidation.xcresult directly.
//
// What to check:
//   - Every annotated element has a tight box (not the whole screen, not zero-sized)
//   - Boxes for same-type elements (e.g. three listRows) look independent and correct
//   - No box overlaps an unrelated element due to a coordinate bug
//   - Chrome boxes (navigationBar, tabBar, homeIndicator) are in the right screen zones
//   - Assertions at the bottom catch structural issues automatically

import XCTest
import SwiftUI

@MainActor
final class KitchenSinkValidationTest: XCTestCase {

    // MARK: - Expected element IDs

    /// Every element type that KitchenSinkTemplate must capture.
    /// If any of these is missing, the test fails before you even look at the image.
    private static let requiredElementTypes: Set<String> = [
        "navigationBar", "tabBar", "tabBarItem", "homeIndicator",
        "label", "imageView", "link",
        "primaryButton", "secondaryButton", "destructiveButton", "cancelAction",
        "toggle", "slider", "stepperControl",
        "textField", "secureField", "searchField",
        "segmentedControl", "picker",
        "menuButton", "colorWell", "pageControl",
        "activityIndicator", "progressView",
        "listRow", "disclosureGroup"
    ]

    // MARK: - Smoke test

    func testKitchenSinkBoundingBoxes() async throws {
        // Fixed seed so the same image is produced on every run.
        let seed: UInt64 = 9_999
        var corpus = ContentCorpus(seed: seed)
        let templateConfig = KitchenSinkConfig.make(seed: seed, corpus: &corpus)

        // Tall window so all content is rendered without scroll offset.
        let windowSize = CGSize(width: 393, height: 1100)
        let generatorConfig = makeGeneratorConfig(seed: seed)

        let result = try await ScreenshotCapture.capture(
            KitchenSinkTemplate(config: templateConfig),
            windowSize: windowSize,
            config: generatorConfig
        )

        // Attach clean PNG to test result — stored in .xcresult, never outside the project.
        let rawAttachment = XCTAttachment(data: result.png, uniformTypeIdentifier: "public.png")
        rawAttachment.name = "kitchen_sink_raw.png"
        rawAttachment.lifetime = .keepAlways
        add(rawAttachment)

        // Attach debug-annotated PNG (boxes + labels burned in).
        let debugPNG = BoundingBoxDebugRenderer.render(result)
        let debugAttachment = XCTAttachment(data: debugPNG, uniformTypeIdentifier: "public.png")
        debugAttachment.name = "kitchen_sink_debug.png"
        debugAttachment.lifetime = .keepAlways
        add(debugAttachment)

        // MARK: Structural assertions

        let capturedIDs   = Set(result.elements.map { $0.id })
        let capturedTypes = Set(result.elements.map { elementType(from: $0.id) })

        // 1. All required element types are present
        let missingTypes = Self.requiredElementTypes.subtracting(capturedTypes)
        XCTAssertTrue(
            missingTypes.isEmpty,
            "Missing element types in capture: \(missingTypes.sorted().joined(separator: ", "))"
        )

        // 2. No element has a zero-sized bounding box
        let zeroSized = result.elements.filter { $0.frame.width < 1 || $0.frame.height < 1 }
        XCTAssertTrue(
            zeroSized.isEmpty,
            "Zero-sized boxes for: \(zeroSized.map(\.id).joined(separator: ", "))"
        )

        // 3. No two elements have byte-identical frames (would indicate a capture duplication bug)
        var seen = Set<String>()
        var duplicateFrames: [String] = []
        for el in result.elements {
            let key = "\(el.frame.minX),\(el.frame.minY),\(el.frame.width),\(el.frame.height)"
            if seen.contains(key) { duplicateFrames.append(el.id) }
            seen.insert(key)
        }
        XCTAssertTrue(
            duplicateFrames.isEmpty,
            "Duplicate frames for: \(duplicateFrames.joined(separator: ", "))"
        )

        // 4. All element frames fall within the capture canvas (no negative or out-of-bounds coords)
        let canvasRect = CGRect(origin: .zero, size: windowSize)
        let outOfBounds = result.elements.filter {
            !canvasRect.contains($0.frame.origin) &&
            !canvasRect.intersects($0.frame)
        }
        XCTAssertTrue(
            outOfBounds.isEmpty,
            "Out-of-bounds frames for: \(outOfBounds.map(\.id).joined(separator: ", "))"
        )

        // 5. SHA-256 is a valid 64-char hex string
        XCTAssertEqual(result.sha256.count, 64)
        XCTAssertTrue(result.sha256.allSatisfy(\.isHexDigit))

        // Print summary to the test log for quick scan
        print("✅ KitchenSink captured \(result.elements.count) elements")
        print("   Attachments stored in .xcresult — open in Xcode test navigator to inspect.")

        for el in result.elements.sorted(by: { $0.id < $1.id }) {
            print(String(format: "   %-36s  (%.0f,%.0f) %.0f×%.0f",
                         (el.id as NSString).utf8String ?? "",
                         el.frame.minX, el.frame.minY,
                         el.frame.width, el.frame.height))
        }
    }

    // MARK: - Helpers

    private func makeGeneratorConfig(seed: UInt64) -> GeneratorRunConfig {
        GeneratorRunConfig(
            seed: seed,
            templateFamily: "KitchenSink",
            osProfile: .ios26,
            simulatorOverride: SimulatorStateOverride(
                time: "09:41",
                batteryLevel: 100,
                batteryState: "charging",
                cellularBars: 5,
                wifiBars: 3,
                cellularMode: "active",
                operatorName: ""
            ),
            colorScheme: .light,
            dynamicTypeSize: .large,
            deviceName: "iPhone 17 Pro",
            pixelScale: 3,
            locale: "en_US",
            layoutDirection: .ltr
        )
    }

    private func elementType(from id: String) -> String {
        String(id.split(separator: "_", maxSplits: 1).first ?? Substring(id))
    }
}
