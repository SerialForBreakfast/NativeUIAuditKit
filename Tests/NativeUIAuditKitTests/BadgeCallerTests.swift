import Foundation
import Testing
import NativeUIAuditKitModels
import NativeUIAuditKit
@testable import NativeUIAuditKitRuntime

struct BadgeCallerTests {
    @Test func actualDetectorLabelConversionKeepsLegacyBoundary() throws {
        let legacy = ModelManifest(modelId: "custom", tensorChannelMapping: [.taxonomyClass("badge")])
        #expect(NativeUIDetectionRequest.modelElementType(for: "badge", manifest: legacy) == nil)
        #expect(NativeUIDetectionRequest.modelElementType(for: "alert", manifest: legacy) == .alert)
        #expect(NativeUIDetectionRequest.modelElementType(for: "new-unknown", manifest: legacy) == nil)
        let strict = ModelManifest(modelId: "custom-badge", expectedOutputs: [.init(name: "confidence", dimensions: [-1, 42])],
            tensorChannelMapping: try ModelTaxonomyBinding.labels(version: "1.1").map { .taxonomyClass($0) },
            taxonomyProfile: ModelTaxonomyBinding.profile, taxonomyVersion: "1.1",
            categoryMapSHA256: try ModelTaxonomyBinding.identity(version: "1.1"))
        try strict.validateTaxonomyBinding()
        #expect(NativeUIDetectionRequest.modelElementType(for: "badge", manifest: strict) == .badge)
        #expect(try JSONDecoder().decode(NativeUIElementType.self, from: JSONEncoder().encode(NativeUIElementType.badge)) == .badge)
    }
}
