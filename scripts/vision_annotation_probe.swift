// Local diagnostic only: fixed rectangle + OCR requests, no app/device control.
import Foundation
import Vision
import ImageIO
import CryptoKit

struct Frame: Codable, Sendable { let id: String; let path: String; let sha256: String }
struct Pair: Codable, Sendable { let id: String; let before: String; let after: String }
struct Input: Codable, Sendable {
    let version: Int; let root: String; let frames: [Frame]; let rectanglesOnly: Bool?
    let featureRevision: Int?; let featureCrop: String?; let pairs: [Pair]?
    let ocrLevel: String?; let languageCorrection: Bool?; let minimumTextHeight: Float?; let textOnly: Bool?
}
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
if let revision = input.featureRevision {
    guard VNGenerateImageFeaturePrintRequest.supportedRevisions.contains(revision),
          let pairs = input.pairs, !pairs.isEmpty, pairs.count <= 80,
          Set(pairs.map(\.id)).count == pairs.count,
          ["scaleFit", "centerCrop"].contains(input.featureCrop ?? "") else {
        throw ProbeError(message: "unsupported_feature_configuration")
    }
    var prints: [String: VNFeaturePrintObservation] = [:]
    var timings: [[String: Any]] = []
    for frame in input.frames {
        try autoreleasepool {
            let url = URL(fileURLWithPath: frame.path).resolvingSymlinksInPath()
            guard url.path.hasPrefix(root) else { throw ProbeError(message: "outside_project") }
            let data = try Data(contentsOf: url)
            let hash = SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
            guard hash == frame.sha256, let source = CGImageSourceCreateWithData(data as CFData, nil),
                  let image = CGImageSourceCreateImageAtIndex(source, 0, nil),
                  image.width * image.height <= 80_000_000 else { throw ProbeError(message: "invalid_or_changed_image") }
            let request = VNGenerateImageFeaturePrintRequest()
            request.revision = revision
            request.imageCropAndScaleOption = input.featureCrop == "scaleFit" ? .scaleFit : .centerCrop
            let start = ProcessInfo.processInfo.systemUptime
            try VNImageRequestHandler(cgImage: image, orientation: .up).perform([request])
            guard let result = request.results?.first as? VNFeaturePrintObservation else {
                throw ProbeError(message: "missing_feature_print")
            }
            prints[frame.id] = result
            timings.append(["id": frame.id, "sha256": hash, "width": image.width, "height": image.height,
                "seconds": ProcessInfo.processInfo.systemUptime - start, "elements": result.elementCount])
        }
    }
    var scores: [[String: Any]] = []
    for pair in pairs {
        guard let before = prints[pair.before], let after = prints[pair.after] else {
            throw ProbeError(message: "missing_pair_frame")
        }
        var distance: Float = 0
        try before.computeDistance(&distance, to: after)
        guard distance.isFinite else { throw ProbeError(message: "nonfinite_distance") }
        scores.append(["id": pair.id, "before": pair.before, "after": pair.after, "distance": distance])
    }
    let receipt: [String: Any] = ["version": 1, "os": ProcessInfo.processInfo.operatingSystemVersionString,
        "revision": revision, "crop": input.featureCrop!,
        "supportedRevisions": Array(VNGenerateImageFeaturePrintRequest.supportedRevisions),
        "frames": timings, "pairs": scores]
    FileHandle.standardOutput.write(try JSONSerialization.data(withJSONObject: receipt, options: [.prettyPrinted, .sortedKeys]))
    exit(0)
}
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
    do { if input.textOnly != true { try VNImageRequestHandler(cgImage: image, orientation: .up).perform([rectangles]) } }
    catch { errors.append("rectangles: \(error)") }
    let rectTime = ProcessInfo.processInfo.systemUptime - start
    let text = VNRecognizeTextRequest()
    guard input.ocrLevel == nil || ["fast", "accurate"].contains(input.ocrLevel!) else { throw ProbeError(message: "ocr_level") }
    text.recognitionLevel = input.ocrLevel == "fast" ? .fast : .accurate
    text.recognitionLanguages = ["en-US"]
    text.usesLanguageCorrection = input.languageCorrection ?? false
    if let height = input.minimumTextHeight {
        guard height.isFinite && height >= 0 && height <= 1 else { throw ProbeError(message: "text_height") }
        text.minimumTextHeight = height
    }
    let ocrStart = ProcessInfo.processInfo.systemUptime
    if input.rectanglesOnly != true {
        do { try VNImageRequestHandler(cgImage: image, orientation: .up).perform([text]) }
        catch { errors.append("ocr: \(error)") }
    }
    outputs.append(Output(id: frame.id, sha256: hash, width: image.width, height: image.height,
        rectangles: (rectangles.results ?? []).map { Proposal(bounds: box($0.boundingBox,image.width,image.height), confidence: $0.confidence, text: nil) },
        text: (text.results ?? []).map { Proposal(bounds: box($0.boundingBox,image.width,image.height), confidence: $0.confidence, text: $0.topCandidates(1).first?.string) },
        rectangleSeconds: rectTime, ocrSeconds: ProcessInfo.processInfo.systemUptime-ocrStart,
        rectangleRevision: rectangles.revision, ocrRevision: text.revision, errors: errors))
}
struct Receipt: Codable, Sendable { let version: Int; let os: String; let results: [Output] }
let encoder = JSONEncoder(); encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
FileHandle.standardOutput.write(try encoder.encode(Receipt(version: 1, os: ProcessInfo.processInfo.operatingSystemVersionString, results: outputs)))
