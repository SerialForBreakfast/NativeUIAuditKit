import Foundation
import NativeUIAuditKitRuntime
import Testing

// TTR supplies a verified installation and trusted decoded contract.
// This adapter uses only the public API from cc72583.
struct TTRReviewContract: Decodable {
    let schemaVersion: Int
    let preprocessing: String
    let manifest: ModelManifest
    let metadata: ModelMetadata

    func provider(compiledURL: URL, expectedCompiledDigest: String) throws -> NativeUILocalModelProvider {
        guard schemaVersion == 1, preprocessing == "yolo-letterbox-v1",
              manifest.modelId == "nativeui-tvos-v3.0" else {
            throw NativeUIModelAvailabilityError.unsupportedPreprocessing
        }
        let detector = try NativeUILocalDetector(url: compiledURL, expectedDigest: expectedCompiledDigest,
            manifest: manifest, metadata: metadata, preprocessing: preprocessing)
        return try NativeUILocalModelProvider(tvOS: detector, allowsHeuristicFocusFallback: false)
    }
}

@Test func reviewAdapterSupportsMissingModels() throws {
    let provider = try NativeUILocalModelProvider()
    #expect(try provider.focusModelURL() == nil)
    // The provider API remains available without any installed model.
    let _: any NativeUIModelProviding = provider
}
