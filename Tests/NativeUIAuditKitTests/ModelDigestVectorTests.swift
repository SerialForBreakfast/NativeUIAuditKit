import Foundation
import Testing
@testable import NativeUIAuditKitRuntime

struct ModelDigestVectorTests {
    @Test func canonicalVectorMatchesIndependentCalculation() throws {
        let project = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
        let root = project.appendingPathComponent(".build/digest-vector-tests/" + UUID().uuidString)
        try FileManager.default.createDirectory(at: root.appendingPathComponent("nested"), withIntermediateDirectories: true)
        // Create files in reverse order to check canonical sorting.
        try Data("focus\n".utf8).write(to: root.appendingPathComponent("nested/b.txt"))
        try Data([0, 1, 255]).write(to: root.appendingPathComponent("a.bin"))
        #expect(try FocusModelIdentity.digest(root) == "7d6c6b1e9b9bf952e0963de83fc3348c5d599d54ad6c5110edf13ccbf1f6cac7")
        try FileManager.default.createDirectory(at: root.appendingPathComponent("empty"), withIntermediateDirectories: false)
        #expect(try FocusModelIdentity.digest(root) == "7d6c6b1e9b9bf952e0963de83fc3348c5d599d54ad6c5110edf13ccbf1f6cac7")
    }
}
