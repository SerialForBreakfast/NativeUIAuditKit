// IntegrationTests.swift
// NativeUIAuditKitTests

import CoreGraphics
import Foundation
import ImageIO
import Testing
@testable import NativeUIAuditKit

@Suite("Integration & NativeUIRecognizing")
struct IntegrationTests {

    @Test("No-op recognizer returns empty elements with .notRequested")
    func noOpRecognizerReturnsNotRequested() async throws {
        let recognizer = NativeUINoOpRecognizer()
        let dummyData = Data([0x89, 0x50, 0x4E, 0x47])
        let result = try await recognizer.recognizeNativeUI(
            inPNGData: dummyData,
            path: "/path/to/screenshot.png",
            sidecar: nil
        )

        #expect(result.elements.isEmpty)
        #expect(result.status == .notRequested)
    }

    @Test("Detector recognizer performs detection on valid PNG data")
    func detectorRecognizerRunsOnPNGData() async throws {
        let fixtureURL = Bundle.module.url(forResource: "kitchen_sink_screen", withExtension: "png")!
        let data = try Data(contentsOf: fixtureURL)

        let recognizer = NativeUIDetectorRecognizer(configuration: .init(minimumConfidence: 0.5))
        let result = try await recognizer.recognizeNativeUI(
            inPNGData: data,
            path: fixtureURL.path,
            sidecar: nil
        )

        #expect(result.status == .success)
        #expect(!result.elements.isEmpty)
        for elem in result.elements {
            #expect(elem.confidence >= 0.5)
        }
    }

    @Test("Detector recognizer safely handles corrupt image data")
    func detectorRecognizerHandlesCorruptData() async throws {
        let corruptData = Data("NotAnImage".utf8)
        let recognizer = NativeUIDetectorRecognizer()
        let result = try await recognizer.recognizeNativeUI(
            inPNGData: corruptData,
            path: "/path/to/corrupt.png",
            sidecar: nil
        )

        #expect(result.elements.isEmpty)
        #expect(result.status == .failed("Invalid or corrupt image data"))
    }

    @Test("NativeUIRecognitionStatus round-trips through Codable")
    func statusCodableRoundTrip() throws {
        let cases: [NativeUIRecognitionStatus] = [
            .success,
            .notRequested,
            .notAvailable,
            .failed("Model loading timed out")
        ]

        let encoder = JSONEncoder()
        let decoder = JSONDecoder()

        for original in cases {
            let data = try encoder.encode(original)
            let decoded = try decoder.decode(NativeUIRecognitionStatus.self, from: data)
            #expect(decoded == original)
        }
    }

    @Test("NativeUIObservations round-trips through Codable")
    func observationsCodableRoundTrip() throws {
        let obs = NativeUIElementObservation(
            id: UUID(),
            elementType: .primaryButton,
            boundingBox: NativeUIRect(x: 0.1, y: 0.8, width: 0.8, height: 0.1),
            boundingBoxPixels: NativeUIRect(x: 100, y: 800, width: 800, height: 100),
            confidence: 0.95,
            visibleText: "Submit",
            confidenceSource: .pixelModel
        )

        let original = NativeUIObservations(elements: [obs], status: .success)
        let encoder = JSONEncoder()
        let decoder = JSONDecoder()

        let data = try encoder.encode(original)
        let decoded = try decoder.decode(NativeUIObservations.self, from: data)

        #expect(decoded.status == .success)
        #expect(decoded.elements.count == 1)
        #expect(decoded.elements[0].elementType == .primaryButton)
        #expect(decoded.elements[0].visibleText == "Submit")
    }

    @Test("tvOS auto-routing performs detection and resolves active focus")
    func tvosDetectionAndFocusResolution() async throws {
        let fixtureURL = Bundle.module.url(forResource: "tvos_home_screen", withExtension: "png")!
        let data = try Data(contentsOf: fixtureURL)

        let recognizer = NativeUIDetectorRecognizer(configuration: .init(minimumConfidence: 0.35, platform: .auto))
        let result = try await recognizer.recognizeNativeUI(
            inPNGData: data,
            path: fixtureURL.path,
            sidecar: nil
        )

        #expect(result.status == .success)
        #expect(!result.elements.isEmpty)

        // Verify tvOS OS UI elements (e.g. collectionItem) are detected
        let collectionItems = result.elements.filter { $0.elementType == .collectionItem }
        #expect(!collectionItems.isEmpty)

        // Verify focus state: on tvOS, exactly one element should be identified as focused
        let focusedElements = result.elements.filter { $0.state.isFocused == true }
        #expect(focusedElements.count == 1)

        // Verify touch target rule was skipped (exempt on tvOS)
        let touchIssues = result.elements.flatMap { $0.issues }.filter { $0.kind == .tappableTargetTooSmall }
        #expect(touchIssues.isEmpty)
    }

    @Test("ModalityHealth and ModalityStatus round-trip through Codable")
    func modalityHealthCodableRoundTrip() throws {
        let statuses: [ModalityStatus] = [
            .available,
            .notRequested,
            .empty,
            .failed(reason: "Vision OCR crashed", domain: "com.apple.Vision", code: 1001),
            .failed(reason: "Unknown failure")
        ]

        let encoder = JSONEncoder()
        let decoder = JSONDecoder()

        for original in statuses {
            let data = try encoder.encode(original)
            let decoded = try decoder.decode(ModalityStatus.self, from: data)
            #expect(decoded == original)
            if case .failed(let reason, let domain, let code) = original {
                #expect(decoded.isFailed == true)
                #expect(decoded.failureReason == reason)
                if let domain = domain {
                    if case .failed(_, let decodedDomain, let decodedCode) = decoded {
                        #expect(decodedDomain == domain)
                        #expect(decodedCode == code)
                    }
                }
            }
        }

        let health = ModalityHealth(
            detector: .available,
            ocr: .failed(reason: "Timeout", domain: "com.apple.Vision", code: -1),
            focus: .available,
            audit: .empty
        )
        #expect(health.hasAnyFailure == true)

        let healthData = try encoder.encode(health)
        let decodedHealth = try decoder.decode(ModalityHealth.self, from: healthData)
        #expect(decodedHealth == health)
    }

    @Test("ModalityHealth reports all requested modalities as available on success")
    func modalityHealthReportsAvailableOnSuccess() async throws {
        let fixtureURL = Bundle.module.url(forResource: "kitchen_sink_screen", withExtension: "png")!
        let data = try Data(contentsOf: fixtureURL)

        let recognizer = NativeUIDetectorRecognizer(configuration: .init(minimumConfidence: 0.5))
        let result = try await recognizer.recognizeNativeUI(
            inPNGData: data,
            path: fixtureURL.path,
            sidecar: nil
        )

        #expect(result.status == .success)
        #expect(result.modalityHealth.detector == .available)
        #expect(result.modalityHealth.ocr == .available)
        #expect(result.modalityHealth.audit == .available)
        #expect(result.modalityHealth.focus == .notRequested) // iOS screen
        #expect(result.modalityHealth.hasAnyFailure == false)
    }

    @Test("ModalityHealth reports ocr as notRequested when text recognition is disabled")
    func modalityHealthReportsNotRequestedWhenDisabled() async throws {
        let fixtureURL = Bundle.module.url(forResource: "kitchen_sink_screen", withExtension: "png")!
        let data = try Data(contentsOf: fixtureURL)

        let config = NativeUIDetectionConfiguration(minimumConfidence: 0.5, includesTextRecognition: false)
        let recognizer = NativeUIDetectorRecognizer(configuration: config)
        let result = try await recognizer.recognizeNativeUI(
            inPNGData: data,
            path: fixtureURL.path,
            sidecar: nil
        )

        #expect(result.status == .success)
        #expect(result.modalityHealth.detector == .available)
        #expect(result.modalityHealth.ocr == .notRequested)
        #expect(result.modalityHealth.audit == .available)
    }

    @Test("ModalityHealth reports ocr as empty on a legitimately text-free image")
    func modalityHealthReportsEmptyForTextFreeImage() async throws {
        let blankData = makeSolidPNGData(width: 200, height: 200)

        let config = NativeUIDetectionConfiguration(minimumConfidence: 0.5, includesTextRecognition: true)
        let recognizer = NativeUIDetectorRecognizer(configuration: config)
        let result = try await recognizer.recognizeNativeUI(
            inPNGData: blankData,
            path: "/path/to/blank.png",
            sidecar: nil
        )

        #expect(result.status == .success)
        #expect(result.modalityHealth.ocr == .empty)
        #expect(result.modalityHealth.ocr.isFailed == false)
    }

    @Test("Permissive modality policy preserves detections and records honest OCR failure")
    func permissiveModalityPolicyPreservesDetectionsOnOCRFailure() async throws {
        let fixtureURL = Bundle.module.url(forResource: "kitchen_sink_screen", withExtension: "png")!
        let data = try Data(contentsOf: fixtureURL)

        let simulatedError = NSError(
            domain: "com.apple.Vision",
            code: 9999,
            userInfo: [NSLocalizedDescriptionKey: "Simulated Vision OCR crash"]
        )

        let config = NativeUIDetectionConfiguration(
            minimumConfidence: 0.5,
            includesTextRecognition: true,
            modalityPolicy: .permissive
        )
        let recognizer = NativeUIDetectorRecognizer(
            configuration: config,
            textRecognitionHandler: { _ in throw simulatedError }
        )

        let result = try await recognizer.recognizeNativeUI(
            inPNGData: data,
            path: fixtureURL.path,
            sidecar: nil
        )

        // Status is success because permissive allows partial results
        #expect(result.status == .success)
        // Detections are preserved
        #expect(!result.elements.isEmpty)
        // Modality health truthfully records the failure
        #expect(result.modalityHealth.ocr.isFailed == true)
        #expect(result.modalityHealth.ocr == .failed(reason: "Simulated Vision OCR crash", domain: "com.apple.Vision", code: 9999))
        #expect(result.modalityHealth.detector == .available)
    }

    @Test("Strict modality policy throws/fails request when OCR fails")
    func strictModalityPolicyFailsOnOCRFailure() async throws {
        let fixtureURL = Bundle.module.url(forResource: "kitchen_sink_screen", withExtension: "png")!
        let data = try Data(contentsOf: fixtureURL)

        let simulatedError = NSError(
            domain: "com.apple.Vision",
            code: 9999,
            userInfo: [NSLocalizedDescriptionKey: "Simulated Vision OCR crash"]
        )

        let config = NativeUIDetectionConfiguration(
            minimumConfidence: 0.5,
            includesTextRecognition: true,
            modalityPolicy: .strict
        )
        let recognizer = NativeUIDetectorRecognizer(
            configuration: config,
            textRecognitionHandler: { _ in throw simulatedError }
        )

        let result = try await recognizer.recognizeNativeUI(
            inPNGData: data,
            path: fixtureURL.path,
            sidecar: nil
        )

        // Overall status must report failure
        #expect(result.status == .failed("Modality 'ocr' failed: Simulated Vision OCR crash"))
        #expect(result.modalityHealth.ocr.isFailed == true)
        #expect(result.modalityHealth.hasAnyFailure == true)
    }

    private func makeSolidPNGData(width: Int = 100, height: Int = 100) -> Data {
        let colorSpace = CGColorSpaceCreateDeviceRGB()
        let context = CGContext(
            data: nil,
            width: width,
            height: height,
            bitsPerComponent: 8,
            bytesPerRow: width * 4,
            space: colorSpace,
            bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
        )!
        context.setFillColor(CGColor(red: 0.1, green: 0.1, blue: 0.1, alpha: 1.0))
        context.fill(CGRect(x: 0, y: 0, width: width, height: height))
        let cgImage = context.makeImage()!
        let data = NSMutableData()
        let dest = CGImageDestinationCreateWithData(data as CFMutableData, "public.png" as CFString, 1, nil)!
        CGImageDestinationAddImage(dest, cgImage, nil)
        CGImageDestinationFinalize(dest)
        return data as Data
    }
}
