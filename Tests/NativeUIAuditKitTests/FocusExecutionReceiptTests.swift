import CoreGraphics
import CoreML
import Foundation
import ImageIO
import NativeUIAuditKitModels
import Testing
@testable import NativeUIAuditKit

struct FocusExecutionReceiptTests: Sendable {
    private func image() throws -> CGImage {
        let ctx = try #require(CGContext(data: nil, width: 64, height: 64, bitsPerComponent: 8,
            bytesPerRow: 256, space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue))
        return try #require(ctx.makeImage())
    }
    private func observation(_ type: NativeUIElementType = .primaryButton, width: Double = 20) -> NativeUIElementObservation {
        NativeUIElementObservation(elementType: type,
            boundingBox: .init(x: 0.1, y: 0.1, width: 0.3, height: 0.3),
            boundingBoxPixels: .init(x: 10, y: 10, width: width, height: 20), confidence: 0.9,
            confidenceSource: .pixelModel)
    }
    private func result(_ probability: Float) -> FocusRingClassifier.Result {
        .init(isFocusedProbability: probability, confidence: abs(probability - 0.5) * 2,
              isFocused: probability >= 0.85, isAmbiguous: probability >= 0.7 && probability < 0.85)
    }

    @Test func mixedScoringAccountsForEveryCandidate() throws {
        let observations = [observation(), observation(), observation(width: 0), observation(.label)]
        var calls = 0
        let (resolved, receipt) = NativeUIDetectionRequest.resolveTVOSFocusWithEvidence(in: try image(),
            observations: observations, threshold: 0.85, ambiguityThreshold: 0.7) { _ in
                calls += 1
                if calls == 2 { throw CocoaError(.fileReadUnknown) }
                return result(0.95)
            }
        #expect(calls == 2)
        #expect(receipt.candidates.map(\.observationID) == observations.map(\.id))
        #expect(receipt.candidates.map(\.disposition) == [.scored, .predictionFailed, .cropRejected, .unsupportedRole])
        #expect(receipt.attemptedPredictions == 2 && receipt.successfulPredictions == 1)
        #expect(!receipt.modelScoringComplete && receipt.modelDigest == nil)
        #expect(resolved[0].state.isFocused == true)
        #expect(resolved[1].state == observations[1].state)
        #expect(try JSONDecoder().decode(FocusExecutionReceipt.self, from: JSONEncoder().encode(receipt)) == receipt)
    }

    @Test func invalidScoresEmptyAndUnsupportedNeverBecomeComplete() throws {
        for p: Float in [.nan, .infinity, -0.1, 1.1] {
            let (_, receipt) = NativeUIDetectionRequest.resolveTVOSFocusWithEvidence(in: try image(),
                observations: [observation()], threshold: 0.85, ambiguityThreshold: 0.7) { _ in result(p) }
            #expect(receipt.successfulPredictions == 0 && !receipt.modelScoringComplete)
            #expect(receipt.candidates[0].disposition == .predictionFailed)
        }
        let (_, invalidConfidence) = NativeUIDetectionRequest.resolveTVOSFocusWithEvidence(in: try image(),
            observations: [observation()], threshold: 0.85, ambiguityThreshold: 0.7) { _ in
                .init(isFocusedProbability: 0.95, confidence: .nan, isFocused: true, isAmbiguous: false)
            }
        #expect(invalidConfidence.failedPredictions == 1 && !invalidConfidence.modelScoringComplete)
        for input in [[], [observation(.label)]] {
            let (_, receipt) = NativeUIDetectionRequest.resolveTVOSFocusWithEvidence(in: try image(),
                observations: input, threshold: 0.85, ambiguityThreshold: 0.7) { _ in
                    Issue.record("Unsupported candidate reached scorer"); return result(0.9)
                }
            #expect(receipt.attemptedPredictions == 0 && !receipt.modelScoringComplete)
        }
    }

    @Test func wireCountsAndTamperedEvidence() throws {
        let (_, receipt) = NativeUIDetectionRequest.resolveTVOSFocusWithEvidence(in: try image(),
            observations: [observation()], threshold: 0.85, ambiguityThreshold: 0.7) { _ in result(0.95) }
        let object = try #require(JSONSerialization.jsonObject(with: JSONEncoder().encode(receipt)) as? [String: Any])
        #expect(object["attemptedPredictions"] as? Int == 1)
        #expect(object["successfulPredictions"] as? Int == 1)
        #expect(object["failedPredictions"] as? Int == 0)
        #expect(object["modelScoringComplete"] as? Bool == true)
        for (key, value): (String, Any) in [("version", 2), ("attemptedPredictions", 9),
            ("successfulPredictions", 0), ("failedPredictions", 1), ("modelScoringComplete", false),
            ("backend", "heuristic")] {
            var changed = object; changed[key] = value
            let bytes = try JSONSerialization.data(withJSONObject: changed)
            #expect(throws: (any Error).self) { try JSONDecoder().decode(FocusExecutionReceipt.self, from: bytes) }
        }
        var changed = object
        let candidates = try #require(object["candidates"] as? [[String: Any]])
        changed["candidates"] = candidates + candidates
        changed["attemptedPredictions"] = 2; changed["successfulPredictions"] = 2
        let duplicateBytes = try JSONSerialization.data(withJSONObject: changed)
        #expect(throws: (any Error).self) { try JSONDecoder().decode(FocusExecutionReceipt.self, from: duplicateBytes) }
        for probability: Any in [-0.1, 1.1, NSNull()] {
            var bad = candidates[0]; bad["probability"] = probability
            changed = object; changed["candidates"] = [bad]
            let bytes = try JSONSerialization.data(withJSONObject: changed)
            #expect(throws: (any Error).self) { try JSONDecoder().decode(FocusExecutionReceipt.self, from: bytes) }
        }
    }

    @Test func successfulSelectionAmbiguityAndTiesRemainStable() throws {
        for probabilities: [Float] in [[0.95, 0.8, 0.2], [0.8, 0.75, 0.2], [0.95, 0.95, 0.2]] {
            var i = 0
            let (observations, receipt) = NativeUIDetectionRequest.resolveTVOSFocusWithEvidence(in: try image(),
                observations: [observation(), observation(), observation()], threshold: 0.85, ambiguityThreshold: 0.7) { _ in
                    defer { i += 1 }; return result(probabilities[i])
                }
            #expect(receipt.modelScoringComplete)
            #expect(receipt.successfulPredictions == 3)
            #expect(observations.filter { $0.state.isFocused == true }.count == (probabilities[0] >= 0.85 ? 1 : 0))
            #expect(observations[2].state.isFocused == false)
            #expect(observations[1].state.isAmbiguousFocus == (probabilities[1] < 0.85))
        }
    }

    @Test func oldResultsDecodeWithoutEvidence() throws {
        let legacy = NativeUIDetailedDetectionResult(elements: [], modalityHealth: .default)
        var object = try #require(JSONSerialization.jsonObject(with: JSONEncoder().encode(legacy)) as? [String: Any])
        object.removeValue(forKey: "focusExecution")
        let decoded = try JSONDecoder().decode(NativeUIDetailedDetectionResult.self,
            from: JSONSerialization.data(withJSONObject: object))
        #expect(decoded.focusExecution == nil)
        let oldRecognizer = NativeUIObservations(elements: [], status: .success)
        var oldObject = try #require(JSONSerialization.jsonObject(with: JSONEncoder().encode(oldRecognizer)) as? [String: Any])
        oldObject.removeValue(forKey: "focusExecution")
        #expect(try JSONDecoder().decode(NativeUIObservations.self,
            from: JSONSerialization.data(withJSONObject: oldObject)).focusExecution == nil)
    }

    @Test func invalidThresholdDoesNotInvokeModelOrEncodeNaN() throws {
        let (_, receipt) = NativeUIDetectionRequest.resolveTVOSFocusWithEvidence(in: try image(),
            observations: [observation()], threshold: .nan, ambiguityThreshold: 0.7) { _ in
                Issue.record("Invalid policy invoked inference"); return result(0.9)
            }
        #expect(receipt.backend == .unavailable && receipt.attemptedPredictions == 0)
        #expect(receipt.candidates[0].disposition == .policyRejected)
        #expect(try JSONDecoder().decode(FocusExecutionReceipt.self, from: JSONEncoder().encode(receipt)) == receipt)
    }

    @Test func artifactDigestDetectsChangesAndRejectsSymlinks() throws {
        let root = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
            .appendingPathComponent(".build/focus-identity-" + UUID().uuidString)
        try FileManager.default.createDirectory(at: root, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: root) }
        #expect(throws: (any Error).self) { try FocusModelIdentity.digest(root) }
        let file = root.appendingPathComponent("weights")
        try Data([1, 2, 3]).write(to: file)
        let first = try FocusModelIdentity.digest(root)
        let repeated = try FocusModelIdentity.digest(root)
        #expect(first.count == 64 && first == repeated)
        try Data([1, 2, 4]).write(to: file)
        #expect(first != (try FocusModelIdentity.digest(root)))
        try FileManager.default.createSymbolicLink(at: root.appendingPathComponent("alias"), withDestinationURL: file)
        #expect(throws: (any Error).self) { try FocusModelIdentity.digest(root) }
    }

    @Test func missingAndInvalidOptionalModelReportFallbackReason() async throws {
        let missing = await NativeUIDetectionRequest.loadFocusClassifierWithEvidence(url: nil)
        #expect(missing.classifier == nil && missing.fallbackReason == "model_missing")
        let bad = await NativeUIDetectionRequest.loadFocusClassifierWithEvidence(url: URL(fileURLWithPath: #filePath))
        #expect(bad.classifier == nil && bad.fallbackReason == "model_load_failed")
    }

    @Test func realRequestAndSessionCarryBackendAndCachedIdentity() async throws {
        let url = try #require(Bundle.module.url(forResource: "tvos_home_screen", withExtension: "png"))
        let source = try #require(CGImageSourceCreateWithURL(url as CFURL, nil))
        let screenshot = try #require(CGImageSourceCreateImageAtIndex(source, 0, nil))
        let config = NativeUIDetectionConfiguration(minimumConfidence: 0.35, includesTextRecognition: false, platform: .tvOS)
        let session = NativeUIDetectionSession(configuration: config)
        let first = try await session.performDetailed(on: screenshot)
        let second = try await session.performDetailed(on: screenshot)
        let evidence = try #require(first.focusExecution)
        #expect(evidence.backend == .coreML)
        #expect(evidence.modelDigest?.count == 64)
        #expect(evidence.modelDigest == second.focusExecution?.modelDigest)
        #expect(evidence.candidates.count == first.elements.count)
        await session.clearCache()
        let third = try await session.performDetailed(on: screenshot)
        #expect(evidence.modelDigest == third.focusExecution?.modelDigest)
        var disabled = config; disabled.useFocusClassifier = false
        let fallback = try await NativeUIDetectionRequest(configuration: disabled).performDetailed(on: screenshot)
        #expect(fallback.focusExecution?.backend == .heuristic)
        #expect(fallback.focusExecution?.fallbackReason == "disabled")
        #expect(fallback.focusExecution?.modelDigest == nil)
        #expect(fallback.focusExecution?.modelScoringComplete == false)
        let custom = try #require(await NativeUIDetectionRequest.loadFocusClassifierIfAvailable())
        let unidentified = FocusRingClassifier(model: custom.model)
        let result = try await NativeUIDetectionRequest(configuration: config).performDetailed(on: screenshot,
            preloadedFocusClassifier: unidentified)
        #expect(result.focusExecution?.backend == .coreML && result.focusExecution?.modelDigest == nil)
        for reason in ["model_missing", "model_load_failed"] {
            let fallback = try await NativeUIDetectionRequest(configuration: config).performDetailed(on: screenshot,
                preloadedFocusLoad: FocusClassifierLoad(classifier: nil, fallbackReason: reason))
            #expect(fallback.focusExecution?.backend == .heuristic)
            #expect(fallback.focusExecution?.fallbackReason == reason)
        }
        let wrapper = try await session.recognizeNativeUI(inPNGData: Data(contentsOf: url), path: "fixture", sidecar: nil)
        #expect(wrapper.focusExecution?.modelDigest == evidence.modelDigest)
        let iosURL = try #require(Bundle.module.url(forResource: "kitchen_sink_screen", withExtension: "png"))
        let iosSource = try #require(CGImageSourceCreateWithURL(iosURL as CFURL, nil))
        let iosImage = try #require(CGImageSourceCreateImageAtIndex(iosSource, 0, nil))
        var ios = config; ios.platform = .iOS
        let iosResult = try await NativeUIDetectionRequest(configuration: ios).performDetailed(on: iosImage)
        #expect(iosResult.focusExecution?.backend == .notRequested)
        #expect(iosResult.focusExecution?.attemptedPredictions == 0)
    }
}
