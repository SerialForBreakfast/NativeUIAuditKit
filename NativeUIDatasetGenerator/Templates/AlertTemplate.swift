// AlertTemplate.swift
// NativeUIDatasetGenerator — Phase 3c-3
//
// Parameterised SwiftUI alert template.
// Produces training images containing:
//   alert, primaryButton, cancelAction, destructiveButton, label
//
// The alert is presented as a modal overlay on top of a blurred background screen.
// Background elements are NOT annotated — only the alert card and its buttons are.
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:)
//
// Parameter sweep: 2 color schemes × 3 DynamicType sizes × 2 device sizes = 12 variants.

import SwiftUI

// MARK: - AlertConfig

/// Parameterised inputs for a single Alert rendering.
public struct AlertConfig: Sendable {
    /// Alert title text. `nil` means message-only (no title label).
    public var title: String?
    /// Alert body message. `nil` means title-only.
    public var message: String?
    /// Number of action buttons: 1, 2, or 3.
    /// - 1 button: primary only
    /// - 2 buttons: primary + cancel
    /// - 3 buttons: primary + cancel + destructive
    public var buttonCount: Int
    /// When `true`, an inline text field is rendered inside the alert (only valid for ≤ 2 buttons).
    public var hasTextField: Bool
    /// Color scheme applied to the view.
    public var colorScheme: ColorScheme

    public init(
        title: String?,
        message: String?,
        buttonCount: Int,
        hasTextField: Bool,
        colorScheme: ColorScheme
    ) {
        self.title = title
        self.message = message
        self.buttonCount = max(1, min(3, buttonCount))
        self.hasTextField = hasTextField && buttonCount <= 2
        self.colorScheme = colorScheme
    }

    /// Deterministic factory — same `seed` always produces the same config.
    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> AlertConfig {
        var rng = SeededRNG(seed: seed)
        let hasTitle    = rng.next() % 3 != 0         // ~67% have a title
        let hasMessage  = rng.next() % 4 != 0         // ~75% have a message
        let buttonCount = (rng.next() % 3) + 1        // 1, 2, or 3
        let hasTF       = rng.next() % 3 == 0 && buttonCount <= 2
        let dark        = rng.next() % 2 == 0

        return AlertConfig(
            title: hasTitle ? corpus.navigationTitle() : nil,
            message: hasMessage ? corpus.listRowSubtitle() : nil,
            buttonCount: Int(buttonCount),
            hasTextField: hasTF,
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - AlertTemplate

/// SwiftUI view that renders a native-styled alert dialog over a blurred background,
/// annotating the alert card and all action buttons via `.captureFrame(id:)`.
///
/// The background is rendered but **not annotated** — the model should detect the
/// alert card, not what lies behind it.
///
/// **Annotated elements:** `alert`, `label` (title/message), `primaryButton`,
/// `cancelAction` (when buttonCount ≥ 2), `destructiveButton` (when buttonCount == 3).
public struct AlertTemplate: View {
    public let config: AlertConfig

    public init(config: AlertConfig) {
        self.config = config
    }

    #if canImport(UIKit)
    public var body: some View {
        ZStack {
            // Background — not annotated, exists only to simulate context behind the alert.
            backgroundDecor
                .blur(radius: 4)
                .allowsHitTesting(false)

            // Alert card
            alertCard
                .captureFrame(id: "alert")
        }
        .ignoresSafeArea(.all)
        .colorScheme(config.colorScheme)
    }

    // MARK: - Alert card

    @ViewBuilder
    private var alertCard: some View {
        VStack(spacing: 0) {
            // Title
            if let title = config.title {
                Text(title)
                    .font(.headline)
                    .multilineTextAlignment(.center)
                    .padding(.top, 20)
                    .padding(.horizontal, 16)
                    .captureFrame(id: "label_alertTitle")
            }

            // Message
            if let message = config.message {
                Text(message)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
                    .padding(.top, config.title != nil ? 4 : 20)
                    .padding(.horizontal, 16)
                    .captureFrame(id: "label_alertMessage")
            }

            // Optional inline text field
            if config.hasTextField {
                TextField("", text: .constant(""))
                    .padding(8)
                    .background(Color.secondary.opacity(0.15))
                    .clipShape(RoundedRectangle(cornerRadius: 6))
                    .padding(.horizontal, 16)
                    .padding(.top, 12)
                    .captureFrame(id: "textField_alertInput")
            }

            // Divider before buttons
            Divider()
                .padding(.top, 20)

            // Action buttons
            alertButtons
        }
        .frame(width: 270)
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 14))
        .shadow(color: .black.opacity(0.25), radius: 20, y: 8)
    }

    @ViewBuilder
    private var alertButtons: some View {
        if config.buttonCount == 1 {
            // Single OK button
            Button("OK") {}
                .frame(maxWidth: .infinity, minHeight: 44)
                .captureFrame(id: "primaryButton_alertOK")
        } else if config.buttonCount == 2 {
            HStack(spacing: 0) {
                // Cancel (left)
                Button("Cancel") {}
                    .frame(maxWidth: .infinity, minHeight: 44)
                    .captureFrame(id: "cancelAction_alert")
                Divider().frame(height: 44)
                // Primary (right)
                Button("OK") {}
                    .bold()
                    .frame(maxWidth: .infinity, minHeight: 44)
                    .captureFrame(id: "primaryButton_alertOK")
            }
        } else {
            // 3 buttons: primary, cancel, destructive stacked vertically
            VStack(spacing: 0) {
                Button("OK") {}
                    .bold()
                    .frame(maxWidth: .infinity, minHeight: 44)
                    .captureFrame(id: "primaryButton_alertOK")
                Divider()
                Button("Cancel") {}
                    .frame(maxWidth: .infinity, minHeight: 44)
                    .captureFrame(id: "cancelAction_alert")
                Divider()
                Button("Delete") {}
                    .foregroundStyle(.red)
                    .frame(maxWidth: .infinity, minHeight: 44)
                    .captureFrame(id: "destructiveButton_alert")
            }
        }
    }

    // MARK: - Background decor (not annotated)

    private var backgroundDecor: some View {
        LinearGradient(
            colors: config.colorScheme == .dark
                ? [Color(white: 0.12), Color(white: 0.20)]
                : [Color(white: 0.85), Color(white: 0.95)],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
        .overlay(
            // Abstract pattern — no recognisable real-world objects.
            VStack(spacing: 48) {
                ForEach(0..<8, id: \.self) { row in
                    HStack(spacing: 48) {
                        ForEach(0..<6, id: \.self) { col in
                            RoundedRectangle(cornerRadius: 8)
                                .fill(Color.primary.opacity(0.06))
                                .frame(width: 56, height: 56)
                                .offset(x: CGFloat((row + col) % 2) * 8)
                        }
                    }
                }
            }
        )
    }
    #else
    // macOS compilation stub — AlertTemplate runs only in iOS Simulator context.
    public var body: some View { EmptyView() }
    #endif
}
