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
    /// Fraction of image height used for each horizontal strip (0 = full-image only).
    /// Set to 0.22 (22%) to fix extreme-aspect-ratio anchor-assignment failure for
    /// navigationBar and textField (see BP-26 in Research/BestPractices.md).
    let stripFraction: Double
    let datasetVersion: String
    let trainedAt: String          // ISO 8601

    static let `default` = TrainingConfig(
        algorithm: "transferLearning",
        featureExtractor: "objectPrint_v1",     // MLObjectDetector.FeatureExtractorType.objectPrint(revision:1)
        maxIterations: 25_000,                  // increased for larger strip-tiled dataset
        batchSize: 32,
        trainingClasses: ["alert", "navigationBar", "primaryButton", "textField", "toggle"],
        subsamplingCapPerClass: 2_000,
        stripFraction: 0.22,                    // 22% of image height, 50% overlap stride
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
