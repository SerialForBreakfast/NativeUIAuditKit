// tvOSAppSwitcherTemplate.swift
// NativeUIDatasetGenerator — tvOS templates
//
// Parameterised tvOS App Switcher multitasking carousel template for OS UI detection.
// Models the Apple TV multitasking tray (double-click TV button): horizontal card carousel,
// active app card elevation/focus, app icons, and title labels.
//
// Annotated elements:
//   collectionItem — multitasking app cards (focused / unfocused)
//   label          — app titles and quit/dismiss hints
//   imageView      — app preview snapshots and app icons

import SwiftUI

// MARK: - tvOSAppSwitcherConfig

public struct tvOSAppSwitcherConfig: Sendable {
    public var apps: [(title: String, icon: String, hue: Double)]
    public var focusedIndex: Int
    public var showCloseHint: Bool

    public init(
        apps: [(title: String, icon: String, hue: Double)],
        focusedIndex: Int = 1,
        showCloseHint: Bool = true
    ) {
        self.apps = apps
        self.focusedIndex = focusedIndex
        self.showCloseHint = showCloseHint
    }

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> tvOSAppSwitcherConfig {
        var rng = SeededRNG(seed: seed)
        let appData: [(title: String, icon: String)] = [
            ("TV", "play.tv.fill"),
            ("Photos", "photo.on.rectangle.angled"),
            ("Music", "music.note"),
            ("Fitness", "flame.fill"),
            ("Settings", "gearshape.fill"),
            ("Arcade", "gamecontroller.fill")
        ]

        let count = 4
        let startIdx = Int(rng.next() % UInt64(appData.count - count + 1))
        var selectedApps: [(title: String, icon: String, hue: Double)] = []
        for i in 0..<count {
            let item = appData[(startIdx + i) % appData.count]
            let hue = Double(rng.next() % 1000) / 1000.0
            selectedApps.append((item.title, item.icon, hue))
        }

        let foc = Int(rng.next() % UInt64(count))
        return tvOSAppSwitcherConfig(
            apps: selectedApps,
            focusedIndex: foc,
            showCloseHint: (rng.next() % 2) == 0
        )
    }
}

// MARK: - tvOSAppSwitcherTemplate View

public struct tvOSAppSwitcherTemplate: View {
    public let config: tvOSAppSwitcherConfig

    public init(config: tvOSAppSwitcherConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack {
            // Dark blurred wallpaper background
            Color(red: 0.06, green: 0.06, blue: 0.09).ignoresSafeArea()

            VStack(spacing: 40) {
                Spacer()

                // Multitasking Cards Carousel
                HStack(spacing: 50) {
                    ForEach(Array(config.apps.enumerated()), id: \.offset) { idx, app in
                        let isFoc = (idx == config.focusedIndex)

                        VStack(spacing: 20) {
                            // Card Preview
                            ZStack {
                                RoundedRectangle(cornerRadius: 24)
                                    .fill(LinearGradient(
                                        colors: [Color(hue: app.hue, saturation: 0.6, brightness: 0.35), Color.black.opacity(0.85)],
                                        startPoint: .topLeading,
                                        endPoint: .bottomTrailing
                                    ))
                                Image(systemName: app.icon)
                                    .font(.system(size: 80))
                                    .foregroundColor(.white.opacity(0.85))
                                    .captureFrame(id: "imageView_app_preview_\(idx)")
                            }
                            .frame(width: isFoc ? 520 : 420, height: isFoc ? 330 : 270)
                            .overlay(
                                RoundedRectangle(cornerRadius: 24)
                                    .stroke(isFoc ? Color.white : Color.white.opacity(0.15), lineWidth: isFoc ? 5 : 1)
                            )
                            .shadow(color: isFoc ? Color.white.opacity(0.35) : Color.black.opacity(0.6), radius: isFoc ? 30 : 12)
                            .captureFrame(id: isFoc ? "collectionItem_app_card_\(idx)_focused" : "collectionItem_app_card_\(idx)_unfocused")

                            // App Icon & Label below card
                            HStack(spacing: 14) {
                                ZStack {
                                    RoundedRectangle(cornerRadius: 10)
                                        .fill(Color.white.opacity(0.2))
                                    Image(systemName: app.icon)
                                        .font(.system(size: 18))
                                        .foregroundColor(.white)
                                }
                                .frame(width: 36, height: 36)
                                .captureFrame(id: "imageView_app_icon_\(idx)")

                                Text(app.title)
                                    .font(.system(size: 26, weight: isFoc ? .bold : .medium))
                                    .foregroundColor(isFoc ? .white : .white.opacity(0.7))
                                    .captureFrame(id: "label_app_title_\(idx)")
                            }
                        }
                        .scaleEffect(isFoc ? 1.05 : 0.95)
                    }
                }

                Spacer()

                if config.showCloseHint {
                    HStack(spacing: 12) {
                        Image(systemName: "chevron.up")
                            .font(.system(size: 20, weight: .bold))
                            .foregroundColor(.white.opacity(0.6))
                        Text("Swipe up on the clickpad to close")
                            .font(.system(size: 22, weight: .medium))
                            .foregroundColor(.white.opacity(0.6))
                    }
                    .padding(.bottom, 40)
                    .captureFrame(id: "label_close_hint")
                }
            }
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}
