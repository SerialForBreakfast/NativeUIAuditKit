import Foundation

/// Additive opt-in model mapping contract. Legacy decoding remains tolerant.
public enum ModelTaxonomyBinding {
    public static let profile = "nativeui-category-binding-v1"
    public static let legacyLabels: [String] = [
        "actionSheet",
        "activityIndicator",
        "alert",
        "cancelAction",
        "collectionItem",
        "colorWell",
        "contextMenu",
        "destructiveButton",
        "disclosureGroup",
        "dynamicIsland",
        "homeIndicator",
        "imageView",
        "label",
        "link",
        "listRow",
        "mapView",
        "menuButton",
        "navigationBar",
        "pageControl",
        "picker",
        "popover",
        "primaryButton",
        "progressView",
        "refreshControl",
        "scrollIndicator",
        "searchField",
        "secondaryButton",
        "secureField",
        "segmentedControl",
        "sheet",
        "sidebar",
        "slider",
        "statusBar",
        "stepperControl",
        "tabBar",
        "textField",
        "toggle",
        "toolbar",
        "tooltip",
        "unknown",
        "webContent"
    ]
    public static func labels(version: String) throws -> [String] {
        switch version {
        case "1.0": return legacyLabels
        case "1.1": return legacyLabels + ["badge"]
        default: throw ModelContractError("Unsupported explicit taxonomy version")
        }
    }
    public static func identity(version: String) throws -> String {
        switch version {
        case "1.0": return "dfc38ffe3b9ee3434f9523e5ca91a6a700fbe32a00249c5cf90cf89885a30660"
        case "1.1": return "4debce8e33bd10aade0c7b7a1c1f625c6c5db8db5af542faffc9d4ab4187beef"
        default: throw ModelContractError("Unsupported explicit taxonomy version")
        }
    }
}

extension ModelManifest {
    /// Validates metadata identity, not the loaded model's artifact bytes or quality.
    public func validateTaxonomyBinding() throws {
        guard let profile = taxonomyProfile else { return }
        guard profile == ModelTaxonomyBinding.profile,
              let version = taxonomyVersion, let identity = categoryMapSHA256 else {
            throw ModelContractError("Unknown explicit profile or missing taxonomy binding")
        }
        guard identity == (try ModelTaxonomyBinding.identity(version: version)) else {
            throw ModelContractError("Explicit category map identity mismatch")
        }
        let allowed = Set(try ModelTaxonomyBinding.labels(version: version))
        let active = activeClassChannels.map { $0.label }
        guard !active.isEmpty, Set(active).count == active.count,
              active.allSatisfy({ allowed.contains($0) }) else {
            throw ModelContractError("Unknown or duplicate explicit class labels")
        }
        guard let confidence = expectedOutputs.first(where: { $0.name == "confidence" }),
              confidence.dimensions.count == 2,
              confidence.dimensions[1] == tensorChannelMapping.count else {
            throw ModelContractError("Explicit confidence shape/map mismatch")
        }
    }

    /// Keep legacy supported labels frozen even when the public enum grows.
    public func permitsObservationLabel(_ label: String) -> Bool {
        guard taxonomyProfile != nil else { return ModelTaxonomyBinding.legacyLabels.contains(label) }
        do { try validateTaxonomyBinding() } catch { return false }
        guard let version = taxonomyVersion,
              let labels = try? ModelTaxonomyBinding.labels(version: version) else { return false }
        return labels.contains(label)
    }
}
