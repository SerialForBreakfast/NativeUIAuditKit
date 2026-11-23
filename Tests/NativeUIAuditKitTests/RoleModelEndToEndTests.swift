import CoreGraphics
import CoreML
import Foundation
import ImageIO
import Testing
import NativeUIAuditKitModels
import NativeUIAuditKit
@testable import NativeUIAuditKitRuntime

/// Opt-in end-to-end run of a taxonomy 1.2 role detector through `performDetailed` and the comparative selector.
/// Set NUIAK_ROLE_E2E_FIXTURE to the JSON from `reports/work/TRAIN666/h3-arm-s/swift_role_e2e.py`.
/// It writes `<fixture>.swift-result.json`. Skipped when the variable is unset, so default runs stay offline and data-free.
struct RoleModelEndToEndTests {
    struct Fixture: Decodable {
        struct Detector: Decodable { let name: String; let compiledModel: String; let classes: [String] }
        struct Case: Decodable { let id: String; let image: String }
        let comparativeDirectory: String
        let gateThreshold: Double
        let confidence: Double
        let nmsIoU: Double
        let detectors: [Detector]
        let cases: [Case]
    }

    struct Provider: NativeUIModelProviding {
        let preloaded: PreloadedModel
        var allowsHeuristicFocusFallback: Bool { false }
        func loadDetector(for platform: NativeUIPlatform) async throws -> PreloadedModel { preloaded }
        func focusModelURL() throws -> URL? { nil }
        func detectorCacheIdentity(for platform: NativeUIPlatform) throws -> String? { nil }
    }

    static func roleManifest(_ classes: [String]) throws -> ModelManifest {
        ModelManifest(modelId: "role-e2e", expectedOutputs: [.init(name: "confidence", dimensions: [-1, classes.count])],
            tensorChannelMapping: classes.map { .taxonomyClass($0) }, taxonomyProfile: ModelTaxonomyBinding.profile,
            taxonomyVersion: "1.2", categoryMapSHA256: try ModelTaxonomyBinding.identity(version: "1.2"))
    }

    static func image(_ path: String) throws -> CGImage {
        let source = try #require(CGImageSourceCreateWithURL(URL(fileURLWithPath: path) as CFURL, nil))
        return try #require(CGImageSourceCreateImageAtIndex(source, 0, nil))
    }

    @Test(.enabled(if: ProcessInfo.processInfo.environment["NUIAK_ROLE_E2E_FIXTURE"] != nil))
    func roleDetectorRunsEndToEndWithComparativeSelector() async throws {
        let path = try #require(ProcessInfo.processInfo.environment["NUIAK_ROLE_E2E_FIXTURE"])
        let fixture = try JSONDecoder().decode(Fixture.self, from: Data(contentsOf: URL(fileURLWithPath: path)))
        var runs: [[String: Any]] = []
        for detector in fixture.detectors {
            let model = try MLModel(contentsOf: URL(fileURLWithPath: detector.compiledModel))
            let metadata = ModelMetadata(modelId: detector.name, architecture: "YOLO11n", inputWidth: 640, inputHeight: 640,
                classLabels: detector.classes, defaultConfidenceThreshold: Float(fixture.confidence),
                recommendedNMSIoUThreshold: Float(fixture.nmsIoU), mAP50: 0)
            let provider = Provider(preloaded: PreloadedModel(model: model, metadata: metadata, manifest: try Self.roleManifest(detector.classes)))
            for nested in [false, true] {
                let config = NativeUIDetectionConfiguration(minimumConfidence: fixture.confidence, includesTextRecognition: false,
                    platform: .tvOS, comparativeFocusDirectory: URL(fileURLWithPath: fixture.comparativeDirectory),
                    comparativeFocusGateThreshold: fixture.gateThreshold, comparativeFocusDropsNestedCandidates: nested)
                let request = NativeUIDetectionRequest(modelProvider: provider, configuration: config)
                var cases: [String: Any] = [:]
                for item in fixture.cases {
                    let result = try await request.performDetailed(on: try Self.image(item.image))
                    let boxes: (NativeUIElementObservation) -> [Double] = {
                        [$0.boundingBoxPixels.x, $0.boundingBoxPixels.y, $0.boundingBoxPixels.width, $0.boundingBoxPixels.height]
                    }
                    let focused = result.elements.filter { $0.state.isFocused == true }
                    #expect(focused.count <= 1)
                    cases[item.id] = [
                        "detections": result.elements.map { ["cls": $0.elementType.rawValue, "box": boxes($0), "conf": $0.confidence] as [String: Any] },
                        "focusBox": focused.first.map(boxes) as Any? ?? NSNull(),
                        "policy": result.focusExecution?.policy ?? "none",
                        "nestedRemoved": result.focusExecution?.candidates.filter { $0.disposition == .nestedCandidateRemoved }.count ?? 0,
                    ]
                }
                runs.append(["detector": detector.name, "nested": nested, "cases": cases])
            }
        }
        try JSONSerialization.data(withJSONObject: ["runs": runs], options: [.sortedKeys])
            .write(to: URL(fileURLWithPath: path + ".swift-result.json"))
    }
}
