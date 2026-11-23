import CoreGraphics
import Foundation
import Testing
import NativeUIAuditKitModels
import NativeUIAuditKit
@testable import NativeUIAuditKitRuntime

/// Taxonomy 1.2 role types through the actual detector label conversion and focus candidate set.
struct RoleTaxonomyCallerTests {
    private let d1Labels = ["button", "cell", "picture", "textField", "toggle", "segmentedControl", "pageControl", "bar", "dialog", "indicator"]

    private func roleManifest() throws -> ModelManifest {
        ModelManifest(modelId: "role-model", expectedOutputs: [.init(name: "confidence", dimensions: [-1, d1Labels.count])],
            tensorChannelMapping: d1Labels.map { .taxonomyClass($0) }, taxonomyProfile: ModelTaxonomyBinding.profile,
            taxonomyVersion: "1.2", categoryMapSHA256: try ModelTaxonomyBinding.identity(version: "1.2"))
    }

    @Test func roleLabelsConvertOnlyUnderExplicit12Binding() throws {
        let strict = try roleManifest()
        for label in d1Labels {
            #expect(NativeUIDetectionRequest.modelElementType(for: label, manifest: strict)?.rawValue == label)
        }
        let legacy = ModelManifest(modelId: "custom", tensorChannelMapping: d1Labels.map { .taxonomyClass($0) })
        for label in ["button", "cell", "picture", "bar", "dialog", "indicator"] {
            #expect(NativeUIDetectionRequest.modelElementType(for: label, manifest: legacy) == nil)
        }
        #expect(NativeUIDetectionRequest.modelElementType(for: "toggle", manifest: legacy) == .toggle)
    }

    @Test func enumRolesMatchTheContractList() throws {
        let roles = ModelTaxonomyBinding.roleLabels.compactMap(NativeUIElementType.init(rawValue:))
        #expect(roles.count == ModelTaxonomyBinding.roleLabels.count)
        // Every 1.2 label has a case, so no explicitly bound label is silently dropped.
        for label in try ModelTaxonomyBinding.labels(version: "1.2") {
            #expect(NativeUIElementType(rawValue: label) != nil)
        }
        for role in roles {
            #expect(try JSONDecoder().decode(NativeUIElementType.self, from: JSONEncoder().encode(role)) == role)
        }
    }

    @Test func focusCandidatesMatchTvbenchRoleModelFocusability() {
        // tvbench SWIFT_FOCUSABLE_ROLES for a role model: adjustable, bar, button, cell, segmentedControl, textField, toggle.
        let expected: Set<NativeUIElementType> = [.adjustable, .bar, .button, .cell, .segmentedControl, .textField, .toggle]
        let d1Types = Set(d1Labels.compactMap(NativeUIElementType.init(rawValue:)) + [.adjustable])
        #expect(d1Types.intersection(FocusRingClassifier.focusableTypes) == expected)
    }

    @Test func comparativeSelectorSeesCellAndButtonCandidates() {
        let boxes: [(NativeUIElementType, CGRect)] = [
            (.cell, CGRect(x: 0.1, y: 0.1, width: 0.4, height: 0.1)),
            (.button, CGRect(x: 0.1, y: 0.3, width: 0.2, height: 0.1)),
            (.picture, CGRect(x: 0.6, y: 0.1, width: 0.3, height: 0.3)),
        ]
        let focusable = boxes.filter { FocusRingClassifier.focusableTypes.contains($0.0) }
        #expect(focusable.map(\.0) == [.cell, .button])
    }

    @Test func auditRuleSetsIncludeRolesWhereEveryCoveredTypeIsIncluded() {
        #expect(AuditRules.interactiveControlClasses.contains(.button))
        #expect(AuditRules.edgeChromeClasses.contains(.bar))
        for role: NativeUIElementType in [.bar, .cell, .dialog, .container] {
            #expect(AuditRules.containerClasses.contains(role))
        }
        for role: NativeUIElementType in [.picture, .adjustable, .indicator] {
            #expect(!AuditRules.interactiveControlClasses.contains(role))
            #expect(!AuditRules.containerClasses.contains(role))
        }
    }
}
