#if os(macOS)
import CoreML
import ImageIO
import Foundation
import NativeUIAuditKit
import NativeUIAuditKitModels
import Testing
@testable import NativeUIAuditKitRuntime

@Suite("Native model archives", .serialized)
struct NativeModelInstallerTests: Sendable {
    enum ParityFailure: Error { case mismatch }
    // This independent writer makes the narrow ZIP fixture used by the native extractor.
    func zip(_ files: [(String, Data)]) -> (Data, [ModelArchiveMember]) {
        var local = Data(), central = Data()
        var members: [ModelArchiveMember] = []
        func int(_ value: Int, _ width: Int) -> Data {
            Data((0..<width).map { UInt8(truncatingIfNeeded: value >> ($0 * 8)) })
        }
        for (path, data) in files {
            let name = Data(path.utf8), start = local.count, crc = Int(ModelArchive.crc32(data))
            local += int(0x04034b50, 4) + int(20, 2) + Data(repeating: 0, count: 8)
            local += int(crc, 4) + int(data.count, 4) + int(data.count, 4) + int(name.count, 2) + int(0, 2) + name + data
            central += int(0x02014b50, 4) + int(0x0314, 2) + int(20, 2) + Data(repeating: 0, count: 8)
            central += int(crc, 4) + int(data.count, 4) + int(data.count, 4) + int(name.count, 2)
            central += Data(repeating: 0, count: 8) + int(0o100644 << 16, 4) + int(start, 4) + name
            members.append(.init(path: path, bytes: data.count, sha256: ModelArchive.hash(data)))
        }
        var end = int(0x06054b50, 4) + Data(repeating: 0, count: 4)
        end += int(files.count, 2) + int(files.count, 2) + int(central.count, 4) + int(local.count, 4) + int(0, 2)
        return (local + central + end, members)
    }

    func archive(_ files: [(String, Data)]) throws -> ModelArchive {
        let (bytes, members) = zip(files)
        return try ModelArchive(bytes: bytes, expectedSHA256: ModelArchive.hash(bytes), members: members)
    }

    func root() throws -> URL {
        let project = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
        let root = project.appendingPathComponent(".build/model-install-tests/" + UUID().uuidString)
        try FileManager.default.createDirectory(at: root, withIntermediateDirectories: true)
        return root
    }

    @Test func rejectsCorruptAndUnsupportedArchives() throws {
        let (bytes, members) = zip([("a.mlpackage/model.bin", Data([1, 2, 3]))])
        _ = try ModelArchive(bytes: bytes, expectedSHA256: ModelArchive.hash(bytes), members: members)
        #expect(throws: ModelArchive.Failure.self) {
            try ModelArchive(bytes: bytes, expectedSHA256: "wrong", members: members)
        }
        for index in [0, 4, 6, 8, 14, bytes.count - 1] {
            var changed = bytes
            changed[index] ^= 1
            #expect(throws: ModelArchive.Failure.self) {
                try ModelArchive(bytes: changed, expectedSHA256: ModelArchive.hash(changed), members: members)
            }
        }
        for name in ["../evil", "/absolute", "a//b", "a\\b", "a/./b", "a:b"] {
            #expect(throws: ModelArchive.Failure.self) { try archive([(name, Data([0]))]) }
        }
        #expect(throws: ModelArchive.Failure.self) { try archive([("a", Data([0])), ("A", Data([0]))]) }
        let missing = Array(members.dropLast())
        #expect(throws: ModelArchive.Failure.self) {
            try ModelArchive(bytes: bytes, expectedSHA256: ModelArchive.hash(bytes), members: missing)
        }
    }

    @Test func extractedBytesAndLinksAreChecked() throws {
        let root = try root()
        let bytes = Data([1, 2, 3])
        let archive = try archive([("model.bin", bytes)])
        let path = root.appendingPathComponent("model.bin")
        try bytes.write(to: path)
        try archive.verifyExtracted(at: root)
        try Data([3, 2, 1]).write(to: path)
        #expect(throws: ModelArchive.Failure.self) { try archive.verifyExtracted(at: root) }
        let linkRoot = try self.root()
        try FileManager.default.createSymbolicLink(at: linkRoot.appendingPathComponent("model.bin"), withDestinationURL: path)
        #expect(throws: ModelArchive.Failure.self) { try archive.verifyExtracted(at: linkRoot) }
    }

    @Test func invalidSourceLeavesFailedAttempt() async throws {
        let root = try root()
        let installer = try NativeModelInstaller(root: root)
        let archive = try archive([("bad.mlpackage/Manifest.json", Data("{}".utf8))])
        await #expect(throws: (any Error).self) {
            try await installer.install(archive: archive, sourceName: "bad.mlpackage", validate: { _ in })
        }
        #expect(await installer.state == .failed)
        let attempts = try FileManager.default.contentsOfDirectory(at: root, includingPropertiesForKeys: nil)
        #expect(attempts.count == 1)
        let receipt = try JSONDecoder().decode(NativeModelInstaller.Receipt.self,
            from: Data(contentsOf: attempts[0].appendingPathComponent("receipt.json")))
        #expect(receipt.state == .failed)
        #expect(!FileManager.default.fileExists(atPath: root.appendingPathComponent(ModelArchive.hash(archive.bytes)).path))
    }

    func residentArchive(stale: Bool = false) throws -> ModelArchive {
        let project = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
        let source = project.appendingPathComponent(stale
            ? "NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/NativeUIModel_tvOS.mlpackage"
            : "NativeUITrainer/yolo_runs/phase6b_tvos_v3/weights/best.mlpackage")
        let iterator = try #require(FileManager.default.enumerator(at: source, includingPropertiesForKeys: [.isRegularFileKey]))
        var files: [(String, Data)] = []
        for case let url as URL in iterator {
            if try url.resourceValues(forKeys: [.isRegularFileKey]).isRegularFile == true {
                files.append(("model.mlpackage/" + String(url.path.dropFirst(source.path.count + 1)), try Data(contentsOf: url)))
            }
        }
        return try archive(files.sorted { $0.0 < $1.0 })
    }

    func compiler() throws -> NativeModelCompiler {
        let project = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
        let executable = project.appendingPathComponent(".build/debug/ModelCompileWorker").resolvingSymlinksInPath()
        return try NativeModelCompiler(executable: executable, expectedDigest: NativeModelCompiler.digest(executable))
    }

    static var residentSourceExists: Bool {
        let project = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
        return FileManager.default.fileExists(atPath: project.appendingPathComponent("NativeUITrainer/yolo_runs/phase6b_tvos_v3/weights/best.mlpackage/Manifest.json").path)
    }

    @Test(.enabled(if: residentSourceExists, "The optional source package is not present."))
    func nativeSourceCompilesAndChecksBeforePublication() async throws {
        let archive = try residentArchive()
        let destination = try root()
        let worker = try compiler()
        let installer = try NativeModelInstaller(root: destination, compiler: worker)
        let manifest = try NativeUIModelAsset.requiredManifest(forTVOS: true)
        let compiled = try await installer.install(archive: archive, sourceName: "model.mlpackage") { url in
            let configuration = MLModelConfiguration()
            configuration.computeUnits = .cpuOnly
            let model = try await MLModel.load(contentsOf: url, configuration: configuration)
            try ModelManifestValidator.validate(model: model, against: manifest)
            try await requireParity(at: url)
        }
        #expect(await installer.state == .ready)
        let receipt = try JSONDecoder().decode(NativeModelInstaller.Receipt.self,
            from: Data(contentsOf: compiled.deletingLastPathComponent().appendingPathComponent("receipt.json")))
        #expect(receipt.compiledDigest == (try NativeUILocalDetector.digest(at: compiled)))
        #expect(receipt.sourceDigest != receipt.compiledDigest)
        await #expect(throws: NativeModelInstaller.Failure.self) {
            try await installer.install(archive: archive, sourceName: "model.mlpackage", validate: { _ in })
        }
        #expect(FileManager.default.fileExists(atPath: compiled.path))
        let restarted = try NativeModelInstaller(root: destination, compiler: worker)
        #expect(try await restarted.recover(archive: archive, sourceName: "model.mlpackage") == compiled)
        let selection = try NativeModelSelection(root: destination, compiler: worker,
            entries: [.init(archive: archive, sourceName: "model.mlpackage")])
        try await selection.restore()
        try await selection.activate(ModelArchive.hash(archive.bytes))
        try await selection.withSelectedModel { try await requireParity(at: $0) }
        let receiptURL = compiled.deletingLastPathComponent().appendingPathComponent("receipt.json")
        let originalReceipt = try Data(contentsOf: receiptURL)
        for (key, value) in [("host", "different-host" as Any), ("schemaVersion", 99 as Any),
                             ("state", "installing" as Any), ("compilerDigest", "wrong" as Any)] {
            var changed = try #require(JSONSerialization.jsonObject(with: originalReceipt) as? [String: Any])
            changed[key] = value
            try JSONSerialization.data(withJSONObject: changed).write(to: receiptURL, options: .atomic)
            await #expect(throws: NativeModelInstaller.Failure.self) {
                try await restarted.recover(archive: archive, sourceName: "model.mlpackage")
            }
            #expect(await restarted.state == .failed)
        }
        try originalReceipt.write(to: receiptURL, options: .atomic)
        #expect(try await restarted.recover(archive: archive, sourceName: "model.mlpackage") == compiled)
        let marker = compiled.appendingPathComponent("unexpected-file")
        try Data([9]).write(to: marker)
        await #expect(throws: NativeModelInstaller.Failure.self) {
            try await restarted.recover(archive: archive, sourceName: "model.mlpackage")
        }
    }

    func requireParity(at compiled: URL) async throws {
        let manifest = try NativeUIModelAsset.requiredManifest(forTVOS: true)
        let detector = try NativeUILocalDetector(url: compiled, expectedDigest: NativeUILocalDetector.digest(at: compiled),
            manifest: manifest, metadata: NativeUIModelAsset.tvOSMetadata)
        let provider = try NativeUILocalModelProvider(tvOS: detector)
        let configuration = NativeUIDetectionConfiguration(includesTextRecognition: false, platform: .tvOS, useFocusClassifier: false)
        let fixture = try #require(Bundle.module.url(forResource: "tvos_home_screen", withExtension: "png"))
        let imageSource = try #require(CGImageSourceCreateWithURL(fixture as CFURL, nil))
        let image = try #require(CGImageSourceCreateImageAtIndex(imageSource, 0, nil))
        let installed = try await NativeUIDetectionRequest(modelProvider: provider, configuration: configuration).perform(on: image)
        let bundled = try await NativeUIDetectionRequest(configuration: configuration).perform(on: image)
        guard installed.count == bundled.count, !installed.isEmpty else { throw ParityFailure.mismatch }
        var differences = 0
        for (a, b) in Swift.zip(installed, bundled) {
            if a.elementType != b.elementType || abs(a.confidence - b.confidence) >= 0.00001
                || abs(a.boundingBoxPixels.x - b.boundingBoxPixels.x) >= 0.01
                || abs(a.boundingBoxPixels.y - b.boundingBoxPixels.y) >= 0.01
                || abs(a.boundingBoxPixels.width - b.boundingBoxPixels.width) >= 0.01
                || abs(a.boundingBoxPixels.height - b.boundingBoxPixels.height) >= 0.01 { differences += 1 }
        }
        print("Native source parity: \(installed.count) detections, \(differences) mismatches")
        guard differences == 0 else { throw ParityFailure.mismatch }
    }

    @Test(.enabled(if: residentSourceExists, "The optional source package is not present."))
    func staleSourceFailsParityAndStaysUnpublished() async throws {
        let archive = try residentArchive(stale: true)
        let destination = try root()
        let installer = try NativeModelInstaller(root: destination, compiler: compiler())
        await #expect(throws: ParityFailure.self) {
            try await installer.install(archive: archive, sourceName: "model.mlpackage") { url in
                try await requireParity(at: url)
            }
        }
        #expect(await installer.state == .failed)
        #expect(!FileManager.default.fileExists(atPath: destination.appendingPathComponent(ModelArchive.hash(archive.bytes)).path))
    }

    @Test func cancelledAttemptDoesNotStart() async throws {
        let destination = try root()
        let installer = try NativeModelInstaller(root: destination)
        let archive = try archive([("bad.mlpackage/Manifest.json", Data("{}".utf8))])
        let task = Task {
            withUnsafeCurrentTask { $0?.cancel() }
            return try await installer.install(archive: archive, sourceName: "bad.mlpackage", validate: { _ in })
        }
        task.cancel()
        await #expect(throws: CancellationError.self) { try await task.value }
        #expect(try FileManager.default.contentsOfDirectory(atPath: destination.path).isEmpty)
    }

    @Test func lowSpaceAndExistingClaimStopBeforeExtraction() async throws {
        let destination = try root()
        let archive = try archive([("bad.mlpackage/Manifest.json", Data("{}".utf8))])
        let installer = try NativeModelInstaller(root: destination, availableBytes: { _ in 0 })
        await #expect(throws: NativeModelInstaller.Failure.self) {
            try await installer.install(archive: archive, sourceName: "bad.mlpackage", validate: { _ in })
        }
        #expect(try FileManager.default.contentsOfDirectory(atPath: destination.path).isEmpty)
        let claim = destination.appendingPathComponent("installing-" + ModelArchive.hash(archive.bytes))
        try FileManager.default.createDirectory(at: claim, withIntermediateDirectories: false)
        let second = try NativeModelInstaller(root: destination)
        await #expect(throws: NativeModelInstaller.Failure.self) {
            try await second.install(archive: archive, sourceName: "bad.mlpackage", validate: { _ in })
        }
        #expect(try FileManager.default.contentsOfDirectory(atPath: destination.path) == [claim.lastPathComponent])
    }

    @Test func ownedProcessFailureTimeoutAndCancellationAreContained() async throws {
        func process(_ command: String, _ arguments: [String] = []) -> Process {
            let process = Process()
            process.executableURL = URL(fileURLWithPath: command)
            process.arguments = arguments
            process.standardOutput = FileHandle.nullDevice
            process.standardError = FileHandle.nullDevice
            return process
        }
        let failed = process("/usr/bin/false")
        await #expect(throws: NativeModelCompiler.Failure.self) {
            try await NativeOwnedProcess.run(failed, timeout: .seconds(1))
        }
        #expect(!failed.isRunning)
        let timed = process("/bin/sleep", ["5"])
        await #expect(throws: NativeModelCompiler.Failure.self) {
            try await NativeOwnedProcess.run(timed, timeout: .milliseconds(20))
        }
        #expect(!timed.isRunning)
        let cancelled = process("/bin/sleep", ["5"])
        let task = Task { try await NativeOwnedProcess.run(cancelled, timeout: .seconds(10)) }
        try await Task.sleep(for: .milliseconds(40))
        task.cancel()
        await #expect(throws: CancellationError.self) { try await task.value }
        #expect(!cancelled.isRunning)
    }

    @Test func changedHelperIsRejected() throws {
        let location = try root().appendingPathComponent("helper")
        try Data([1, 2, 3]).write(to: location)
        #expect(throws: NativeModelCompiler.Failure.self) {
            try NativeModelCompiler(executable: location, expectedDigest: String(repeating: "0", count: 64))
        }
    }
}
#endif
