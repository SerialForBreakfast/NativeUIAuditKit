import Foundation
import FixtureExperiments
import Darwin

func output<T: Encodable>(_ value: T) throws {
    let encoder = JSONEncoder(); encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
    FileHandle.standardOutput.write(try encoder.encode(value)); print("")
}

do {
    let args = Array(CommandLine.arguments.dropFirst())
    guard let action = args.first else { throw ExperimentError("Expected validate, preflight, run, status, cancel, reconcile, or make-reference.") }
    var values = [String: String](); var flags = Set<String>(); var index = 1
    while index < args.count {
        let key = args[index]
        if ["--retry-failed", "--clear-cancel"].contains(key) {
            guard flags.insert(key).inserted else { throw ExperimentError("duplicate_option") }
            index += 1
        } else {
            guard key.hasPrefix("--"), index + 1 < args.count, values[key] == nil else { throw ExperimentError("invalid_option") }
            values[key] = args[index + 1]; index += 2
        }
    }
    func value(_ name: String) throws -> String {
        guard let v = values[name] else { throw ExperimentError("missing_" + name) }; return v
    }
    func url(_ name: String) throws -> URL { URL(fileURLWithPath: try value(name)).standardizedFileURL }
    let allowed = action == "make-reference" ? ["--output", "--renderer-source-sha256"] :
                  action == "configure" ? ["--workspace", "--renderer", "--renderer-source", "--output", "--max-load"] :
                  action == "cancel" ? ["--workspace", "--experiment-id"] :
                  action == "validate" ? ["--bundle"] : ["--bundle", "--host", "--max-jobs"]
    guard Set(values.keys).isSubset(of: Set(allowed)), action == "run" || flags.isEmpty else { throw ExperimentError("unsupported_option") }
    if action == "configure" {
        guard let load = Double(values["--max-load"] ?? "8") else { throw ExperimentError("invalid_load_limit") }
        try configureHost(workspace: url("--workspace"), renderer: url("--renderer"), source: url("--renderer-source"),
                          output: url("--output"), maxLoad: load)
        try output(["state": "configured"])
    } else if action == "cancel" {
        let result = try requestCancellation(workspace: url("--workspace"), experimentID: value("--experiment-id"))
        try output(result); exit(result.exitCode)
    } else if action == "make-reference" {
        try makeReference(at: url("--output"), rendererSourceSHA256: value("--renderer-source-sha256"))
        try output(["state": "created"])
    } else if action == "validate" {
        let e = try validateBundle(url("--bundle")); try output(["state": "valid", "experimentID": e.id])
    } else {
        let executable = URL(fileURLWithPath: CommandLine.arguments[0]).resolvingSymlinksInPath()
        let runner = try Runner(bundle: url("--bundle"), hostFile: url("--host"), runnerIdentity: fileDigest(executable))
        let result: OperationResult
        switch action {
        case "preflight": result = try runner.preflight()
        case "status": result = try runner.status()
        case "cancel": result = try runner.cancel()
        case "reconcile": result = try runner.reconcile()
        case "run":
            guard let count = Int(values["--max-jobs"] ?? "100") else { throw ExperimentError("invalid_batch_limit") }
            result = try runner.run(maxJobs: count, retryFailed: flags.contains("--retry-failed"), clearCancel: flags.contains("--clear-cancel"))
        default: throw ExperimentError("unknown_action")
        }
        try output(result); exit(result.exitCode)
    }
} catch {
    let busy = String(describing: error) == "resource_busy"
    try? output(["state": busy ? "deferred_resources" : "failed", "reason": String(describing: error)])
    exit(busy ? 75 : 1)
}
