// tvOSTopShelfMenuTemplate.swift
// NativeUIDatasetGenerator — tvOS templates
//
// Parameterised tvOS Top Shelf & Hero Carousel template for OS UI detection (TASK-6b-E1).
// Models full-bleed hero banners with play/trailer buttons, metadata tags, and content shelves.
//
// Annotated elements:
//   collectionItem  — hero featured card and bottom shelf content cards
//   primaryButton   — "Play" / "Watch Now" action button
//   secondaryButton — "Trailer" and "Add to Up Next" action buttons
//   label           — title, genre/metadata tags, synopsis description, shelf section titles
//   imageView       — hero backdrop artwork, rating bug badge, shelf thumbnails

import SwiftUI

// MARK: - tvOSTopShelfMenuConfig

public struct tvOSTopShelfMenuConfig: Sendable {
    public var title: String
    public var subtitle: String
    public var synopsis: String
    public var tags: [String]
    public var shelfItems: [(title: String, hue: Double)]
    public var focusedTarget: FocusTarget // 0: Play, 1: Trailer, 2: Watchlist, 3..N: shelf items
    public var heroHue: Double

    public enum FocusTarget: Int, Sendable {
        case play = 0
        case trailer = 1
        case watchlist = 2
        case shelf0 = 3
        case shelf1 = 4
        case shelf2 = 5
        case shelf3 = 6
    }

    public init(
        title: String,
        subtitle: String,
        synopsis: String,
        tags: [String],
        shelfItems: [(title: String, hue: Double)],
        focusedTarget: FocusTarget = .play,
        heroHue: Double = 0.55
    ) {
        self.title = title
        self.subtitle = subtitle
        self.synopsis = synopsis
        self.tags = tags
        self.shelfItems = shelfItems
        self.focusedTarget = focusedTarget
        self.heroHue = heroHue
    }

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> tvOSTopShelfMenuConfig {
        var rng = SeededRNG(seed: seed)
        let titles = ["Foundation", "Severance", "Ted Lasso", "The Morning Show", "Slow Horses", "For All Mankind", "Silo"]
        let synopses = [
            "A complex saga humans scattered on planets throughout the galaxy all living under the rule of the Galactic Empire.",
            "Mark leads a team of office workers whose memories have been surgically divided between their work and personal lives.",
            "An American football coach is hired to manage a British soccer team, bringing optimism and biscuits.",
            "An unapologetically candid look at the modern workplace through the lens of the people who help America wake up."
        ]
        let tagsPool = ["Sci-Fi", "Drama", "Comedy", "Thriller", "4K HDR", "Dolby Atmos", "TV-MA", "CC"]

        let title = titles[Int(rng.next() % UInt64(titles.count))]
        let synopsis = synopses[Int(rng.next() % UInt64(synopses.count))]
        let heroHue = Double(rng.next() % 1000) / 1000.0

        var shelf: [(title: String, hue: Double)] = []
        for _ in 0..<4 {
            let hue = Double(rng.next() % 1000) / 1000.0
            shelf.append((corpus.listRowTitle(), hue))
        }

        let focRaw = Int(rng.next() % 7)
        let focus = FocusTarget(rawValue: focRaw) ?? .play

        return tvOSTopShelfMenuConfig(
            title: title,
            subtitle: "Season \(Int(rng.next() % 3) + 1) • Episode \(Int(rng.next() % 10) + 1)",
            synopsis: synopsis,
            tags: [tagsPool[Int(rng.next() % 4)], "4K HDR", "Dolby Atmos", "TV-MA"],
            shelfItems: shelf,
            focusedTarget: focus,
            heroHue: heroHue
        )
    }
}

// MARK: - tvOSTopShelfMenuTemplate View

public struct tvOSTopShelfMenuTemplate: View {
    public let config: tvOSTopShelfMenuConfig

    public init(config: tvOSTopShelfMenuConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack(alignment: .topLeading) {
            // Full-bleed cinematic backdrop gradient
            LinearGradient(
                colors: [
                    Color(hue: config.heroHue, saturation: 0.7, brightness: 0.35),
                    Color(red: 0.06, green: 0.06, blue: 0.09)
                ],
                startPoint: .topTrailing,
                endPoint: .bottomLeading
            ).ignoresSafeArea()

            VStack(alignment: .leading, spacing: 24) {
                // Top Hero Section
                VStack(alignment: .leading, spacing: 18) {
                    Text(config.title)
                        .font(.system(size: 56, weight: .heavy))
                        .foregroundColor(.white)
                        .shadow(color: .black.opacity(0.8), radius: 10)
                        .captureFrame(id: "label_hero_title")

                    HStack(spacing: 16) {
                        Text(config.subtitle)
                            .font(.system(size: 24, weight: .semibold))
                            .foregroundColor(.white.opacity(0.9))
                            .captureFrame(id: "label_hero_subtitle")

                        ForEach(config.tags, id: \.self) { tag in
                            Text(tag)
                                .font(.system(size: 16, weight: .bold))
                                .foregroundColor(.white)
                                .padding(.horizontal, 10)
                                .padding(.vertical, 4)
                                .background(Color.white.opacity(0.18))
                                .cornerRadius(6)
                                .captureFrame(id: "label_tag_\(tag)")
                        }
                    }

                    Text(config.synopsis)
                        .font(.system(size: 22))
                        .foregroundColor(.white.opacity(0.8))
                        .lineLimit(3)
                        .frame(maxWidth: 960, alignment: .leading)
                        .captureFrame(id: "label_hero_synopsis")

                    // Transport Buttons
                    HStack(spacing: 24) {
                        // Play Button (Primary)
                        let isPlayFoc = (config.focusedTarget == .play)
                        HStack(spacing: 12) {
                            Image(systemName: "play.fill")
                                .font(.system(size: 22))
                                .captureFrame(id: "imageView_play_icon")
                            Text("Watch Now")
                                .font(.system(size: 24, weight: .bold))
                        }
                        .foregroundColor(isPlayFoc ? .black : .white)
                        .padding(.horizontal, 36)
                        .frame(height: 68)
                        .background(isPlayFoc ? Color.white : Color.white.opacity(0.2))
                        .cornerRadius(18)
                        .scaleEffect(isPlayFoc ? 1.08 : 1.0)
                        .shadow(color: isPlayFoc ? Color.white.opacity(0.5) : Color.clear, radius: 16)
                        .captureFrame(id: isPlayFoc ? "primaryButton_play_focused" : "primaryButton_play_unfocused")

                        // Trailer Button (Secondary)
                        let isTrailerFoc = (config.focusedTarget == .trailer)
                        HStack(spacing: 12) {
                            Image(systemName: "film")
                                .font(.system(size: 20))
                                .captureFrame(id: "imageView_trailer_icon")
                            Text("Trailer")
                                .font(.system(size: 22, weight: .semibold))
                        }
                        .foregroundColor(isTrailerFoc ? .black : .white)
                        .padding(.horizontal, 28)
                        .frame(height: 68)
                        .background(isTrailerFoc ? Color.white : Color.white.opacity(0.15))
                        .cornerRadius(18)
                        .scaleEffect(isTrailerFoc ? 1.08 : 1.0)
                        .shadow(color: isTrailerFoc ? Color.white.opacity(0.5) : Color.clear, radius: 16)
                        .captureFrame(id: isTrailerFoc ? "secondaryButton_trailer_focused" : "secondaryButton_trailer_unfocused")

                        // Watchlist Button (Secondary)
                        let isWatchlistFoc = (config.focusedTarget == .watchlist)
                        HStack(spacing: 12) {
                            Image(systemName: "plus")
                                .font(.system(size: 20))
                                .captureFrame(id: "imageView_watchlist_icon")
                            Text("Add to Up Next")
                                .font(.system(size: 22, weight: .semibold))
                        }
                        .foregroundColor(isWatchlistFoc ? .black : .white)
                        .padding(.horizontal, 28)
                        .frame(height: 68)
                        .background(isWatchlistFoc ? Color.white : Color.white.opacity(0.15))
                        .cornerRadius(18)
                        .scaleEffect(isWatchlistFoc ? 1.08 : 1.0)
                        .shadow(color: isWatchlistFoc ? Color.white.opacity(0.5) : Color.clear, radius: 16)
                        .captureFrame(id: isWatchlistFoc ? "secondaryButton_watchlist_focused" : "secondaryButton_watchlist_unfocused")
                    }
                    .padding(.top, 8)
                }
                .padding(.horizontal, 90)
                .padding(.top, 70)

                Spacer()

                // Bottom Shelf Carousel
                VStack(alignment: .leading, spacing: 16) {
                    Text("Related Shows")
                        .font(.system(size: 28, weight: .bold))
                        .foregroundColor(.white)
                        .captureFrame(id: "label_shelf_heading")

                    HStack(spacing: 36) {
                        ForEach(Array(config.shelfItems.enumerated()), id: \.offset) { idx, item in
                            let isFoc = (config.focusedTarget.rawValue == 3 + idx)
                            VStack(alignment: .leading, spacing: 10) {
                                ZStack {
                                    RoundedRectangle(cornerRadius: 16)
                                        .fill(LinearGradient(
                                            colors: [Color(hue: item.hue, saturation: 0.6, brightness: 0.5), Color.black.opacity(0.6)],
                                            startPoint: .topLeading,
                                            endPoint: .bottomTrailing
                                        ))
                                    Image(systemName: "play.circle.fill")
                                        .font(.system(size: 44))
                                        .foregroundColor(.white.opacity(0.85))
                                        .captureFrame(id: "imageView_card_thumb_\(idx)")
                                }
                                .frame(width: 400, height: 230)
                                .scaleEffect(isFoc ? 1.12 : 1.0)
                                .overlay(
                                    RoundedRectangle(cornerRadius: 16)
                                        .stroke(isFoc ? Color.white : Color.clear, lineWidth: 3)
                                )
                                .shadow(color: isFoc ? Color.white.opacity(0.5) : Color.clear, radius: 16)
                                .captureFrame(id: isFoc ? "collectionItem_related_\(idx)_focused" : "collectionItem_related_\(idx)_unfocused")

                                Text(item.title)
                                    .font(.system(size: 20, weight: isFoc ? .bold : .medium))
                                    .foregroundColor(isFoc ? .white : .white.opacity(0.7))
                                    .frame(width: 400, alignment: .leading)
                                    .captureFrame(id: "label_card_title_\(idx)")
                            }
                        }
                    }
                }
                .padding(.horizontal, 90)
                .padding(.bottom, 60)
            }
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}
