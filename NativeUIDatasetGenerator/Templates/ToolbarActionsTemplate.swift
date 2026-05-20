// ToolbarActionsTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI toolbar template (TASK-5b-22, class: toolbar).
// Covers a bottom UIToolbar / SwiftUI `.toolbar` with multiple action buttons —
// a structural pattern not yet present in any template. The model must learn to
// distinguish `toolbar` (bottom, content-editing context) from `tabBar`.
//
// Annotated elements:
//   toolbar        — SwiftUI ToolbarItem(placement: .bottomBar) row (auto-detected via
//                    UIToolbar in the UIKit hierarchy)
//   navigationBar  — auto-detected
//   secondaryButton — individual toolbar action items
//   listRow        — document/item rows in the main content area
//   label          — row labels
//
// NOTE on toolbar annotation: UIToolbar is detected by detectChromeFrames via the
// UIKit hierarchy walk. The `toolbar` class key is inserted alongside `navigationBar`.
// A `.bottomBar` ToolbarItem causes UIKit to synthesize a UIToolbar below the content.
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - ToolbarAction

public struct ToolbarAction: Sendable {
    public var label: String
    public var iconName: String
}

// MARK: - ToolbarActionsConfig

public struct ToolbarActionsConfig: Sendable {
    public var title: String
    /// Toolbar action buttons (2–4 items including a flexible spacer).
    public var actions: [ToolbarAction]
    /// List rows to populate the main content area.
    public var rows: [(title: String, subtitle: String)]
    public var colorScheme: ColorScheme

    public init(
        title: String,
        actions: [ToolbarAction],
        rows: [(title: String, subtitle: String)],
        colorScheme: ColorScheme
    ) {
        self.title = title
        self.actions = actions
        self.rows = rows
        self.colorScheme = colorScheme
    }

    private static let actionPool: [ToolbarAction] = [
        ToolbarAction(label: "Delete",    iconName: "trash"),
        ToolbarAction(label: "Share",     iconName: "square.and.arrow.up"),
        ToolbarAction(label: "Move",      iconName: "folder"),
        ToolbarAction(label: "Archive",   iconName: "archivebox"),
        ToolbarAction(label: "Flag",      iconName: "flag"),
        ToolbarAction(label: "Reply",     iconName: "arrowshape.turn.up.left"),
        ToolbarAction(label: "Forward",   iconName: "arrowshape.turn.up.right"),
        ToolbarAction(label: "Print",     iconName: "printer"),
    ]

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> ToolbarActionsConfig {
        var rng = SeededRNG(seed: seed)
        let dark     = rng.next() % 2 == 0
        let actCount = 2 + Int(rng.next() % 3)   // 2–4 toolbar actions
        var pool     = actionPool
        var acts: [ToolbarAction] = []
        for _ in 0..<actCount {
            let idx = Int(rng.next() % UInt64(pool.count))
            acts.append(pool[idx])
            pool.remove(at: idx)
        }
        let rowCount = 4 + Int(rng.next() % 4)   // 4–7 rows
        var rows: [(title: String, subtitle: String)] = []
        for _ in 0..<rowCount {
            rows.append((title: corpus.listRowTitle(), subtitle: corpus.listRowSubtitle()))
        }
        return ToolbarActionsConfig(
            title: corpus.navigationTitle(),
            actions: acts,
            rows: rows,
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - ToolbarActionsTemplate

public struct ToolbarActionsTemplate: View {
    public let config: ToolbarActionsConfig

    public init(config: ToolbarActionsConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack {
            Color(UIColor.systemGroupedBackground).ignoresSafeArea()

            NavigationStack {
                List {
                    ForEach(Array(config.rows.enumerated()), id: \.offset) { idx, row in
                        VStack(alignment: .leading, spacing: 2) {
                            Text(row.title)
                                .font(.body)
                                .captureFrame(id: "label_row_title_\(idx)")
                            Text(row.subtitle)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                                .captureFrame(id: "label_row_subtitle_\(idx)")
                        }
                        .padding(.vertical, 4)
                        .captureFrame(id: "listRow_\(idx)")
                    }
                }
                .navigationTitle(config.title)
                .navigationBarTitleDisplayMode(.inline)
                // Bottom toolbar items — UIKit synthesizes a UIToolbar
                .toolbar {
                    ToolbarItemGroup(placement: .bottomBar) {
                        ForEach(Array(config.actions.enumerated()), id: \.offset) { idx, action in
                            Button {
                            } label: {
                                Label(action.label, systemImage: action.iconName)
                            }
                            .captureFrame(id: "secondaryButton_toolbar_\(idx)")
                            if idx < config.actions.count - 1 {
                                Spacer()
                            }
                        }
                    }
                }
            }
        }
        .ignoresSafeArea(.all)
        .colorScheme(config.colorScheme)
    }
}
