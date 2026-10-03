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
import CryptoKit

/// Explicit corpus repair, separate from the normal offline unit suite.
@MainActor
final class PageDotRegenerationTest: XCTestCase {
    private struct Catalog: Decodable, Sendable {
        let version: String
        let members: [Member]
    }
    private struct Member: Decodable, Sendable {
        let id: String
        let family: String
        let seed: UInt64
        let width: Int
        let height: Int
        let scale: Int
        let colorScheme: GeneratorColorScheme
        let dynamicTypeSize: GeneratorDynamicTypeSize
        let locale: String
        let layoutDirection: GeneratorLayoutDirection
        let deviceName: String
        let simulatorState: SimulatorStateOverride
        let accessibilityFlags: AccessibilityFlags
    }

    func testApprovedPageDotRegeneration() async throws {
        let env = ProcessInfo.processInfo.environment
        guard env["NUA_PAGE_REGEN_EXECUTE"] == "approved-41" else {
            throw XCTSkip("Explicit corpus regeneration approval required")
        }
        let path = try XCTUnwrap(env["NUA_PAGE_REGEN_CATALOG"])
        let url = URL(fileURLWithPath: path)
        guard url.resolvingSymlinksInPath() == url, env["SIMULATOR_UDID"] == env["NUA_PAGE_REGEN_TARGET"] else {
            throw CocoaError(.fileReadInvalidFileName)
        }
        let data = try Data(contentsOf: url)
        let digest = SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
        XCTAssertEqual(digest, env["NUA_PAGE_REGEN_SHA256"])
        guard digest == env["NUA_PAGE_REGEN_SHA256"], data.count < 2_000_000 else { throw CocoaError(.fileReadCorruptFile) }
        let catalog = try JSONDecoder().decode(Catalog.self, from: data)
        guard catalog.version == "page-dot-regeneration-v1", catalog.members.count == 666,
              Set(catalog.members.map(\.id)).count == 666 else { throw CocoaError(.fileReadCorruptFile) }
        let fm = FileManager.default
        let output = fm.urls(for: .documentDirectory, in: .userDomainMask)[0].appendingPathComponent("page-regeneration-41")
        guard !fm.fileExists(atPath: output.path) else { throw CocoaError(.fileWriteFileExists) }
        try fm.createDirectory(at: output, withIntermediateDirectories: false)
        let started = ProcessInfo.processInfo.systemUptime
        var bytes = 0
        for (index, row) in catalog.members.enumerated() {
            guard ProcessInfo.processInfo.systemUptime - started < 1200,
                  row.id.range(of: "^img_[0-9]{6}$", options: .regularExpression) != nil,
                  [2, 3].contains(row.scale), ["MediaCardGrid", "ProgressActivity"].contains(row.family) else {
                throw CocoaError(.userCancelled)
            }
            let config = GeneratorRunConfig(seed: row.seed, templateFamily: row.family,
                osProfile: row.scale == 3 ? .ios26 : .ios17, simulatorOverride: row.simulatorState,
                colorScheme: row.colorScheme, dynamicTypeSize: row.dynamicTypeSize, deviceName: row.deviceName,
                pixelScale: row.scale, locale: row.locale, layoutDirection: row.layoutDirection,
                accessibilityFlags: row.accessibilityFlags)
            var corpus = ContentCorpus(seed: row.seed)
            let view: AnyView
            if row.family == "MediaCardGrid" {
                view = AnyView(MediaCardGridTemplate(config: .make(seed: row.seed, corpus: &corpus)))
            } else {
                view = AnyView(ProgressActivityTemplate(config: .make(seed: row.seed, corpus: &corpus)))
            }
            let result = try await ScreenshotCapture.capture(view, config: config)
            let dots = try XCTUnwrap(result.elements.first { $0.id == "pageControl_0" })
            guard [25.0,40.0,55.0,70.0].contains(where: { abs(dots.frame.width - $0) < 1 }),
                  abs(dots.frame.height - 10) < 1,
                  Int(result.pixelSize.width) == row.width, Int(result.pixelSize.height) == row.height else {
                throw CocoaError(.fileReadCorruptFile)
            }
            bytes += result.png.count
            guard bytes < 2 * 1024 * 1024 * 1024 else { throw CocoaError(.fileWriteOutOfSpace) }
            try result.png.write(to: output.appendingPathComponent(row.id + ".png"), options: .withoutOverwriting)
            let annotation = output.appendingPathComponent(row.id + ".json")
            try AnnotationWriter.write(result: result, config: config, imageFileName: row.id + ".png",
                templateFamily: row.family, generatorVersion: "page-dot-repair-41", to: annotation)
            bytes += try Data(contentsOf: annotation).count
            if index % 50 == 0 { print("PAGE_REGEN_PROGRESS \(index + 1)/666 bytes=\(bytes)") }
        }
        let receipt: [String: Any] = ["count": 666, "catalogSHA256": digest,
            "runtimeOS": ProcessInfo.processInfo.operatingSystemVersionString,
            "seconds": ProcessInfo.processInfo.systemUptime - started, "bytes": bytes]
        try JSONSerialization.data(withJSONObject: receipt, options: [.sortedKeys, .prettyPrinted])
            .write(to: output.appendingPathComponent("receipt.json"), options: .withoutOverwriting)
        print("PAGE_REGEN_COMPLETE \(output.path)")
    }
}

@MainActor
final class KitchenSinkValidationTest: XCTestCase {

    /// Opt-in rendered regression: exercise both repaired templates, not a mock
    /// geometry formula. Attach evidence to the project-local xcresult only.
    func testPageDotIntrinsicGeometry() async throws {
        guard ProcessInfo.processInfo.environment["NUA_PAGE_DOT_PROBE"] == "1" else {
            throw XCTSkip("Select the bounded page-dot rendering probe explicitly")
        }
        for width in [375.0, 430.0] {
            for count in 2...5 {
                for family in ["MediaCardGrid", "ProgressActivity"] {
                    var corpus = ContentCorpus(seed: 40)
                    let view: AnyView
                    if family == "MediaCardGrid" {
                        var config = MediaCardGridConfig.make(seed: 40, corpus: &corpus)
                        config.pageCount = count
                        config.currentPage = 0
                        view = AnyView(MediaCardGridTemplate(config: config))
                    } else {
                        var config = ProgressActivityConfig.make(seed: 40, corpus: &corpus)
                        config.pageCount = count
                        config.currentPage = 0
                        view = AnyView(ProgressActivityTemplate(config: config))
                    }
                    let result = try await ScreenshotCapture.capture(view,
                        windowSize: CGSize(width: width, height: 1100), config: makeGeneratorConfig(seed: 40))
                    let dots = try XCTUnwrap(result.elements.first { $0.id == "pageControl_0" })
                    XCTAssertLessThan(dots.frame.width, width / 2, "Whole-row capture: \(family)")
                    XCTAssertGreaterThan(dots.frame.height, 0)
                    XCTAssertEqual(dots.frame.width, 10 + Double(count - 1) * 15, accuracy: 1)
                    XCTAssertEqual(dots.frame.height, 10, accuracy: 1)
                    let attachment = XCTAttachment(data: result.png, uniformTypeIdentifier: "public.png")
                    attachment.name = "\(family)-\(Int(width))-\(count)-raw"
                    attachment.lifetime = .keepAlways
                    add(attachment)
                    let overlay = XCTAttachment(data: BoundingBoxDebugRenderer.render(result), uniformTypeIdentifier: "public.png")
                    overlay.name = "\(family)-\(Int(width))-\(count)-bounds"
                    overlay.lifetime = .keepAlways
                    add(overlay)
                    print("PAGE_DOT_GEOMETRY \(family) width=\(width) count=\(count) bounds=\(dots.frame)")
                }
            }
        }
    }

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
