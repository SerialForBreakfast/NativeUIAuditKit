// ContextMenuTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI context menu template (TASK-5b-17).
// Compiled exclusively into the iOS GeneratorRunner Xcode target.
//
// Annotated elements:
//   contextMenu — the context menu action list (manual captureFrame on the menu card)
//   listRow     — the preview row that triggered the context menu
//   label       — action labels inside the context menu
//
// Context menu is rendered manually (not via .contextMenu{}) so that
// captureFrame can attach to the action list boundary. The system
// .contextMenu renders in a separate UIMenuController window.
//
// Layout: Simulates a long-press-triggered context menu appearing over a
// list row, with the preview of the row above and the action menu below.
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - ContextMenuConfig

/// Parameterised inputs for a single ContextMenu rendering.
public struct ContextMenuConfig: Sendable {
    /// The row label that the context menu was triggered from.
    public var rowLabel: String
    /// Context menu action labels (2–5 items).
    public var actionLabels: [String]
    /// Whether the last action is destructive (red).
    public var hasDestructiveAction: Bool
    /// Color scheme applied to the view.
    public var colorScheme: ColorScheme

    public init(
        rowLabel: String,
        actionLabels: [String],
        hasDestructiveAction: Bool,
        colorScheme: ColorScheme
    ) {
        self.rowLabel = rowLabel
        self.actionLabels = actionLabels
        self.hasDestructiveAction = hasDestructiveAction
        self.colorScheme = colorScheme
    }

    private static let destructiveLabels = ["Delete", "Remove", "Clear"]

    /// Deterministic factory — same `seed` always produces the same config.
    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> ContextMenuConfig {
        var rng = SeededRNG(seed: seed)
        let dark            = rng.next() % 2 == 0
        let actionCount     = 2 + Int(rng.next() % 4)   // 2–5 actions
        let hasDestructive  = rng.next() % 2 == 0

        var actions: [String] = []
        for _ in 0..<(actionCount - (hasDestructive ? 1 : 0)) {
            actions.append(corpus.buttonLabel())
        }
        if hasDestructive {
            let destIdx = Int(rng.next() % UInt64(destructiveLabels.count))
            actions.append(destructiveLabels[destIdx])
        }

        return ContextMenuConfig(
            rowLabel: corpus.listRowTitle(),
            actionLabels: actions,
            hasDestructiveAction: hasDestructive,
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - ContextMenuTemplate

/// SwiftUI view rendering a simulated context menu activation.
///
/// Shows: dimmed background, a preview row at the top, and the context menu
/// action list below it — mimicking UIKit's UIMenu presentation.
///
/// **Platform scope:** iOS GeneratorRunner target only.
public struct ContextMenuTemplate: View {
    public let config: ContextMenuConfig

    public init(config: ContextMenuConfig) {
        self.config = config
    }

    public var body: some View {
        GeometryReader { proxy in
            let rowY: CGFloat = proxy.size.height * 0.28
            let menuTopY: CGFloat = rowY + 60

            ZStack(alignment: .topLeading) {
                // Dimmed background
                Color.black.opacity(0.45)
                    .ignoresSafeArea()

                // Preview row (the element that was long-pressed)
                HStack {
                    Image(systemName: "doc.text")
                        .foregroundStyle(.secondary)
                    Text(config.rowLabel)
                        .font(.body)
                    Spacer()
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 14)
                .background(Color(UIColor.systemBackground))
                .clipShape(RoundedRectangle(cornerRadius: 12))
                .shadow(radius: 8)
                .captureFrame(id: "listRow_preview_0")
                .padding(.horizontal, 24)
                .padding(.top, rowY)

                // Context menu action list
                VStack(spacing: 0) {
                    ForEach(Array(config.actionLabels.enumerated()), id: \.offset) { idx, label in
                        let isLast       = idx == config.actionLabels.count - 1
                        let isDestructive = isLast && config.hasDestructiveAction

                        Button(label) {}
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .frame(height: 44)
                            .foregroundStyle(isDestructive ? .red : Color.accentColor)
                            .captureFrame(id: "label_action_\(idx)")
                            .padding(.horizontal, 16)

                        if !isLast {
                            Divider()
                                .padding(.horizontal, 0)
                        }
                    }
                }
                .background(
                    RoundedRectangle(cornerRadius: 14)
                        .fill(Color(UIColor.systemBackground).opacity(0.97))
                        .shadow(color: .black.opacity(0.18), radius: 12, x: 0, y: 4)
                )
                .clipShape(RoundedRectangle(cornerRadius: 14))
                .captureFrame(id: "contextMenu_0")
                .padding(.horizontal, 24)
                .padding(.top, menuTopY)
            }
        }
        .ignoresSafeArea(.all)
        .colorScheme(config.colorScheme)
    }
}
