import Foundation
import Testing
@testable import NativeUIAuditKitModels

struct RecoverableManifestTests: Sendable {
    @Test func requiredManifestErrorsAreRecoverableAndPathFree() throws {
        #expect(throws: (any Error).self) { try NativeUIModelAsset.readRequiredManifest(at: nil) }
        do {
            _ = try NativeUIModelAsset.readRequiredManifest(at: URL(fileURLWithPath: #filePath))
            Issue.record("Swift source is not a valid model manifest")
        } catch {
            #expect(!error.localizedDescription.contains(#filePath))
        }
        _ = try NativeUIModelAsset.requiredManifest(forTVOS: true)
        _ = try NativeUIModelAsset.requiredManifest(forTVOS: false)
        #expect(try NativeUIModelAsset.requiredModelURL(forTVOS: true).pathExtension == "mlmodelc")
    }
}
