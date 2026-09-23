// swift-tools-version: 6.0

import PackageDescription

let package = Package(
    name: "NativeUIAuditKit",
    platforms: [
        .macOS(.v15),
        .iOS(.v17),
        .macCatalyst(.v17),
        .visionOS(.v1)
    ],
    products: [
        .library(
            name: "NativeUIAuditKitModels",
            targets: ["NativeUIAuditKitModels"]
        ),
        .library(
            name: "NativeUIAuditKit",
            targets: ["NativeUIAuditKit"]
        )
    ],
    dependencies: [
        .package(url: "https://github.com/apple/swift-docc-plugin", from: "1.3.0")
    ],
    targets: [
        // Trained CoreML model asset + versioned metadata. Depend on this directly if you
        // bring your own inference code and just want the model (e.g. ViewLens).
        .target(
            name: "NativeUIAuditKitModels",
            path: "NativeUIAuditKitModels/Sources/NativeUIAuditKitModels",
            // NativeUIDetector_v1.mlpackage.mlmodel is an uncompiled Create ML export, kept
            // on disk for provenance but not shipped as a loadable resource — iOS_v1 exposes
            // its ModelDescriptor metadata only, not a bundled asset. See Task 1/3 notes.
            exclude: [
                "NativeUIDetector_v1.mlpackage.mlmodel",
                "NativeUIModel_tvOS.mlpackage"
            ],
            resources: [
                .copy("Resources/NativeUIDetector_v2.mlmodelc"),
                .copy("Resources/NativeUIModel_tvOS.mlmodelc"),
                .copy("Resources/FocusRingDetector.mlmodelc"),
                .copy("Resources/model_manifest_tvos_v1.json"),
                .copy("Resources/model_manifest_ios_v2.json"),
                .copy("training_config_v1.json"),
                .copy("training_config_v2.json")
            ]
        ),
        // Full Vision-style detection request wrapper, built on NativeUIAuditKitModels.
        .target(
            name: "NativeUIAuditKit",
            dependencies: ["NativeUIAuditKitModels"],
            path: "Sources/NativeUIAuditKit"
        ),
        // Offline diagnostic adapters sharing the production perception primitives.
        .executableTarget(
            name: "AnchorTool",
            dependencies: ["NativeUIAuditKit"],
            path: "Tools/AnchorTool"
        ),
        .executableTarget(
            name: "TransitionTool",
            dependencies: ["NativeUIAuditKit"],
            path: "Tools/TransitionTool"
        ),
        .executableTarget(
            name: "FocusRingTool",
            dependencies: ["NativeUIAuditKit"],
            path: "Tools/FocusRingTool"
        ),
        // macOS orchestrator — drives xcrun commands, writes annotations, manages the manifest.
        // Templates/ is iOS-only; it lives in the separate GeneratorRunner Xcode project
        // and is never compiled into this SPM target. Explicitly excluded to suppress warnings.
        .executableTarget(
            name: "NativeUIDatasetGenerator",
            path: "NativeUIDatasetGenerator",
            exclude: ["Templates"],
            sources: ["Sources"],
            resources: [.copy("Assets/Wallpapers")]
        ),
        .executableTarget(
            name: "NativeUIDatasetGeneratorOverlay",
            path: "NativeUIDatasetGeneratorOverlay/Sources"
        ),
        // Trains the 5-class iOS object-detection model via Create ML.
        // macOS-only; requires Xcode (CreateML framework).
        .executableTarget(
            name: "NativeUITrainer",
            path: "NativeUITrainer/Sources",
            linkerSettings: [
                .linkedFramework("CreateML", .when(platforms: [.macOS]))
            ]
        ),
        .testTarget(
            name: "NativeUIAuditKitTests",
            dependencies: ["NativeUIAuditKit"],
            path: "Tests/NativeUIAuditKitTests",
            resources: [
                .copy("Fixtures/kitchen_sink_screen.png"),
                .copy("Fixtures/tvos_home_screen.png")
            ]
        ),
        .testTarget(
            name: "NativeUIAuditKitModelsTests",
            dependencies: ["NativeUIAuditKitModels"],
            path: "Tests/NativeUIAuditKitModelsTests"
        ),
        .testTarget(
            name: "NativeUIDatasetGeneratorTests",
            dependencies: ["NativeUIDatasetGenerator"],
            path: "Tests/NativeUIDatasetGeneratorTests"
        )
    ]
)
