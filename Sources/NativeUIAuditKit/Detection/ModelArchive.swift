import CryptoKit
import Foundation

/// Internal archive contract. The caller supplies an independently trusted inventory.
struct ModelArchiveMember: Codable, Sendable, Equatable {
    let path: String
    let bytes: Int
    let sha256: String
}

struct ModelArchive: Sendable {
    enum Failure: Error { case invalidArchive, invalidInventory, hashMismatch }
    let bytes: Data
    let members: [ModelArchiveMember]

    static func hash(_ bytes: Data) -> String {
        SHA256.hash(data: bytes).map { String(format: "%02x", $0) }.joined()
    }

    static func crc32(_ bytes: Data) -> UInt32 {
        var crc: UInt32 = 0xffffffff
        for byte in bytes {
            crc ^= UInt32(byte)
            for _ in 0..<8 { crc = (crc >> 1) ^ ((crc & 1) == 1 ? 0xedb88320 : 0) }
        }
        return ~crc
    }

    static func validPath(_ path: String) -> Bool {
        !path.isEmpty && path.utf8.count <= 512 && path.utf8.allSatisfy { $0 >= 32 && $0 < 127 }
        && !path.contains("\\") && !path.contains(":")
        && path.split(separator: "/", omittingEmptySubsequences: false).allSatisfy {
            !$0.isEmpty && $0 != "." && $0 != ".."
        }
    }

    init(bytes: Data, expectedSHA256: String, members: [ModelArchiveMember]) throws {
        guard bytes.count <= 32 * 1024 * 1024, Self.hash(bytes) == expectedSHA256 else {
            throw Failure.hashMismatch
        }
        guard !members.isEmpty, members.count <= 256,
              Set(members.map { $0.path.lowercased() }).count == members.count,
              members.allSatisfy({ Self.validPath($0.path) && $0.bytes >= 0 && $0.bytes <= 64 * 1024 * 1024 }),
              members.reduce(0, { $0 + $1.bytes }) <= 64 * 1024 * 1024 else { throw Failure.invalidInventory }
        var offset = 0
        var entries: [(offset: Int, name: Data, crc: Int, size: Int)] = []
        let expected = Dictionary(uniqueKeysWithValues: members.map { ($0.path, $0) })
        var seen = Set<String>()
        func integer(_ start: Int, _ count: Int) throws -> Int {
            guard start >= 0, start <= bytes.count - count else { throw Failure.invalidArchive }
            return (0..<count).reduce(0) { $0 | (Int(bytes[start + $1]) << (8 * $1)) }
        }
        func slice(_ start: Int, _ count: Int) throws -> Data {
            guard count >= 0, start >= 0, start <= bytes.count - count else { throw Failure.invalidArchive }
            return bytes.subdata(in: start..<(start + count))
        }
        // Accept only the stored, regular-file ZIP format made by model_release.py.
        while try integer(offset, 4) == 0x04034b50 {
            guard entries.count < 256, try integer(offset + 4, 2) == 20,
                  try integer(offset + 6, 2) == 0, try integer(offset + 8, 2) == 0,
                  try integer(offset + 28, 2) == 0 else { throw Failure.invalidArchive }
            let size = try integer(offset + 18, 4)
            guard size == (try integer(offset + 22, 4)) else { throw Failure.invalidArchive }
            let name = try slice(offset + 30, integer(offset + 26, 2))
            guard let path = String(data: name, encoding: .utf8), let member = expected[path],
                  seen.insert(path).inserted, member.bytes == size else { throw Failure.invalidInventory }
            let payload = try slice(offset + 30 + name.count, size)
            guard Self.hash(payload) == member.sha256,
                  Int(Self.crc32(payload)) == (try integer(offset + 14, 4)) else { throw Failure.hashMismatch }
            entries.append((offset, name, try integer(offset + 14, 4), size))
            offset += 30 + name.count + size
        }
        let centralStart = offset
        for entry in entries {
            guard try integer(offset, 4) == 0x02014b50,
                  try integer(offset + 4, 2) == 0x0314,
                  try integer(offset + 6, 2) == 20,
                  try integer(offset + 8, 2) == 0, try integer(offset + 10, 2) == 0,
                  try integer(offset + 16, 4) == entry.crc,
                  try integer(offset + 20, 4) == entry.size,
                  try integer(offset + 24, 4) == entry.size,
                  try integer(offset + 28, 2) == entry.name.count,
                  try integer(offset + 30, 2) == 0, try integer(offset + 32, 2) == 0,
                  try integer(offset + 34, 2) == 0, try integer(offset + 36, 2) == 0,
                  try integer(offset + 38, 4) == (0o100644 << 16),
                  try integer(offset + 42, 4) == entry.offset,
                  try slice(offset + 46, entry.name.count) == entry.name else { throw Failure.invalidArchive }
            offset += 46 + entry.name.count
        }
        guard seen.count == members.count,
              try integer(offset, 4) == 0x06054b50,
              try integer(offset + 4, 2) == 0, try integer(offset + 6, 2) == 0,
              try integer(offset + 8, 2) == entries.count,
              try integer(offset + 10, 2) == entries.count,
              try integer(offset + 12, 4) == offset - centralStart,
              try integer(offset + 16, 4) == centralStart,
              try integer(offset + 20, 2) == 0,
              offset + 22 == bytes.count else { throw Failure.invalidArchive }
        self.bytes = bytes
        self.members = members
    }

    func verifyExtracted(at root: URL) throws {
        var remaining = Dictionary(uniqueKeysWithValues: members.map { ($0.path, $0) })
        var pending = [root]
        var directories = 0
        while let directory = pending.popLast() {
            directories += 1
            guard directories <= 1024 else { throw Failure.invalidArchive }
            for url in try FileManager.default.contentsOfDirectory(at: directory, includingPropertiesForKeys: nil) {
                let info = try url.resourceValues(forKeys: [.isDirectoryKey, .isSymbolicLinkKey, .isRegularFileKey, .fileSizeKey])
                guard info.isSymbolicLink != true else { throw Failure.invalidArchive }
                if info.isDirectory == true { pending.append(url); continue }
                let name = String(url.path.dropFirst(root.path.count + 1))
                guard info.isRegularFile == true, let member = remaining.removeValue(forKey: name),
                      info.fileSize == member.bytes,
                      Self.hash(try Data(contentsOf: url)) == member.sha256 else { throw Failure.hashMismatch }
            }
        }
        guard remaining.isEmpty else { throw Failure.invalidInventory }
    }
}
