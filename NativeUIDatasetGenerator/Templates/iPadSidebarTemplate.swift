// iPadSidebarTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised split-view sidebar template (TASK-5b-22, class: sidebar).
// Simulates an iPadOS regular-width layout with a left sidebar list and a right
// detail pane. Because we need both columns visible simultaneously (the `sidebar`
// element is the whole left column), this is drawn manually inside a ZStack/HStack
// rather than using NavigationSplitView (which is non-deterministic for column widths).
//
// Annotated elements:
//   sidebar      — left column panel (the entire sidebar area)
//   listRow      — each row inside the sidebar
//   label        — sidebar section header, row titles, and detail content labels
//   navigationBar — auto-detected (from NavigationStack inside detail pane)
//   imageView    — detail pane hero placeholder
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - SidebarItem

public struct SidebarItem: Sendable {
    public var label: String
    public var iconName: String
    public var isSelected: Bool
}

// MARK: - iPadSidebarConfig

public struct iPadSidebarConfig: Sendable {
    public var sidebarTitle: String
    public var items: [SidebarItem]   // 4–7 sidebar items
    public var detailTitle: String
    public var detailBody: String
    public var detailHue: Double
    public var colorScheme: ColorScheme

    public init(
        sidebarTitle: String,
        items: [SidebarItem],
        detailTitle: String,
        detailBody: String,
        detailHue: Double,
        colorScheme: ColorScheme
    ) {
        self.sidebarTitle = sidebarTitle
        self.items = items
        self.detailTitle = detailTitle
        self.detailBody = detailBody
        self.detailHue = detailHue
        self.colorScheme = colorScheme
    }

    private static let navItems: [(label: String, icon: String)] = [
        ("Inbox",       "tray.fill"),
        ("Sent",        "paperplane.fill"),
        ("Drafts",      "doc.fill"),
        ("Favourites",  "star.fill"),
        ("Archive",     "archivebox.fill"),
        ("Trash",       "trash.fill"),
        ("Folders",     "folder.fill"),
        ("Labels",      "tag.fill"),
        ("Reports",     "chart.bar.fill"),
        ("Settings",    "gearshape.fill"),
    ]

    private static let detailBodies = [
        "Select an item from the sidebar to view its contents here.",
        "The selected section contains items matching your current filters.",
        "No additional configuration is required for this section.",
        "Content for the selected category is displayed in this area.",
    ]

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> iPadSidebarConfig {
        var rng   = SeededRNG(seed: seed)
        let dark  = rng.next() % 2 == 0
        let count = 4 + Int(rng.next() % 4)   // 4–7 items
        let selIdx = Int(rng.next() % UInt64(count))
        let pool  = navItems.shuffled(using: &rng)
        var items: [SidebarItem] = []
        for i in 0..<count {
            let def = pool[i % pool.count]
            items.append(SidebarItem(label: def.label, iconName: def.icon,
                                     isSelected: i == selIdx))
        }
        let hue = Double(rng.next() % 1000) / 1000.0
        let detBody = detailBodies[Int(rng.next() % UInt64(detailBodies.count))]
        return iPadSidebarConfig(
            sidebarTitle: corpus.navigationTitle(),
            items: items,
            detailTitle: items[selIdx].label,
            detailBody: detBody,
            detailHue: hue,
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - iPadSidebarTemplate

public struct iPadSidebarTemplate: View {
    public let config: iPadSidebarConfig

    public init(config: iPadSidebarConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack {
            Color(UIColor.systemBackground).ignoresSafeArea()

            GeometryReader { proxy in
                let sidebarW: CGFloat = min(280, proxy.size.width * 0.30)

                HStack(spacing: 0) {
                    // ── Left sidebar pane ──
                    VStack(alignment: .leading, spacing: 0) {
                        Text(config.sidebarTitle)
                            .font(.headline)
                            .padding(.horizontal, 16)
                            .padding(.top, 60)
                            .padding(.bottom, 12)
                            .captureFrame(id: "label_sidebar_title")

                        ForEach(Array(config.items.enumerated()), id: \.offset) { idx, item in
                            HStack(spacing: 10) {
                                Image(systemName: item.iconName)
                                    .foregroundStyle(item.isSelected ? .white : .accentColor)
                                    .frame(width: 20)
                                Text(item.label)
                                    .font(.body)
                                    .foregroundStyle(item.isSelected ? .white : .primary)
                                    .captureFrame(id: "label_sidebar_row_\(idx)")
                                Spacer()
                            }
                            .padding(.horizontal, 12)
                            .padding(.vertical, 10)
                            .background(
                                item.isSelected
                                    ? Color.accentColor
                                    : Color.clear
                            )
                            .clipShape(RoundedRectangle(cornerRadius: 8))
                            .padding(.horizontal, 8)
                            .captureFrame(id: "listRow_\(idx)")
                        }
                        Spacer()
                    }
                    .frame(width: sidebarW)
                    .background(Color(UIColor.secondarySystemBackground))
                    .captureFrame(id: "sidebar_0")

                    Divider()

                    // ── Right detail pane ──
                    VStack(alignment: .leading, spacing: 12) {
                        Color(hue: config.detailHue, saturation: 0.35, brightness: 0.70)
                            .frame(maxWidth: .infinity)
                            .frame(height: 160)
                            .overlay(
                                Image(systemName: "doc.text.image")
                                    .font(.largeTitle)
                                    .foregroundStyle(.white.opacity(0.6))
                            )
                            .captureFrame(id: "imageView_detail_hero")

                        Text(config.detailTitle)
                            .font(.title3.bold())
                            .padding(.horizontal, 20)
                            .captureFrame(id: "label_detail_title")

                        Text(config.detailBody)
                            .font(.body)
                            .foregroundStyle(.secondary)
                            .padding(.horizontal, 20)
                            .captureFrame(id: "label_detail_body")

                        Spacer()
                    }
                    .padding(.top, 44)   // approximate nav bar offset (no nav bar in detail pane)
                }
            }
        }
        .ignoresSafeArea(.all)
        .colorScheme(config.colorScheme)
    }
}

// MARK: - Array+shuffled(using:) (local copy for this file)

private extension Array {
    func shuffled(using rng: inout SeededRNG) -> [Element] {
        var copy = self
        for i in stride(from: copy.count - 1, through: 1, by: -1) {
            let j = Int(rng.next() % UInt64(i + 1))
            copy.swapAt(i, j)
        }
        return copy
    }
}
