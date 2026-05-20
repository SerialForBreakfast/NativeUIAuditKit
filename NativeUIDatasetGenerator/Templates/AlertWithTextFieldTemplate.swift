// AlertWithTextFieldTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised alert-with-embedded-textField template (TASK-5b-22).
// Structural distinction: AlertTemplate covers 1–3 button alerts. This template
// specifically generates the common "input alert" pattern where a textField
// appears inside the alert card — training the model to co-detect `alert`
// and `textField` in the same image.
//
// All modal elements are drawn manually (system alert APIs render in a separate
// UIKit window inaccessible to GeometryReader preference keys).
//
// Annotated elements:
//   alert          — the alert card
//   textField      — input field inside the alert
//   primaryButton  — confirm/OK button
//   cancelAction   — cancel button
//   label          — alert title and message text
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - AlertWithTextFieldConfig

public struct AlertWithTextFieldConfig: Sendable {
    public var alertTitle: String
    public var alertMessage: String
    /// Placeholder text shown inside the input field.
    public var fieldPlaceholder: String
    /// Current field value (may be empty for empty state).
    public var fieldValue: String
    public var confirmLabel: String
    public var cancelLabel: String
    public var colorScheme: ColorScheme
    /// Background screen hue (behind the dim scrim).
    public var bgHue: Double

    public init(
        alertTitle: String,
        alertMessage: String,
        fieldPlaceholder: String,
        fieldValue: String,
        confirmLabel: String,
        cancelLabel: String,
        colorScheme: ColorScheme,
        bgHue: Double
    ) {
        self.alertTitle = alertTitle
        self.alertMessage = alertMessage
        self.fieldPlaceholder = fieldPlaceholder
        self.fieldValue = fieldValue
        self.confirmLabel = confirmLabel
        self.cancelLabel = cancelLabel
        self.colorScheme = colorScheme
        self.bgHue = bgHue
    }

    private static let titles = [
        "Rename Item", "Enter Name", "Add Tag", "Set Password",
        "New Folder", "Edit Title", "Enter Code", "Search",
    ]
    private static let messages = [
        "Type a new name for this item.",
        "Enter a descriptive name so you can find it later.",
        "Add a tag to organise your items.",
        "Choose a strong password for this item.",
    ]
    private static let placeholders = [
        "Name", "Enter name...", "Tag name", "Password", "Folder name", "Title",
    ]
    private static let confirmLabels = ["OK", "Save", "Add", "Rename", "Create"]

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> AlertWithTextFieldConfig {
        var rng    = SeededRNG(seed: seed)
        let dark   = rng.next() % 2 == 0
        let hue    = Double(rng.next() % 1000) / 1000.0
        let titleIdx = Int(rng.next() % UInt64(titles.count))
        let msgIdx   = Int(rng.next() % UInt64(messages.count))
        let phIdx    = Int(rng.next() % UInt64(placeholders.count))
        let confIdx  = Int(rng.next() % UInt64(confirmLabels.count))
        let hasValue = rng.next() % 2 == 0
        return AlertWithTextFieldConfig(
            alertTitle: titles[titleIdx],
            alertMessage: messages[msgIdx],
            fieldPlaceholder: placeholders[phIdx],
            fieldValue: hasValue ? corpus.listRowTitle() : "",
            confirmLabel: confirmLabels[confIdx],
            cancelLabel: "Cancel",
            colorScheme: dark ? .dark : .light,
            bgHue: hue
        )
    }
}

// MARK: - AlertWithTextFieldTemplate

public struct AlertWithTextFieldTemplate: View {
    public let config: AlertWithTextFieldConfig

    public init(config: AlertWithTextFieldConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack {
            // Background screen (blurred by scrim)
            Color(hue: config.bgHue, saturation: 0.25, brightness: config.colorScheme == .dark ? 0.20 : 0.85)
                .ignoresSafeArea()

            // Dim scrim
            Color.black.opacity(0.45)
                .ignoresSafeArea()

            // Alert card (manually drawn)
            VStack(spacing: 0) {
                VStack(spacing: 6) {
                    Text(config.alertTitle)
                        .font(.headline)
                        .multilineTextAlignment(.center)
                        .captureFrame(id: "label_title")
                    Text(config.alertMessage)
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                        .multilineTextAlignment(.center)
                        .captureFrame(id: "label_message")
                }
                .padding(.top, 20)
                .padding(.horizontal, 16)
                .padding(.bottom, 14)

                // Input field
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 8)
                        .fill(Color(UIColor.secondarySystemBackground))
                        .frame(height: 36)
                    if config.fieldValue.isEmpty {
                        Text(config.fieldPlaceholder)
                            .font(.body)
                            .foregroundStyle(.secondary)
                            .padding(.horizontal, 10)
                    } else {
                        Text(config.fieldValue)
                            .font(.body)
                            .padding(.horizontal, 10)
                    }
                }
                .captureFrame(id: "textField_0")
                .padding(.horizontal, 16)
                .padding(.bottom, 18)

                Divider()

                // Buttons row
                HStack(spacing: 0) {
                    Button(config.cancelLabel) {}
                        .font(.body)
                        .frame(maxWidth: .infinity, minHeight: 44)
                        .foregroundStyle(.primary)
                        .captureFrame(id: "cancelAction_0")

                    Divider().frame(height: 44)

                    Button(config.confirmLabel) {}
                        .font(.body.bold())
                        .frame(maxWidth: .infinity, minHeight: 44)
                        .foregroundStyle(Color.accentColor)
                        .captureFrame(id: "primaryButton_0")
                }
            }
            .background(Color(UIColor.systemBackground))
            .clipShape(RoundedRectangle(cornerRadius: 14))
            .shadow(color: .black.opacity(0.20), radius: 20, x: 0, y: 6)
            .captureFrame(id: "alert_0")
            .frame(width: 270)
        }
        .ignoresSafeArea(.all)
        .colorScheme(config.colorScheme)
    }
}
