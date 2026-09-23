import CryptoKit
import Foundation

/// Internal load-bound content identity, never a filesystem path in public output.
enum FocusModelIdentity {
    enum Failure: Error { case invalidArtifact, changedDuringLoad }

    static func digest(_ root: URL) throws -> String {
        let root = root.resolvingSymlinksInPath().standardizedFileURL
        guard try root.resourceValues(forKeys: [.isDirectoryKey]).isDirectory == true else {
            throw Failure.invalidArtifact
        }
        var pending = [root]
        var directories = 0
        var records: [(String, Int, String)] = []
        var total = 0
        while let directory = pending.popLast() {
            directories += 1
            guard directories <= 1024 else { throw Failure.invalidArtifact }
            // Throw on enumeration failures instead of sealing a silently partial tree.
            for url in try FileManager.default.contentsOfDirectory(at: directory,
                includingPropertiesForKeys: [.isRegularFileKey, .isDirectoryKey, .isSymbolicLinkKey, .fileSizeKey]) {
            let values = try url.resourceValues(forKeys: [.isRegularFileKey, .isDirectoryKey, .isSymbolicLinkKey, .fileSizeKey])
            guard values.isSymbolicLink != true else { throw Failure.invalidArtifact }
            if values.isDirectory == true { pending.append(url); continue }
            guard values.isRegularFile == true, let size = values.fileSize,
                  size >= 0, size <= 64 * 1024 * 1024, records.count < 1024 else { throw Failure.invalidArtifact }
            total += size
            guard total <= 128 * 1024 * 1024 else { throw Failure.invalidArtifact }
            let name = String(url.path.dropFirst(root.path.count + 1))
            guard !name.contains("\n"), !name.contains("\0") else { throw Failure.invalidArtifact }
            let bytes = try Data(contentsOf: url)
            guard bytes.count == size else { throw Failure.invalidArtifact }
            records.append((name, size, SHA256.hash(data: bytes).map { String(format: "%02x", $0) }.joined()))
            }
        }
        guard !records.isEmpty else { throw Failure.invalidArtifact }
        let canonical = "compiled-tree-sha256-v1\n" + records.sorted { $0.0 < $1.0 }
            .map { "\($0.0)\0\($0.1)\0\($0.2)\n" }.joined()
        return SHA256.hash(data: Data(canonical.utf8)).map { String(format: "%02x", $0) }.joined()
    }
}

struct FocusClassifierLoad: Sendable {
    let classifier: FocusRingClassifier?
    let fallbackReason: String?
}
