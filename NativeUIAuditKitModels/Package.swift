// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "NativeUIAuditKitModels",
    platforms: [.macOS(.v15), .iOS(.v17)],
    products: [
        .library(name: "NativeUIAuditKitModels", targets: ["NativeUIAuditKitModels"])
    ],
    targets: [
        .target(
            name: "NativeUIAuditKitModels",
            path: "Sources/NativeUIAuditKitModels",
            resources: [
                .process("NativeUIDetector_v1.mlpackage")
            ]
        )
    ]
)
