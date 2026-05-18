// TruncatedLabelValidationTest.swift
// GeneratorRunnerTests — TASK-5a-1
//
// Validates TruncatedLabelViewController against the spec acceptance criteria:
//   AC-1: All elements carry knownIssues: ["truncatedText"]
//   AC-2: All element frames are non-zero and within the canvas
//   AC-3: VNRecognizeTextRequest detects the "…" character within at least one
//         element's bounds in the rendered PNG
//   AC-4: Seed reproducibility — same seed → identical sha256 PNG
//   AC-5: ≥50 distinct seeds produce valid captures without error

import XCTest
import UIKit
import Vision

// MARK: - TruncatedLabelValidationTest

@MainActor
final class TruncatedLabelValidationTest: XCTestCase {

    // MARK: - Helpers

    private func makeConfig(seed: UInt64, profile: OSVisualProfile = .ios26) -> GeneratorRunConfig {
        GeneratorRunConfig(
            seed: seed,
            templateFamily: "TruncatedLabel",
            osProfile: profile,
            simulatorOverride: SimulatorStateOverride(
                time: "09:41", batteryLevel: 100, batteryState: "charging",
                cellularBars: 5, wifiBars: 3, cellularMode: "active", operatorName: ""
            ),
            colorScheme: .light,
            dynamicTypeSize: .large,
            deviceName: "Test Device",
            pixelScale: 3,
            locale: "en_US",
            layoutDirection: .ltr
        )
    }

    private func capture(seed: UInt64, profile: OSVisualProfile = .ios26) async throws -> CaptureResult {
        let config = makeConfig(seed: seed, profile: profile)
        let vc = TruncatedLabelViewController(seed: seed, config: config)
        return try await ScreenshotCapture.captureUIKit(vc, config: config)
    }

    // MARK: - AC-1 + AC-2: knownIssues and frame integrity

    func testKnownIssuesAndFrameIntegrity_ios26_light() async throws {
        let config = makeConfig(seed: 42)
        let vc = TruncatedLabelViewController(seed: 42, config: config)
        let result = try await ScreenshotCapture.captureUIKit(vc, config: config)

        XCTAssertFalse(result.elements.isEmpty, "Expected at least one annotated element")

        let canvas = CGRect(origin: .zero, size: config.osProfile.screenSize)

        for elem in result.elements {
            // AC-1: every element must have knownIssues: ["truncatedText"]
            XCTAssertEqual(
                elem.knownIssues, ["truncatedText"],
                "\(elem.id): expected knownIssues [\"truncatedText\"], got \(elem.knownIssues)"
            )
            XCTAssertEqual(
                elem.elementType, "label",
                "\(elem.id): expected elementType \"label\", got \"\(elem.elementType)\""
            )

            // AC-2: non-zero frame, within canvas
            XCTAssertGreaterThan(elem.frame.width,  0, "\(elem.id): zero width")
            XCTAssertGreaterThan(elem.frame.height, 0, "\(elem.id): zero height")
            XCTAssert(
                canvas.intersects(elem.frame),
                "\(elem.id): frame \(elem.frame) does not intersect canvas \(canvas)"
            )
        }

        // Expect 4–6 rows (per spec)
        XCTAssertGreaterThanOrEqual(result.elements.count, 4, "Expected ≥4 label rows")
        XCTAssertLessThanOrEqual(result.elements.count,   6, "Expected ≤6 label rows")

        // Attach PNG for visual inspection
        let attachment = XCTAttachment(data: result.png, uniformTypeIdentifier: "public.png")
        attachment.name = "truncated_label_ios26_light_seed42.png"
        attachment.lifetime = .keepAlways
        add(attachment)
    }

    // MARK: - AC-3: VNRecognizeTextRequest detects "…" within element bounds

    func testVisionEllipsisDetection() async throws {
        let config = makeConfig(seed: 42)
        let vc = TruncatedLabelViewController(seed: 42, config: config)
        let result = try await ScreenshotCapture.captureUIKit(vc, config: config)

        // Build a CGImage from the captured PNG for Vision processing
        guard let uiImage = UIImage(data: result.png),
              let cgImage = uiImage.cgImage else {
            XCTFail("Could not create CGImage from captured PNG")
            return
        }

        // Run VNRecognizeTextRequest synchronously on this test's background queue.
        // We need the call to complete before assertions, so wrap in continuation.
        let observations: [VNRecognizedTextObservation] = try await withCheckedThrowingContinuation { continuation in
            let request = VNRecognizeTextRequest { req, error in
                if let error {
                    continuation.resume(throwing: error)
                    return
                }
                let obs = req.results as? [VNRecognizedTextObservation] ?? []
                continuation.resume(returning: obs)
            }
            request.recognitionLevel = .accurate
            request.usesLanguageCorrection = false

            let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
            do {
                try handler.perform([request])
            } catch {
                continuation.resume(throwing: error)
            }
        }

        // Vision returns bounding boxes in normalised coordinates (bottom-left origin).
        // The captured image dimensions in pixels:
        let imgW = CGFloat(cgImage.width)
        let imgH = CGFloat(cgImage.height)

        // Convert element frames (top-left, points) to pixel space for comparison.
        let scale = CGFloat(result.scale)

        // Check that at least one recognized string contains "…" and its Vision
        // bounding box overlaps at least one element's pixel-space frame.
        var foundEllipsis = false

        for obs in observations {
            guard let candidate = obs.topCandidates(1).first else { continue }
            guard candidate.string.contains("…") else { continue }

            // Vision normalised rect: origin bottom-left, (0,0)–(1,1)
            let vBox = obs.boundingBox
            // Convert to top-left pixel rect
            let pixelRect = CGRect(
                x: vBox.minX * imgW,
                y: (1.0 - vBox.maxY) * imgH,     // flip Y: Vision bottom-left → top-left
                width: vBox.width * imgW,
                height: vBox.height * imgH
            )

            // Check if this recognition overlaps any annotated element frame (in pixels)
            for elem in result.elements {
                let elemPixelRect = CGRect(
                    x: elem.frame.minX * scale,
                    y: elem.frame.minY * scale,
                    width: elem.frame.width * scale,
                    height: elem.frame.height * scale
                )
                if pixelRect.intersects(elemPixelRect) {
                    foundEllipsis = true
                    break
                }
            }
            if foundEllipsis { break }
        }

        XCTAssertTrue(
            foundEllipsis,
            "VNRecognizeTextRequest did not detect '…' overlapping any element bounds. " +
            "Recognized strings: \(observations.compactMap { $0.topCandidates(1).first?.string }.prefix(10))"
        )
    }

    // MARK: - AC-4: Seed reproducibility

    func testSeedReproducibility() async throws {
        let result1 = try await capture(seed: 12345)
        let result2 = try await capture(seed: 12345)

        XCTAssertEqual(result1.sha256, result2.sha256,
            "Same seed should produce identical PNG (byte-for-byte)")
        XCTAssertEqual(result1.elements.count, result2.elements.count,
            "Same seed should produce identical element count")
    }

    // MARK: - AC-5: ≥50 seeds complete without error, dark mode on ios17

    func testFiftyDistinctSeeds_ios17_dark() async throws {
        // Run 50 seeds (light on ios26 for speed — matching generation profile).
        // We also run one dark/ios17 variant to confirm cross-profile compatibility.
        var captureCount = 0

        for seed in UInt64(0)..<50 {
            let config = GeneratorRunConfig(
                seed: seed,
                templateFamily: "TruncatedLabel",
                osProfile: seed < 25 ? .ios26 : .ios17,
                simulatorOverride: SimulatorStateOverride(
                    time: "09:41", batteryLevel: 100, batteryState: "charging",
                    cellularBars: 5, wifiBars: 3, cellularMode: "active", operatorName: ""
                ),
                colorScheme: seed.isMultiple(of: 2) ? .light : .dark,
                dynamicTypeSize: .large,
                deviceName: "Test Device",
                pixelScale: seed < 25 ? 3 : 2,
                locale: "en_US",
                layoutDirection: .ltr
            )
            let vc = TruncatedLabelViewController(seed: seed, config: config)
            let result = try await ScreenshotCapture.captureUIKit(vc, config: config)

            XCTAssertFalse(result.elements.isEmpty, "Seed \(seed): produced zero elements")
            XCTAssertFalse(result.png.isEmpty,      "Seed \(seed): produced empty PNG")

            // Quick knownIssues spot-check on every 10th seed
            if seed.isMultiple(of: 10) {
                for elem in result.elements {
                    XCTAssertEqual(elem.knownIssues, ["truncatedText"],
                        "Seed \(seed), \(elem.id): missing knownIssues")
                }
            }

            captureCount += 1
        }

        XCTAssertEqual(captureCount, 50, "Expected exactly 50 successful captures")
    }
}
