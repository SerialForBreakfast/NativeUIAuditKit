import Foundation
import CryptoKit
import Darwin

public enum MatrixPreset: String, CaseIterable {
    case smoke
    case core
    case full
    case edge
}

public struct MatrixGenerator {
    public static func generateMatrix(
        at output: URL,
        rendererSourceSHA256: String,
        preset: MatrixPreset = .core,
        experimentID: String = "matrix-exp-01",
        corpusDir: URL? = nil
    ) throws {
        try noLinks(output)
        try require(validID(experimentID), "invalid_experiment_id")
        try require(validHash(rendererSourceSHA256), "invalid_hash")
        try require(!FileManager.default.fileExists(atPath: output.path), "output_collision")

        try FileManager.default.createDirectory(at: output, withIntermediateDirectories: true)
        let assetsDir = output.appendingPathComponent("assets")
        try FileManager.default.createDirectory(at: assetsDir, withIntermediateDirectories: true)

        // Write expected.json
        let expected = Expected(schema: "authored-pair-v1", framesPerJob: 2, width: 1920, height: 1080)
        try write(expected, output.appendingPathComponent("expected.json"))

        // Populate assets
        if let corpus = corpusDir, FileManager.default.fileExists(atPath: corpus.path) {
            try linkCorpus(from: corpus, to: assetsDir)
        } else {
            try generateBaseAssets(in: assetsDir)
        }

        // Generate jobs based on preset
        let jobs = makeJobs(preset: preset, experimentID: experimentID)
        try require((1...100).contains(jobs.count), "invalid_job_count")

        // Inventory assets and expected.json
        let fileArtifacts = try inventory(output)

        // Construct experiment manifest
        var limits = Limits()
        limits.timeoutSeconds = 60
        limits.maxOutputBytes = 268435456 // 256 MiB
        limits.maxAttempts = 2

        let experiment = Experiment(
            id: experimentID,
            rendererSourceSHA256: rendererSourceSHA256,
            files: fileArtifacts,
            jobs: jobs,
            limits: limits
        )

        try write(experiment, output.appendingPathComponent("experiment.json"))

        // Validate complete bundle against strict contract
        _ = try validateBundle(output)
    }

    private static func linkCorpus(from source: URL, to destination: URL) throws {
        let items = try inventory(source)
        for item in items {
            let srcURL = source.appendingPathComponent(item.path)
            let dstURL = destination.appendingPathComponent(item.path)
            try FileManager.default.createDirectory(at: dstURL.deletingLastPathComponent(), withIntermediateDirectories: true)
            // Use hard link if possible, fallback to copy
            if link(srcURL.path, dstURL.path) != 0 {
                try FileManager.default.copyItem(at: srcURL, to: dstURL)
            }
        }
    }

    private static func generateBaseAssets(in assetsDir: URL) throws {
        // Base metadata manifest
        let manifest: [String: Any] = [
            "generator": "FixtureExperimentMatrixGenerator",
            "version": "1.0",
            "resolution": "1080p",
            "created": ISO8601DateFormatter().string(from: Date())
        ]
        let manifestData = try JSONSerialization.data(withJSONObject: manifest, options: [.sortedKeys, .prettyPrinted])
        try manifestData.write(to: assetsDir.appendingPathComponent("manifest.json"))

        // Baseline placeholder image (minimal 1x1 png or 100x100 pattern)
        let samplePNGData = Data([
            0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0x00, 0x00, 0x00, 0x0d,
            0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
            0x08, 0x06, 0x00, 0x00, 0x00, 0x1f, 0x15, 0xc4, 0x89, 0x00, 0x00, 0x00,
            0x0a, 0x49, 0x44, 0x41, 0x54, 0x78, 0x9c, 0x63, 0x00, 0x01, 0x00, 0x00,
            0x05, 0x00, 0x01, 0x0d, 0x0a, 0x2d, 0xb4, 0x00, 0x00, 0x00, 0x00, 0x49,
            0x45, 0x4e, 0x44, 0xae, 0x42, 0x60, 0x82
        ])
        try samplePNGData.write(to: assetsDir.appendingPathComponent("placeholder_poster.png"))
        try samplePNGData.write(to: assetsDir.appendingPathComponent("placeholder_backdrop.png"))
    }

    private static func makeJobs(preset: MatrixPreset, experimentID: String) -> [Job] {
        switch preset {
        case .smoke:
            return [
                Job(id: "smoke_shelf", layout: "shelf", ancestry: "\(experimentID)-smoke-shelf"),
                Job(id: "smoke_grid", layout: "grid", ancestry: "\(experimentID)-smoke-grid"),
                Job(id: "smoke_hero", layout: "hero_detail", ancestry: "\(experimentID)-smoke-hero"),
                Job(id: "smoke_top_nav", layout: "top_nav_shelf", ancestry: "\(experimentID)-smoke-top-nav")
            ]

        case .core:
            let layouts = ["shelf", "grid", "hero_detail", "top_nav_shelf", "settings_list", "action_dialog", "focus_maze"]
            let themes = ["dark_standard", "light_standard"]
            var jobs = [Job]()
            for layout in layouts {
                for theme in themes {
                    let jobID = "\(layout)_\(theme)"
                    jobs.append(Job(
                        id: jobID,
                        layout: layout,
                        ancestry: "\(experimentID)-\(jobID)",
                        theme: theme,
                        density: "standard_spacing"
                    ))
                }
            }
            return jobs

        case .full:
            var jobs = [Job]()
            let layouts = ["shelf", "grid", "hero_detail", "top_nav_shelf", "settings_list", "action_dialog", "focus_maze"]
            let themes = ["dark_standard", "light_standard", "dark_low_contrast"]
            let densities = ["standard_spacing", "dense_abutting"]
            for (idx, layout) in layouts.enumerated() {
                let theme = themes[idx % themes.count]
                let density = densities[idx % densities.count]
                let overlay = idx % 3 == 0 ? "apns_top_banner" : (idx % 3 == 1 ? "scrim_modal_sheet" : "none")
                let jobID = "full_\(layout)_\(theme)_\(density)"
                jobs.append(Job(
                    id: jobID,
                    layout: layout,
                    ancestry: "\(experimentID)-\(jobID)",
                    theme: theme,
                    density: density,
                    overlay: overlay
                ))
            }
            return jobs

        case .edge:
            return [
                Job(id: "edge_01_label_bleed", layout: "shelf", ancestry: "\(experimentID)-e01", theme: "dark_standard", density: "dense_abutting"),
                Job(id: "edge_02_dark_ring", layout: "grid", ancestry: "\(experimentID)-e02", theme: "dark_low_contrast", density: "standard_spacing"),
                Job(id: "edge_03_barrier_sink", layout: "focus_maze", ancestry: "\(experimentID)-e03", theme: "dark_standard", density: "standard_spacing"),
                Job(id: "edge_04_isolated_cell", layout: "grid", ancestry: "\(experimentID)-e04", theme: "light_standard", density: "sparse_isolated"),
                Job(id: "edge_05_destructive_gating", layout: "action_dialog", ancestry: "\(experimentID)-e05", theme: "dark_standard", density: "standard_spacing"),
                Job(id: "edge_06_trailing_chevron", layout: "settings_list", ancestry: "\(experimentID)-e06", theme: "dark_standard", density: "standard_spacing"),
                Job(id: "edge_07_transient_modal", layout: "action_dialog", ancestry: "\(experimentID)-e07", theme: "dark_standard", density: "standard_spacing", overlay: "scrim_modal_sheet"),
                Job(id: "edge_08_motion_drift", layout: "shelf", ancestry: "\(experimentID)-e08", theme: "dark_standard", density: "standard_spacing"),
                Job(id: "edge_09_symbol_align", layout: "top_nav_shelf", ancestry: "\(experimentID)-e09", theme: "light_standard", density: "standard_spacing"),
                Job(id: "edge_10_text_truncation", layout: "settings_list", ancestry: "\(experimentID)-e10", theme: "dark_standard", density: "dense_abutting")
            ]
        }
    }
}
