// ADR-0035 phase A: exact Apple Foundation Model token counts for rendered prompt variants.
// Uses SystemLanguageModel.tokenCount(for:). It counts tokens; it generates no text.
// Usage: swift scripts/qa666/fm_token_count.swift <prompts.json> <out.json>
// prompts.json: [{"id": "...", "text": "..."}]. out.json: contextSize, availability, schema tokens, per-id counts.
import Foundation
import FoundationModels

@Generable struct PlanStep {
    @Guide(.anyOf(["focus", "activate", "back"])) var op: String
    var target: String?
    @Guide(.range(1...3)) var times: Int
}

@Generable struct Plan {
    var steps: [PlanStep]
    @Guide(.anyOf(["done", "replan", "abstain"])) var after: String
}

@Generable struct Expect {
    var focused: String?
    var screen: String?
    @Guide(.range(0...3)) var activations: Int
}

@Generable struct QAPlanStep {
    @Guide(.anyOf(["focus", "activate", "back"])) var op: String
    var target: String?
    @Guide(.range(1...3)) var times: Int
    var expect: Expect
}

@Generable struct QAPlan {
    var steps: [QAPlanStep]
    @Guide(.anyOf(["done", "replan", "abstain"])) var after: String
}

struct Item: Decodable { let id: String; let text: String }

let args = CommandLine.arguments
guard args.count == 3 else { FileHandle.standardError.write("usage: fm_token_count.swift in.json out.json\n".data(using: .utf8)!); exit(2) }
let items = try JSONDecoder().decode([Item].self, from: Data(contentsOf: URL(fileURLWithPath: args[1])))
let model = SystemLanguageModel.default
guard model.isAvailable else {
    let out: [String: Any] = ["availability": "\(model.availability)", "counts": [:]]
    try JSONSerialization.data(withJSONObject: out, options: [.sortedKeys]).write(to: URL(fileURLWithPath: args[2]))
    exit(0)
}
var counts: [String: Int] = [:]
for item in items { counts[item.id] = try await model.tokenCount(for: item.text) }
let out: [String: Any] = [
    "availability": "\(model.availability)",
    "contextSize": model.contextSize,
    "schemaTokens": ["plan-schema-v1": try await model.tokenCount(for: Plan.generationSchema),
                     "qa-plan-schema-v1": try await model.tokenCount(for: QAPlan.generationSchema)],
    "counts": counts,
]
try JSONSerialization.data(withJSONObject: out, options: [.sortedKeys]).write(to: URL(fileURLWithPath: args[2]))
print("counted \(counts.count) prompts")
