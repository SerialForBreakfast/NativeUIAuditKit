// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "NativeUIAuditKitModels",
    platforms: [.macOS(.v14), .iOS(.v17), .macCatalyst(.v17), .visionOS(.v1)],
    products: [
        .library(name: "NativeUIAuditKitModels", targets: ["NativeUIAuditKitModels"])
    ],
    targets: [
        .target(name: "NativeUIModelContracts"),
        .target(
            name: "NativeUIAuditKitModels",
            dependencies: ["NativeUIModelContracts"],
            path: "Sources/NativeUIAuditKitModels",
            exclude: ["NativeUIDetector_v1.mlpackage.mlmodel", "NativeUIModel_tvOS.mlpackage"],
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
        .testTarget(name: "StandaloneModelTests", dependencies: ["NativeUIAuditKitModels"])
    ]
)
