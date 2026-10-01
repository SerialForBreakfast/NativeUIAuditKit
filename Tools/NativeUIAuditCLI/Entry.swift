import Foundation
import Darwin

struct CLIArguments: Sendable {
    let command: String
    let input: String?
    let root: String
    let options: ScanOptions
    let format: String
    static let usage = """
    nativeui-audit doctor [--root DIR]
    nativeui-audit scan IMAGE [--root DIR] [--platform auto|iOS|tvOS]
                         [--min-confidence 0.5] [--no-ocr] [--strict] [--format json|table]
    nativeui-audit scan-batch DIR [same options]
    nativeui-audit mcp --root DIR

    CLI root defaults to cwd; relative inputs resolve against root. MCP requires an explicit root.
    Batch: nonrecursive visible PNG/JPEG entries, at most 128; each <=50MiB/24MP.
    Strict fails processing degradation, not heuristic audit warnings. No navigation or training.
    """
    static func parse(_ args: [String], cwd: String = FileManager.default.currentDirectoryPath) throws -> CLIArguments {
        guard let command = args.first, ["doctor", "scan", "scan-batch", "mcp"].contains(command) else {
            throw AuditError("usage", usage)
        }
        var options = ScanOptions(); var root = cwd; var format = "json"
        var positional: [String] = []; var seen = Set<String>(); var i = 1
        while i < args.count {
            let arg = args[i]
            if arg.hasPrefix("--") {
                guard seen.insert(arg).inserted else { throw AuditError("usage", "Duplicate option \(arg)") }
                if arg == "--no-ocr" { options.ocr = false }
                else if arg == "--strict" { options.strict = true }
                else if ["--root", "--platform", "--min-confidence", "--format"].contains(arg) {
                    i += 1
                    guard i < args.count else { throw AuditError("usage", "Missing value for \(arg)") }
                    switch arg {
                    case "--root": root = args[i]
                    case "--platform": options.platform = args[i]
                    case "--min-confidence":
                        guard let n = Double(args[i]) else { throw AuditError("usage", "Invalid confidence") }
                        options.minConfidence = n
                    default: format = args[i]
                    }
                } else { throw AuditError("usage", "Unknown option \(arg)") }
            } else { positional.append(arg) }
            i += 1
        }
        try options.validate()
        guard ["json", "table"].contains(format),
              positional.count == (["scan", "scan-batch"].contains(command) ? 1 : 0) else {
            throw AuditError("usage", usage)
        }
        if ["doctor", "mcp"].contains(command), !seen.isSubset(of: ["--root"]) {
            throw AuditError("usage", "\(command) accepts only --root")
        }
        if command == "mcp", !seen.contains("--root") { throw AuditError("usage", "MCP requires --root DIR") }
        return CLIArguments(command: command, input: positional.first, root: root, options: options, format: format)
    }
}

@main
enum AuditMain {
    static func main() async {
        do {
            let args = Array(CommandLine.arguments.dropFirst())
            if args == ["--help"] || args == ["help"] { print(CLIArguments.usage); return }
            let cli = try CLIArguments.parse(args)
            let service = AuditService(scope: try FileScope(cli.root))
            // Apple runtimes may log to stdout. Reserve the original pipe for our output.
            let protocolFD = dup(STDOUT_FILENO)
            guard protocolFD >= 0, dup2(STDERR_FILENO, STDOUT_FILENO) >= 0 else {
                throw AuditError("stdio_failed", "Cannot isolate structured output.")
            }
            let output = FileHandle(fileDescriptor: protocolFD, closeOnDealloc: true)
            if cli.command == "mcp" {
                let server = MCPServer(service: service)
                var reader = LineReader()
                while let line = try reader.next() {
                    if let reply = await server.handle(line) {
                        var data = try reply.data(); data.append(10)
                        try output.write(contentsOf: data)
                    }
                }
                return
            }
            let payload: JSON
            switch cli.command {
            case "doctor": payload = await service.doctor()
            case "scan": payload = await service.scan(cli.input ?? "", options: cli.options)
            default: payload = try await service.batch(cli.input ?? "", options: cli.options)
            }
            if cli.format == "table" { try output.write(contentsOf: Data((table(payload) + "\n").utf8)) }
            else { try output.write(contentsOf: payload.data() + Data([10])) }
            if payload["strictFailure"]?.boolean == true { exit(1) }
        } catch {
            let failure = AuditError.wrap(error)
            let payload = JSON.object(["schemaVersion": .number(1), "status": .string("failed"), "error": failure.json])
            if let data = try? payload.data() { try? FileHandle.standardError.write(contentsOf: data + Data([10])) }
            exit(2)
        }
    }

    static func table(_ payload: JSON) -> String {
        if case .array(let results) = payload["results"] {
            return "INPUT\tSTATUS\n" + results.map { "\($0["input"]?.string ?? "")\t\($0["status"]?.string ?? "")" }.joined(separator: "\n")
        }
        var lines = ["Status: \(payload["status"]?.string ?? "unknown")"]
        if let error = payload["error"]?["message"]?.string { lines.append(error) }
        if case .array(let elements) = payload["runtime"]?["result"]?["elements"] {
            lines.append("TYPE\tCONFIDENCE\tFOCUSED\tTEXT")
            for e in elements {
                let text = (e["visibleText"]?.string ?? "").replacingOccurrences(of: "\n", with: " ").replacingOccurrences(of: "\t", with: " ")
                lines.append("\(e["elementType"]?.string ?? "")\t\(e["confidence"]?.number ?? 0)\t\(e["state"]?["isFocused"]?.boolean?.description ?? "unknown")\t\(text)")
            }
        }
        return lines.joined(separator: "\n")
    }
}
