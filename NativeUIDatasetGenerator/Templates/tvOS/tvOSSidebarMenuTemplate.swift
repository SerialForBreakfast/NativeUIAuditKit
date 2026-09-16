// tvOSSidebarMenuTemplate.swift
// NativeUIDatasetGenerator — tvOS templates
//
// Parameterised tvOS Navigation Sidebar template for OS UI detection (TASK-6b-E1).
// Models split-screen navigation sidebars (e.g. Apple TV app, streaming apps) with active selection indicators.
//
// Annotated elements:
//   sidebar        — left navigation sidebar container
//   listRow        — navigation rows (Home, Movies, TV Shows, Library, Settings)
//   searchField    — search input at top of sidebar
//   collectionItem — content poster tiles in main content pane
//   label          — navigation titles and content descriptions
//   imageView      — poster artwork and sidebar icons

import SwiftUI

// MARK: - tvOSSidebarMenuConfig

public struct tvOSSidebarMenuConfig: Sendable {
    public var navItems: [(title: String, icon: String)]
    public var selectedNavIndex: Int
    public var focusedNavIndex: Int? // nil if focus is in main content
    public var focusedContentIndex: Int? // index of focused grid card
    public var contentCards: [(title: String, hue: Double)]

    public init(
        navItems: [(title: String, icon: String)],
        selectedNavIndex: Int = 0,
        focusedNavIndex: Int? = 0,
        focusedContentIndex: Int? = nil,
        contentCards: [(title: String, hue: Double)] = []
    ) {
        self.navItems = navItems
        self.selectedNavIndex = selectedNavIndex
        self.focusedNavIndex = focusedNavIndex
        self.focusedContentIndex = focusedContentIndex
        self.contentCards = contentCards
    }

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> tvOSSidebarMenuConfig {
        var rng = SeededRNG(seed: seed)
        let items: [(title: String, icon: String)] = [
            ("Search", "magnifyingglass"),
            ("Home", "house.fill"),
            ("Movies", "film.fill"),
            ("TV Shows", "tv.fill"),
            ("Sports", "sportscourt.fill"),
            ("Library", "square.stack.3d.up.fill"),
            ("Settings", "gearshape.fill")
        ]

        let selected = Int(rng.next() % UInt64(items.count))
        let focusInSidebar = (rng.next() % 2 == 0)

        var cards: [(title: String, hue: Double)] = []
        for _ in 0..<6 {
            let hue = Double(rng.next() % 1000) / 1000.0
            cards.append((corpus.listRowTitle(), hue))
        }

        return tvOSSidebarMenuConfig(
            navItems: items,
            selectedNavIndex: selected,
            focusedNavIndex: focusInSidebar ? selected : nil,
            focusedContentIndex: focusInSidebar ? nil : Int(rng.next() % 6),
            contentCards: cards
        )
    }
}

// MARK: - tvOSSidebarMenuTemplate View

public struct tvOSSidebarMenuTemplate: View {
    public let config: tvOSSidebarMenuConfig

    public init(config: tvOSSidebarMenuConfig) {
        self.config = config
    }

    private let contentColumns = [
        GridItem(.fixed(380), spacing: 40),
        GridItem(.fixed(380), spacing: 40),
        GridItem(.fixed(380), spacing: 40)
    ]

    public var body: some View {
        ZStack(alignment: .topLeading) {
            Color(red: 0.05, green: 0.05, blue: 0.08).ignoresSafeArea()

            HStack(spacing: 0) {
                // 1. Pinned Navigation Sidebar
                VStack(alignment: .leading, spacing: 14) {
                    // Search header
                    HStack(spacing: 16) {
                        Image(systemName: "magnifyingglass")
                            .foregroundColor(.white.opacity(0.8))
                        Text("Search")
                            .font(.system(size: 24))
                            .foregroundColor(.white.opacity(0.6))
                        Spacer()
                    }
                    .padding(.horizontal, 24)
                    .frame(width: 420, height: 64)
                    .background(Color.white.opacity(0.08))
                    .cornerRadius(16)
                    .captureFrame(id: "searchField_sidebar_search")
                    .padding(.top, 50)
                    .padding(.bottom, 16)

                    // Nav Rows
                    ForEach(Array(config.navItems.dropFirst().enumerated()), id: \.offset) { idx, item in
                        let actualIdx = idx + 1
                        let isSelected = (actualIdx == config.selectedNavIndex)
                        let isFocused = (actualIdx == config.focusedNavIndex)

                        HStack(spacing: 20) {
                            Image(systemName: item.icon)
                                .font(.system(size: 24))
                                .foregroundColor(isFocused ? Color.black : (isSelected ? Color.white : Color.white.opacity(0.7)))
                                .captureFrame(id: "imageView_nav_icon_\(actualIdx)")

                            Text(item.title)
                                .font(.system(size: 26, weight: isFocused || isSelected ? .bold : .medium))
                                .foregroundColor(isFocused ? Color.black : (isSelected ? Color.white : Color.white.opacity(0.7)))
                                .captureFrame(id: "label_nav_title_\(actualIdx)")

                            Spacer()

                            if isSelected && !isFocused {
                                Circle()
                                    .fill(Color.white)
                                    .frame(width: 8, height: 8)
                            }
                        }
                        .padding(.horizontal, 24)
                        .frame(width: 420, height: 72)
                        .background(isFocused ? Color.white : (isSelected ? Color.white.opacity(0.15) : Color.clear))
                        .cornerRadius(18)
                        .shadow(color: isFocused ? Color.white.opacity(0.4) : Color.clear, radius: 14)
                        .captureFrame(id: isFocused ? "listRow_nav_\(actualIdx)_focused" : "listRow_nav_\(actualIdx)_unfocused")
                    }

                    Spacer()
                }
                .padding(.leading, 60)
                .frame(width: 500)
                .background(Color.black.opacity(0.4))
                .captureFrame(id: "sidebar_main_navigation")

                // 2. Main Content Area
                VStack(alignment: .leading, spacing: 32) {
                    Text(config.navItems[config.selectedNavIndex].title)
                        .font(.system(size: 48, weight: .heavy))
                        .foregroundColor(.white)
                        .padding(.top, 50)
                        .captureFrame(id: "navigationBar_content_header")

                    LazyVGrid(columns: contentColumns, spacing: 36) {
                        ForEach(Array(config.contentCards.enumerated()), id: \.offset) { cIdx, card in
                            let isCardFocused = (cIdx == config.focusedContentIndex)

                            VStack(alignment: .leading, spacing: 12) {
                                ZStack {
                                    RoundedRectangle(cornerRadius: 18)
                                        .fill(LinearGradient(
                                            colors: [Color(hue: card.hue, saturation: 0.6, brightness: 0.5), Color.black],
                                            startPoint: .topLeading,
                                            endPoint: .bottomTrailing
                                        ))
                                    Image(systemName: "play.circle.fill")
                                        .font(.system(size: 52))
                                        .foregroundColor(.white.opacity(0.85))
                                }
                                .frame(width: 380, height: 220)
                                .scaleEffect(isCardFocused ? 1.15 : 1.0)
                                .overlay(
                                    RoundedRectangle(cornerRadius: 18)
                                        .stroke(isCardFocused ? Color.white : Color.clear, lineWidth: 3)
                                )
                                .shadow(color: isCardFocused ? Color.white.opacity(0.5) : Color.black.opacity(0.5), radius: 20)
                                .captureFrame(id: isCardFocused ? "collectionItem_card_\(cIdx)_focused" : "collectionItem_card_\(cIdx)_unfocused")

                                Text(card.title)
                                    .font(.system(size: 22, weight: isCardFocused ? .bold : .medium))
                                    .foregroundColor(isCardFocused ? .white : .white.opacity(0.7))
                                    .frame(width: 380, alignment: .leading)
                                    .captureFrame(id: "label_card_title_\(cIdx)")
                            }
                        }
                    }

                    Spacer()
                }
                .padding(.leading, 60)
            }
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}
