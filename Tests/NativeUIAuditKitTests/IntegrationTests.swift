// IntegrationTests.swift
// NativeUIAuditKitTests

import CoreGraphics
import Foundation
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
}
