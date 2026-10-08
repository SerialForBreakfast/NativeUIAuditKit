import Foundation
import CoreML
import Testing
import NativeUIAuditKitModels

@Test func standaloneResourcesMatchCurrentModels() async throws {
    #expect(try NativeUIModelAsset.requiredManifest(forTVOS: false).modelId == "nativeui-ios-v2.0")
    #expect(try NativeUIModelAsset.requiredManifest(forTVOS: true).modelId == "nativeui-tvos-v3.0")
    #expect(NativeUIModelAsset.focusRingDetectorURL != nil)
    let configuration = NativeUIModelAsset.makeConfiguration(computeUnits: .cpuOnly)
    let ios = try await NativeUIModelAsset.loadModel(configuration: configuration)
    let tvos = try await NativeUIModelAsset.loadTVOSModel(configuration: configuration)
    let focus = try await NativeUIModelAsset.loadFocusRingDetector(configuration: configuration)
    #expect(!ios.modelDescription.inputDescriptionsByName.isEmpty)
    #expect(!tvos.modelDescription.outputDescriptionsByName.isEmpty)
    #expect(focus != nil)
}
