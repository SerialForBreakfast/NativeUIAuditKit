// tvOSAlertTemplate.swift
// NativeUIDatasetGenerator — tvOS templates
//
// Parameterised tvOS modal alert / dialog template for OS UI detection.
// Models system confirmation dialogs, permission alerts, and software update prompts.
//
// Annotated elements:
//   alert          — the modal dialog container
//   primaryButton  — action / confirmation buttons (focused / unfocused)
//   cancelAction   — cancel / dismiss button (focused / unfocused)
//   label          — alert title and message text

import SwiftUI

// MARK: - tvOSAlertConfig

public struct tvOSAlertConfig: Sendable {
    public var title: String
    public var message: String
    public var primaryActionTitle: String
    public var secondaryActionTitle: String?
    public var cancelActionTitle: String
    public var focusedButtonIndex: Int // 0: primary, 1: secondary (if present), 2: cancel

    public init(
        title: String,
        message: String,
        primaryActionTitle: String,
        secondaryActionTitle: String? = nil,
        cancelActionTitle: String = "Cancel",
        focusedButtonIndex: Int = 0
    ) {
        self.title = title
        self.message = message
        self.primaryActionTitle = primaryActionTitle
        self.secondaryActionTitle = secondaryActionTitle
        self.cancelActionTitle = cancelActionTitle
        self.focusedButtonIndex = focusedButtonIndex
    }

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> tvOSAlertConfig {
        var rng = SeededRNG(seed: seed)
        let hasSecondary = (rng.next() % 2 == 0)
        let buttonCount = hasSecondary ? 3 : 2
        let focIdx = Int(rng.next() % UInt64(buttonCount))

        return tvOSAlertConfig(
            title: corpus.alertTitle(),
            message: corpus.alertMessage(),
            primaryActionTitle: "Continue",
            secondaryActionTitle: hasSecondary ? "Remind Me Later" : nil,
            cancelActionTitle: "Cancel",
            focusedButtonIndex: focIdx
        )
    }
}

// MARK: - tvOSAlertTemplate View

public struct tvOSAlertTemplate: View {
    public let config: tvOSAlertConfig

    public init(config: tvOSAlertConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack {
            // Dimmed background
            Color.black.opacity(0.85).ignoresSafeArea()

            // Centered Alert Dialog Container
            VStack(spacing: 28) {
                VStack(spacing: 14) {
                    Text(config.title)
                        .font(.system(size: 34, weight: .bold))
                        .foregroundColor(.white)
                        .multilineTextAlignment(.center)
                        .captureFrame(id: "label_alert_title")

                    Text(config.message)
                        .font(.system(size: 22))
                        .foregroundColor(.white.opacity(0.8))
                        .multilineTextAlignment(.center)
                        .padding(.horizontal, 32)
                        .captureFrame(id: "label_alert_message")
                }
                .padding(.top, 40)

                Divider()
                    .background(Color.white.opacity(0.2))

                // Action Buttons
                VStack(spacing: 16) {
                    // Primary Action
                    buttonView(
                        title: config.primaryActionTitle,
                        isFocused: (config.focusedButtonIndex == 0),
                        id: config.focusedButtonIndex == 0 ? "primaryButton_action_focused" : "primaryButton_action_unfocused"
                    )

                    // Secondary Action (Optional)
                    if let secTitle = config.secondaryActionTitle {
                        buttonView(
                            title: secTitle,
                            isFocused: (config.focusedButtonIndex == 1),
                            id: config.focusedButtonIndex == 1 ? "primaryButton_sec_focused" : "primaryButton_sec_unfocused"
                        )
                    }

                    // Cancel Action
                    let cancelIdx = config.secondaryActionTitle != nil ? 2 : 1
                    buttonView(
                        title: config.cancelActionTitle,
                        isFocused: (config.focusedButtonIndex == cancelIdx),
                        id: config.focusedButtonIndex == cancelIdx ? "cancelAction_dismiss_focused" : "cancelAction_dismiss_unfocused"
                    )
                }
                .padding(.bottom, 36)
            }
            .frame(width: 760)
            .background(Color(red: 0.16, green: 0.16, blue: 0.20))
            .cornerRadius(28)
            .shadow(color: Color.black.opacity(0.8), radius: 40)
            .captureFrame(id: "alert_modal_container")
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }

    private func buttonView(title: String, isFocused: Bool, id: String) -> some View {
        Text(title)
            .font(.system(size: 24, weight: isFocused ? .bold : .medium))
            .foregroundColor(isFocused ? .black : .white)
            .frame(width: 660, height: 68)
            .background(isFocused ? Color.white : Color.white.opacity(0.12))
            .cornerRadius(16)
            .shadow(color: isFocused ? Color.white.opacity(0.5) : Color.clear, radius: 16)
            .captureFrame(id: id)
    }
}
