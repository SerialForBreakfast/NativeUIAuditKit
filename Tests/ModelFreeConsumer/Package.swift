// swift-tools-version: 6.0
import PackageDescription

// The verification script copies the exact repository sources into this package.
let package = Package(name: "ModelFreeConsumer", platforms: [.macOS(.v14)], targets: [
    .target(name: "NativeUIModelContracts"),
    .target(name: "NativeUIAuditKitRuntime", dependencies: ["NativeUIModelContracts"]),
    .executableTarget(name: "ModelFreeProbe", dependencies: ["NativeUIAuditKitRuntime"])
])
