// TrainingConfig.swift
// NativeUITrainer
//
// Records training hyperparameters alongside the exported .mlpackage.

import Foundation

struct TrainingConfig: Codable {
    let algorithm: String
    let featureExtractor: String
    let maxIterations: Int
    let batchSize: Int
    let trainingClasses: [String]
    let subsamplingCapPerClass: Int
    let datasetVersion: String
    let trainedAt: String          // ISO 8601

    static let `default` = TrainingConfig(
        algorithm: "transferLearning",
        featureExtractor: "objectPrint_v1",     // MLObjectDetector.FeatureExtractorType.objectPrint(revision:1)
        maxIterations: 10_000,
        batchSize: 32,
        trainingClasses: ["alert", "navigationBar", "primaryButton", "textField", "toggle"],
        subsamplingCapPerClass: 2_000,
        datasetVersion: "unknown",
        trainedAt: ISO8601DateFormatter().string(from: Date())
    )

    func write(to url: URL) throws {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        let data = try encoder.encode(self)
        try data.write(to: url)
    }
}
