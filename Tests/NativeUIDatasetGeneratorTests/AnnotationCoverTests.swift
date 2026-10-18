import Foundation
import Testing
@testable import NativeUIDatasetGenerator

/// ACTIONS417: a capture can mark content under chrome occluded or excluded. Nil keeps the historical rule.
struct AnnotationCoverTests: Sendable {
    private func elements(_ input: [AnnotatedElement]) -> [AnnotationJSON.Element] {
        let result = CaptureResult(png: Data(), sha256: String(repeating: "0", count: 64), elements: input,
            pixelSize: CGSize(width: 100, height: 200), pointSize: CGSize(width: 50, height: 100), scale: 2)
        let state = SimulatorStateOverride(time: "09:41", batteryLevel: 100, batteryState: "charging",
            cellularBars: 5, wifiBars: 3, cellularMode: "active", operatorName: "")
        let config = GeneratorRunConfig(seed: 1, templateFamily: "test", osProfile: .ios17, simulatorOverride: state,
            colorScheme: .light, dynamicTypeSize: .large, deviceName: "test", pixelScale: 2, locale: "en_US",
            layoutDirection: .ltr)
        return AnnotationWriter.buildJSON(result: result, config: config, imageFileName: "test.png",
            templateFamily: "test", generatorVersion: "test").elements.sorted { $0.id < $1.id }
    }

    @Test func defaultElementsKeepTheHistoricalRule() {
        let out = elements([AnnotatedElement(id: "label_a", elementType: "label", frame: CGRect(x: 5, y: 5, width: 10, height: 10))])
        #expect(!out[0].occluded)
        #expect(out[0].occlusionType == nil)
        #expect(!out[0].excluded)
        #expect(out[0].exclusionReason == nil)
    }

    @Test func measuredCoverIsWritten() {
        let out = elements([
            AnnotatedElement(id: "label_a", elementType: "label", frame: CGRect(x: 5, y: 5, width: 10, height: 10),
                             occlusionType: "scroll"),
            AnnotatedElement(id: "label_b", elementType: "label", frame: CGRect(x: 5, y: 30, width: 10, height: 10),
                             exclusionReason: "coveredByChrome"),
        ])
        #expect(out[0].occluded && out[0].occlusionType == "scroll" && !out[0].excluded)
        #expect(out[1].excluded && out[1].exclusionReason == "coveredByChrome")
    }

    @Test func imageBoundaryWinsOverMeasuredCover() {
        let out = elements([AnnotatedElement(id: "label_a", elementType: "label",
            frame: CGRect(x: -5, y: 5, width: 20, height: 10), occlusionType: "scroll")])
        #expect(out[0].occluded && out[0].occlusionType == "imageBoundary")
    }
}
