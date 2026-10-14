#if os(macOS)
import CoreML
import Darwin
import Foundation

/// The host supplies a verified helper. This type does not discover or download executables.
struct NativeModelCompiler: Sendable {
    enum Failure: Error { case unavailable, identityChanged, timeout, workerFailed(Int32), missingOutput }
    let executable: URL
    let expectedDigest: String
    let timeout: Duration

    init(executable: URL, expectedDigest: String, timeout: Duration = .seconds(120)) throws {
        guard timeout > .zero, timeout <= .seconds(120) else { throw Failure.unavailable }
        let url = executable.resolvingSymlinksInPath().standardizedFileURL
        guard try Self.digest(url) == expectedDigest else { throw Failure.identityChanged }
        self.executable = url
        self.expectedDigest = expectedDigest
        self.timeout = timeout
    }

    static func digest(_ url: URL) throws -> String {
        let info = try url.resourceValues(forKeys: [.isRegularFileKey, .isSymbolicLinkKey, .fileSizeKey])
        guard info.isRegularFile == true, info.isSymbolicLink != true,
              let count = info.fileSize, count <= 128 * 1024 * 1024 else { throw Failure.unavailable }
        let bytes = try Data(contentsOf: url)
        guard bytes.count == count else { throw Failure.identityChanged }
        return ModelArchive.hash(bytes)
    }

    func compile(source: URL, expectedSourceDigest: String) async throws -> URL {
        try Task.checkCancellation()
        guard try Self.digest(executable) == expectedDigest else { throw Failure.identityChanged }
        let stage = source.deletingLastPathComponent().deletingLastPathComponent()
        let scratch = stage.appendingPathComponent("compiler-scratch")
        try FileManager.default.createDirectory(at: scratch, withIntermediateDirectories: false, attributes: [.posixPermissions: 0o700])
        let process = Process()
        process.executableURL = executable
        process.arguments = ["--compile-v1", source.path, expectedSourceDigest]
        process.environment = ["TMPDIR": scratch.path, "PATH": "/usr/bin:/bin", "LANG": "C"]
        process.standardInput = FileHandle.nullDevice
        process.standardOutput = FileHandle.nullDevice
        process.standardError = FileHandle.nullDevice
        try await NativeOwnedProcess.run(process, timeout: timeout)
        guard try Self.digest(executable) == expectedDigest else { throw Failure.identityChanged }
        let output = stage.appendingPathComponent("model.mlmodelc")
        guard FileManager.default.fileExists(atPath: output.path) else { throw Failure.missingOutput }
        return output
    }
}

enum NativeOwnedProcess {
    static func run(_ process: Process, timeout: Duration) async throws {
        try Task.checkCancellation()
        try process.run()
        let deadline = ContinuousClock.now.advanced(by: timeout)
        do {
            while process.isRunning {
                try Task.checkCancellation()
                guard ContinuousClock.now < deadline else { throw NativeModelCompiler.Failure.timeout }
                try await Task.sleep(for: .milliseconds(20))
            }
            try Task.checkCancellation()
            guard process.terminationStatus == 0 else {
                throw NativeModelCompiler.Failure.workerFailed(process.terminationStatus)
            }
        } catch {
            // This process belongs to this operation. Never target a shared service.
            if process.isRunning { Darwin.kill(process.processIdentifier, SIGKILL) }
            process.waitUntilExit()
            throw error
        }
    }
}

/// The helper supports one fixed operation. It is not an arbitrary command service.
package enum NativeModelCompileOperation {
    package static func run(arguments: [String]) async throws {
        guard arguments.count == 3, arguments[0] == "--compile-v1" else {
            throw NativeModelCompiler.Failure.unavailable
        }
        let source = URL(fileURLWithPath: arguments[1]).standardizedFileURL
        guard source.path == source.resolvingSymlinksInPath().path,
              source.pathExtension == "mlpackage", source.deletingLastPathComponent().lastPathComponent == "payload",
              try NativeUILocalDetector.digest(at: source) == arguments[2] else {
            throw NativeModelCompiler.Failure.identityChanged
        }
        try NativeModelInstaller.validateSourcePackage(source)
        let output = source.deletingLastPathComponent().deletingLastPathComponent().appendingPathComponent("model.mlmodelc")
        guard !FileManager.default.fileExists(atPath: output.path) else { throw NativeModelInstaller.Failure.collision }
        let temporary = try await MLModel.compileModel(at: source)
        // Loading also stays inside the helper before the host validates the result.
        let configuration = MLModelConfiguration()
        configuration.computeUnits = .cpuOnly
        _ = try await MLModel.load(contentsOf: temporary, configuration: configuration)
        guard try NativeUILocalDetector.digest(at: source) == arguments[2] else {
            throw NativeModelCompiler.Failure.identityChanged
        }
        try FileManager.default.copyItem(at: temporary, to: output)
    }
}
#endif
