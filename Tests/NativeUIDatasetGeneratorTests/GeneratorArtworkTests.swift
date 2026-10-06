import Foundation
import Testing
import CoreGraphics
import CryptoKit
import ImageIO
@testable import NativeUIDatasetGenerator

struct GeneratorArtworkTests {
    @Test func splitCampaignContract() throws {
        try fixture { root, _, original in
            #expect(throws: (any Error).self) { try GeneratorArtworkCatalog.validatePair(catalogData: encoded([original]), campaignVersion: "ios-artwork-campaign-v2") }
            try GeneratorArtworkCatalog.validatePair(catalogData: encoded([original]), campaignVersion: "ios-artwork-campaign-v1")
            var row = original; row["dataRole"] = "train"
            let loaded = try GeneratorArtworkCatalog.load(encoded([row], version: "ios-generator-artwork-v2"), root: root)
            let image = try #require(loaded["a"])
            let recipes = GeneratorArtworkSplitCampaign.plannedRecipes()
            #expect(recipes.count == 96)
            #expect(recipes.filter { $0.dataRole == "train" }.count == 60)
            var assets: [String: GeneratorArtwork] = [:]
            for recipe in recipes {
                if let id = recipe.assetID {
                    row["id"] = id; row["ancestryGroup"] = recipe.family; row["dataRole"] = recipe.dataRole
                    let entry = try JSONDecoder().decode(GeneratorArtworkCatalog.Entry.self,
                        from: JSONSerialization.data(withJSONObject: row))
                    assets[id] = GeneratorArtwork(entry: entry, image: image.image)
                }
            }
            let target = "F3EF9DB8-0B0F-4757-B653-D1628269F6FF"
            let plan = GeneratorArtworkSplitCampaign(schemaVersion: "ios-artwork-campaign-v2",
                target: target, catalogSHA256: "abc", recipes: recipes)
            let data = try JSONEncoder().encode(plan)
            #expect(try GeneratorArtworkSplitCampaign.load(data, catalogHash: "abc", assets: assets, target: target).recipes == recipes)
            #expect(throws: (any Error).self) { try GeneratorArtworkSplitCampaign.load(data, catalogHash: "abc", assets: assets, target: "booted") }
            #expect(throws: (any Error).self) { try GeneratorArtworkSplitCampaign.load(data, catalogHash: "changed", assets: assets, target: target) }
            assets.removeValue(forKey: recipes[1].assetID!)
            #expect(throws: (any Error).self) { try GeneratorArtworkSplitCampaign.load(data, catalogHash: "abc", assets: assets, target: target) }
            row = original; row["dataRole"] = "unassigned"
            #expect(throws: (any Error).self) { try GeneratorArtworkCatalog.load(encoded([row], version: "ios-generator-artwork-v2"), root: root) }
        }
    }

    @Test func campaignPlanIsFrozenAndTargetBound() throws {
        let target = "F3EF9DB8-0B0F-4757-B653-D1628269F6FF"
        let rows = GeneratorArtworkCampaign.plannedRecipes()
        #expect(rows.count == 96)
        #expect(Set(rows.map(\.id)).count == 96)
        let plan = GeneratorArtworkCampaign(schemaVersion: "ios-artwork-campaign-v1", target: target,
            catalogSHA256: "abc", lowAsset: "low", busyAsset: "busy", recipes: rows)
        let data = try JSONEncoder().encode(plan)
        #expect(try GeneratorArtworkCampaign.load(data, catalogHash: "abc", assetIDs: ["low", "busy"], target: target).recipes == rows)
        for (hash, ids, actual) in [("changed", Set(["low", "busy"]), target),
                                    ("abc", Set(["low"]), target), ("abc", Set(["low", "busy"]), "booted")] {
            #expect(throws: (any Error).self) { try GeneratorArtworkCampaign.load(data, catalogHash: hash, assetIDs: ids, target: actual) }
        }
        let partial = GeneratorArtworkCampaign(schemaVersion: plan.schemaVersion, target: target,
            catalogSHA256: "abc", lowAsset: "low", busyAsset: "busy", recipes: Array(rows.dropLast()))
        #expect(throws: (any Error).self) { try GeneratorArtworkCampaign.load(JSONEncoder().encode(partial), catalogHash: "abc", assetIDs: ["low", "busy"], target: target) }
    }
    private func fixture(_ body: (URL, Data, [String: Any]) throws -> Void) throws {
        let root = URL(fileURLWithPath: #filePath).deletingLastPathComponent()
            .deletingLastPathComponent().deletingLastPathComponent()
            .appendingPathComponent(".build/debug-output/asset200-" + UUID().uuidString)
        try FileManager.default.createDirectory(at: root, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: root) }
        let context = try #require(CGContext(data: nil, width: 40, height: 20, bitsPerComponent: 8,
            bytesPerRow: 160, space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue))
        context.setFillColor(CGColor(red: 0.8, green: 0.2, blue: 0.1, alpha: 1))
        context.fill(CGRect(x: 0, y: 0, width: 40, height: 20))
        let image = try #require(context.makeImage())
        let encoded = NSMutableData()
        let dest = try #require(CGImageDestinationCreateWithData(encoded, "public.png" as CFString, 1, nil))
        CGImageDestinationAddImage(dest, image, nil)
        #expect(CGImageDestinationFinalize(dest))
        let bytes = encoded as Data
        try bytes.write(to: root.appendingPathComponent("art.png"))
        let entry: [String: Any] = ["id": "a", "path": "art.png", "bytes": bytes.count,
            "sha256": SHA256.hash(data: bytes).map { String(format: "%02x", $0) }.joined(),
            "width": 40, "height": 20, "ancestryGroup": "test", "dataRole": "development",
            "rightsStatus": "verified", "reviewStatus": "verified",
            "rightsEvidence": ["generated test pixels"], "reviewEvidence": ["deterministic fixture"]]
        try body(root, bytes, entry)
    }

    private func encoded(_ entries: [[String: Any]], version: String = "ios-generator-artwork-v1") throws -> Data {
        try JSONSerialization.data(withJSONObject: ["schemaVersion": version, "assets": entries])
    }

    @Test func loadAndPlacement() throws {
        try fixture { root, _, entry in
            let catalog = try GeneratorArtworkCatalog.load(encoded([entry]), root: root)
            let image = try #require(catalog["a"])
            let viewport = CGRect(x: 10, y: 20, width: 100, height: 100)
            #expect(try image.contentRect(in: viewport, placement: .fit) == CGRect(x: 10, y: 45, width: 100, height: 50))
            #expect(try image.contentRect(in: viewport, placement: .fill) == CGRect(x: -40, y: 20, width: 200, height: 100))
            #expect(throws: (any Error).self) { try image.contentRect(in: .zero, placement: .fit) }
        }
    }

    @Test func rejectMalformedAndUnreviewed() throws {
        try fixture { root, _, entry in
            let changes: [(String, Any)] = [("width", 41), ("height", 5000), ("bytes", 0),
                ("sha256", String(repeating: "0", count: 64)), ("path", "../art.png"),
                ("path", "/art.png"), ("path", "missing.png"), ("path", "./art.png"),
                ("dataRole", "train"), ("rightsStatus", "pending"), ("reviewStatus", "rejected"),
                ("reviewEvidence", []), ("extra", true)]
            for (key, value) in changes {
                var changed = entry; changed[key] = value
                #expect(throws: (any Error).self) { try GeneratorArtworkCatalog.load(encoded([changed]), root: root) }
            }
            #expect(throws: (any Error).self) { try GeneratorArtworkCatalog.load(encoded([entry, entry]), root: root) }
            #expect(throws: (any Error).self) { try GeneratorArtworkCatalog.load(encoded([entry], version: "next"), root: root) }
        }
    }

    @Test func rejectCorruptBytesAndSymlinks() throws {
        try fixture { root, _, entry in
            let link = root.appendingPathComponent("linked.png")
            try FileManager.default.createSymbolicLink(at: link, withDestinationURL: root.appendingPathComponent("art.png"))
            var row = entry; row["path"] = "linked.png"
            #expect(throws: (any Error).self) { try GeneratorArtworkCatalog.load(encoded([row]), root: root) }
            let bad = Data("not an image".utf8)
            try bad.write(to: root.appendingPathComponent("art.png"))
            row = entry; row["bytes"] = bad.count
            row["sha256"] = SHA256.hash(data: bad).map { String(format: "%02x", $0) }.joined()
            #expect(throws: (any Error).self) { try GeneratorArtworkCatalog.load(encoded([row]), root: root) }
        }
    }
}
