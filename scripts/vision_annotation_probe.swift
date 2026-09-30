// Local diagnostic only: fixed rectangle + OCR requests, no app/device control.
import Foundation
import Vision
import ImageIO
import CryptoKit

struct Frame: Codable, Sendable { let id: String; let path: String; let sha256: String }
struct Input: Codable, Sendable { let version: Int; let root: String; let frames: [Frame] }
struct Proposal: Codable, Sendable { let bounds: [Double]; let confidence: Float; let text: String? }
struct Output: Codable, Sendable {
    let id: String; let sha256: String; let width: Int; let height: Int
    let rectangles: [Proposal]; let text: [Proposal]
    let rectangleSeconds: Double; let ocrSeconds: Double
    let rectangleRevision: Int; let ocrRevision: Int
    let errors: [String]
}
func box(_ b: CGRect, _ width: Int, _ height: Int) -> [Double] {
    [b.minX*Double(width), (1-b.maxY)*Double(height), b.width*Double(width), b.height*Double(height)]
}
struct ProbeError: Error { let message: String }
let input = try JSONDecoder().decode(Input.self, from: FileHandle.standardInput.readDataToEndOfFile())
guard input.version == 1, !input.frames.isEmpty, input.frames.count <= 40,
      Set(input.frames.map(\.id)).count == input.frames.count else { throw ProbeError(message: "invalid_input") }
let root = URL(fileURLWithPath: input.root).resolvingSymlinksInPath().path + "/"
var outputs: [Output] = []
for frame in input.frames {
    let url = URL(fileURLWithPath: frame.path).resolvingSymlinksInPath()
    guard url.path.hasPrefix(root) else { throw ProbeError(message: "outside_project") }
    let data = try Data(contentsOf: url)
    let hash = SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
    guard hash == frame.sha256, let source = CGImageSourceCreateWithData(data as CFData, nil),
          let image = CGImageSourceCreateImageAtIndex(source, 0, nil),
          image.width * image.height <= 80_000_000 else { throw ProbeError(message: "invalid_or_changed_image") }
    let rectangles = VNDetectRectanglesRequest()
    rectangles.maximumObservations = 40
    rectangles.minimumSize = 0.01
    rectangles.minimumAspectRatio = 0.05
    rectangles.maximumAspectRatio = 1
    rectangles.minimumConfidence = 0.5
    rectangles.quadratureTolerance = 15
    var errors: [String] = []
    let start = ProcessInfo.processInfo.systemUptime
    do { try VNImageRequestHandler(cgImage: image, orientation: .up).perform([rectangles]) }
    catch { errors.append("rectangles: \(error)") }
    let rectTime = ProcessInfo.processInfo.systemUptime - start
    let text = VNRecognizeTextRequest()
    text.recognitionLevel = .accurate
    text.recognitionLanguages = ["en-US"]
    text.usesLanguageCorrection = false
    let ocrStart = ProcessInfo.processInfo.systemUptime
    do { try VNImageRequestHandler(cgImage: image, orientation: .up).perform([text]) }
    catch { errors.append("ocr: \(error)") }
    outputs.append(Output(id: frame.id, sha256: hash, width: image.width, height: image.height,
        rectangles: (rectangles.results ?? []).map { Proposal(bounds: box($0.boundingBox,image.width,image.height), confidence: $0.confidence, text: nil) },
        text: (text.results ?? []).map { Proposal(bounds: box($0.boundingBox,image.width,image.height), confidence: $0.confidence, text: $0.topCandidates(1).first?.string) },
        rectangleSeconds: rectTime, ocrSeconds: ProcessInfo.processInfo.systemUptime-ocrStart,
        rectangleRevision: rectangles.revision, ocrRevision: text.revision, errors: errors))
}
struct Receipt: Codable, Sendable { let version: Int; let os: String; let results: [Output] }
let encoder = JSONEncoder(); encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
FileHandle.standardOutput.write(try encoder.encode(Receipt(version: 1, os: ProcessInfo.processInfo.operatingSystemVersionString, results: outputs)))
