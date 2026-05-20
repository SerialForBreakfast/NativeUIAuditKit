// MenuButtonTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI Menu (pull-down) button template (TASK-5b-22, class: menuButton).
// Covers SwiftUI Menu / UIButton with .menu — not represented in any prior template.
//
// Annotated elements:
//   menuButton   — SwiftUI Menu (the trigger button, closed state)
//   listRow      — surrounding list rows that provide context
//   label        — row labels and section headers
//   navigationBar — auto-detected
//
// The menu is always shown in its closed/trigger state (annotation = the button that
// opens the menu). The expanded popover state is covered by PopoverTemplate.
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - MenuButtonConfig

public struct MenuButtonConfig: Sendable {
    public var title: String
    /// Items shown in the first menu (2–4 options).
    public var menuItems: [String]
    /// Label for the first menu trigger.
    public var menuTriggerLabel: String
    /// Current selection display text.
    public var selectedLabel: String
    /// Whether a second menu button is shown in another row.
    public var showSecondMenu: Bool
    public var secondMenuLabel: String
    public var secondMenuItems: [String]
    public var colorScheme: ColorScheme

    public init(
        title: String,
        menuItems: [String],
        menuTriggerLabel: String,
        selectedLabel: String,
        showSecondMenu: Bool,
        secondMenuLabel: String,
        secondMenuItems: [String],
        colorScheme: ColorScheme
    ) {
        self.title = title
        self.menuItems = menuItems
        self.menuTriggerLabel = menuTriggerLabel
        self.selectedLabel = selectedLabel
        self.showSecondMenu = showSecondMenu
        self.secondMenuLabel = secondMenuLabel
        self.secondMenuItems = secondMenuItems
        self.colorScheme = colorScheme
    }

    /// Standard SwiftUI sort/filter option pools.
    private static let sortOptions = ["Newest First", "Oldest First", "A–Z", "Z–A", "Most Popular"]
    private static let filterOptions = ["All", "Unread", "Flagged", "Archived", "Deleted"]
    private static let viewOptions = ["List", "Grid", "Compact", "Detailed"]

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> MenuButtonConfig {
        var rng = SeededRNG(seed: seed)
        let dark       = rng.next() % 2 == 0
        let showSecond = rng.next() % 2 == 0
        let menuCount  = 2 + Int(rng.next() % 3)   // 2–4 items
        let pool       = sortOptions
        var items: [String] = []
        for i in 0..<menuCount { items.append(pool[Int(rng.next() % UInt64(pool.count))]) }
        let selectedIdx = Int(rng.next() % UInt64(items.count))
        let secondPool = filterOptions
        var items2: [String] = []
        for _ in 0..<3 { items2.append(secondPool[Int(rng.next() % UInt64(secondPool.count))]) }
        return MenuButtonConfig(
            title: corpus.navigationTitle(),
            menuItems: items,
            menuTriggerLabel: "Sort",
            selectedLabel: items[selectedIdx],
            showSecondMenu: showSecond,
            secondMenuLabel: "Filter",
            secondMenuItems: items2,
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - MenuButtonTemplate

public struct MenuButtonTemplate: View {
    public let config: MenuButtonConfig

    public init(config: MenuButtonConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack {
            Color(UIColor.systemGroupedBackground).ignoresSafeArea()

            NavigationStack {
                List {
                    Section {
                        // Row 1: Sort menu
                        HStack {
                            Text(config.menuTriggerLabel)
                                .font(.body)
                                .captureFrame(id: "label_sort")
                            Spacer()
                            // SwiftUI Menu renders as a menu button — the tappable
                            // trigger is the `menuButton` annotation target.
                            Menu {
                                ForEach(config.menuItems, id: \.self) { item in
                                    Button(item) {}
                                }
                            } label: {
                                HStack(spacing: 4) {
                                    Text(config.selectedLabel)
                                        .font(.body)
                                        .foregroundStyle(.secondary)
                                    Image(systemName: "chevron.up.chevron.down")
                                        .font(.caption2)
                                        .foregroundStyle(.secondary)
                                }
                            }
                            .captureFrame(id: "menuButton_0")
                        }
                        .padding(.vertical, 2)
                        .captureFrame(id: "listRow_0")

                        // Row 2: optional filter menu
                        if config.showSecondMenu {
                            HStack {
                                Text(config.secondMenuLabel)
                                    .font(.body)
                                    .captureFrame(id: "label_filter")
                                Spacer()
                                Menu {
                                    ForEach(config.secondMenuItems, id: \.self) { item in
                                        Button(item) {}
                                    }
                                } label: {
                                    HStack(spacing: 4) {
                                        Text(config.secondMenuItems.first ?? "All")
                                            .font(.body)
                                            .foregroundStyle(.secondary)
                                        Image(systemName: "chevron.up.chevron.down")
                                            .font(.caption2)
                                            .foregroundStyle(.secondary)
                                    }
                                }
                                .captureFrame(id: "menuButton_1")
                            }
                            .padding(.vertical, 2)
                            .captureFrame(id: "listRow_1")
                        }
                    } header: {
                        Text("Display Options")
                            .captureFrame(id: "label_section_display")
                    }

                    // Filler rows to show the menu in context
                    Section {
                        ForEach(0..<4, id: \.self) { idx in
                            HStack {
                                Image(systemName: "doc.text")
                                    .foregroundStyle(.secondary)
                                    .frame(width: 24)
                                Text("Item \(idx + 1)")
                                    .font(.body)
                                Spacer()
                                Text("...")
                                    .font(.caption)
                                    .foregroundStyle(.tertiary)
                            }
                            .captureFrame(id: "listRow_content_\(idx)")
                        }
                    }
                }
                .navigationTitle(config.title)
                .navigationBarTitleDisplayMode(.inline)
            }
        }
        .ignoresSafeArea(.all)
        .colorScheme(config.colorScheme)
    }
}
