import Foundation
import Testing
@testable import NativeUIDatasetGenerator

struct VisualProbeCatalogTests: Sendable {
    @Test func allRequiredIntersectionsPerFamily() {
        let catalog = VisualProbeCatalog.make(contentSeed: 7)
        #expect(catalog.planningOnly)
        #expect(catalog.partition == "development")
        #expect(catalog.maximumCaptureBatch == 48)
        #expect(catalog.cases.count == 144)
        #expect(Set(catalog.cases.map(\.id)).count == 144)
        let groups = Dictionary(grouping: catalog.cases, by: \.group)
        #expect(groups.count == 3)
        for rows in groups.values {
            #expect(rows.count == 48)
            #expect(Set(rows.map { "\($0.config.colorScheme.rawValue)/\($0.profile)" }).count == 4)
            let fixedType = rows[0].config.templateFamily == "DynamicTypeOverflow"
            #expect(Set(rows.map { "\($0.config.colorScheme.rawValue)/\($0.config.dynamicTypeSize.rawValue)" }).count == (fixedType ? 2 : 12))
            if fixedType {
                #expect(rows.allSatisfy { $0.config.dynamicTypeSize == .accessibilityExtraExtraExtraLarge })
            }
            #expect(Set(rows.map { "\($0.config.simulatorOverride.time)/\($0.config.simulatorOverride.batteryLevel)" }).count == 25)
            #expect(Set(rows.map { "\($0.config.simulatorOverride.cellularBars)/\($0.config.simulatorOverride.wifiBars)" }).count == 12)
            #expect(Set(rows.map { "\($0.config.simulatorOverride.batteryLevel)/\($0.config.simulatorOverride.batteryState)" }).count == 10)
            #expect(Set(rows.map { "\($0.config.colorScheme.rawValue)/\($0.config.simulatorOverride.batteryState)" }).count == 4)
            #expect(rows.allSatisfy { $0.config.seed == 7 && $0.config.locale == "en_US" })
        }
    }

    @Test func deterministicRoundtripAndSeedIsolation() throws {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.sortedKeys]
        let a = try encoder.encode(VisualProbeCatalog.make(contentSeed: .max))
        #expect(a == (try encoder.encode(VisualProbeCatalog.make(contentSeed: .max))))
        let decoded = try JSONDecoder().decode(VisualProbeCatalog.self, from: a)
        #expect(try encoder.encode(decoded) == a)
        #expect(Set(decoded.cases.map(\.group)).isDisjoint(with:
            Set(VisualProbeCatalog.make(contentSeed: 0).cases.map(\.group))))
        // A different seed is a recipe identity, NOT proof of independent source lineage.
        #expect(decoded.partition == "development")
    }

    @Test func validationRejectsTamperingAndUnboundedSelections() throws {
        let plan = VisualProbeCatalog.make(contentSeed: 19)
        let ids = Array(plan.cases.prefix(48).map(\.id))
        #expect(try plan.validatedBatch(ids: ids).count == 48)
        for bad in [[], ["unknown"], [ids[0], ids[0]], Array(plan.cases.prefix(49).map(\.id))] {
            #expect(throws: VisualProbeCatalog.ValidationError.self) { try plan.validatedBatch(ids: bad) }
        }
        let data = try JSONEncoder().encode(plan)
        #expect(try VisualProbeCatalog.decodeFrozen(data).validatedBatch(ids: ids).count == 48)
        var value = try #require(JSONSerialization.jsonObject(with: data) as? [String: Any])
        value["extra"] = "ignored-by-Codable-is-not-allowed"
        #expect(throws: VisualProbeCatalog.ValidationError.self) {
            try VisualProbeCatalog.decodeFrozen(JSONSerialization.data(withJSONObject: value))
        }
        value.removeValue(forKey: "extra")
        value["partition"] = "test"
        let modified = try JSONDecoder().decode(VisualProbeCatalog.self,
            from: JSONSerialization.data(withJSONObject: value))
        #expect(throws: VisualProbeCatalog.ValidationError.self) { try modified.validatedBatch(ids: ids) }
        value["partition"] = "development"
        var cases = try #require(value["cases"] as? [[String: Any]])
        var config = try #require(cases[0]["config"] as? [String: Any])
        config["seed"] = 20
        cases[0]["config"] = config
        value["cases"] = cases
        let changedConfig = try JSONDecoder().decode(VisualProbeCatalog.self,
            from: JSONSerialization.data(withJSONObject: value))
        #expect(throws: VisualProbeCatalog.ValidationError.self) { try changedConfig.validatedBatch(ids: ids) }
    }
}
