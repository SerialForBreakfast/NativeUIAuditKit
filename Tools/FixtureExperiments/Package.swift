// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "FixtureExperiments",
    platforms: [.macOS(.v14)],
    products: [
        .library(name: "FixtureExperiments", targets: ["FixtureExperiments"]),
        .executable(name: "fixture-experiment", targets: ["FixtureExperimentCLI"])
    ],
    targets: [
        .target(name: "FixtureExperiments"),
        .executableTarget(name: "FixtureExperimentCLI", dependencies: ["FixtureExperiments"]),
        .testTarget(name: "FixtureExperimentsTests", dependencies: ["FixtureExperiments"])
    ]
)
