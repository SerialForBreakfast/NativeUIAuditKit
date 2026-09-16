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
        #expect(focusedElements[0].state.focusConfidence != nil)
        #expect(focusedElements[0].state.focusConfidence! >= 0.5)
        #expect(focusedElements[0].state.focusScore != nil)
        #expect(focusedElements[0].state.isAmbiguousFocus == false)

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

    @Test("tvOS focus abstains when multiple candidates compete within score margin")
    func tvosFocusAbstainsOnAmbiguousCandidates() {
        // Create an image with two adjacent list rows with almost identical high luminance (0.85 vs 0.82)
        let img = makeImage(width: 400, height: 200) { ctx in
            // Row 1
            ctx.setFillColor(CGColor(red: 0.85, green: 0.85, blue: 0.85, alpha: 1.0))
            ctx.fill(CGRect(x: 20, y: 20, width: 360, height: 60))
            // Row 2
            ctx.setFillColor(CGColor(red: 0.82, green: 0.82, blue: 0.82, alpha: 1.0))
            ctx.fill(CGRect(x: 20, y: 100, width: 360, height: 60))
        }

        let obs1 = NativeUIElementObservation(
            id: UUID(),
            elementType: .listRow,
            boundingBox: NativeUIRect(x: 0.05, y: 0.1, width: 0.9, height: 0.3),
            boundingBoxPixels: NativeUIRect(x: 20, y: 20, width: 360, height: 60),
            confidence: 0.95,
            confidenceSource: .pixelModel
        )
        let obs2 = NativeUIElementObservation(
            id: UUID(),
            elementType: .listRow,
            boundingBox: NativeUIRect(x: 0.05, y: 0.5, width: 0.9, height: 0.3),
            boundingBoxPixels: NativeUIRect(x: 20, y: 100, width: 360, height: 60),
            confidence: 0.95,
            confidenceSource: .pixelModel
        )

        let resolved = NativeUIDetectionRequest.resolveTVOSFocus(
            in: img,
            observations: [obs1, obs2],
            minScoreThreshold: 0.35,
            minMargin: 0.12
        )

        // Neither element should claim isFocused == true because margin < 0.12
        for elem in resolved {
            #expect(elem.state.isFocused == nil, "Ambiguous focus must abstain and leave isFocused nil")
            #expect(elem.state.isAmbiguousFocus == true, "Competing candidates within margin must have isAmbiguousFocus == true")
            #expect(elem.state.focusScore != nil)
            #expect(elem.state.focusConfidence != nil)
        }
    }

    @Test("tvOS focus abstains when all candidates score below threshold")
    func tvosFocusAbstainsOnLowScore() {
        // Create an image with dark rows (luminance ~ 0.10 < 0.35)
        let img = makeImage(width: 400, height: 200) { ctx in
            ctx.setFillColor(CGColor(red: 0.10, green: 0.10, blue: 0.10, alpha: 1.0))
            ctx.fill(CGRect(x: 20, y: 20, width: 360, height: 60))
            ctx.fill(CGRect(x: 20, y: 100, width: 360, height: 60))
        }

        let obs1 = NativeUIElementObservation(
            id: UUID(),
            elementType: .listRow,
            boundingBox: NativeUIRect(x: 0.05, y: 0.1, width: 0.9, height: 0.3),
            boundingBoxPixels: NativeUIRect(x: 20, y: 20, width: 360, height: 60),
            confidence: 0.95,
            confidenceSource: .pixelModel
        )
        let obs2 = NativeUIElementObservation(
            id: UUID(),
            elementType: .listRow,
            boundingBox: NativeUIRect(x: 0.05, y: 0.5, width: 0.9, height: 0.3),
            boundingBoxPixels: NativeUIRect(x: 20, y: 100, width: 360, height: 60),
            confidence: 0.95,
            confidenceSource: .pixelModel
        )

        let resolved = NativeUIDetectionRequest.resolveTVOSFocus(
            in: img,
            observations: [obs1, obs2],
            minScoreThreshold: 0.35,
            minMargin: 0.12
        )

        for elem in resolved {
            #expect(elem.state.isFocused == nil)
            #expect(elem.state.isAmbiguousFocus == false)
            #expect(elem.state.focusConfidence == 0.0)
        }
    }

    @Test("tvOS focus asserts confident winner on clear margin")
    func tvosFocusAssertsConfidentWinnerOnClearMargin() {
        // Create an image with one solid white focused row (0.95) and one dark unfocused row (0.15)
        let img = makeImage(width: 400, height: 200) { ctx in
            // Focused row
            ctx.setFillColor(CGColor(red: 0.95, green: 0.95, blue: 0.95, alpha: 1.0))
            ctx.fill(CGRect(x: 20, y: 20, width: 360, height: 60))
            // Unfocused row
            ctx.setFillColor(CGColor(red: 0.15, green: 0.15, blue: 0.15, alpha: 1.0))
            ctx.fill(CGRect(x: 20, y: 100, width: 360, height: 60))
        }

        let obsWinner = NativeUIElementObservation(
            id: UUID(),
            elementType: .listRow,
            boundingBox: NativeUIRect(x: 0.05, y: 0.1, width: 0.9, height: 0.3),
            boundingBoxPixels: NativeUIRect(x: 20, y: 20, width: 360, height: 60),
            confidence: 0.95,
            confidenceSource: .pixelModel
        )
        let obsRunnerUp = NativeUIElementObservation(
            id: UUID(),
            elementType: .listRow,
            boundingBox: NativeUIRect(x: 0.05, y: 0.5, width: 0.9, height: 0.3),
            boundingBoxPixels: NativeUIRect(x: 20, y: 100, width: 360, height: 60),
            confidence: 0.95,
            confidenceSource: .pixelModel
        )

        let resolved = NativeUIDetectionRequest.resolveTVOSFocus(
            in: img,
            observations: [obsWinner, obsRunnerUp],
            minScoreThreshold: 0.35,
            minMargin: 0.12
        )

        let winner = resolved.first(where: { $0.id == obsWinner.id })!
        let runnerUp = resolved.first(where: { $0.id == obsRunnerUp.id })!

        #expect(winner.state.isFocused == true)
        #expect(winner.state.focusConfidence != nil && winner.state.focusConfidence! >= 0.80)
        #expect(winner.state.isAmbiguousFocus == false)

        #expect(runnerUp.state.isFocused == false)
        #expect(runnerUp.state.focusConfidence == 0.0)
        #expect(runnerUp.state.isAmbiguousFocus == false)
    }

    @Test("tvOS peer-relative geometry heuristic rewards expanded collection items")
    func tvosPeerRelativeGeometryRewardsExpandedItem() {
        // Three collection items in the same row (y: 50).
        // Item 1 is expanded (width: 230, height: 230, area: 52900).
        // Items 2 & 3 are unexpanded (width: 200, height: 200, area: 40000).
        // Median peer area is 40000; Item 1 scale ratio is 1.32x (~1.15x per dimension).
        let img = makeImage(width: 800, height: 350) { ctx in
            // Draw dark background
            ctx.setFillColor(CGColor(red: 0.05, green: 0.05, blue: 0.05, alpha: 1.0))
            ctx.fill(CGRect(x: 0, y: 0, width: 800, height: 350))

            // Draw Item 1 with bright white border outline
            ctx.setStrokeColor(CGColor(red: 1.0, green: 1.0, blue: 1.0, alpha: 1.0))
            ctx.setLineWidth(6.0)
            ctx.stroke(CGRect(x: 20, y: 50, width: 230, height: 230))

            // Draw Item 2 with thin faint border
            ctx.setStrokeColor(CGColor(red: 0.3, green: 0.3, blue: 0.3, alpha: 1.0))
            ctx.setLineWidth(2.0)
            ctx.stroke(CGRect(x: 280, y: 65, width: 200, height: 200))

            // Draw Item 3 with thin faint border
            ctx.stroke(CGRect(x: 510, y: 65, width: 200, height: 200))
        }

        let obsExpanded = NativeUIElementObservation(
            id: UUID(),
            elementType: .collectionItem,
            boundingBox: NativeUIRect(x: 0.025, y: 0.14, width: 0.287, height: 0.657),
            boundingBoxPixels: NativeUIRect(x: 20, y: 50, width: 230, height: 230),
            confidence: 0.95,
            confidenceSource: .pixelModel
        )
        let obsPeer1 = NativeUIElementObservation(
            id: UUID(),
            elementType: .collectionItem,
            boundingBox: NativeUIRect(x: 0.35, y: 0.185, width: 0.25, height: 0.57),
            boundingBoxPixels: NativeUIRect(x: 280, y: 65, width: 200, height: 200),
            confidence: 0.95,
            confidenceSource: .pixelModel
        )
        let obsPeer2 = NativeUIElementObservation(
            id: UUID(),
            elementType: .collectionItem,
            boundingBox: NativeUIRect(x: 0.637, y: 0.185, width: 0.25, height: 0.57),
            boundingBoxPixels: NativeUIRect(x: 510, y: 65, width: 200, height: 200),
            confidence: 0.95,
            confidenceSource: .pixelModel
        )

        let resolved = NativeUIDetectionRequest.resolveTVOSFocus(
            in: img,
            observations: [obsExpanded, obsPeer1, obsPeer2],
            minScoreThreshold: 0.35,
            minMargin: 0.12
        )

        let winner = resolved.first(where: { $0.id == obsExpanded.id })!
        #expect(winner.state.isFocused == true)
        #expect(winner.state.focusConfidence != nil && winner.state.focusConfidence! > 0.6)
        #expect(winner.state.isAmbiguousFocus == false)
    }

    private func makeImage(width: Int, height: Int, drawing: (CGContext) -> Void) -> CGImage {
        let colorSpace = CGColorSpaceCreateDeviceRGB()
        let ctx = CGContext(
            data: nil,
            width: width,
            height: height,
            bitsPerComponent: 8,
            bytesPerRow: width * 4,
            space: colorSpace,
            bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
        )!
        // Flip context vertically so drawing (0, 0) is at top-left, matching CGImage pixel coordinates
        ctx.translateBy(x: 0, y: CGFloat(height))
        ctx.scaleBy(x: 1.0, y: -1.0)
        drawing(ctx)
        return ctx.makeImage()!
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
