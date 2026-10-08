#if os(macOS)
import CoreML
import Darwin
import Foundation

/// Internal local-install prototype. It does not download or select active models.
actor NativeModelInstaller {
    enum Failure: Error { case busy, collision, unsafeRoot, insufficientSpace, invalidReceipt, staleHost, cleanupPending }
    enum State: String, Codable, Sendable { case absent, installing, ready, failed }
    struct Receipt: Codable, Sendable {
        let schemaVersion: Int
        let state: State
        let archiveSHA256: String
        let sourceDigest: String?
        let compiledDigest: String?
        let host: String
        let sourceName: String
        let compilerDigest: String?
    }
    private(set) var state: State = .absent
    private var busy = false
    let root: URL
    let compiler: NativeModelCompiler?
    let availableBytes: @Sendable (URL) throws -> Int

    init(root: URL, compiler: NativeModelCompiler? = nil,
         availableBytes: @escaping @Sendable (URL) throws -> Int = {
             try $0.resourceValues(forKeys: [.volumeAvailableCapacityKey]).volumeAvailableCapacity ?? 0
         }) throws {
        let root = root.standardizedFileURL
        guard root.isFileURL, root.path == root.resolvingSymlinksInPath().path,
              try root.resourceValues(forKeys: [.isDirectoryKey]).isDirectory == true else { throw Failure.unsafeRoot }
        self.root = root
        self.compiler = compiler
        self.availableBytes = availableBytes
    }

    /// Preserve failed attempts. Return a new compiled path only after all checks pass.
    func install(archive: ModelArchive, sourceName: String,
                 validate: @Sendable (URL) async throws -> Void) async throws -> URL {
        guard !busy else { throw Failure.busy }
        guard ModelArchive.validPath(sourceName), !sourceName.contains("/"), sourceName.hasSuffix(".mlpackage"),
              archive.members.contains(where: { $0.path.hasPrefix(sourceName + "/") }) else {
            throw ModelArchive.Failure.invalidInventory
        }
        busy = true
        defer { busy = false }
        try Task.checkCancellation()
        let digest = ModelArchive.hash(archive.bytes)
        guard root.path == root.resolvingSymlinksInPath().path else { throw Failure.unsafeRoot }
        let destination = root.appendingPathComponent(digest)
        guard !FileManager.default.fileExists(atPath: destination.path) else { throw Failure.collision }
        let free = try availableBytes(root)
        let required = archive.bytes.count + archive.members.reduce(0) { $0 + $1.bytes } + 128 * 1024 * 1024
        guard free > required else { throw Failure.insufficientSpace }
        // A directory claim also excludes another installer instance using this root.
        let claim = root.appendingPathComponent("installing-" + digest)
        guard claim.path.withCString({ Darwin.mkdir($0, 0o700) }) == 0 else {
            if errno == EEXIST { throw Failure.busy }
            throw NSError(domain: NSPOSIXErrorDomain, code: Int(errno))
        }
        // Remove only this operation's empty claim. Interrupted claims need explicit review.
        defer { _ = claim.path.withCString { Darwin.rmdir($0) } }
        let stage = root.appendingPathComponent("attempt-" + UUID().uuidString)
        try FileManager.default.createDirectory(at: stage, withIntermediateDirectories: false, attributes: [.posixPermissions: 0o700])
        state = .installing
        let host = Self.hostIdentity
        func writeReceipt(_ state: State, _ source: String? = nil, _ compiled: String? = nil) throws {
            let receipt = Receipt(schemaVersion: 2, state: state, archiveSHA256: digest,
                                  sourceDigest: source, compiledDigest: compiled, host: host,
                                  sourceName: sourceName, compilerDigest: compiler?.expectedDigest)
            try JSONEncoder().encode(receipt).write(to: stage.appendingPathComponent("receipt.json"), options: .atomic)
        }
        do {
            try writeReceipt(.installing)
            let zip = stage.appendingPathComponent("verified-input.zip")
            try archive.bytes.write(to: zip, options: .withoutOverwriting)
            let payload = stage.appendingPathComponent("payload")
            try FileManager.default.createDirectory(at: payload, withIntermediateDirectories: false, attributes: [.posixPermissions: 0o700])
            try await Self.extract(zip: zip, payload: payload)
            try archive.verifyExtracted(at: payload)
            try Task.checkCancellation()
            let source = payload.appendingPathComponent(sourceName)
            try Self.validateSourcePackage(source)
            let sourceDigest = try NativeUILocalDetector.digest(at: source)
            guard let compiler else { throw NativeModelCompiler.Failure.unavailable }
            let compiled = try await compiler.compile(source: source, expectedSourceDigest: sourceDigest)
            try Task.checkCancellation()
            try archive.verifyExtracted(at: payload)
            try await validate(compiled)
            try Task.checkCancellation()
            let compiledDigest = try NativeUILocalDetector.digest(at: compiled)
            try writeReceipt(.ready, sourceDigest, compiledDigest)
            try FileManager.default.moveItem(at: stage, to: destination)
            guard claim.path.withCString({ Darwin.rmdir($0) }) == 0 else { throw Failure.cleanupPending }
            state = .ready
            return destination.appendingPathComponent("model.mlmodelc")
        } catch {
            state = .failed
            try? writeReceipt(.failed)
            throw error
        }
    }

    /// Recheck a completed installation after restart. Never resume an unfinished attempt.
    func recover(archive: ModelArchive, sourceName: String) throws -> URL {
        guard !busy else { throw Failure.busy }
        state = .failed
        guard ModelArchive.validPath(sourceName), !sourceName.contains("/"), sourceName.hasSuffix(".mlpackage") else {
            throw Failure.invalidReceipt
        }
        let digest = ModelArchive.hash(archive.bytes)
        guard !FileManager.default.fileExists(atPath: root.appendingPathComponent("installing-" + digest).path) else {
            throw Failure.busy
        }
        let directory = root.appendingPathComponent(digest)
        guard directory.path == directory.resolvingSymlinksInPath().path else { throw Failure.unsafeRoot }
        let receiptURL = directory.appendingPathComponent("receipt.json")
        let info = try receiptURL.resourceValues(forKeys: [.isRegularFileKey, .isSymbolicLinkKey, .fileSizeKey])
        guard info.isRegularFile == true, info.isSymbolicLink != true, let size = info.fileSize, size <= 16_384 else {
            throw Failure.invalidReceipt
        }
        let receipt = try JSONDecoder().decode(Receipt.self, from: Data(contentsOf: receiptURL))
        guard receipt.schemaVersion == 2, receipt.state == .ready, receipt.archiveSHA256 == digest,
              receipt.sourceName == sourceName, let compiler,
              receipt.compilerDigest == compiler.expectedDigest else { throw Failure.invalidReceipt }
        guard receipt.host == Self.hostIdentity else { throw Failure.staleHost }
        let payload = directory.appendingPathComponent("payload")
        try archive.verifyExtracted(at: payload)
        let source = payload.appendingPathComponent(sourceName)
        let compiled = directory.appendingPathComponent("model.mlmodelc")
        guard try NativeUILocalDetector.digest(at: source) == receipt.sourceDigest,
              try NativeUILocalDetector.digest(at: compiled) == receipt.compiledDigest else { throw Failure.invalidReceipt }
        state = .ready
        return compiled
    }

    static var hostIdentity: String {
        ProcessInfo.processInfo.operatingSystemVersionString + "|" + architecture
    }

    private static var architecture: String {
        #if arch(arm64)
        "arm64"
        #elseif arch(x86_64)
        "x86_64"
        #else
        "unknown"
        #endif
    }

    // Core ML can abort the process for malformed package manifests.
    // Check the supported package structure before calling its compiler.
    static func validateSourcePackage(_ source: URL) throws {
        let url = source.appendingPathComponent("Manifest.json")
        let size = try url.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? Int.max
        guard size <= 65_536,
              let object = try JSONSerialization.jsonObject(with: Data(contentsOf: url)) as? [String: Any],
              object["fileFormatVersion"] as? String == "1.0.0",
              let root = object["rootModelIdentifier"] as? String,
              let entries = object["itemInfoEntries"] as? [String: [String: String]],
              let model = entries[root], model["path"]?.hasSuffix(".mlmodel") == true,
              !entries.isEmpty, entries.count <= 256 else { throw ModelArchive.Failure.invalidInventory }
        for entry in entries.values {
            guard let path = entry["path"], ModelArchive.validPath(path),
                  entry["name"] != nil, entry["author"] != nil, entry["description"] != nil,
                  FileManager.default.fileExists(atPath: source.appendingPathComponent("Data").appendingPathComponent(path).path)
            else { throw ModelArchive.Failure.invalidInventory }
        }
    }

    private static func extract(zip: URL, payload: URL) async throws {
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/ditto")
        process.arguments = ["-x", "-k", "--norsrc", "--noextattr", "--noacl", zip.path, payload.path]
        process.standardOutput = FileHandle.nullDevice
        process.standardError = FileHandle.nullDevice
        try await NativeOwnedProcess.run(process, timeout: .seconds(30))
    }
}
#endif
