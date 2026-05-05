// DatasetManifest.swift
// NativeUIDatasetGenerator
//
// Maintains the top-level manifest.json for the dataset.
// Appends one ManifestEntry per generated image and keeps a running
// classDistribution count across all 41 element types.
//
// Concurrency: DatasetManifest is not an actor; callers must serialize
// access themselves. The macOS orchestrator generates images serially per
// simulator, so no locking is required in the initial implementation.

import Foundation

// MARK: - Dataset split

/// Which training partition an image belongs to.
public enum DatasetSplit: String, Codable, Sendable {
    /// Primary training set (typically 80% of all images).
    case train
    /// Hyperparameter-tuning validation set (typically 10%).
    case validation
    /// Held-out test set — not used during training (typically 10%).
    case test
}

// MARK: - ManifestEntry

/// One record in the top-level `manifest.json`, one per generated PNG.
public struct ManifestEntry: Codable, Sendable {
    public let fileName: String
    public let split: DatasetSplit
    public let sha256: String
    public let templateFamily: String
    public let generatorSeed: UInt64
    public let generationDate: Date
    public let simulatorState: SimulatorStateOverride
    /// `true` when the image shows a single element type in isolation (no background clutter).
    public let isolationTemplate: Bool
    /// `true` when the element count in the annotation is fewer than 2.
    public let lowDensity: Bool
    /// Device name used during generation (e.g. `"iPhone 15 Pro"`).
    public let deviceName: String
    /// The pixel scale factor (2 or 3).
    public let pixelScale: Int

    public init(
        fileName: String,
        split: DatasetSplit,
        sha256: String,
        templateFamily: String,
        generatorSeed: UInt64,
        generationDate: Date = Date(),
        simulatorState: SimulatorStateOverride,
        isolationTemplate: Bool,
        lowDensity: Bool,
        deviceName: String,
        pixelScale: Int
    ) {
        self.fileName = fileName
        self.split = split
        self.sha256 = sha256
        self.templateFamily = templateFamily
        self.generatorSeed = generatorSeed
        self.generationDate = generationDate
        self.simulatorState = simulatorState
        self.isolationTemplate = isolationTemplate
        self.lowDensity = lowDensity
        self.deviceName = deviceName
        self.pixelScale = pixelScale
    }
}

// MARK: - DatasetManifest

/// In-memory representation of `manifest.json`.
///
/// Load from disk with `DatasetManifest(from:)`, mutate with `append(_:elements:)`,
/// then flush with `save(to:)`. Maintains a `classDistribution` count across all
/// 41 `NativeUIElementType.rawValue` strings.
public struct DatasetManifest: Codable {

    public private(set) var entries: [ManifestEntry] = []
    /// Per-class instance counts across all entries. Keys are `NativeUIElementType.rawValue` strings.
    public private(set) var classDistribution: [String: Int] = [:]
    /// Total number of images in the manifest.
    public var imageCount: Int { entries.count }

    public init() {}

    // MARK: - Mutations

    /// Append a new entry and update `classDistribution`.
    ///
    /// - Parameters:
    ///   - entry: The `ManifestEntry` to append.
    ///   - elementTypes: The `elementType` rawValues present in the paired annotation.
    ///     Used to update the running class distribution.
    public mutating func append(_ entry: ManifestEntry, elementTypes: [String]) {
        entries.append(entry)
        for type_ in elementTypes {
            classDistribution[type_, default: 0] += 1
        }
    }

    // MARK: - Persistence

    /// Load a manifest from a JSON file, or return an empty manifest if the file does not exist.
    ///
    /// - Parameter url: Path to `manifest.json` on disk.
    /// - Throws: A `DecodingError` if the file exists but cannot be parsed.
    public static func load(from url: URL) throws -> DatasetManifest {
        guard FileManager.default.fileExists(atPath: url.path) else {
            return DatasetManifest()
        }
        let data = try Data(contentsOf: url)
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return try decoder.decode(DatasetManifest.self, from: data)
    }

    /// Write the manifest to disk as pretty-printed JSON.
    ///
    /// - Parameter url: Destination file URL (parent directory must exist).
    /// - Throws: File system or encoding errors.
    public func save(to url: URL) throws {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        encoder.dateEncodingStrategy = .iso8601
        let data = try encoder.encode(self)
        try data.write(to: url, options: .atomic)
    }

    // MARK: - Reporting

    /// Returns the imbalance ratio: max class count / min class count.
    /// Returns `nil` if fewer than 2 classes have been observed.
    public var imbalanceRatio: Double? {
        let counts = classDistribution.values.filter { $0 > 0 }
        guard let maxCount = counts.max(), let minCount = counts.min(), minCount > 0 else {
            return nil
        }
        return Double(maxCount) / Double(minCount)
    }

    /// Returns classes whose instance count is below `floor`.
    public func underrepresented(floor: Int) -> [String] {
        classDistribution
            .filter { $0.value < floor }
            .map(\.key)
            .sorted()
    }
}
