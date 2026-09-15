// tvOSTopTabBarTemplate.swift
// NativeUIDatasetGenerator — tvOS templates
//
// Parameterised tvOS Top Tab Bar template for OS UI detection.
// Models top-of-screen navigation chrome on Apple TV (pinned in top 15% of image height).
//
// Annotated elements:
//   tabBar         — top navigation bar container
//   primaryButton  — individual tab navigation buttons (focused / unfocused)
//   collectionItem — featured content cards below the tab bar
//   label          — tab titles and section headers

import SwiftUI

// MARK: - tvOSTopTabBarConfig

public struct tvOSTopTabBarConfig: Sendable {
    public var tabs: [String]
    public var focusedTabIndex: Int
    public var heroTitle: String

    public init(tabs: [String], focusedTabIndex: Int, heroTitle: String) {
        self.tabs = tabs
        self.focusedTabIndex = focusedTabIndex
        self.heroTitle = heroTitle
    }

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> tvOSTopTabBarConfig {
        var rng = SeededRNG(seed: seed)
        let tabNames = ["Apple TV+", "MLS Season Pass", "Store", "Library", "Search"]
        let focIdx = Int(rng.next() % UInt64(tabNames.count))

        return tvOSTopTabBarConfig(
            tabs: tabNames,
            focusedTabIndex: focIdx,
            heroTitle: corpus.navigationTitle()
        )
    }
}

// MARK: - tvOSTopTabBarTemplate View

public struct tvOSTopTabBarTemplate: View {
    public let config: tvOSTopTabBarConfig

    public init(config: tvOSTopTabBarConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack(alignment: .top) {
            Color(red: 0.04, green: 0.04, blue: 0.06).ignoresSafeArea()

            VStack(spacing: 0) {
                // Top Tab Bar Container (pinned in top 15% of screen height)
                HStack(spacing: 24) {
                    ForEach(Array(config.tabs.enumerated()), id: \.offset) { idx, tab in
                        let isFoc = (idx == config.focusedTabIndex)
                        Text(tab)
                            .font(.system(size: 24, weight: isFoc ? .bold : .medium))
                            .foregroundColor(isFoc ? .black : .white.opacity(0.8))
                            .padding(.horizontal, 28)
                            .padding(.vertical, 12)
                            .background(isFoc ? Color.white : Color.clear)
                            .cornerRadius(20)
                            .shadow(color: isFoc ? Color.white.opacity(0.4) : Color.clear, radius: 14)
                            .captureFrame(id: isFoc ? "primaryButton_tab_\(idx)_focused" : "primaryButton_tab_\(idx)_unfocused")
                    }
                }
                .frame(maxWidth: .infinity)
                .frame(height: 110)
                .background(Color.black.opacity(0.3))
                .captureFrame(id: "tabBar_top_navigation")
                .padding(.top, 20)

                // Hero Content Area Below Tab Bar
                VStack(alignment: .leading, spacing: 20) {
                    Text(config.heroTitle)
                        .font(.system(size: 48, weight: .heavy))
                        .foregroundColor(.white)
                        .captureFrame(id: "label_hero_title")

                    ZStack {
                        RoundedRectangle(cornerRadius: 24)
                            .fill(LinearGradient(
                                colors: [Color.blue.opacity(0.6), Color.purple.opacity(0.4)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            ))
                        Image(systemName: "play.circle.fill")
                            .font(.system(size: 80))
                            .foregroundColor(.white.opacity(0.9))
                    }
                    .frame(width: 1740, height: 680)
                    .captureFrame(id: "collectionItem_hero_banner_unfocused")
                }
                .padding(.horizontal, 90)
                .padding(.top, 40)
            }
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}
