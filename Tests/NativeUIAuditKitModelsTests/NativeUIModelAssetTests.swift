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
}
