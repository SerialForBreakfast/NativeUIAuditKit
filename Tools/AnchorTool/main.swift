import Foundation
import NativeUIAuditKit
import Darwin

struct Region: Decodable, Sendable { let text: String; let bounds: [Double] }
struct Item: Decodable, Sendable {
    let id: String; let required: [String]; let optional: [String]; let forbidden: [String]
    let regions: [Region]
}
struct Request: Decodable, Sendable { let version: Int; let items: [Item] }
struct Result: Encodable, Sendable {
    let id: String; let status: String; let missingRequired: [String]
    let matchedRequired: [String]; let matchedForbidden: [String]; let milliseconds: Double
}
struct Reply: Encodable, Sendable { let version: Int; let results: [Result]; let host: String }
enum Invalid: Error { case request, bounds }

func run() throws {
    var bytes = Data()
    while let chunk = try FileHandle.standardInput.read(upToCount: 65536), !chunk.isEmpty {
        bytes.append(chunk); guard bytes.count <= 8_388_608 else { throw Invalid.request }
    }
    let request = try JSONDecoder().decode(Request.self, from: bytes)
    guard request.version == 1, !request.items.isEmpty, request.items.count <= 16,
          Set(request.items.map(\.id)).count == request.items.count else { throw Invalid.request }
    var results: [Result] = []
    for item in request.items {
        guard !item.id.isEmpty, item.id.utf8.count <= 1024, item.regions.count <= 256,
              [item.required, item.optional, item.forbidden].allSatisfy({ $0.count <= 16 && $0.allSatisfy { !$0.isEmpty && $0.utf8.count <= 4096 } }),
              item.regions.allSatisfy({ !$0.text.isEmpty && $0.text.utf8.count <= 4096 }) else { throw Invalid.request }
        let regions = try item.regions.map { r -> RecognizedTextRegion in
            let b = r.bounds
            guard b.count == 4, b.allSatisfy(\.isFinite), b[0] >= 0, b[1] >= 0,
                  b[2] > 0, b[3] > 0, b[0]+b[2] <= 1.000000001, b[1]+b[3] <= 1.000000001 else { throw Invalid.bounds }
            return RecognizedTextRegion(text: r.text, boundingBox: NativeUIRect(x: b[0], y: 1-b[1]-b[3], width: b[2], height: b[3]))
        }
        let start = ProcessInfo.processInfo.systemUptime
        let result = TextAnchorVerifier.evaluate(TextAnchorRequirements(required: item.required, optional: item.optional, forbidden: item.forbidden), against: regions)
        let status: String
        switch result.status { case .verified: status = "verified"; case .unverified: status = "unverified"; case .ambiguous: status = "ambiguous" }
        results.append(Result(id: item.id, status: status, missingRequired: result.missingRequired,
                              matchedRequired: result.matchedRequired.map(\.anchor), matchedForbidden: result.matchedForbidden.map(\.anchor),
                              milliseconds: (ProcessInfo.processInfo.systemUptime-start)*1000))
    }
    let encoder = JSONEncoder(); encoder.outputFormatting = [.sortedKeys]
    FileHandle.standardOutput.write(try encoder.encode(Reply(version: 1, results: results, host: ProcessInfo.processInfo.operatingSystemVersionString)))
}
do { try run() } catch {
    FileHandle.standardError.write(Data("AnchorTool failed: \(error)\n".utf8)); exit(2)
}
