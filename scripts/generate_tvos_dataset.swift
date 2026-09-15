#!/usr/bin/env swift
// generate_tvos_dataset.swift
// NativeUIAuditKit — High-throughput tvOS OS UI Synthetic Dataset Generator
//
// Renders 1080p (1920×1080) tvOS OS UI screenshots directly via SwiftUI ImageRenderer
// on macOS without requiring simulator execution or host app harnesses.
// Generates schema v1.0 annotations with exact pixel bounding boxes and focus states.
//
// Usage:
//   swift scripts/generate_tvos_dataset.swift [--count 2000] [--output dataset/tvos_dataset]

import Foundation
import CoreGraphics
import ImageIO
import CryptoKit
import SwiftUI
import UniformTypeIdentifiers

// MARK: - FramePreference & Modifier

public struct FramePreference: PreferenceKey {
    public static var defaultValue: [String: CGRect] { [:] }
    public static func reduce(value: inout [String: CGRect], nextValue: () -> [String: CGRect]) {
        value.merge(nextValue()) { _, new in new }
    }
}

public extension View {
    func captureFrame(id: String) -> some View {
        background(
            GeometryReader { geo in
                Color.clear.preference(
                    key: FramePreference.self,
                    value: [id: geo.frame(in: .global)]
                )
            }
        )
    }
}

// MARK: - Seeded RNG

public struct SeededRNG {
    private var state: UInt64
    public init(seed: UInt64) { self.state = seed != 0 ? seed : 0xDEADBEEFCAFEBABE }
    public mutating func next() -> UInt64 {
        state &+= 0x9E3779B97F4A7C15
        var z = state
        z = (z ^ (z >> 30)) &* 0xBF58476D1CE4E5B9
        z = (z ^ (z >> 27)) &* 0x94D049BB133111EB
        return z ^ (z >> 31)
    }
}

// MARK: - Content Corpus

public struct ContentCorpus {
    private var rng: SeededRNG
    public init(seed: UInt64) { self.rng = SeededRNG(seed: seed) }

    private let appTitles = [
        "Photos", "Music", "TV", "Podcasts", "Arcade", "App Store",
        "Settings", "Fitness", "News", "Books", "Calculator", "Weather",
        "Home", "Files", "Notes", "Reminders", "Maps", "Clock",
        "TVTestRig", "FixtureApp", "SpeedTest", "YouTube", "Netflix", "Prime Video"
    ]

    private let navTitles = [
        "Home", "Settings", "Library", "Search", "General", "Accounts",
        "Network", "Video and Audio", "Accessibility", "System", "Remotes"
    ]

    private let settingRows = [
        "Wi-Fi", "Bluetooth", "AirPlay and HomeKit", "Audio Output",
        "Subtitles and Captioning", "Siri", "Software Updates", "Sleep After",
        "Screensaver", "Language", "Legal & Regulatory", "Reset"
    ]

    private let alertTitles = [
        "Software Update Available", "Sign In to Apple TV", "Allow TVTestRig Access?",
        "Erase All Content and Settings?", "Remote Battery Low", "AirPlay Passcode Required"
    ]

    private let alertMessages = [
        "A new tvOS version is ready to install. Do you want to download and update now?",
        "Enter your Apple Account password to continue.",
        "TVTestRig is attempting to inspect screen elements for test automation.",
        "This will restore your Apple TV to factory settings. This action cannot be undone.",
        "Connect your Siri Remote to a charger soon.",
        "Enter the code displayed on your TV to continue connecting."
    ]

    public mutating func appTitle() -> String {
        appTitles[Int(rng.next() % UInt64(appTitles.count))]
    }
    public mutating func navTitle() -> String {
        navTitles[Int(rng.next() % UInt64(navTitles.count))]
    }
    public mutating func settingRow() -> String {
        settingRows[Int(rng.next() % UInt64(settingRows.count))]
    }
    public mutating func alertTitle() -> String {
        alertTitles[Int(rng.next() % UInt64(alertTitles.count))]
    }
    public mutating func alertMessage() -> String {
        alertMessages[Int(rng.next() % UInt64(alertMessages.count))]
    }
}

// MARK: - Templates

// 1. Home Screen
struct HomeScreenView: View {
    let seed: UInt64
    var corpus: ContentCorpus

    var body: some View {
        var rng = SeededRNG(seed: seed)
        let apps = (0..<10).map { i -> (title: String, hue: Double, isFocused: Bool) in
            let hue = Double(rng.next() % 1000) / 1000.0
            return (appsList[i % appsList.count], hue, i == 2)
        }
        let columns = [
            GridItem(.fixed(308), spacing: 48),
            GridItem(.fixed(308), spacing: 48),
            GridItem(.fixed(308), spacing: 48),
            GridItem(.fixed(308), spacing: 48),
            GridItem(.fixed(308), spacing: 48)
        ]

        ZStack(alignment: .topLeading) {
            LinearGradient(
                colors: [Color(red: 0.08, green: 0.08, blue: 0.12), Color.black],
                startPoint: .top, endPoint: .bottom
            ).ignoresSafeArea()

            VStack(alignment: .leading, spacing: 32) {
                // Top shelf
                ZStack {
                    RoundedRectangle(cornerRadius: 24)
                        .fill(Color.blue.opacity(0.35))
                    HStack(spacing: 24) {
                        Image(systemName: "tv.fill").font(.system(size: 64)).foregroundColor(.white)
                            .captureFrame(id: "imageView_shelf_icon")
                        Text("Featured on Apple TV")
                            .font(.system(size: 38, weight: .bold))
                            .foregroundColor(.white)
                            .captureFrame(id: "label_shelf_title")
                    }
                }
                .frame(width: 1720, height: 340)
                .captureFrame(id: "collectionItem_shelf_0_unfocused")
                .padding(.top, 40)
                .padding(.leading, 100)

                // Grid
                LazyVGrid(columns: columns, spacing: 36) {
                    ForEach(0..<10, id: \.self) { idx in
                        let app = apps[idx]
                        VStack(spacing: 12) {
                            ZStack {
                                RoundedRectangle(cornerRadius: 16)
                                    .fill(Color(hue: app.hue, saturation: 0.7, brightness: 0.6))
                                Image(systemName: "app.fill")
                                    .font(.system(size: 44)).foregroundColor(.white)
                            }
                            .frame(width: 308, height: 175)
                            .scaleEffect(app.isFocused ? 1.15 : 1.0)
                            .overlay(RoundedRectangle(cornerRadius: 16).stroke(app.isFocused ? Color.white : Color.clear, lineWidth: 3))
                            .shadow(color: app.isFocused ? Color.white.opacity(0.6) : Color.clear, radius: 20)
                            .captureFrame(id: app.isFocused ? "collectionItem_app_\(idx)_focused" : "collectionItem_app_\(idx)_unfocused")

                            Text(app.title)
                                .font(.system(size: 20, weight: app.isFocused ? .bold : .medium))
                                .foregroundColor(app.isFocused ? .white : .white.opacity(0.7))
                                .frame(width: 308)
                                .captureFrame(id: "label_app_\(idx)")
                        }
                    }
                }
                .padding(.leading, 100)
            }
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }

    private let appsList = [
        "Photos", "Music", "TV", "Podcasts", "Arcade",
        "Settings", "Fitness", "YouTube", "FixtureApp", "TVTestRig"
    ]
}

// 2. Settings Split-View
struct SettingsView: View {
    let seed: UInt64
    var corpus: ContentCorpus

    var body: some View {
        var rng = SeededRNG(seed: seed)
        let focusIdx = Int(rng.next() % 6)
        let categories = ["General", "Users", "Video and Audio", "Remotes", "Network", "System"]

        ZStack(alignment: .topLeading) {
            Color(red: 0.05, green: 0.05, blue: 0.08).ignoresSafeArea()

            VStack(alignment: .leading, spacing: 20) {
                Text("Settings")
                    .font(.system(size: 44, weight: .bold))
                    .foregroundColor(.white)
                    .padding(.horizontal, 90)
                    .padding(.top, 50)
                    .captureFrame(id: "navigationBar_title")

                HStack(alignment: .top, spacing: 80) {
                    VStack(spacing: 12) {
                        ForEach(0..<categories.count, id: \.self) { idx in
                            let isFoc = (idx == focusIdx)
                            HStack {
                                Text(categories[idx])
                                    .font(.system(size: 26, weight: isFoc ? .bold : .medium))
                                    .foregroundColor(isFoc ? .black : .white)
                                    .captureFrame(id: "label_cat_\(idx)")
                                Spacer()
                                Image(systemName: "chevron.right")
                                    .foregroundColor(isFoc ? .black.opacity(0.6) : .white.opacity(0.4))
                            }
                            .padding(.horizontal, 28)
                            .frame(width: 580, height: 74)
                            .background(isFoc ? Color.white : Color.white.opacity(0.08))
                            .cornerRadius(16)
                            .captureFrame(id: isFoc ? "listRow_cat_\(idx)_focused" : "listRow_cat_\(idx)_unfocused")
                        }
                    }

                    VStack(spacing: 14) {
                        ForEach(0..<5, id: \.self) { idx in
                            HStack {
                                Text("Option \(idx + 1)")
                                    .font(.system(size: 26))
                                    .foregroundColor(.white)
                                    .captureFrame(id: "label_opt_\(idx)")
                                Spacer()
                                Toggle("", isOn: .constant(idx % 2 == 0))
                                    .labelsHidden()
                                    .captureFrame(id: "toggle_setting_\(idx)")
                            }
                            .padding(.horizontal, 28)
                            .frame(width: 980, height: 78)
                            .background(Color.white.opacity(0.06))
                            .cornerRadius(16)
                            .captureFrame(id: "listRow_setting_\(idx)_unfocused")
                        }
                    }
                }
                .padding(.horizontal, 90)
            }
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}

// 3. Alert Modal
struct AlertView: View {
    let seed: UInt64
    var corpus: ContentCorpus

    var body: some View {
        var rng = SeededRNG(seed: seed)
        let focusBtn = Int(rng.next() % 2) // 0: primary, 1: cancel

        ZStack {
            Color.black.opacity(0.85).ignoresSafeArea()

            VStack(spacing: 28) {
                VStack(spacing: 12) {
                    Text("Allow TVTestRig Access?")
                        .font(.system(size: 34, weight: .bold))
                        .foregroundColor(.white)
                        .captureFrame(id: "label_alert_title")
                    Text("This allows TVTestRig to automate Apple TV navigation.")
                        .font(.system(size: 22))
                        .foregroundColor(.white.opacity(0.8))
                        .padding(.horizontal, 32)
                        .multilineTextAlignment(.center)
                        .captureFrame(id: "label_alert_message")
                }
                .padding(.top, 40)

                VStack(spacing: 16) {
                    Text("Continue")
                        .font(.system(size: 24, weight: focusBtn == 0 ? .bold : .medium))
                        .foregroundColor(focusBtn == 0 ? .black : .white)
                        .frame(width: 660, height: 68)
                        .background(focusBtn == 0 ? Color.white : Color.white.opacity(0.12))
                        .cornerRadius(16)
                        .captureFrame(id: focusBtn == 0 ? "primaryButton_action_focused" : "primaryButton_action_unfocused")

                    Text("Cancel")
                        .font(.system(size: 24, weight: focusBtn == 1 ? .bold : .medium))
                        .foregroundColor(focusBtn == 1 ? .black : .white)
                        .frame(width: 660, height: 68)
                        .background(focusBtn == 1 ? Color.white : Color.white.opacity(0.12))
                        .cornerRadius(16)
                        .captureFrame(id: focusBtn == 1 ? "cancelAction_dismiss_focused" : "cancelAction_dismiss_unfocused")
                }
                .padding(.bottom, 36)
            }
            .frame(width: 760)
            .background(Color(red: 0.16, green: 0.16, blue: 0.20))
            .cornerRadius(28)
            .captureFrame(id: "alert_dialog_box")
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}

// 4. Top Tab Bar
struct TabBarView: View {
    let seed: UInt64
    var corpus: ContentCorpus

    var body: some View {
        var rng = SeededRNG(seed: seed)
        let tabs = ["Apple TV+", "Store", "Library", "Search"]
        let focIdx = Int(rng.next() % UInt64(tabs.count))

        ZStack(alignment: .top) {
            Color(red: 0.04, green: 0.04, blue: 0.06).ignoresSafeArea()

            VStack(spacing: 0) {
                HStack(spacing: 24) {
                    ForEach(0..<tabs.count, id: \.self) { idx in
                        let isFoc = (idx == focIdx)
                        Text(tabs[idx])
                            .font(.system(size: 24, weight: isFoc ? .bold : .medium))
                            .foregroundColor(isFoc ? .black : .white.opacity(0.8))
                            .padding(.horizontal, 28)
                            .padding(.vertical, 12)
                            .background(isFoc ? Color.white : Color.clear)
                            .cornerRadius(20)
                            .captureFrame(id: isFoc ? "primaryButton_tab_\(idx)_focused" : "primaryButton_tab_\(idx)_unfocused")
                    }
                }
                .frame(maxWidth: .infinity)
                .frame(height: 110)
                .background(Color.black.opacity(0.3))
                .captureFrame(id: "tabBar_top_navigation")
                .padding(.top, 20)

                VStack(alignment: .leading, spacing: 20) {
                    Text("Featured Collection")
                        .font(.system(size: 48, weight: .heavy))
                        .foregroundColor(.white)
                        .captureFrame(id: "label_featured_title")

                    RoundedRectangle(cornerRadius: 24)
                        .fill(Color.purple.opacity(0.4))
                        .frame(width: 1740, height: 680)
                        .captureFrame(id: "collectionItem_featured_card_unfocused")
                }
                .padding(.horizontal, 90)
                .padding(.top, 40)
            }
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}

// 5. Hard Negative
struct HardNegativeView: View {
    let seed: UInt64

    var body: some View {
        var rng = SeededRNG(seed: seed)
        let hue1 = Double(rng.next() % 1000) / 1000.0
        let hue2 = Double(rng.next() % 1000) / 1000.0

        LinearGradient(
            colors: [Color(hue: hue1, saturation: 0.8, brightness: 0.3), Color(hue: hue2, saturation: 0.7, brightness: 0.1), Color.black],
            startPoint: .topLeading, endPoint: .bottomTrailing
        )
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}

// MARK: - Generator Orchestrator

@MainActor
func generateDataset() async {
    let totalTarget = 2000
    let homeCount = 500
    let settingsCount = 500
    let alertCount = 500
    let tabCount = 400
    let negativeCount = 100

    let outDir = URL(fileURLWithPath: "dataset/tvos_dataset")
    let fm = FileManager.default
    try? fm.createDirectory(at: outDir.appendingPathComponent("train"), withIntermediateDirectories: true)
    try? fm.createDirectory(at: outDir.appendingPathComponent("validation"), withIntermediateDirectories: true)
    try? fm.createDirectory(at: outDir.appendingPathComponent("test"), withIntermediateDirectories: true)

    print("Generating \(totalTarget) tvOS OS UI images at 1920x1080 into \(outDir.path)...")
    let start = Date()

    var globalIndex = 0

    func renderAndSave<V: View>(view: V, family: String) {
        var capturedFrames: [String: CGRect] = [:]
        let wrapped = view.onPreferenceChange(FramePreference.self) { prefs in
            capturedFrames = prefs
        }

        let renderer = ImageRenderer(content: wrapped)
        renderer.scale = 1.0
        guard let cgImg = renderer.cgImage else {
            fputs("WARNING: Failed to render image for \(family)_\(globalIndex)\n", stderr)
            return
        }

        // Determine split: 80% train, 10% validation, 10% test
        let split: String
        let mod = globalIndex % 10
        if mod == 9 { split = "test" }
        else if mod == 8 { split = "validation" }
        else { split = "train" }

        let fileBase = String(format: "img_%06d", globalIndex)
        let pngURL = outDir.appendingPathComponent(split).appendingPathComponent("\(fileBase).png")
        let jsonURL = outDir.appendingPathComponent(split).appendingPathComponent("\(fileBase).json")

        // Save PNG
        guard let dest = CGImageDestinationCreateWithURL(pngURL as CFURL, UTType.png.identifier as CFString, 1, nil) else { return }
        CGImageDestinationAddImage(dest, cgImg, nil)
        CGImageDestinationFinalize(dest)

        let pngData = (try? Data(contentsOf: pngURL)) ?? Data()
        let sha256 = SHA256.hash(data: pngData).map { String(format: "%02x", $0) }.joined()

        // Build Elements
        var elements: [[String: Any]] = []
        for (id, frame) in capturedFrames {
            let elemType = id.components(separatedBy: "_").first ?? id
            let isFocused = id.contains("_focused") ? true : (id.contains("_unfocused") ? false : nil)

            let xNorm = max(0.0, min(1.0, frame.minX / 1920.0))
            let yNorm = max(0.0, min(1.0, 1.0 - (frame.minY + frame.height) / 1080.0))
            let wNorm = max(0.0, min(1.0 - xNorm, frame.width / 1920.0))
            let hNorm = max(0.0, min(1.0 - yNorm, frame.height / 1080.0))

            var stateDict: [String: Any] = ["isEnabled": true, "isSelected": false]
            if let f = isFocused { stateDict["isFocused"] = f }

            let elemDict: [String: Any] = [
                "id": id,
                "elementType": elemType,
                "framework": "SwiftUI",
                "boundsPixels": ["x": frame.minX, "y": frame.minY, "width": frame.width, "height": frame.height],
                "boundsPoints": ["x": frame.minX, "y": frame.minY, "width": frame.width, "height": frame.height],
                "boundsVisionNormalized": ["x": xNorm, "y": yNorm, "width": wNorm, "height": hNorm],
                "visibleText": NSNull(),
                "accessibilityLabel": NSNull(),
                "traits": [] as [String],
                "state": stateDict,
                "occluded": false,
                "excluded": false,
                "knownIssues": [] as [String]
            ]
            elements.append(elemDict)
        }

        let sidecar: [String: Any] = [
            "schemaVersion": "1.0",
            "imageSHA256": sha256,
            "image": [
                "fileName": "\(fileBase).png",
                "pixelWidth": 1920,
                "pixelHeight": 1080,
                "scale": 1,
                "platform": "tvOS",
                "osVersion": "tvOS 17.2",
                "deviceName": "Apple TV 4K",
                "interfaceIdiom": "tv",
                "orientation": "landscape",
                "colorScheme": "dark",
                "dynamicTypeSize": "large",
                "locale": "en_US",
                "layoutDirection": "ltr",
                "safeAreaInsets": ["top": 60, "left": 90, "bottom": 60, "right": 90],
                "reduceTransparency": false,
                "increaseContrast": false,
                "boldText": false,
                "buttonShapes": false,
                "onOffLabels": false,
                "smartInvert": false
            ],
            "generatorProfile": [
                "templateFamily": family,
                "seed": globalIndex,
                "generatorVersion": "tvos-1.0",
                "isolationTemplate": false,
                "lowDensity": false,
                "simulatorState": [
                    "time": "09:41",
                    "batteryLevel": 100,
                    "batteryState": "charging",
                    "cellularBars": 0,
                    "wifiBars": 3,
                    "operatorName": ""
                ]
            ],
            "elements": elements
        ]

        if let jsonBytes = try? JSONSerialization.data(withJSONObject: sidecar, options: [.prettyPrinted, .sortedKeys]) {
            try? jsonBytes.write(to: jsonURL)
        }

        globalIndex += 1
        if globalIndex % 200 == 0 {
            let el = Date().timeIntervalSince(start)
            print("  Progress: \(globalIndex)/\(totalTarget) images generated (\(String(format: "%.1f", Double(globalIndex) / el)) fps)...")
        }
    }

    var corpus = ContentCorpus(seed: 42)

    // 1. Home Screen
    for i in 0..<homeCount {
        renderAndSave(view: HomeScreenView(seed: UInt64(i), corpus: corpus), family: "tvOSHomeScreen")
    }
    // 2. Settings
    for i in 0..<settingsCount {
        renderAndSave(view: SettingsView(seed: UInt64(i), corpus: corpus), family: "tvOSSettings")
    }
    // 3. Alert
    for i in 0..<alertCount {
        renderAndSave(view: AlertView(seed: UInt64(i), corpus: corpus), family: "tvOSAlert")
    }
    // 4. Tab Bar
    for i in 0..<tabCount {
        renderAndSave(view: TabBarView(seed: UInt64(i), corpus: corpus), family: "tvOSTopTabBar")
    }
    // 5. Hard Negatives
    for i in 0..<negativeCount {
        renderAndSave(view: HardNegativeView(seed: UInt64(i)), family: "tvOSHardNegatives")
    }

    let elapsed = Date().timeIntervalSince(start)
    print("Complete! Generated \(globalIndex) images in \(String(format: "%.1f", elapsed))s (\(String(format: "%.1f", Double(globalIndex) / elapsed)) fps).")

    // Write manifest
    let manifest: [String: Any] = [
        "generatorVersion": "tvos-1.0",
        "generatedAt": ISO8601DateFormatter().string(from: Date()),
        "totalImages": globalIndex,
        "resolution": "1920x1080",
        "platform": "tvOS",
        "templateCounts": [
            "tvOSHomeScreen": homeCount,
            "tvOSSettings": settingsCount,
            "tvOSAlert": alertCount,
            "tvOSTopTabBar": tabCount,
            "tvOSHardNegatives": negativeCount
        ]
    ]
    if let mData = try? JSONSerialization.data(withJSONObject: manifest, options: [.prettyPrinted, .sortedKeys]) {
        try? mData.write(to: outDir.appendingPathComponent("manifest.json"))
    }
}

Task { @MainActor in
    await generateDataset()
    exit(0)
}
RunLoop.main.run()
