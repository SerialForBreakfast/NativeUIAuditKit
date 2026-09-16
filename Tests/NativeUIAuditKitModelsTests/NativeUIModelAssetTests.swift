// NativeUIModelAssetTests.swift
// NativeUIAuditKitModelsTests
//
// Smoke tests confirming the bundled model resource actually resolves and loads for any
// consumer of this package — this is the guarantee ViewLens and other consumers depend on.

import CoreML
import XCTest
@testable import NativeUIAuditKitModels

final class NativeUIModelAssetTests: XCTestCase {

    func testDefaultModelURLResolves() throws {
        let url = NativeUIModelAsset.defaultModelURL
        XCTAssertTrue(FileManager.default.fileExists(atPath: url.path),
            "Bundled model resource not found at \(url.path)")
    }

    func testModelLoads() async throws {
        let model = try await NativeUIModelAsset.loadModel()
        XCTAssertNotNil(model)
    }

    func testMetadataMatchesModel() {
        let metadata = NativeUIModelAsset.metadata
        XCTAssertEqual(metadata.classLabels.count, 5)
        XCTAssertEqual(metadata.inputWidth, 640)
        XCTAssertEqual(metadata.inputHeight, 640)
        XCTAssertEqual(metadata.classLabels,
            ["alert", "navigationBar", "primaryButton", "textField", "toggle"])
    }

    func testTVOSModelURLResolves() throws {
        let url = NativeUIModelAsset.tvOSModelURL
        XCTAssertTrue(FileManager.default.fileExists(atPath: url.path),
            "Bundled tvOS model resource not found at \(url.path)")
    }

    func testTVOSModelLoads() async throws {
        let model = try await NativeUIModelAsset.loadTVOSModel()
        XCTAssertNotNil(model)
    }

    func testTVOSMetadataMatchesModel() {
        let metadata = NativeUIModelAsset.tvOSMetadata
        XCTAssertEqual(metadata.classLabels.count, 41)
        XCTAssertEqual(metadata.inputWidth, 640)
        XCTAssertEqual(metadata.inputHeight, 640)
        XCTAssertEqual(metadata.classLabels[4], "collectionItem")
        XCTAssertEqual(metadata.classLabels[12], "label")
        XCTAssertEqual(metadata.classLabels[34], "tabBar")
        XCTAssertEqual(metadata.mAP50, 0.9950)

        // The descriptor lists the 10 classes with actual training instances
        XCTAssertEqual(ModelRegistry.tvOS.trainedClasses.count, 10)
    }

    func testLoadModelWithDescriptor() async throws {
        let tvOSModel = try await NativeUIModelAsset.loadModel(descriptor: ModelRegistry.tvOS)
        XCTAssertNotNil(tvOSModel)

        let iOSModel = try await NativeUIModelAsset.loadModel(descriptor: ModelRegistry.iOS)
        XCTAssertNotNil(iOSModel)
    }

    func testManifestsLoadAndValidate() {
        let tvOS = NativeUIModelAsset.tvOSManifest
        XCTAssertEqual(tvOS.modelId, "nativeui-tvos-v1.0")
        XCTAssertEqual(tvOS.inputWidth, 640)
        XCTAssertEqual(tvOS.inputHeight, 640)
        XCTAssertEqual(tvOS.tensorChannelMapping.count, 80)
        XCTAssertEqual(tvOS.label(forChannel: 4), "collectionItem")
        XCTAssertEqual(tvOS.label(forChannel: 12), "label")
        XCTAssertEqual(tvOS.label(forChannel: 34), "tabBar")
        XCTAssertNil(tvOS.label(forChannel: 41), "Channel 41 should be padding and have nil label")
        XCTAssertEqual(tvOS.activeClassChannels.count, 41)

        let iOS = NativeUIModelAsset.iOSManifest
        XCTAssertEqual(iOS.modelId, "nativeui-ios-v2.0")
        XCTAssertEqual(iOS.inputWidth, 640)
        XCTAssertEqual(iOS.inputHeight, 640)
        XCTAssertEqual(iOS.tensorChannelMapping.count, 80)
        XCTAssertEqual(iOS.activeClassChannels.count, 5)
        XCTAssertEqual(iOS.label(forChannel: 0), "alert")
        XCTAssertEqual(iOS.label(forChannel: 2), "primaryButton")
        XCTAssertNil(iOS.label(forChannel: 5), "Channel 5 should be padding and have nil label")
    }

    func testModelManifestValidationPassesForBundledModels() async throws {
        let tvOSModel = try await NativeUIModelAsset.loadTVOSModel()
        XCTAssertNoThrow(try ModelManifestValidator.validate(model: tvOSModel, against: NativeUIModelAsset.tvOSManifest))

        let iOSModel = try await NativeUIModelAsset.loadModel()
        XCTAssertNoThrow(try ModelManifestValidator.validate(model: iOSModel, against: NativeUIModelAsset.iOSManifest))
    }

    func testModelManifestValidationRejectsMismatchedContract() async throws {
        let tvOSModel = try await NativeUIModelAsset.loadTVOSModel()

        // Manifest expecting 99 channels instead of 80
        var mismatchedChannels = NativeUIModelAsset.tvOSManifest.tensorChannelMapping
        mismatchedChannels.append(.padding)
        let mismatchedManifest = ModelManifest(
            modelId: "mismatched-model",
            architecture: "YOLO11n",
            expectedOutputs: [
                ModelTensorShapeContract(name: "confidence", dimensions: [-1, 81]),
                ModelTensorShapeContract(name: "coordinates", dimensions: [-1, 4])
            ],
            tensorChannelMapping: mismatchedChannels
        )

        XCTAssertThrowsError(try ModelManifestValidator.validate(model: tvOSModel, against: mismatchedManifest)) { error in
            guard let contractError = error as? ModelContractError else {
                XCTFail("Expected ModelContractError, got \(error)")
                return
            }
            XCTAssertTrue(contractError.reason.contains("mismatch") || contractError.reason.contains("does not match"),
                          "Expected mismatch reason, got \(contractError.reason)")
        }

        // Manifest expecting nonexistent output
        let missingOutputManifest = ModelManifest(
            modelId: "missing-output",
            architecture: "YOLO11n",
            expectedOutputs: [
                ModelTensorShapeContract(name: "nonexistent_tensor", dimensions: [-1, 4])
            ],
            tensorChannelMapping: []
        )

        XCTAssertThrowsError(try ModelManifestValidator.validate(model: tvOSModel, against: missingOutputManifest)) { error in
            XCTAssertTrue(error is ModelContractError)
        }
    }

    func testModelMetadataLicenseDisclosure() async throws {
        let expectedLicense = "AGPL-3.0 License (https://ultralytics.com/license)"

        let iosModel = try await NativeUIModelAsset.loadModel()
        let iosLicense = iosModel.modelDescription.metadata[.license] as? String
        XCTAssertEqual(iosLicense, expectedLicense, "iOS model metadata must declare AGPL-3.0 License with URL")

        let tvOSModel = try await NativeUIModelAsset.loadTVOSModel()
        let tvOSLicense = tvOSModel.modelDescription.metadata[.license] as? String
        XCTAssertEqual(tvOSLicense, expectedLicense, "tvOS model metadata must declare AGPL-3.0 License with URL")
    }
}
