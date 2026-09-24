// RichContentFeedTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised rich content feed template for the 41-class holdout addon.
// Covers indicators and content types previously missing from holdout:
//   collectionItem, mapView, activityIndicator, refreshControl, scrollIndicator,
//   link, tooltip, imageView, label, navigationBar.
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset() (BP-01)
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - RichContentFeedConfig

public struct RichContentFeedConfig: Sendable {
    public var title: String
    public var locationName: String
    public var cardTitles: [String]
    public var showTooltip: Bool
    public var colorScheme: ColorScheme

    public init(
        title: String,
        locationName: String,
        cardTitles: [String],
        showTooltip: Bool,
        colorScheme: ColorScheme
    ) {
        self.title = title
        self.locationName = locationName
        self.cardTitles = cardTitles
        self.showTooltip = showTooltip
        self.colorScheme = colorScheme
    }

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> RichContentFeedConfig {
        var rng = SeededRNG(seed: seed)
        let isDark = (rng.next() % 2) == 0
        let showTip = (rng.next() % 2) == 0

        let titles = ["Explore Places", "Local Guides", "Travel Highlights", "City Discoveries"]
        let locations = ["San Francisco, CA", "Seattle, WA", "Austin, TX", "Denver, CO", "Chicago, IL"]
        let cards = [
            "Golden Gate Park", "Waterfront Promenade", "Downtown Arts Center", "Historic District",
            "Botanical Conservatory", "Mountain Vista Trail", "Harbor Market Square", "Civic Center Plaza"
        ]

        let title = titles[Int(rng.next() % UInt64(titles.count))]
        let location = locations[Int(rng.next() % UInt64(locations.count))]

        var selectedCards: [String] = []
        let cardCount = 4
        for i in 0..<cardCount {
            selectedCards.append(cards[(Int(rng.next() % UInt64(cards.count)) + i) % cards.count])
        }

        return RichContentFeedConfig(
            title: title,
            locationName: location,
            cardTitles: selectedCards,
            showTooltip: showTip,
            colorScheme: isDark ? .dark : .light
        )
    }
}

// MARK: - RichContentFeedTemplate View

public struct RichContentFeedTemplate: View {
    public let config: RichContentFeedConfig

    public init(config: RichContentFeedConfig) {
        self.config = config
    }

    private var isDark: Bool { config.colorScheme == .dark }
    private var bgColor: Color { isDark ? Color.black : Color(white: 0.95) }
    private var cardBg: Color { isDark ? Color(white: 0.16) : Color.white }
    private var textColor: Color { isDark ? .white : .black }
    private var subtextColor: Color { isDark ? Color(white: 0.65) : Color(white: 0.45) }

    public var body: some View {
        ZStack(alignment: .top) {
            bgColor.ignoresSafeArea(.all)

            VStack(spacing: 0) {
                // Navigation Bar Header
                HStack {
                    Text(config.title)
                        .font(.title2.weight(.bold))
                        .foregroundColor(textColor)
                        .captureFrame(id: "label_feedTitle")

                    Spacer()

                    Button(action: {}) {
                        Image(systemName: "magnifyingglass")
                            .foregroundColor(.blue)
                    }
                }
                .padding(.horizontal, 16)
                .padding(.top, 54)
                .padding(.bottom, 10)
                .background(isDark ? Color(white: 0.12) : Color(white: 0.98))
                .captureFrame(id: "navigationBar_feedNav")

                // Pull-to-refresh control indicator at top of scrollable feed
                HStack(spacing: 8) {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: .gray))
                    Text("Checking for updates…")
                        .font(.caption)
                        .foregroundColor(subtextColor)
                }
                .frame(maxWidth: .infinity)
                .frame(height: 36)
                .background(bgColor)
                .captureFrame(id: "refreshControl_topSpinner")

                ScrollView {
                    VStack(spacing: 16) {
                        // 1. Map View Embedded Card
                        renderMapViewCard()

                        // 2. Collection Items 2x2 Grid
                        renderCollectionItemsGrid()

                        // 3. Activity Indicator loading section
                        renderLoadingSection()

                        // 4. Link & Footer
                        renderFooterAndLinks()
                    }
                    .padding(.horizontal, 16)
                    .padding(.top, 10)
                    .padding(.bottom, 40)
                }
            }

            // Scroll indicator along the right edge of screen
            VStack {
                Spacer().frame(height: 120)
                Capsule()
                    .fill(Color.gray.opacity(0.6))
                    .frame(width: 3, height: 60)
                    .captureFrame(id: "scrollIndicator_edgeBar")
                Spacer()
            }
            .frame(maxWidth: .infinity, alignment: .trailing)
            .padding(.trailing, 4)

            // Optional Tooltip overlay
            if config.showTooltip {
                renderTooltip()
            }
        }
        .preferredColorScheme(config.colorScheme)
    }

    // MARK: - Sections

    @ViewBuilder
    private func renderMapViewCard() -> some View {
        VStack(alignment: .leading, spacing: 0) {
            ZStack(alignment: .bottomLeading) {
                // Synthesized Map styling
                Rectangle()
                    .fill(isDark ? Color(red: 0.18, green: 0.24, blue: 0.28) : Color(red: 0.82, green: 0.90, blue: 0.88))
                    .frame(height: 140)
                    .overlay(
                        VStack(spacing: 6) {
                            HStack {
                                Spacer()
                                Image(systemName: "mappin.circle.fill")
                                    .font(.title)
                                    .foregroundColor(.red)
                                Spacer()
                            }
                            Text(config.locationName)
                                .font(.caption.weight(.semibold))
                                .foregroundColor(textColor)
                        }
                    )

                LinearGradient(colors: [.clear, Color.black.opacity(0.4)], startPoint: .top, endPoint: .bottom)
                    .frame(height: 40)
            }
            .cornerRadius(12)
            .captureFrame(id: "mapView_heroMap")
        }
    }

    @ViewBuilder
    private func renderCollectionItemsGrid() -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Featured Landmarks")
                .font(.headline)
                .foregroundColor(textColor)
                .captureFrame(id: "label_sectionHeader")

            LazyVGrid(columns: [GridItem(.flexible(), spacing: 12), GridItem(.flexible(), spacing: 12)], spacing: 12) {
                ForEach(0..<config.cardTitles.count, id: \.self) { idx in
                    VStack(alignment: .leading, spacing: 6) {
                        Rectangle()
                            .fill(LinearGradient(colors: [.blue.opacity(0.7), .teal.opacity(0.5)], startPoint: .topLeading, endPoint: .bottomTrailing))
                            .frame(height: 80)
                            .cornerRadius(8)
                            .overlay(
                                Image(systemName: "photo.fill")
                                    .foregroundColor(.white.opacity(0.8))
                                    .captureFrame(id: "imageView_cardThumb\(idx)")
                            )

                        Text(config.cardTitles[idx])
                            .font(.subheadline.weight(.semibold))
                            .foregroundColor(textColor)
                            .lineLimit(1)
                            .captureFrame(id: "label_cardTitle\(idx)")

                        Text("Free admission • 0.8 mi")
                            .font(.caption2)
                            .foregroundColor(subtextColor)
                    }
                    .padding(8)
                    .background(cardBg)
                    .cornerRadius(10)
                    .captureFrame(id: "collectionItem_card\(idx)")
                }
            }
        }
    }

    @ViewBuilder
    private func renderLoadingSection() -> some View {
        HStack(spacing: 12) {
            ProgressView()
                .progressViewStyle(CircularProgressViewStyle(tint: .blue))
                .scaleEffect(1.1)
                .captureFrame(id: "activityIndicator_loader")

            Text("Loading additional recommendations…")
                .font(.footnote)
                .foregroundColor(subtextColor)
                .captureFrame(id: "label_loadingText")

            Spacer()
        }
        .padding(14)
        .background(cardBg)
        .cornerRadius(10)
    }

    @ViewBuilder
    private func renderFooterAndLinks() -> some View {
        VStack(spacing: 8) {
            Text("Data sourced from OpenMap Services.")
                .font(.caption)
                .foregroundColor(subtextColor)

            HStack(spacing: 16) {
                Text("Privacy Policy")
                    .font(.caption.weight(.medium))
                    .foregroundColor(.blue)
                    .underline()
                    .captureFrame(id: "link_privacy")

                Text("Terms of Service")
                    .font(.caption.weight(.medium))
                    .foregroundColor(.blue)
                    .underline()
                    .captureFrame(id: "link_terms")
            }
        }
        .padding(.vertical, 8)
    }

    @ViewBuilder
    private func renderTooltip() -> some View {
        VStack(spacing: 4) {
            Text("Tap any card to view detailed directions")
                .font(.caption.weight(.medium))
                .foregroundColor(.white)
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 8)
        .background(Color.black.opacity(0.85))
        .cornerRadius(8)
        .shadow(radius: 4)
        .padding(.top, 140)
        .captureFrame(id: "tooltip_hint")
    }
}
