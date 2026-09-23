import Foundation
import Testing
@testable import NativeUIDatasetGenerator

struct AnnotationStateTests: Sendable {
    private func document(_ schema: AnnotationWriter.Schema, enabled: Bool?, selected: Bool?) throws -> AnnotationJSON {
        let element = AnnotatedElement(id: "button", elementType: "primaryButton",
            frame: CGRect(x: -2, y: 10, width: 20, height: 10),
            isEnabled: enabled, isSelected: selected)
        let result = CaptureResult(png: Data(), sha256: String(repeating: "0", count: 64),
            elements: [element], pixelSize: CGSize(width: 100, height: 200),
            pointSize: CGSize(width: 50, height: 100), scale: 2)
        let state = SimulatorStateOverride(time: "09:41", batteryLevel: 100,
            batteryState: "charging", cellularBars: 5, wifiBars: 3,
            cellularMode: "active", operatorName: "")
        let config = GeneratorRunConfig(seed: 1, templateFamily: "test", osProfile: .ios17,
            simulatorOverride: state, colorScheme: .dark, dynamicTypeSize: .medium,
            deviceName: "test", pixelScale: 2, locale: "en_US", layoutDirection: .ltr)
        let root = URL(fileURLWithPath: #filePath).deletingLastPathComponent()
            .deletingLastPathComponent().deletingLastPathComponent()
        let directory = root.appendingPathComponent(".build/annotation-state-tests")
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        let output = directory.appendingPathComponent(UUID().uuidString + ".json")
        try AnnotationWriter.write(result: result, config: config,
            imageFileName: "test.png", templateFamily: "test", generatorVersion: "test",
            to: output, schema: schema)
        return try JSONDecoder().decode(AnnotationJSON.self, from: Data(contentsOf: output))
    }

    @Test func measuredTrueFalseUnknownRoundtrip() throws {
        for enabled: Bool? in [nil, false, true] {
            for selected: Bool? in [nil, false, true] {
                let original = try document(.measuredState, enabled: enabled, selected: selected)
                let data = try JSONEncoder().encode(original)
                let decoded = try JSONDecoder().decode(AnnotationJSON.self, from: data)
                #expect(decoded.schemaVersion == "1.2")
                #expect(decoded.elements[0].state.isEnabled == enabled)
                #expect(decoded.elements[0].state.isSelected == selected)
                #expect(decoded.elements[0].occluded)
                // Native boxes retain offscreen geometry; only Vision boxes intersect image.
                #expect(decoded.elements[0].boundsPixels.x == -4)
                #expect(decoded.elements[0].boundsVisionNormalized.x == 0)
                let object = try #require(JSONSerialization.jsonObject(with: data) as? [String: Any])
                let elements = try #require(object["elements"] as? [[String: Any]])
                let state = try #require(elements[0]["state"] as? [String: Any])
                #expect(state.keys.contains("isEnabled"))
                #expect(state.keys.contains("isSelected"))
                if enabled == nil { #expect(state["isEnabled"] is NSNull) }
                if selected == nil { #expect(state["isSelected"] is NSNull) }
            }
        }
    }

    @Test func legacyRemainsFrozenEvenWithMeasuredValues() throws {
        let legacy = try document(.legacy, enabled: false, selected: true)
        #expect(legacy.schemaVersion == "1.0")
        #expect(legacy.elements[0].state.isEnabled == true)
        #expect(legacy.elements[0].state.isSelected == false)
        let data = try JSONEncoder().encode(legacy)
        #expect(try JSONDecoder().decode(AnnotationJSON.self, from: data).elements[0].state.isEnabled == true)
    }

    @Test func missingRequiredStateIsNotUnknown() throws {
        #expect(throws: DecodingError.self) {
            try JSONDecoder().decode(AnnotationJSON.ElementState.self,
                from: Data("{\"isSelected\":false}".utf8))
        }
    }
}
