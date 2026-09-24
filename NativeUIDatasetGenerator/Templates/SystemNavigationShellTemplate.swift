// SystemNavigationShellTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised system navigation shell template for the 41-class holdout addon.
// Covers chrome and navigation controls that were previously missing from holdout:
//   tabBar, toolbar, sidebar, statusBar, dynamicIsland, searchField,
//   navigationBar, listRow, label.
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset() (BP-01)
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - SystemNavigationShellConfig

public struct SystemNavigationShellConfig: Sendable {
    public var hasSidebar: Bool
    public var hasDynamicIsland: Bool
    public var title: String
    public var searchPlaceholder: String
    public var items: [String]
    public var colorScheme: ColorScheme
    public var timeText: String

    public init(
        hasSidebar: Bool,
        hasDynamicIsland: Bool,
        title: String,
        searchPlaceholder: String,
        items: [String],
        colorScheme: ColorScheme,
        timeText: String
    ) {
        self.hasSidebar = hasSidebar
        self.hasDynamicIsland = hasDynamicIsland
        self.title = title
        self.searchPlaceholder = searchPlaceholder
        self.items = items
        self.colorScheme = colorScheme
        self.timeText = timeText
    }

    public static func make(seed: UInt64, corpus: inout ContentCorpus, osProfile: OSVisualProfile = .ios26) -> SystemNavigationShellConfig {
        var rng = SeededRNG(seed: seed)
        let isDark = (rng.next() % 2) == 0
        let hasSidebar = (rng.next() % 3) == 0  // ~33% have split sidebar layout
        let hasDynamicIsland = osProfile.hasDynamicIsland

        let titles = ["Documents", "Workspace", "Library", "Explorer", "Projects", "Catalog"]
        let searches = ["Search documents", "Find items", "Filter results", "Quick search", "Search library"]
        let itemPool = [
            "Project Proposal 2026.pdf", "Executive Summary.docx", "Quarterly Budget.xlsx",
            "App Architecture.key", "Design Guidelines.sketch", "User Interview Notes.txt",
            "Security Audit Report.pdf", "Release Checklist.md"
        ]

        let title = titles[Int(rng.next() % UInt64(titles.count))]
        let search = searches[Int(rng.next() % UInt64(searches.count))]
        let itemCount = 3 + Int(rng.next() % 4) // 3–6 rows
        var selectedItems: [String] = []
        for i in 0..<itemCount {
            selectedItems.append(itemPool[i % itemPool.count])
        }

        let times = ["09:41", "12:30", "14:15", "18:00"]
        let time = times[Int(rng.next() % UInt64(times.count))]

        return SystemNavigationShellConfig(
            hasSidebar: hasSidebar,
            hasDynamicIsland: hasDynamicIsland,
            title: title,
            searchPlaceholder: search,
            items: selectedItems,
            colorScheme: isDark ? .dark : .light,
            timeText: time
        )
    }
}

// MARK: - SystemNavigationShellTemplate View

public struct SystemNavigationShellTemplate: View {
    public let config: SystemNavigationShellConfig

    public init(config: SystemNavigationShellConfig) {
        self.config = config
    }

    private var isDark: Bool { config.colorScheme == .dark }
    private var bgColor: Color { isDark ? Color.black : Color(white: 0.94) }
    private var navBg: Color { isDark ? Color(white: 0.12) : Color(white: 0.98) }
    private var textColor: Color { isDark ? .white : .black }
    private var subtextColor: Color { isDark ? Color(white: 0.65) : Color(white: 0.45) }
    private var rowBg: Color { isDark ? Color(white: 0.16) : Color.white }

    public var body: some View {
        ZStack(alignment: .top) {
            bgColor.ignoresSafeArea(.all)

            VStack(spacing: 0) {
                // Top status bar area
                renderStatusBar()

                // Navigation Header + Search
                renderNavigationBar()

                // Main body: sidebar (optional) + list content
                HStack(spacing: 0) {
                    if config.hasSidebar {
                        renderSidebar()
                        Divider()
                    }

                    renderContentList()
                }

                // Toolbar actions strip
                renderToolbar()

                // Bottom Tab Bar
                renderTabBar()
            }
        }
        .preferredColorScheme(config.colorScheme)
    }

    // MARK: - Subcomponents

    @ViewBuilder
    private func renderStatusBar() -> some View {
        HStack {
            Text(config.timeText)
                .font(.footnote.weight(.semibold))
                .foregroundColor(textColor)
                .padding(.leading, 24)

            Spacer()

            if config.hasDynamicIsland {
                Capsule()
                    .fill(Color.black)
                    .frame(width: 124, height: 35)
                    .overlay(
                        HStack(spacing: 6) {
                            Circle().fill(Color.green).frame(width: 8, height: 8)
                            Spacer()
                            Circle().fill(Color(white: 0.2)).frame(width: 11, height: 11)
                        }
                        .padding(.horizontal, 10)
                    )
                    .captureFrame(id: "dynamicIsland_island")
            }

            Spacer()

            HStack(spacing: 4) {
                Image(systemName: "cellularbars").foregroundColor(textColor)
                Image(systemName: "wifi").foregroundColor(textColor)
                Image(systemName: "battery.75").foregroundColor(textColor)
            }
            .font(.footnote)
            .padding(.trailing, 24)
        }
        .frame(height: 50)
        .background(navBg)
        .captureFrame(id: "statusBar_top")
    }

    @ViewBuilder
    private func renderNavigationBar() -> some View {
        VStack(spacing: 8) {
            HStack {
                Text(config.title)
                    .font(.title2.weight(.bold))
                    .foregroundColor(textColor)
                    .captureFrame(id: "label_navTitle")

                Spacer()

                Button(action: {}) {
                    Image(systemName: "ellipsis.circle")
                        .font(.title3)
                        .foregroundColor(.blue)
                }
            }
            .padding(.horizontal, 16)

            // Search field
            HStack(spacing: 8) {
                Image(systemName: "magnifyingglass")
                    .foregroundColor(subtextColor)
                Text(config.searchPlaceholder)
                    .foregroundColor(subtextColor)
                    .font(.body)
                Spacer()
            }
            .padding(.horizontal, 10)
            .frame(height: 38)
            .background(isDark ? Color(white: 0.22) : Color(white: 0.90))
            .cornerRadius(10)
            .padding(.horizontal, 16)
            .padding(.bottom, 6)
            .captureFrame(id: "searchField_input")
        }
        .background(navBg)
        .captureFrame(id: "navigationBar_header")
    }

    @ViewBuilder
    private func renderSidebar() -> some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack {
                Text("FAVORITES")
                    .font(.caption.weight(.semibold))
                    .foregroundColor(subtextColor)
                Spacer()
            }
            .padding(.top, 12)

            Label("All Files", systemImage: "folder")
                .foregroundColor(textColor)
                .font(.subheadline)

            Label("Shared", systemImage: "person.2")
                .foregroundColor(textColor)
                .font(.subheadline)

            Label("Recent", systemImage: "clock")
                .foregroundColor(textColor)
                .font(.subheadline)

            Spacer()
        }
        .padding(.horizontal, 12)
        .frame(width: 130)
        .background(navBg.opacity(0.85))
        .captureFrame(id: "sidebar_panel")
    }

    @ViewBuilder
    private func renderContentList() -> some View {
        ScrollView {
            VStack(spacing: 8) {
                ForEach(0..<config.items.count, id: \.self) { idx in
                    HStack(spacing: 12) {
                        Image(systemName: "doc.fill")
                            .foregroundColor(.blue)
                            .font(.title3)

                        VStack(alignment: .leading, spacing: 2) {
                            Text(config.items[idx])
                                .font(.body.weight(.medium))
                                .foregroundColor(textColor)
                                .captureFrame(id: "label_rowTitle\(idx)")

                            Text("Updated yesterday • 2.4 MB")
                                .font(.caption)
                                .foregroundColor(subtextColor)
                        }

                        Spacer()

                        Image(systemName: "chevron.right")
                            .font(.footnote)
                            .foregroundColor(subtextColor)
                    }
                    .padding(.horizontal, 14)
                    .frame(height: 56)
                    .background(rowBg)
                    .cornerRadius(10)
                    .padding(.horizontal, 12)
                    .captureFrame(id: "listRow_item\(idx)")
                }
            }
            .padding(.top, 10)
        }
    }

    @ViewBuilder
    private func renderToolbar() -> some View {
        HStack {
            Button(action: {}) {
                Image(systemName: "line.3.horizontal.decrease.circle")
                    .font(.title3)
                    .foregroundColor(.blue)
            }

            Spacer()

            Text("\(config.items.count) Items")
                .font(.caption)
                .foregroundColor(subtextColor)
                .captureFrame(id: "label_toolbarCount")

            Spacer()

            Button(action: {}) {
                Image(systemName: "square.and.arrow.up")
                    .font(.title3)
                    .foregroundColor(.blue)
            }
        }
        .padding(.horizontal, 20)
        .frame(height: 44)
        .background(navBg)
        .captureFrame(id: "toolbar_actions")
    }

    @ViewBuilder
    private func renderTabBar() -> some View {
        HStack {
            Spacer()
            VStack(spacing: 3) {
                Image(systemName: "folder.fill").font(.system(size: 20)).foregroundColor(.blue)
                Text("Browse").font(.caption2).foregroundColor(.blue)
            }
            Spacer()
            VStack(spacing: 3) {
                Image(systemName: "clock").font(.system(size: 20)).foregroundColor(subtextColor)
                Text("Recent").font(.caption2).foregroundColor(subtextColor)
            }
            Spacer()
            VStack(spacing: 3) {
                Image(systemName: "star").font(.system(size: 20)).foregroundColor(subtextColor)
                Text("Favorites").font(.caption2).foregroundColor(subtextColor)
            }
            Spacer()
        }
        .frame(height: 52)
        .background(navBg)
        .overlay(Divider(), alignment: .top)
        .captureFrame(id: "tabBar_bottom")
    }
}
