// ModalDialogueFlowTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised composite modal dialogue flow template for the 41-class holdout addon.
// Covers contextual containers and action controls that were previously missing from holdout:
//   alert, actionSheet, sheet, popover, contextMenu, cancelAction, destructiveButton,
//   primaryButton, secondaryButton, label.
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset() (BP-01)
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - ModalDialogueMode

public enum ModalDialogueMode: Int, Sendable, CaseIterable {
    case alert = 0
    case actionSheet = 1
    case sheet = 2
    case popover = 3
    case contextMenu = 4
}

// MARK: - ModalDialogueFlowConfig

public struct ModalDialogueFlowConfig: Sendable {
    public var mode: ModalDialogueMode
    public var title: String
    public var message: String
    public var primaryLabel: String
    public var secondaryLabel: String
    public var cancelLabel: String
    public var destructiveLabel: String
    public var colorScheme: ColorScheme

    public init(
        mode: ModalDialogueMode,
        title: String,
        message: String,
        primaryLabel: String,
        secondaryLabel: String,
        cancelLabel: String,
        destructiveLabel: String,
        colorScheme: ColorScheme
    ) {
        self.mode = mode
        self.title = title
        self.message = message
        self.primaryLabel = primaryLabel
        self.secondaryLabel = secondaryLabel
        self.cancelLabel = cancelLabel
        self.destructiveLabel = destructiveLabel
        self.colorScheme = colorScheme
    }

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> ModalDialogueFlowConfig {
        var rng = SeededRNG(seed: seed)
        let modeIndex = Int(rng.next() % UInt64(ModalDialogueMode.allCases.count))
        let mode = ModalDialogueMode(rawValue: modeIndex) ?? .alert
        let isDark = (rng.next() % 2) == 0

        let titles = ["Confirm Action", "Warning", "Discard Draft", "Save Changes", "Select Option", "Notice"]
        let messages = [
            "Are you sure you want to proceed with this operation?",
            "Unsaved changes will be permanently discarded.",
            "Choose a destination folder for these exported items.",
            "This action cannot be undone once confirmed.",
            "Review your selection before continuing."
        ]
        let primaries = ["Save", "Continue", "Apply", "Export", "Confirm", "Done"]
        let secondaries = ["Details", "Options", "Share", "Duplicate", "Edit"]
        let cancels = ["Cancel", "Dismiss", "Close", "Not Now"]
        let destructives = ["Delete", "Discard", "Remove All", "Clear Cache", "Erase"]

        let title = titles[Int(rng.next() % UInt64(titles.count))]
        let message = messages[Int(rng.next() % UInt64(messages.count))]
        let primary = primaries[Int(rng.next() % UInt64(primaries.count))]
        let secondary = secondaries[Int(rng.next() % UInt64(secondaries.count))]
        let cancel = cancels[Int(rng.next() % UInt64(cancels.count))]
        let destructive = destructives[Int(rng.next() % UInt64(destructives.count))]

        return ModalDialogueFlowConfig(
            mode: mode,
            title: title,
            message: message,
            primaryLabel: primary,
            secondaryLabel: secondary,
            cancelLabel: cancel,
            destructiveLabel: destructive,
            colorScheme: isDark ? .dark : .light
        )
    }
}

// MARK: - ModalDialogueFlowTemplate View

public struct ModalDialogueFlowTemplate: View {
    public let config: ModalDialogueFlowConfig

    public init(config: ModalDialogueFlowConfig) {
        self.config = config
    }

    private var isDark: Bool { config.colorScheme == .dark }
    private var bgColor: Color { isDark ? Color(white: 0.12) : Color(white: 0.95) }
    private var cardBg: Color { isDark ? Color(white: 0.22) : Color.white }
    private var textColor: Color { isDark ? .white : .black }
    private var subtextColor: Color { isDark ? Color(white: 0.70) : Color(white: 0.40) }

    public var body: some View {
        ZStack {
            bgColor.ignoresSafeArea(.all)

            // Dimmed background screen elements representing an active host app
            VStack(spacing: 16) {
                HStack {
                    Text("App Workflow")
                        .font(.headline)
                        .foregroundColor(textColor.opacity(0.35))
                    Spacer()
                }
                .padding(.horizontal, 20)
                .padding(.top, 50)

                RoundedRectangle(cornerRadius: 12)
                    .fill(cardBg.opacity(0.4))
                    .frame(height: 120)
                    .padding(.horizontal, 20)

                RoundedRectangle(cornerRadius: 12)
                    .fill(cardBg.opacity(0.4))
                    .frame(height: 120)
                    .padding(.horizontal, 20)

                Spacer()
            }
            .blur(radius: 2)

            // Semi-transparent modal dimming scrim
            Color.black.opacity(isDark ? 0.55 : 0.35)
                .ignoresSafeArea(.all)

            // Active modal presentation based on mode
            switch config.mode {
            case .alert:
                renderAlertModal()
            case .actionSheet:
                renderActionSheetModal()
            case .sheet:
                renderSheetModal()
            case .popover:
                renderPopoverModal()
            case .contextMenu:
                renderContextMenuModal()
            }
        }
        .preferredColorScheme(config.colorScheme)
    }

    // MARK: - Mode Renderers

    @ViewBuilder
    private func renderAlertModal() -> some View {
        VStack(spacing: 0) {
            VStack(spacing: 8) {
                Text(config.title)
                    .font(.headline)
                    .foregroundColor(textColor)
                    .multilineTextAlignment(.center)
                    .captureFrame(id: "label_alertTitle")

                Text(config.message)
                    .font(.subheadline)
                    .foregroundColor(subtextColor)
                    .multilineTextAlignment(.center)
                    .captureFrame(id: "label_alertMsg")
            }
            .padding(.horizontal, 20)
            .padding(.top, 20)
            .padding(.bottom, 16)

            Divider()

            HStack(spacing: 0) {
                Button(action: {}) {
                    Text(config.cancelLabel)
                        .font(.body)
                        .foregroundColor(.blue)
                        .frame(maxWidth: .infinity, minHeight: 44)
                        .captureFrame(id: "cancelAction_alertDismiss")
                }

                Divider().frame(height: 44)

                Button(action: {}) {
                    Text(config.destructiveLabel)
                        .font(.body.weight(.semibold))
                        .foregroundColor(.red)
                        .frame(maxWidth: .infinity, minHeight: 44)
                        .captureFrame(id: "destructiveButton_alertConfirm")
                }
            }
        }
        .frame(width: 270)
        .background(cardBg)
        .cornerRadius(14)
        .shadow(color: Color.black.opacity(0.2), radius: 16, x: 0, y: 8)
        .captureFrame(id: "alert_dialog")
    }

    @ViewBuilder
    private func renderActionSheetModal() -> some View {
        VStack(spacing: 8) {
            Spacer()

            VStack(spacing: 0) {
                VStack(spacing: 4) {
                    Text(config.title)
                        .font(.footnote.weight(.semibold))
                        .foregroundColor(subtextColor)
                        .captureFrame(id: "label_actionSheetTitle")

                    Text(config.message)
                        .font(.caption)
                        .foregroundColor(subtextColor)
                        .captureFrame(id: "label_actionSheetMsg")
                }
                .padding(.vertical, 14)
                .frame(maxWidth: .infinity)

                Divider()

                Button(action: {}) {
                    Text(config.secondaryLabel)
                        .font(.body)
                        .foregroundColor(.blue)
                        .frame(maxWidth: .infinity, minHeight: 50)
                        .captureFrame(id: "secondaryButton_actionSheetOption")
                }

                Divider()

                Button(action: {}) {
                    Text(config.destructiveLabel)
                        .font(.body.weight(.semibold))
                        .foregroundColor(.red)
                        .frame(maxWidth: .infinity, minHeight: 50)
                        .captureFrame(id: "destructiveButton_actionSheetDelete")
                }
            }
            .background(cardBg)
            .cornerRadius(14)
            .captureFrame(id: "actionSheet_container")

            Button(action: {}) {
                Text(config.cancelLabel)
                    .font(.body.weight(.semibold))
                    .foregroundColor(.blue)
                    .frame(maxWidth: .infinity, minHeight: 54)
                    .background(cardBg)
                    .cornerRadius(14)
                    .captureFrame(id: "cancelAction_actionSheetCancel")
            }
        }
        .padding(.horizontal, 10)
        .padding(.bottom, 24)
    }

    @ViewBuilder
    private func renderSheetModal() -> some View {
        VStack(spacing: 0) {
            Spacer()

            VStack(spacing: 16) {
                // Drag handle
                Capsule()
                    .fill(subtextColor.opacity(0.5))
                    .frame(width: 36, height: 5)
                    .padding(.top, 8)

                HStack {
                    Button(action: {}) {
                        Text(config.cancelLabel)
                            .font(.body)
                            .foregroundColor(.blue)
                            .captureFrame(id: "cancelAction_sheetDismiss")
                    }

                    Spacer()

                    Text(config.title)
                        .font(.headline)
                        .foregroundColor(textColor)
                        .captureFrame(id: "label_sheetTitle")

                    Spacer()

                    Button(action: {}) {
                        Text(config.primaryLabel)
                            .font(.body.weight(.semibold))
                            .foregroundColor(.blue)
                            .captureFrame(id: "primaryButton_sheetSave")
                    }
                }
                .padding(.horizontal, 16)

                Divider()

                VStack(alignment: .leading, spacing: 12) {
                    Text(config.message)
                        .font(.subheadline)
                        .foregroundColor(subtextColor)
                        .captureFrame(id: "label_sheetBody")

                    RoundedRectangle(cornerRadius: 8)
                        .fill(bgColor)
                        .frame(height: 80)
                }
                .padding(.horizontal, 16)
                .padding(.bottom, 30)
            }
            .frame(maxWidth: .infinity)
            .background(cardBg)
            .cornerRadius(16)
            .captureFrame(id: "sheet_panel")
        }
    }

    @ViewBuilder
    private func renderPopoverModal() -> some View {
        VStack(spacing: 12) {
            HStack {
                Text(config.title)
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor(textColor)
                    .captureFrame(id: "label_popoverTitle")
                Spacer()
            }

            Text(config.message)
                .font(.footnote)
                .foregroundColor(subtextColor)
                .captureFrame(id: "label_popoverBody")

            Divider()

            HStack {
                Button(action: {}) {
                    Text(config.secondaryLabel)
                        .font(.footnote)
                        .foregroundColor(.blue)
                        .captureFrame(id: "secondaryButton_popoverAction")
                }

                Spacer()

                Button(action: {}) {
                    Text(config.primaryLabel)
                        .font(.footnote.weight(.semibold))
                        .foregroundColor(.white)
                        .padding(.horizontal, 14)
                        .padding(.vertical, 6)
                        .background(Color.blue)
                        .cornerRadius(8)
                        .captureFrame(id: "primaryButton_popoverDone")
                }
            }
        }
        .padding(16)
        .frame(width: 280)
        .background(cardBg)
        .cornerRadius(14)
        .shadow(color: Color.black.opacity(0.18), radius: 12, x: 0, y: 6)
        .captureFrame(id: "popover_bubble")
    }

    @ViewBuilder
    private func renderContextMenuModal() -> some View {
        VStack(spacing: 12) {
            // Target item that was long-pressed
            HStack {
                Circle().fill(Color.blue).frame(width: 28, height: 28)
                Text(config.title)
                    .font(.body.weight(.medium))
                    .foregroundColor(textColor)
                Spacer()
            }
            .padding(12)
            .background(cardBg)
            .cornerRadius(10)
            .frame(width: 250)

            // Context menu action card
            VStack(spacing: 0) {
                Button(action: {}) {
                    HStack {
                        Text(config.secondaryLabel).foregroundColor(textColor)
                        Spacer()
                        Image(systemName: "square.and.arrow.up").foregroundColor(subtextColor)
                    }
                    .padding(.horizontal, 14)
                    .frame(height: 44)
                    .captureFrame(id: "secondaryButton_contextMenuShare")
                }

                Divider()

                Button(action: {}) {
                    HStack {
                        Text(config.destructiveLabel).foregroundColor(.red)
                        Spacer()
                        Image(systemName: "trash").foregroundColor(.red)
                    }
                    .padding(.horizontal, 14)
                    .frame(height: 44)
                    .captureFrame(id: "destructiveButton_contextMenuDelete")
                }

                Divider()

                Button(action: {}) {
                    HStack {
                        Text(config.cancelLabel).foregroundColor(subtextColor)
                        Spacer()
                    }
                    .padding(.horizontal, 14)
                    .frame(height: 44)
                    .captureFrame(id: "cancelAction_contextMenuCancel")
                }
            }
            .frame(width: 250)
            .background(cardBg)
            .cornerRadius(12)
            .shadow(color: Color.black.opacity(0.2), radius: 14, x: 0, y: 6)
            .captureFrame(id: "contextMenu_actions")
        }
    }
}
