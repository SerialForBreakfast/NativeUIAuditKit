import Foundation
import Testing
@testable import NativeUIAuditKitModels

struct TaxonomyBindingTests {
    private func manifest(strict: Bool = false, version: String = "1.1") throws -> ModelManifest {
        let labels = strict ? try ModelTaxonomyBinding.labels(version: version) : ["alert", "badge", "unsupported"]
        return ModelManifest(modelId: "custom-valid-id", expectedOutputs: [
            .init(name: "confidence", dimensions: [-1, labels.count + 1])
        ], tensorChannelMapping: labels.map { .taxonomyClass($0) } + [.padding],
            taxonomyProfile: strict ? ModelTaxonomyBinding.profile : nil,
            taxonomyVersion: strict ? version : nil,
            categoryMapSHA256: strict ? try ModelTaxonomyBinding.identity(version: version) : nil)
    }
    private func object(_ manifest: ModelManifest) throws -> [String: Any] {
        try #require(JSONSerialization.jsonObject(with: JSONEncoder().encode(manifest)) as? [String: Any])
    }
    private func decode(_ object: [String: Any]) throws -> ModelManifest {
        try JSONDecoder().decode(ModelManifest.self, from: JSONSerialization.data(withJSONObject: object))
    }
    @Test func legacyDefaultsCustomIDsAndRoundtripStayCompatible() throws {
        let m = try manifest()
        let decoded = try JSONDecoder().decode(ModelManifest.self, from: JSONEncoder().encode(m))
        #expect(decoded == m)
        #expect(decoded.taxonomyProfile == nil)
        #expect(decoded.label(forChannel: 1) == "badge") // Public mapping unchanged.
        #expect(decoded.permitsObservationLabel("alert"))
        #expect(!decoded.permitsObservationLabel("badge"))
        #expect(!decoded.permitsObservationLabel("unsupported"))
        let raw = try object(m)
        #expect(raw["taxonomyProfile"] == nil)
        var unknown = raw
        unknown["tensorChannelMapping"] = [["type": "future-kind", "label": "badge"]]
        #expect(try decode(unknown).tensorChannelMapping == [.padding])
    }
    @Test func explicit42And41PaddingPreserveOrderAndRoundtrip() throws {
        for version in ["1.0", "1.1"] {
            let m = try manifest(strict: true, version: version)
            try m.validateTaxonomyBinding()
            #expect(try JSONDecoder().decode(ModelManifest.self, from: JSONEncoder().encode(m)) == m)
            #expect(m.label(forChannel: 0) == "actionSheet")
            #expect(m.label(forChannel: m.tensorChannelMapping.count - 1) == nil)
            #expect(m.permitsObservationLabel("badge") == (version == "1.1"))
            if version == "1.1" { #expect(m.label(forChannel: 41) == "badge") }
        }
    }
    @Test func explicitSubsetsAndPaddingDoNotClaimFullTaxonomyCoverage() throws {
        for version in ["1.0", "1.1"] {
            var raw = try object(manifest(strict: true, version: version))
            raw["tensorChannelMapping"] = [["type": "padding"], ["type": "class", "label": "alert"]]
            raw["expectedOutputs"] = [["name": "confidence", "dimensions": [-1, 2], "dataType": "Float32"]]
            let subset = try decode(raw)
            #expect(subset.activeClassChannels.count == 1)
            #expect(subset.label(forChannel: 0) == nil)
            #expect(subset.label(forChannel: 1) == "alert")
            for mapping in [[["type": "padding"], ["type": "padding"]],
                            [["type": "class", "label": "alert"], ["type": "class", "label": "alert"]]] {
                raw["tensorChannelMapping"] = mapping
                #expect(throws: (any Error).self) { try decode(raw) }
            }
        }
    }

    @Test func malformedExplicitBindingNeverDowngrades() throws {
        let original = try object(manifest(strict: true))
        for (key, value) in [("taxonomyProfile", "unknown"), ("taxonomyProfile", ""),
                             ("taxonomyVersion", "9.0"), ("categoryMapSHA256", "wrong")] {
            var bad = original; bad[key] = value
            #expect(throws: (any Error).self) { try decode(bad) }
        }
        for key in ["taxonomyVersion", "categoryMapSHA256"] {
            var bad = original; bad.removeValue(forKey: key)
            #expect(throws: (any Error).self) { try decode(bad) }
        }
        for kind in ["unknown-kind", "padding"] {
            var bad = original; bad["tensorChannelMapping"] = [["type": kind, "label": "badge"]]
            #expect(throws: (any Error).self) { try decode(bad) }
        }
        var label = original; label["tensorChannelMapping"] = [["type": "class", "label": "unsupported"]]
        #expect(throws: (any Error).self) { try decode(label) }
        var shape = original; shape["expectedOutputs"] = [["name": "confidence", "dimensions": [-1, 99], "dataType": "Float32"]]
        #expect(throws: (any Error).self) { try decode(shape) }
    }
}
