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
        .executableTarget(
            name: "NativeUIDatasetGenerator",
            path: "NativeUIDatasetGenerator",
            sources: ["Sources", "Templates"],
            resources: [.copy("Assets/Wallpapers")]
        ),
        .executableTarget(
            name: "NativeUIDatasetGeneratorOverlay",
            path: "NativeUIDatasetGeneratorOverlay/Sources"
        ),
        .testTarget(
            name: "NativeUIAuditKitTests",
            dependencies: ["NativeUIAuditKit"],
            path: "Tests/NativeUIAuditKitTests"
        )
    ]
)
