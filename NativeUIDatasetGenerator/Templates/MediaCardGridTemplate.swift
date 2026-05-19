// MediaCardGridTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI media card grid template (TASK-5b-7).
// Compiled exclusively into the iOS GeneratorRunner Xcode target.
//
// Annotated elements:
//   collectionItem — each card cell in the grid
//   imageView      — the thumbnail image inside each card
//   label          — the card title below the thumbnail
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - MediaCardConfig

/// One card in the grid.
public struct MediaCardConfig: Sendable {
    public var title: String
    public var hue: Double         // 0–1, drives thumbnail tint
    public var symbolName: String  // SF Symbol for placeholder thumbnail

    public init(title: String, hue: Double, symbolName: String) {
        self.title = title
        self.hue = hue
        self.symbolName = symbolName
    }
}

// MARK: - MediaCardGridConfig

/// Parameterised inputs for a single MediaCardGrid rendering.
public struct MediaCardGridConfig: Sendable {
    /// Navigation bar title.
    public var title: String
    /// Card items to show (4–9 cards).
    public var cards: [MediaCardConfig]
    /// Number of columns (2 or 3).
    public var columnCount: Int
    /// Color scheme applied to the view.
    public var colorScheme: ColorScheme

    public init(
        title: String,
        cards: [MediaCardConfig],
        columnCount: Int,
        colorScheme: ColorScheme
    ) {
        self.title = title
        self.cards = cards
        self.columnCount = columnCount
        self.colorScheme = colorScheme
    }

    private static let symbols = [
        "photo", "film", "music.note", "play.circle",
        "doc.richtext", "map", "camera", "waveform",
        "newspaper", "star.fill",
    ]

    /// Deterministic factory — same `seed` always produces the same config.
    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> MediaCardGridConfig {
        var rng = SeededRNG(seed: seed)
        let dark      = rng.next() % 2 == 0
        let cols      = rng.next() % 2 == 0 ? 2 : 3
        let cardCount = 4 + Int(rng.next() % 6)  // 4–9 cards

        var cards: [MediaCardConfig] = []
        for _ in 0..<cardCount {
            let hue = Double(rng.next() % 1000) / 1000.0
            let sym = symbols[Int(rng.next() % UInt64(symbols.count))]
            cards.append(MediaCardConfig(
                title: corpus.listRowTitle(),
                hue: hue,
                symbolName: sym
            ))
        }

        return MediaCardGridConfig(
            title: corpus.navigationTitle(),
            cards: cards,
            columnCount: cols,
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - MediaCardGridTemplate

/// SwiftUI view rendering a 2- or 3-column media card grid.
///
/// **Platform scope:** iOS GeneratorRunner target only.
public struct MediaCardGridTemplate: View {
    public let config: MediaCardGridConfig

    public init(config: MediaCardGridConfig) {
        self.config = config
    }

    private var columns: [GridItem] {
        Array(repeating: GridItem(.flexible(), spacing: 12), count: config.columnCount)
    }

    public var body: some View {
        NavigationStack {
            ZStack {
                Color(UIColor.systemGroupedBackground).ignoresSafeArea()

                ScrollView {
                    LazyVGrid(columns: columns, spacing: 12) {
                        ForEach(Array(config.cards.enumerated()), id: \.offset) { idx, card in
                            VStack(alignment: .leading, spacing: 0) {
                                // Thumbnail image
                                ZStack {
                                    Color(hue: card.hue, saturation: 0.55, brightness: 0.75)
                                    Image(systemName: card.symbolName)
                                        .font(.system(size: 28))
                                        .foregroundStyle(.white.opacity(0.9))
                                }
                                .aspectRatio(4/3, contentMode: .fit)
                                .clipShape(RoundedRectangle(cornerRadius: 8))
                                .captureFrame(id: "imageView_thumb_\(idx)")

                                // Card title label — captureFrame before padding (BP-18)
                                Text(card.title)
                                    .font(.caption.weight(.medium))
                                    .lineLimit(2)
                                    .captureFrame(id: "label_card_\(idx)")
                                    .padding(.top, 6)
                                    .padding(.horizontal, 2)
                            }
                            .padding(8)
                            .background(Color(UIColor.systemBackground))
                            .clipShape(RoundedRectangle(cornerRadius: 12))
                            .captureFrame(id: "collectionItem_\(idx)")
                        }
                    }
                    .padding(16)
                }
            }
            .ignoresSafeArea(.all)
            .navigationTitle(config.title)
            .navigationBarTitleDisplayMode(.large)
            .colorScheme(config.colorScheme)
        }
        .colorScheme(config.colorScheme)
    }
}
