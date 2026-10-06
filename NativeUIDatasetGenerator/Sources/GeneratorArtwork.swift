import Foundation
import CoreGraphics
import CryptoKit
import ImageIO

/// Frozen development campaign. No runtime calls or file writes in planning.
struct GeneratorArtworkCampaign: Codable {
    let schemaVersion: String
    let target: String
    let catalogSHA256: String
    let lowAsset: String
    let busyAsset: String
    let recipes: [Recipe]

    struct Recipe: Codable, Equatable {
        let id: String
        let layout: String
        let theme: String
        let density: String
        let seed: UInt64
        let condition: String
        var family: String? = nil
        var dataRole: String? = nil
        var assetID: String? = nil
    }

    static func plannedRecipes() -> [Recipe] {
        var rows: [Recipe] = []
        for layout in ["grid", "detail"] {
            for theme in ["light", "dark"] {
                for density in ["low", "high"] {
                    for seed: UInt64 in 200...203 {
                        for condition in ["procedural", "low", "busy"] {
                            rows.append(Recipe(id: "\(layout)-\(theme)-\(density)-\(seed)-\(condition)",
                                layout: layout, theme: theme, density: density, seed: seed, condition: condition))
                        }
                    }
                }
            }
        }
        return rows
    }

    static func load(_ data: Data, catalogHash: String, assetIDs: Set<String>, target: String) throws -> Self {
        guard data.count <= 1_048_576 else { throw GeneratorArtworkCatalog.Failure.invalidCatalog }
        let plan = try JSONDecoder().decode(Self.self, from: data)
        guard try JSONSerialization.jsonObject(with: data) as? NSDictionary ==
                JSONSerialization.jsonObject(with: JSONEncoder().encode(plan)) as? NSDictionary,
              plan.schemaVersion == "ios-artwork-campaign-v1",
              plan.target == target, target == "F3EF9DB8-0B0F-4757-B653-D1628269F6FF",
              plan.catalogSHA256 == catalogHash, plan.lowAsset != plan.busyAsset,
              assetIDs.contains(plan.lowAsset), assetIDs.contains(plan.busyAsset),
              plan.recipes == plannedRecipes() else { throw GeneratorArtworkCatalog.Failure.invalidCatalog }
        return plan
    }
}

/// Explicit split-aware campaign; v1 development behavior remains unchanged.
struct GeneratorArtworkSplitCampaign: Codable {
    let schemaVersion: String
    let target: String
    let catalogSHA256: String
    let recipes: [GeneratorArtworkCampaign.Recipe]

    static func plannedRecipes() -> [GeneratorArtworkCampaign.Recipe] {
        var rows: [GeneratorArtworkCampaign.Recipe] = []
        for subject in 0..<8 {
            let family = "artwork204-family-r1-s\(subject)"
            let role = subject < 5 ? "train" : subject < 7 ? "validation" : "test"
            for theme in ["light", "dark"] {
                for density in ["low", "high"] {
                    for condition in ["procedural", "t1", "t2"] {
                        rows.append(.init(id: "art204-s\(subject)-\(theme)-\(density)-\(condition)",
                            layout: "grid", theme: theme, density: density, seed: UInt64(20400 + subject),
                            condition: condition, family: family, dataRole: role,
                            assetID: condition == "procedural" ? nil : "artwork204-r1-s\(subject)-v0-\(condition)"))
                    }
                }
            }
        }
        return rows
    }

    static func load(_ data: Data, catalogHash: String, assets: [String: GeneratorArtwork], target: String) throws -> Self {
        guard data.count <= 1_048_576 else { throw GeneratorArtworkCatalog.Failure.invalidCatalog }
        let plan = try JSONDecoder().decode(Self.self, from: data)
        guard try JSONSerialization.jsonObject(with: data) as? NSDictionary ==
                JSONSerialization.jsonObject(with: JSONEncoder().encode(plan)) as? NSDictionary,
              plan.schemaVersion == "ios-artwork-campaign-v2", plan.target == target,
              target == "F3EF9DB8-0B0F-4757-B653-D1628269F6FF", plan.catalogSHA256 == catalogHash,
              plan.recipes == plannedRecipes(),
              Set(assets.keys) == Set(plan.recipes.compactMap(\.assetID)) else {
            throw GeneratorArtworkCatalog.Failure.invalidCatalog
        }
        for recipe in plan.recipes {
            if let id = recipe.assetID {
                guard let entry = assets[id]?.entry, entry.dataRole == recipe.dataRole,
                      entry.ancestryGroup == recipe.family else { throw GeneratorArtworkCatalog.Failure.invalidAsset(id) }
            }
        }
        return plan
    }
}

/// Generator-only development asset contract. No UI annotations or training admission.
struct GeneratorArtworkCatalog: Codable, Sendable {
    let schemaVersion: String
    let assets: [Entry]

    struct Entry: Codable, Sendable {
        let id: String
        let path: String
        let sha256: String
        let bytes: Int
        let width: Int
        let height: Int
        let ancestryGroup: String
        let dataRole: String
        let rightsStatus: String
        let reviewStatus: String
        let rightsEvidence: [String]
        let reviewEvidence: [String]
    }

    enum Failure: Error { case invalidCatalog, invalidAsset(String), unknownID(String), invalidGeometry }

    static func validatePair(catalogData: Data, campaignVersion: String?) throws {
        let version = try JSONDecoder().decode(Self.self, from: catalogData).schemaVersion
        guard (version == "ios-generator-artwork-v1" && campaignVersion == "ios-artwork-campaign-v1") ||
              (version == "ios-generator-artwork-v2" && campaignVersion == "ios-artwork-campaign-v2") else {
            throw Failure.invalidCatalog
        }
    }

    /// Decode and validate the entire bounded catalogue before any renderer mutation.
    static func load(_ data: Data, root: URL) throws -> [String: GeneratorArtwork] {
        guard data.count <= 1_048_576 else { throw Failure.invalidCatalog }
        let catalog = try JSONDecoder().decode(Self.self, from: data)
        let input = try JSONSerialization.jsonObject(with: data) as? NSDictionary
        let canonical = try JSONSerialization.jsonObject(with: JSONEncoder().encode(catalog)) as? NSDictionary
        guard input == canonical, ["ios-generator-artwork-v1", "ios-generator-artwork-v2"].contains(catalog.schemaVersion),
              !catalog.assets.isEmpty, catalog.assets.count <= 64,
              Set(catalog.assets.map(\.id)).count == catalog.assets.count,
              Set(catalog.assets.map(\.sha256)).count == catalog.assets.count,
              root.isFileURL, root.standardizedFileURL.path == root.resolvingSymlinksInPath().path
        else { throw Failure.invalidCatalog }
        var result: [String: GeneratorArtwork] = [:]
        var totalPixels = 0
        var totalBytes = 0
        var roles: [String: String] = [:]
        for entry in catalog.assets {
            guard !entry.id.isEmpty, !entry.ancestryGroup.isEmpty,
                  (catalog.schemaVersion == "ios-generator-artwork-v1" ? entry.dataRole == "development" :
                    ["train", "validation", "test"].contains(entry.dataRole)), entry.rightsStatus == "verified",
                  entry.reviewStatus == "verified", !entry.rightsEvidence.isEmpty,
                  !entry.reviewEvidence.isEmpty,
                  (entry.rightsEvidence + entry.reviewEvidence).allSatisfy({ !$0.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }),
                  entry.sha256.range(of: "^[0-9a-f]{64}$", options: .regularExpression) != nil,
                  entry.bytes > 0, entry.bytes <= 64 * 1024 * 1024,
                  (1...4096).contains(entry.width), (1...4096).contains(entry.height),
                  entry.width * entry.height <= 16_777_216,
                  !entry.path.isEmpty, !entry.path.hasPrefix("/"),
                  entry.path.split(separator: "/", omittingEmptySubsequences: false)
                    .allSatisfy({ !$0.isEmpty && $0 != "." && $0 != ".." })
            else { throw Failure.invalidAsset(entry.id) }
            guard roles[entry.ancestryGroup] == nil || roles[entry.ancestryGroup] == entry.dataRole else {
                throw Failure.invalidAsset(entry.id)
            }
            roles[entry.ancestryGroup] = entry.dataRole
            totalPixels += entry.width * entry.height
            totalBytes += entry.bytes
            guard totalPixels <= 64_000_000, totalBytes <= 128 * 1024 * 1024 else {
                throw Failure.invalidCatalog
            }
            let url = root.appendingPathComponent(entry.path)
            guard url.path == url.standardizedFileURL.path,
                  url.path == url.resolvingSymlinksInPath().path,
                  url.path.hasPrefix(root.standardizedFileURL.path + "/") else {
                throw Failure.invalidAsset(entry.id)
            }
            let info = try url.resourceValues(forKeys: [.isRegularFileKey, .fileSizeKey])
            guard info.isRegularFile == true, info.fileSize == entry.bytes else {
                throw Failure.invalidAsset(entry.id)
            }
            let bytes = try Data(contentsOf: url)
            guard bytes.count == entry.bytes,
                  SHA256.hash(data: bytes).map({ String(format: "%02x", $0) }).joined() == entry.sha256,
                  let source = CGImageSourceCreateWithData(bytes as CFData, nil),
                  CGImageSourceGetType(source) as String? == "public.png",
                  CGImageSourceGetCount(source) == 1,
                  let props = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [CFString: Any],
                  (props[kCGImagePropertyPixelWidth] as? Int) == entry.width,
                  (props[kCGImagePropertyPixelHeight] as? Int) == entry.height,
                  (props[kCGImagePropertyOrientation] as? Int ?? 1) == 1,
                  let image = CGImageSourceCreateImageAtIndex(source, 0,
                    [kCGImageSourceShouldCacheImmediately: true] as CFDictionary),
                  image.width == entry.width, image.height == entry.height else {
                throw Failure.invalidAsset(entry.id)
            }
            result[entry.id] = GeneratorArtwork(entry: entry, image: image)
        }
        return result
    }
}

/// Immutable decoded CGImage, shared for read-only rendering; no mutable backing API exposed.
struct GeneratorArtwork: @unchecked Sendable {
    let entry: GeneratorArtworkCatalog.Entry
    let image: CGImage

    enum Placement: String, Codable, Sendable { case fit, fill }

    /// Rectangular content extent before rounded viewport masking. Not UI ground truth.
    func contentRect(in viewport: CGRect, placement: Placement) throws -> CGRect {
        guard !viewport.isNull, !viewport.isInfinite,
              [viewport.minX, viewport.minY, viewport.width, viewport.height].allSatisfy(\.isFinite),
              viewport.width > 0, viewport.height > 0 else {
            throw GeneratorArtworkCatalog.Failure.invalidGeometry
        }
        let x = viewport.width / CGFloat(image.width)
        let y = viewport.height / CGFloat(image.height)
        let scale = placement == .fit ? min(x, y) : max(x, y)
        let width = CGFloat(image.width) * scale
        let height = CGFloat(image.height) * scale
        return CGRect(x: viewport.midX - width / 2, y: viewport.midY - height / 2,
                      width: width, height: height)
    }
}
