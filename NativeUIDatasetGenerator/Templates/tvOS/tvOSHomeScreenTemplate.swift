// tvOSHomeScreenTemplate.swift
// NativeUIDatasetGenerator — tvOS templates
//
// Parameterised tvOS Home Screen template for OS UI detection.
// Models the Apple TV home screen layout: Top Shelf banner/cards, Dock / App icon grid,
// and focus engine states (elevation, white highlight border, and drop shadow).
//
// Annotated elements:
//   collectionItem — app icons in the grid (focused / unfocused) and shelf items
//   label          — app titles below the icons
//   imageView      — app icon artwork / shelf artwork
//
// Layout rules:
//   - Fixed 16:9 canvas (1920×1080)
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - .captureFrame(id:) attached before layout padding

import SwiftUI

// MARK: - tvOSAppIconConfig

public struct tvOSAppIconConfig: Sendable {
    public var title: String
    public var symbolName: String
    public var hue: Double
    public var isFocused: Bool

    public init(title: String, symbolName: String, hue: Double, isFocused: Bool = false) {
        self.title = title
        self.symbolName = symbolName
        self.hue = hue
        self.isFocused = isFocused
    }
}

// MARK: - tvOSHomeScreenConfig

public struct tvOSHomeScreenConfig: Sendable {
    public var shelfTitle: String
    public var shelfSymbol: String
    public var shelfHue: Double
    public var isShelfFocused: Bool
    public var apps: [tvOSAppIconConfig]
    public var colorScheme: ColorScheme

    public init(
        shelfTitle: String,
        shelfSymbol: String,
        shelfHue: Double,
        isShelfFocused: Bool,
        apps: [tvOSAppIconConfig],
        colorScheme: ColorScheme = .dark
    ) {
        self.shelfTitle = shelfTitle
        self.shelfSymbol = shelfSymbol
        self.shelfHue = shelfHue
        self.isShelfFocused = isShelfFocused
        self.apps = apps
        self.colorScheme = colorScheme
    }

    private static let symbols = [
        "tv", "play.tv.fill", "film.fill", "music.note.tv",
        "gamecontroller.fill", "gearshape.fill", "photo.tv", "sparkles.tv",
        "appletvremote.gen4.fill", "antenna.radiowaves.left.and.right"
    ]

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> tvOSHomeScreenConfig {
        var rng = SeededRNG(seed: seed)
        let count = 10 // 2 rows of 5 icons
        let focusedTarget = Int(rng.next() % UInt64(count + 1)) // 0..count (count = shelf focused)

        var appList: [tvOSAppIconConfig] = []
        for i in 0..<count {
            let sym = symbols[i % symbols.count]
            let hue = Double(rng.next() % 1000) / 1000.0
            let isFoc = (i == focusedTarget)
            appList.append(tvOSAppIconConfig(
                title: corpus.listRowTitle(),
                symbolName: sym,
                hue: hue,
                isFocused: isFoc
            ))
        }

        let shelfFoc = (focusedTarget == count)
        let shelfHue = Double(rng.next() % 1000) / 1000.0

        return tvOSHomeScreenConfig(
            shelfTitle: corpus.navigationTitle(),
            shelfSymbol: symbols[Int(rng.next() % UInt64(symbols.count))],
            shelfHue: shelfHue,
            isShelfFocused: shelfFoc,
            apps: appList,
            colorScheme: .dark
        )
    }
}

// MARK: - tvOSHomeScreenTemplate View

public struct tvOSHomeScreenTemplate: View {
    public let config: tvOSHomeScreenConfig

    public init(config: tvOSHomeScreenConfig) {
        self.config = config
    }

    private let columns = [
        GridItem(.fixed(308), spacing: 48),
        GridItem(.fixed(308), spacing: 48),
        GridItem(.fixed(308), spacing: 48),
        GridItem(.fixed(308), spacing: 48),
        GridItem(.fixed(308), spacing: 48),
    ]

    public var body: some View {
        ZStack(alignment: .topLeading) {
            // Dark gradient wallpaper
            LinearGradient(
                colors: [Color(red: 0.08, green: 0.08, blue: 0.12), Color(red: 0.02, green: 0.02, blue: 0.04)],
                startPoint: .top,
                endPoint: .bottom
            )
            .ignoresSafeArea()

            VStack(alignment: .leading, spacing: 32) {
                // Top Shelf Banner
                ZStack {
                    RoundedRectangle(cornerRadius: 24)
                        .fill(LinearGradient(
                            colors: [Color(hue: config.shelfHue, saturation: 0.7, brightness: 0.5), Color.black.opacity(0.8)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        ))
                    HStack(spacing: 24) {
                        Image(systemName: config.shelfSymbol)
                            .font(.system(size: 64))
                            .foregroundColor(.white)
                            .captureFrame(id: "imageView_shelf_art")
                        VStack(alignment: .leading, spacing: 8) {
                            Text(config.shelfTitle)
                                .font(.system(size: 38, weight: .bold))
                                .foregroundColor(.white)
                                .captureFrame(id: "label_shelf_title")
                            Text("Featured on Apple TV")
                                .font(.system(size: 22))
                                .foregroundColor(.white.opacity(0.7))
                        }
                        Spacer()
                    }
                    .padding(.horizontal, 48)
                }
                .frame(width: 1720, height: 340)
                .scaleEffect(config.isShelfFocused ? 1.03 : 1.0)
                .overlay(
                    RoundedRectangle(cornerRadius: 24)
                        .stroke(config.isShelfFocused ? Color.white : Color.clear, lineWidth: 4)
                )
                .shadow(color: config.isShelfFocused ? Color.white.opacity(0.4) : Color.black.opacity(0.5), radius: 24)
                .captureFrame(id: config.isShelfFocused ? "collectionItem_shelf_0_focused" : "collectionItem_shelf_0_unfocused")
                .padding(.top, 40)
                .padding(.leading, 100)

                // App Grid (Dock + Row 2)
                LazyVGrid(columns: columns, spacing: 36) {
                    ForEach(Array(config.apps.enumerated()), id: \.offset) { idx, app in
                        VStack(spacing: 12) {
                            // App Poster Card (308×175 pt)
                            ZStack {
                                RoundedRectangle(cornerRadius: 16)
                                    .fill(LinearGradient(
                                        colors: [Color(hue: app.hue, saturation: 0.65, brightness: 0.7), Color(hue: app.hue, saturation: 0.8, brightness: 0.4)],
                                        startPoint: .topLeading,
                                        endPoint: .bottomTrailing
                                    ))
                                Image(systemName: app.symbolName)
                                    .font(.system(size: 48))
                                    .foregroundColor(.white)
                                    .captureFrame(id: "imageView_app_\(idx)")
                            }
                            .frame(width: 308, height: 175)
                            .scaleEffect(app.isFocused ? 1.15 : 1.0)
                            .overlay(
                                RoundedRectangle(cornerRadius: 16)
                                    .stroke(app.isFocused ? Color.white : Color.clear, lineWidth: 3)
                            )
                            .shadow(
                                color: app.isFocused ? Color.white.opacity(0.6) : Color.black.opacity(0.4),
                                radius: app.isFocused ? 24 : 8,
                                y: app.isFocused ? 12 : 4
                            )
                            .captureFrame(id: app.isFocused ? "collectionItem_app_\(idx)_focused" : "collectionItem_app_\(idx)_unfocused")

                            // Title Label
                            Text(app.title)
                                .font(.system(size: 20, weight: app.isFocused ? .bold : .medium))
                                .foregroundColor(app.isFocused ? .white : .white.opacity(0.7))
                                .lineLimit(1)
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
}
