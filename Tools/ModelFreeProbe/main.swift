import Foundation
import NativeUIAuditKitRuntime

// This consumer links only the resource-free product.
@main struct ModelFreeProbe {
    static func main() async throws {
        let provider = try NativeUILocalModelProvider()
        let session = NativeUIDetectionSession(modelProvider: provider)
        do {
            try await session.warm(platforms: [.tvOS])
            throw ProbeFailure.unexpectedModel
        } catch NativeUIModelAvailabilityError.unavailable(let name) {
            print("PASS: no bundled weights; missing \(name) returns a typed error")
        }
    }
    enum ProbeFailure: Error { case unexpectedModel }
}
