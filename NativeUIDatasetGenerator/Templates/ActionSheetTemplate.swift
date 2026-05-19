// ActionSheetTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI action sheet template (TASK-5b-10).
// Compiled exclusively into the iOS GeneratorRunner Xcode target.
//
// Annotated elements:
//   actionSheet      — the action sheet card (manual captureFrame)
//   destructiveButton — the red destructive action button
//   cancelAction      — the cancel button at the sheet bottom
//
// Action sheet is rendered manually (not via .confirmationDialog) so that
// captureFrame can attach to the precise card boundary. The system
// .confirmationDialog renders in a new window inaccessible to GeometryReader.
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - ActionSheetConfig

/// Parameterised inputs for a single ActionSheet rendering.
public struct ActionSheetConfig: Sendable {
    /// Sheet title text.
    public var title: String
    /// Optional message below the title.
    public var message: String?
    /// Non-destructive action labels (1–3 items).
    public var actionLabels: [String]
    /// Destructive action label.
    public var destructiveLabel: String
    /// Color scheme applied to the view.
    public var colorScheme: ColorScheme

    public init(
        title: String,
        message: String?,
        actionLabels: [String],
        destructiveLabel: String,
        colorScheme: ColorScheme
    ) {
        self.title = title
        self.message = message
        self.actionLabels = actionLabels
        self.destructiveLabel = destructiveLabel
        self.colorScheme = colorScheme
    }

    private static let destructiveLabels = [
        "Delete", "Remove", "Clear All", "Discard Changes", "Unsubscribe",
    ]

    /// Deterministic factory — same `seed` always produces the same config.
    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> ActionSheetConfig {
        var rng = SeededRNG(seed: seed)
        let dark        = rng.next() % 2 == 0
        let actionCount = 1 + Int(rng.next() % 3)     // 1–3 regular actions
        let hasMessage  = rng.next() % 2 == 0
        let destIdx     = Int(rng.next() % UInt64(destructiveLabels.count))

        var actions: [String] = []
        for _ in 0..<actionCount { actions.append(corpus.buttonLabel()) }

        return ActionSheetConfig(
            title: corpus.navigationTitle(),
            message: hasMessage ? corpus.listRowTitle() : nil,
            actionLabels: actions,
            destructiveLabel: destructiveLabels[destIdx],
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - ActionSheetTemplate

/// SwiftUI view rendering an iOS-style action sheet over a dimmed background.
///
/// Manually drawn to allow `captureFrame(id: "actionSheet_0")` on the card boundary.
///
/// **Platform scope:** iOS GeneratorRunner target only.
public struct ActionSheetTemplate: View {
    public let config: ActionSheetConfig

    public init(config: ActionSheetConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack(alignment: .bottom) {
            // Dimmed content background
            Color.black.opacity(0.35)
                .ignoresSafeArea()

            VStack(spacing: 8) {
                // Main action sheet card
                VStack(spacing: 0) {
                    // Title + message header
                    if config.message != nil || !config.title.isEmpty {
                        VStack(spacing: 4) {
                            Text(config.title)
                                .font(.footnote.weight(.semibold))
                                .foregroundStyle(.secondary)
                                .multilineTextAlignment(.center)

                            if let msg = config.message {
                                Text(msg)
                                    .font(.footnote)
                                    .foregroundStyle(.secondary)
                                    .multilineTextAlignment(.center)
                            }
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 14)
                        .padding(.horizontal, 16)

                        Divider()
                    }

                    // Regular action buttons
                    ForEach(Array(config.actionLabels.enumerated()), id: \.offset) { idx, label in
                        Button(label) {}
                            .frame(maxWidth: .infinity, minHeight: 56)
                            .font(.body)
                            .foregroundStyle(Color.accentColor)

                        if idx < config.actionLabels.count - 1 {
                            Divider()
                        }
                    }

                    Divider()

                    // Destructive button — annotated before trailing padding (BP-18)
                    Button(config.destructiveLabel) {}
                        .frame(maxWidth: .infinity, minHeight: 56)
                        .font(.body.weight(.medium))
                        .foregroundStyle(.red)
                        .captureFrame(id: "destructiveButton_0")
                }
                .background(
                    RoundedRectangle(cornerRadius: 14)
                        .fill(Color(UIColor.systemBackground).opacity(0.95))
                )
                .clipShape(RoundedRectangle(cornerRadius: 14))
                .captureFrame(id: "actionSheet_0")
                .padding(.horizontal, 8)

                // Cancel button — separate rounded card
                Button("Cancel") {}
                    .frame(maxWidth: .infinity, minHeight: 56)
                    .font(.body.weight(.semibold))
                    .foregroundStyle(Color.accentColor)
                    .background(
                        RoundedRectangle(cornerRadius: 14)
                            .fill(Color(UIColor.systemBackground).opacity(0.95))
                    )
                    .clipShape(RoundedRectangle(cornerRadius: 14))
                    .captureFrame(id: "cancelAction_0")
                    .padding(.horizontal, 8)
                    .padding(.bottom, 32)
            }
        }
        .ignoresSafeArea(.all)
        .colorScheme(config.colorScheme)
    }
}
