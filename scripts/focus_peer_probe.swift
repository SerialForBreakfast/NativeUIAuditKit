import Foundation
import CoreGraphics
import CoreML
import ImageIO
import Darwin

// Diagnostic only: compiled alongside unchanged producer source, never installed.
struct ProbeItem: Decodable { let id: String; let path: String; let bounds: [Double] }
struct ProbeRequest: Decodable { let model: String; let items: [ProbeItem] }
struct ProbeRow: Encodable {
    let id: String
    let png: String
    let probability: Double
    let confidence: Double
    let secondProbability: Double
    let zeroScoreMayHideFailure: Bool
}

@main struct PeerProbe {
    static func main() async {
        let fd = dup(STDOUT_FILENO)
        dup2(STDERR_FILENO, STDOUT_FILENO)
        do {
            let request = try JSONDecoder().decode(ProbeRequest.self, from: FileHandle.standardInput.readDataToEndOfFile())
            guard !request.items.isEmpty, request.items.count <= 32 else { throw TVTestRigError.invalidArgument }
            let url = URL(fileURLWithPath: request.model)
            let config = MLModelConfiguration(); config.computeUnits = .all
            let model = try MLModel(contentsOf: url, configuration: config)
            guard model.modelDescription.outputDescriptionsByName["is_focused_prob"] != nil,
                  model.modelDescription.outputDescriptionsByName["confidence"] != nil else {
                throw TVTestRigError.invalidArgument
            }
            let scorer = FocusDetectorService(modelURL: url)
            var rows: [ProbeRow] = []
            for item in request.items {
                guard item.bounds.count == 4,
                      let source = CGImageSourceCreateWithURL(URL(fileURLWithPath: item.path) as CFURL, nil),
                      let image = CGImageSourceCreateImageAtIndex(source, 0, nil) else { throw TVTestRigError.invalidArgument }
                let b = item.bounds
                let roi = try NormalizedRectangle(x: b[0] / Double(image.width), y: b[1] / Double(image.height),
                                                  width: b[2] / Double(image.width), height: b[3] / Double(image.height))
                guard let raw = LocalVisionOCRService.crop(image, roi: roi),
                      let crop = FocusDetectorService.resize(raw, side: 256) else { throw TVTestRigError.invalidArgument }
                let bytes = NSMutableData()
                guard let dest = CGImageDestinationCreateWithData(bytes, "public.png" as CFString, 1, nil) else {
                    throw TVTestRigError.invalidArgument
                }
                CGImageDestinationAddImage(dest, crop, nil)
                guard CGImageDestinationFinalize(dest) else { throw TVTestRigError.invalidArgument }
                let first = await scorer.score(image: image, roi: roi)
                let second = await scorer.score(image: image, roi: roi)
                rows.append(ProbeRow(id: item.id, png: (bytes as Data).base64EncodedString(),
                                     probability: first.isFocusedProb, confidence: first.confidence,
                                     secondProbability: second.isFocusedProb,
                                     zeroScoreMayHideFailure: first == .zero || second == .zero))
            }
            FileHandle(fileDescriptor: fd, closeOnDealloc: true).write(try JSONEncoder().encode(rows))
        } catch {
            FileHandle.standardError.write(Data("Peer focus probe failed: \(error)\n".utf8)); exit(2)
        }
    }
}
