// QA666: Apple Foundation Model (on-device SystemLanguageModel only) planner bridge.
// It reads 1 JSON request per stdin line and writes 1 JSON reply per stdout line.
// Reply shape matches the Ollama fields that LocalOllamaSession reads:
//   {"message":{"content":"<plan JSON>"},"prompt_eval_count":N,"eval_count":M,"load_duration":0}
// Token counts come from SystemLanguageModel.tokenCount(for:). Prompt tokens include the schema. Image tokens are not countable (see below).
// Each request uses a fresh LanguageModelSession (single turn, no history) and greedy sampling.
// Request: {"prompt":"...","image":"<base64 JPEG or null>","schema":"plan|plan-described|plan-words|press","maxOutput":1500}
// Build: swiftc -O scripts/qa666/fm_bridge.swift -o .build/qa666-fm/fm_bridge
import CoreGraphics
import Foundation
import FoundationModels
import ImageIO

@Generable struct PlanStep {
    @Guide(.anyOf(["focus", "activate", "back"])) var op: String
    var target: String?
    @Guide(.range(1...3)) var times: Int
}

@Generable struct Plan {
    @Guide(.maximumCount(6)) var steps: [PlanStep]
    @Guide(.anyOf(["done", "replan", "abstain"])) var after: String
}

// plan-described: the same fields and limits as Plan, with @Guide descriptions (ADR-0035 stage 2, schema slot).
@Generable struct DescribedStep {
    @Guide(description: "activate moves focus to the target and presses select. focus only moves focus and never presses select. back presses Menu once.",
           .anyOf(["focus", "activate", "back"])) var op: String
    @Guide(description: "The control to use, as named in the task, on the screen or in the snapshot. Null for back.") var target: String?
    @Guide(description: "For activate: how many select presses the task asks for. Otherwise 1.", .range(1...3)) var times: Int
}

@Generable struct DescribedPlan {
    @Guide(description: "The steps for the task. Empty if you abstain.", .maximumCount(6)) var steps: [DescribedStep]
    @Guide(description: "done if the steps complete the task. replan if you must see a new screen first. abstain if the task control is not on this screen or the task cannot be done here.",
           .anyOf(["done", "replan", "abstain"])) var after: String
}

// plan-words: op values in words; the bridge maps them to activate / focus / back (ADR-0035 stage 2, schema slot).
@Generable struct WordStep {
    @Guide(description: "What the remote does to the target.", .anyOf(["press select on", "move focus to", "go back"])) var action: String
    @Guide(description: "The control, as named in the task, on the screen or in the snapshot. Null for go back.") var target: String?
    @Guide(description: "How many times: the number of select presses the task asks for, otherwise 1.", .range(1...3)) var times: Int
}

@Generable struct WordPlan {
    @Guide(description: "The steps for the task. Empty if you abstain.", .maximumCount(6)) var steps: [WordStep]
    @Guide(description: "done if the steps complete the task. replan if you must see a new screen first. abstain if the task control is not on this screen.",
           .anyOf(["done", "replan", "abstain"])) var after: String
}
let wordOps = ["press select on": "activate", "move focus to": "focus", "go back": "back"]

// press: the host's yes/no question for 1 planned target (ADR-0035 host question). Reply {"press": true|false}.
@Generable struct PressAnswer {
    @Guide(description: "true if the task needs the remote to press select on this control. false if the task only needs focus on this control.")
    var press: Bool
}

struct Request: Decodable { let prompt: String; let image: String?; let schema: String; let maxOutput: Int? }

func emit(_ object: [String: Any]) {
    let data = try! JSONSerialization.data(withJSONObject: object, options: [.sortedKeys])
    FileHandle.standardOutput.write(data + Data("\n".utf8))
}

func image(_ base64: String) throws -> CGImage {
    guard let data = Data(base64Encoded: base64), let source = CGImageSourceCreateWithData(data as CFData, nil),
          let cg = CGImageSourceCreateImageAtIndex(source, 0, nil) else { throw NSError(domain: "fm_bridge", code: 2, userInfo: [NSLocalizedDescriptionKey: "image decode failed"]) }
    return cg
}

let model = SystemLanguageModel.default
guard model.isAvailable else { emit(["error": "unavailable: \(model.availability)"]); exit(3) }
emit(["ready": true, "contextSize": model.contextSize, "vision": model.capabilities.contains(.vision),
      "guidedGeneration": model.capabilities.contains(.guidedGeneration)])
let schemaTokens = try await model.tokenCount(for: Plan.generationSchema)
let describedTokens = try await model.tokenCount(for: DescribedPlan.generationSchema)
let wordTokens = try await model.tokenCount(for: WordPlan.generationSchema)
let pressTokens = try await model.tokenCount(for: PressAnswer.generationSchema)

while let line = readLine(strippingNewline: true) {
    var counted: Int? = nil
    do {
        let req = try JSONDecoder().decode(Request.self, from: Data(line.utf8))
        guard ["plan", "plan-described", "plan-words", "press"].contains(req.schema) else { throw NSError(domain: "fm_bridge", code: 4, userInfo: [NSLocalizedDescriptionKey: "unsupported schema \(req.schema)"]) }
        let cg = try req.image.map(image)
        let prompt = Prompt {
            req.prompt
            if let cg { Attachment(cg) }
        }
        // tokenCount(for:) fails (ModelManagerError 1001) for any prompt with an image on macOS 27.0.1, and generation works.
        // For an image prompt, the count is the text and schema only; the reply marks the image tokens as not counted.
        let promptTokens = try await (cg == nil ? model.tokenCount(for: prompt) : model.tokenCount(for: req.prompt)) +
            (["plan": schemaTokens, "plan-described": describedTokens, "plan-words": wordTokens, "press": pressTokens][req.schema] ?? 0)
        counted = promptTokens
        let options = GenerationOptions(samplingMode: .greedy, maximumResponseTokens: req.maxOutput ?? 1_500)
        let session = LanguageModelSession(model: model)
        if req.schema == "press" {
            let r = try await session.respond(to: prompt, generating: PressAnswer.self, options: options)
            let text = String(data: try JSONSerialization.data(withJSONObject: ["press": r.content.press], options: [.sortedKeys]), encoding: .utf8)!
            emit(["message": ["content": text], "prompt_eval_count": promptTokens, "eval_count": try await model.tokenCount(for: r.rawContent.jsonString),
                  "load_duration": 0, "imageTokensCounted": cg == nil ? NSNull() : false, "raw": r.rawContent.jsonString])
            continue
        }
        let parts: [(String, String?, Int)]; let after: String; let raw: GeneratedContent
        if req.schema == "plan" {
            let r = try await session.respond(to: prompt, generating: Plan.self, options: options)
            parts = r.content.steps.map { ($0.op, $0.target, $0.times) }; after = r.content.after; raw = r.rawContent
        } else if req.schema == "plan-words" {
            let r = try await session.respond(to: prompt, generating: WordPlan.self, options: options)
            parts = r.content.steps.map { (wordOps[$0.action] ?? $0.action, $0.target, $0.times) }; after = r.content.after; raw = r.rawContent
        } else {
            let r = try await session.respond(to: prompt, generating: DescribedPlan.self, options: options)
            parts = r.content.steps.map { ($0.op, $0.target, $0.times) }; after = r.content.after; raw = r.rawContent
        }
        let steps: [[String: Any]] = parts.map { (op, target, times) in
            ["op": op, "target": op == "back" ? NSNull() : (target.map { $0 as Any } ?? NSNull()), "times": times]
        }
        let text = String(data: try JSONSerialization.data(withJSONObject: ["steps": steps, "after": after], options: [.sortedKeys]), encoding: .utf8)!
        let outputTokens = try await model.tokenCount(for: raw.jsonString)
        emit(["message": ["content": text], "prompt_eval_count": promptTokens, "eval_count": outputTokens, "load_duration": 0,
              "imageTokensCounted": cg == nil ? NSNull() : false, "raw": raw.jsonString])
    } catch {
        // After the prompt is counted, a generation error is a refusal with known usage (content is empty).
        if let counted { emit(["error": "\(error)", "message": ["content": ""], "prompt_eval_count": counted, "eval_count": 0, "load_duration": 0]) }
        else { emit(["error": "\(error)"]) }
    }
}
