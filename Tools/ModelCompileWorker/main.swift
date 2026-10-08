import Foundation
import NativeUIAuditKitRuntime

@main struct ModelCompileWorker {
    static func main() async {
        do {
            try await NativeModelCompileOperation.run(arguments: Array(CommandLine.arguments.dropFirst()))
        } catch {
            // The parent retains the attempt and reports this failure.
            exit(1)
        }
    }
}
