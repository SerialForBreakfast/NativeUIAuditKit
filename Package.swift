// swift-tools-version: 6.0

import PackageDescription

let package = Package(
    name: "NativeUIAuditKit",
    platforms: [
        .macOS(.v15)
    ],
    products: [
        .library(
            name: "NativeUIAuditKit",
            targets: ["NativeUIAuditKit"]
        )
    ],
    targets: [
        .target(
            name: "NativeUIAuditKit",
            path: "Sources/NativeUIAuditKit"
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
            path: "Tests/NativeUIAuditKitTests"
        )
    ]
)
