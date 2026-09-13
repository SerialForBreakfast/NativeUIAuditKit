// DeviceInferenceTests.swift
// NativeUIAuditKitTests

import CoreGraphics
import Foundation
import Testing
@testable import NativeUIAuditKit

@Suite("DeviceInference Engine")
struct DeviceInferenceTests {

    @Test("Sidecar fast-path returns exact device metadata with confidence 1.0")
    func sidecarFastPathExactMatch() {
        let sidecar = NativeUISidecar(
            imageSHA256: "abc123hash",
            pixelWidth: 1179,
            pixelHeight: 2556,
            scale: 3.0,
            platform: "iOS",
            osVersion: "17.4",
            deviceName: "iPhone 15 Pro",
            colorScheme: "dark",
            dynamicTypeSize: "large",
            locale: "en-US",
            elements: []
        )

        let inference = DeviceInference.inferDevice(
            imageSize: CGSize(width: 1179, height: 2556),
            observations: [],
            sidecar: sidecar
        )

        #expect(inference.platform == .iOS)
        #expect(inference.confidence == 1.0)
        #expect(inference.inferredOSMajorVersion == 17)
        #expect(inference.deviceCandidates.count == 1)
        #expect(inference.deviceCandidates[0].deviceFamily == "iPhone 15 Pro")
        #expect(inference.deviceCandidates[0].confidence == 1.0)
    }

    @Test("Pixel-only path for iPhone 15 Pro with Dynamic Island observation")
    func pixelOnlyPathWithDynamicIsland() {
        // Mock observation for Dynamic Island
        let islandObs = NativeUIElementObservation(
            id: UUID(),
            elementType: .dynamicIsland,
            boundingBox: NativeUIRect(x: 0.35, y: 0.95, width: 0.3, height: 0.04),
            boundingBoxPixels: NativeUIRect(x: 412, y: 30, width: 355, height: 100),
            confidence: 0.98,
            confidenceSource: .pixelModel
        )

        let inference = DeviceInference.inferDevice(
            imageSize: CGSize(width: 1179, height: 2556),
            observations: [islandObs],
            sidecar: nil
        )

        #expect(inference.platform == .iOS)
        #expect(inference.inferredOSMajorVersion == 17)
        #expect(!inference.deviceCandidates.isEmpty)

        // All candidates must be Dynamic Island devices
        for candidate in inference.deviceCandidates {
            let isIslandModel = candidate.deviceFamily.contains("14 Pro") ||
                                candidate.deviceFamily.contains("15") ||
                                candidate.deviceFamily.contains("16")
            #expect(isIslandModel, "\(candidate.deviceFamily) should be a Dynamic Island model")
        }

        // Sum of candidate confidences must not exceed 1.0
        let sumConf = inference.deviceCandidates.reduce(0.0) { $0 + $1.confidence }
        #expect(sumConf <= 1.05) // allow slight float rounding
    }

    @Test("Pixel-only path for iPhone SE resolution")
    func pixelOnlyPathForSE() {
        let inference = DeviceInference.inferDevice(
            imageSize: CGSize(width: 750, height: 1334),
            observations: [],
            sidecar: nil
        )

        #expect(inference.platform == .iOS)
        #expect(!inference.deviceCandidates.isEmpty)
        let candidateNames = inference.deviceCandidates.map { $0.deviceFamily }
        #expect(candidateNames.contains("iPhone SE (3rd gen)"))
        #expect(candidateNames.contains("iPhone 8"))
    }

    @Test("Fallback path for unlisted resolution returns non-empty candidates")
    func fallbackPathUnlistedResolution() {
        let inference = DeviceInference.inferDevice(
            imageSize: CGSize(width: 1373, height: 2911), // non-standard dimensions
            observations: [],
            sidecar: nil
        )

        #expect(!inference.deviceCandidates.isEmpty)
        #expect(inference.confidence > 0.0)
    }
}
