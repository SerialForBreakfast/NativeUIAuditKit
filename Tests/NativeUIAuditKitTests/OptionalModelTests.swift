import CoreGraphics
import Foundation
import ImageIO
import NativeUIAuditKit
import NativeUIAuditKitModels
import Testing
@testable import NativeUIAuditKitRuntime

@Suite("Optional local models", .serialized)
struct OptionalModelTests {
    @Test func missingModelsRemainUnavailable() async throws {
        let provider = try NativeUILocalModelProvider()
        let session = NativeUIDetectionSession(modelProvider: provider)
        await #expect(throws: NativeUIModelAvailabilityError.unavailable("tvOS detector")) {
            try await session.warm(platforms: [.tvOS])
        }
        #expect(await session.isWarmed(for: .tvOS) == false)
        #expect(try provider.focusModelURL() == nil)
    }

    @Test func rejectWrongDigestAndPreprocessing() throws {
        let url = try NativeUIModelAsset.requiredModelURL(forTVOS: false)
        let manifest = try NativeUIModelAsset.requiredManifest(forTVOS: false)
        #expect(throws: NativeUIModelAvailabilityError.changedArtifact) {
            try NativeUILocalDetector(url: url, expectedDigest: String(repeating: "0", count: 64),
                manifest: manifest, metadata: NativeUIModelAsset.metadata)
        }
        #expect(throws: NativeUIModelAvailabilityError.unsupportedPreprocessing) {
            try NativeUILocalDetector(url: url, expectedDigest: "", manifest: manifest,
                metadata: NativeUIModelAsset.metadata, preprocessing: "scale-fill")
        }
        #expect(throws: ModelContractError.self) {
            try NativeUILocalDetector(url: url, expectedDigest: NativeUILocalDetector.digest(at: url),
                manifest: manifest, metadata: NativeUIModelAsset.tvOSMetadata)
        }
    }

    @Test func localAndBundledDetectorsUseIdenticalInference() async throws {
        for tv in [false, true] {
            let url = try NativeUIModelAsset.requiredModelURL(forTVOS: tv)
            let detector = try NativeUILocalDetector(url: url, expectedDigest: NativeUILocalDetector.digest(at: url),
                manifest: NativeUIModelAsset.requiredManifest(forTVOS: tv),
                metadata: tv ? NativeUIModelAsset.tvOSMetadata : NativeUIModelAsset.metadata)
            let focus = NativeUIModelAsset.focusRingDetectorURL
            let provider = try NativeUILocalModelProvider(iOS: tv ? nil : detector, tvOS: tv ? detector : nil,
                focusURL: focus, focusDigest: focus.map { try NativeUILocalDetector.digest(at: $0) })
            let configuration = NativeUIDetectionConfiguration(includesTextRecognition: false, platform: tv ? .tvOS : .iOS)
            let fixture = try #require(Bundle.module.url(forResource: tv ? "tvos_home_screen" : "kitchen_sink_screen", withExtension: "png"))
            let source = try #require(CGImageSourceCreateWithURL(fixture as CFURL, nil))
            let image = try #require(CGImageSourceCreateImageAtIndex(source, 0, nil))
            let bundled = try await NativeUIDetectionRequest(configuration: configuration).performDetailed(on: image)
            let session = NativeUIDetectionSession(modelProvider: provider, configuration: configuration)
            let local = try await session.performDetailed(on: image)
            #expect(!local.elements.isEmpty)
            #expect(local.elements.count == bundled.elements.count)
            for (a, b) in zip(local.elements, bundled.elements) {
                #expect(a.elementType == b.elementType)
                #expect(a.boundingBoxPixels == b.boundingBoxPixels)
                #expect(abs(a.confidence - b.confidence) < 0.000001)
                #expect(a.state.isFocused == b.state.isFocused)
            }
            #expect(await session.isWarmed(for: tv ? .tvOS : .iOS))
            await session.clearCache()
            #expect(await session.isWarmed(for: tv ? .tvOS : .iOS) == false)
        }
    }

    @Test func missingFocusDoesNotSilentlyUseHeuristics() async throws {
        let url = try NativeUIModelAsset.requiredModelURL(forTVOS: true)
        let detector = try NativeUILocalDetector(url: url, expectedDigest: NativeUILocalDetector.digest(at: url),
            manifest: NativeUIModelAsset.requiredManifest(forTVOS: true), metadata: NativeUIModelAsset.tvOSMetadata)
        let fixture = try #require(Bundle.module.url(forResource: "tvos_home_screen", withExtension: "png"))
        let source = try #require(CGImageSourceCreateWithURL(fixture as CFURL, nil))
        let image = try #require(CGImageSourceCreateImageAtIndex(source, 0, nil))
        for fallback in [false, true] {
            let provider = try NativeUILocalModelProvider(tvOS: detector, allowsHeuristicFocusFallback: fallback)
            let result = try await NativeUIDetectionRequest(modelProvider: provider,
                configuration: .init(includesTextRecognition: false, platform: .tvOS)).performDetailed(on: image)
            #expect(result.focusExecution?.backend == (fallback ? .heuristic : .unavailable))
            #expect(result.focusExecution?.attemptedPredictions == 0)
            let receipt = try #require(result.focusExecution)
            #expect(try JSONDecoder().decode(FocusExecutionReceipt.self, from: JSONEncoder().encode(receipt)) == receipt)
            if !fallback { #expect(result.elements.allSatisfy { $0.state.isFocused == nil }) }
        }
        #expect(throws: ModelContractError.self) { try NativeUILocalModelProvider(iOS: detector) }
    }

    @Test func changedModelFailsBeforeCoreMLLoad() async throws {
        let project = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
        let root = project.appendingPathComponent(".build/model-identity-tests/" + UUID().uuidString)
        try FileManager.default.createDirectory(at: root, withIntermediateDirectories: true)
        let path = root.appendingPathComponent("fake.bin")
        try Data([1]).write(to: path)
        let detector = try NativeUILocalDetector(url: root, expectedDigest: NativeUILocalDetector.digest(at: root),
            manifest: NativeUIModelAsset.requiredManifest(forTVOS: true), metadata: NativeUIModelAsset.tvOSMetadata)
        let provider = try NativeUILocalModelProvider(tvOS: detector)
        try Data([2]).write(to: path)
        await #expect(throws: NativeUIModelAvailabilityError.changedArtifact) { try await provider.loadDetector(for: .tvOS) }
    }

    @Test func detectorRejectsWrongInputAndOutputRank() async throws {
        let model = try await NativeUIModelAsset.loadTVOSModel()
        let base = try NativeUIModelAsset.requiredManifest(forTVOS: true)
        for inputSize in [320, 640] {
            let manifest = ModelManifest(modelId: base.modelId, inputWidth: inputSize, inputHeight: inputSize,
                expectedInputs: base.expectedInputs,
                expectedOutputs: [.init(name: "coordinates", dimensions: [4])],
                tensorChannelMapping: base.tensorChannelMapping)
            #expect(throws: ModelContractError.self) { try ModelManifestValidator.validate(model: model, against: manifest) }
        }
    }
}
