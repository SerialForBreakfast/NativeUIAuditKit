import Foundation
import ImageIO
import CryptoKit

struct Input: Decodable { let id: String; let path: String; let sha256: String }
struct Result: Encodable { let id: String; let sha256: String; let report: HCFOuterRingReport }
let inputs = try JSONDecoder().decode([Input].self, from: Data(contentsOf: URL(fileURLWithPath: CommandLine.arguments[1])))
guard inputs.count > 0 && inputs.count <= 300 else { throw TVTestRigError.invalidArgument }
var results: [Result] = []
for input in inputs {
    let data = try Data(contentsOf: URL(fileURLWithPath: input.path))
    guard data.count <= 32 * 1024 * 1024,
          SHA256.hash(data: data).map({ String(format: "%02x", $0) }).joined() == input.sha256,
          let source = CGImageSourceCreateWithData(data as CFData, nil),
          let image = CGImageSourceCreateImageAtIndex(source, 0, nil),
          image.width * image.height <= 40_000_000 else { throw TVTestRigError.invalidArgument }
    results.append(.init(id: input.id, sha256: input.sha256, report: try HCFOuterRingDetector.analyze(image)))
}
try JSONEncoder().encode(results).write(to: URL(fileURLWithPath: CommandLine.arguments[2]), options: .withoutOverwriting)
