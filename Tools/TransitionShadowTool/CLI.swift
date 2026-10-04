import Foundation

struct ShadowRequest: Decodable, Sendable {
    let schemaVersion: Int; let mode: String; let root: String; let pairs: [TransitionPair]
}

@main struct TransitionShadowCLI {
    static func main() async {
        do { try await run() }
        catch { FileHandle.standardError.write(Data("transition-shadow: \(error)\n".utf8)); exit(2) }
    }
    static func run() async throws {
        let args = Array(CommandLine.arguments.dropFirst())
        guard args.count == 8 else { throw TransitionFailure.invalidRequest }
        var options: [String:String] = [:]
        for i in stride(from:0,to:args.count,by:2) {
            guard ["--bundle","--manifest-sha256","--request","--output"].contains(args[i]),options[args[i]] == nil
            else { throw TransitionFailure.invalidRequest }; options[args[i]] = args[i+1]
        }
        let output = URL(fileURLWithPath:options["--output"]!).standardizedFileURL
        guard !FileManager.default.fileExists(atPath:output.path),
              output.deletingLastPathComponent().resolvingSymlinksInPath() == output.deletingLastPathComponent()
        else { throw TransitionFailure.outputCollision }
        let requestURL = URL(fileURLWithPath:options["--request"]!)
        guard (try requestURL.resourceValues(forKeys:[.fileSizeKey]).fileSize ?? Int.max) <= 1_048_576
        else { throw TransitionFailure.invalidRequest }
        let bytes = try Data(contentsOf:requestURL); let raw = try StrictJSON.object(bytes)
        guard Set(raw.keys) == ["schemaVersion","mode","root","pairs"],let pairs = raw["pairs"] as? [[String:Any]]
        else { throw TransitionFailure.invalidRequest }
        for pair in pairs {
            guard Set(pair.keys) == ["id","actionID","beforeObservationID","afterObservationID","before","after"]
            else { throw TransitionFailure.invalidRequest }
            for name in ["before","after"] {
                guard let frame = pair[name] as? [String:Any], Set(frame.keys) == ["path","sha256"] else { throw TransitionFailure.invalidRequest }
            }
        }
        let request = try JSONDecoder().decode(ShadowRequest.self,from:bytes)
        guard request.schemaVersion == 1,["off","encode","score"].contains(request.mode),
              !request.pairs.isEmpty,request.pairs.count <= 128,
              Set(request.pairs.map(\.id)).count == request.pairs.count,
              request.pairs.allSatisfy({ [$0.id,$0.actionID,$0.beforeObservationID,$0.afterObservationID].allSatisfy { !$0.isEmpty && $0.utf8.count <= 512 } })
        else { throw TransitionFailure.invalidRequest }
        let root = URL(fileURLWithPath:request.root).standardizedFileURL
        guard root.path != "/",root.resolvingSymlinksInPath() == root else { throw TransitionFailure.invalidPath }
        let start = ProcessInfo.processInfo.systemUptime
        let observer: TransitionChangeObserver?
        if request.mode == "score" {
            observer = try TransitionChangeObserver(bundle:URL(fileURLWithPath:options["--bundle"]!).standardizedFileURL,
                manifestSHA256:options["--manifest-sha256"]!)
        } else { observer = nil }
        let loadSeconds = ProcessInfo.processInfo.systemUptime-start
        var results: [[String:Any]] = []; var failed = 0
        var encoder = TransitionEncoder()
        for pair in request.pairs {
            var result: [String:Any] = ["id":pair.id,"actionID":pair.actionID,
                "beforeObservationID":pair.beforeObservationID,"afterObservationID":pair.afterObservationID,
                "beforeSHA256":pair.before.sha256,"afterSHA256":pair.after.sha256]
            if request.mode == "off" { result["state"] = "skipped"; results.append(result); continue }
            do {
                let encodeStart = ProcessInfo.processInfo.systemUptime
                let tensor = try encoder.pair(pair,root:root)
                result["preprocessingSeconds"] = ProcessInfo.processInfo.systemUptime-encodeStart
                result["encodedSHA256"] = tensor.withUnsafeBytes { TransitionContract.sha(Data($0)) }
                if let observer {
                    let inferenceStart = ProcessInfo.processInfo.systemUptime
                    let probability = try await observer.predict(tensor)
                    result["inferenceSeconds"] = ProcessInfo.processInfo.systemUptime-inferenceStart
                    result["probability"] = probability
                    result["decision"] = try TransitionContract.decision(probability)
                    result["state"] = "scored"
                } else { result["state"] = "encoded" }
            } catch {
                result["state"] = "failed"; result["error"] = String(describing:error); failed += 1
            }
            results.append(result)
        }
        if let observer { try await observer.verifyUnchanged() }
        let tree = if let observer { observer.modelTreeSHA256 } else { "not_loaded" }
        let reply: [String:Any] = ["schemaVersion":1,"task":"focus-change-only","mode":request.mode,
            "requestSHA256":TransitionContract.sha(bytes),"modelLoaded":observer != nil,
            "modelID":observer?.modelID ?? TransitionContract.modelID,"compiledTreeSHA256":tree,
            "inputEncoding":TransitionContract.encoding,"backend":"cpuOnly",
            "changedThreshold":0.85,"unchangedThreshold":0.15,"releaseEligible":false,
            "loadSeconds":loadSeconds,"elapsedSeconds":ProcessInfo.processInfo.systemUptime-start,
            "failed":failed,"results":results]
        try JSONSerialization.data(withJSONObject:reply,options:[.prettyPrinted,.sortedKeys]).write(to:output,options:.withoutOverwriting)
        if failed > 0 { exit(1) }
    }
}
