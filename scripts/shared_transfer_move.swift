// Used only after verified-SMB exclusive rename returns ENOTSUP.
import Foundation

guard CommandLine.arguments.count == 3 else { exit(2) }
do {
    try FileManager.default.moveItem(
        atPath: CommandLine.arguments[1], toPath: CommandLine.arguments[2])
} catch {
    // Avoid dumping source/destination paths or host-account details into logs.
    fputs("Non-overwriting publication failed.\n", stderr)
    exit(2)
}
