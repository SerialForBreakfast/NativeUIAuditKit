// tvOSPINEntryTemplate.swift
// NativeUIDatasetGenerator — tvOS templates
//
// Parameterised tvOS PIN / Passcode Entry template for OS UI detection.
// Models Apple TV AirPlay code, Restrictions passcode, and Purchase PIN dialogs:
// title, passcode digit slots (secureField), and on-screen numeric keypad.
//
// Annotated elements:
//   secureField    — passcode digit boxes / PIN slots
//   collectionItem — numeric keypad buttons (0–9)
//   label          — prompt title, instructions, digit labels
//   cancelAction   — cancel / back button

import SwiftUI

// MARK: - tvOSPINEntryConfig

public struct tvOSPINEntryConfig: Sendable {
    public var promptTitle: String
    public var promptSubtitle: String
    public var pinLength: Int
    public var filledDigits: Int
    public var focusedKey: Int // 0..9 for digit keys, 10 for Cancel
    public var keypadHue: Double

    public init(
        promptTitle: String = "AirPlay Passcode",
        promptSubtitle: String = "Enter the passcode shown on Apple TV",
        pinLength: Int = 4,
        filledDigits: Int = 2,
        focusedKey: Int = 5,
        keypadHue: Double = 0.6
    ) {
        self.promptTitle = promptTitle
        self.promptSubtitle = promptSubtitle
        self.pinLength = pinLength
        self.filledDigits = filledDigits
        self.focusedKey = focusedKey
        self.keypadHue = keypadHue
    }

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> tvOSPINEntryConfig {
        var rng = SeededRNG(seed: seed)
        let prompts = [
            ("AirPlay Passcode", "Enter the passcode displayed on your Apple TV to connect."),
            ("Enter Restrictions Passcode", "Enter the 4-digit passcode to access restricted content."),
            ("Purchase Passcode", "Enter your passcode to authorize this purchase."),
            ("Conference Room PIN", "Enter the PIN displayed on the conference room display.")
        ]
        let p = prompts[Int(rng.next() % UInt64(prompts.count))]
        let length = (rng.next() % 2 == 0) ? 4 : 6
        let filled = Int(rng.next() % UInt64(length))
        let foc = Int(rng.next() % 11) // 0..9 digits, 10 cancel

        return tvOSPINEntryConfig(
            promptTitle: p.0,
            promptSubtitle: p.1,
            pinLength: length,
            filledDigits: filled,
            focusedKey: foc,
            keypadHue: Double(rng.next() % 1000) / 1000.0
        )
    }
}

// MARK: - tvOSPINEntryTemplate View

public struct tvOSPINEntryTemplate: View {
    public let config: tvOSPINEntryConfig

    public init(config: tvOSPINEntryConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack {
            Color.black.opacity(0.85).ignoresSafeArea()

            VStack(spacing: 36) {
                // Header Titles
                VStack(spacing: 12) {
                    Text(config.promptTitle)
                        .font(.system(size: 40, weight: .bold))
                        .foregroundColor(.white)
                        .captureFrame(id: "label_pin_title")

                    Text(config.promptSubtitle)
                        .font(.system(size: 24))
                        .foregroundColor(.white.opacity(0.7))
                        .captureFrame(id: "label_pin_subtitle")
                }

                // PIN Slot Boxes (secureField)
                HStack(spacing: 24) {
                    ForEach(0..<config.pinLength, id: \.self) { idx in
                        let isFilled = idx < config.filledDigits
                        ZStack {
                            RoundedRectangle(cornerRadius: 16)
                                .fill(Color.white.opacity(0.12))
                                .frame(width: 64, height: 74)
                                .overlay(
                                    RoundedRectangle(cornerRadius: 16)
                                        .stroke(Color.white.opacity(0.3), lineWidth: 2)
                                )

                            if isFilled {
                                Circle()
                                    .fill(Color.white)
                                    .frame(width: 20, height: 20)
                            }
                        }
                        .captureFrame(id: "secureField_pin_slot_\(idx)")
                    }
                }
                .padding(.vertical, 10)

                // Numeric Keypad Grid (3 columns x 4 rows)
                VStack(spacing: 16) {
                    // Rows 1-3: digits 1-9
                    ForEach(0..<3) { row in
                        HStack(spacing: 20) {
                            ForEach(0..<3) { col in
                                let digit = row * 3 + col + 1
                                let isFoc = (config.focusedKey == digit)
                                keypadButton(digit: "\(digit)", isFocused: isFoc, id: "collectionItem_keypad_\(digit)")
                            }
                        }
                    }

                    // Row 4: Cancel, 0, Backspace/Delete
                    HStack(spacing: 20) {
                        // Cancel button
                        let isCancelFoc = (config.focusedKey == 10)
                        Text("Cancel")
                            .font(.system(size: 24, weight: isCancelFoc ? .bold : .medium))
                            .foregroundColor(isCancelFoc ? Color.black : Color.white)
                            .frame(width: 100, height: 68)
                            .background(isCancelFoc ? Color.white : Color.white.opacity(0.12))
                            .cornerRadius(16)
                            .shadow(color: isCancelFoc ? Color.white.opacity(0.35) : Color.clear, radius: 12)
                            .captureFrame(id: isCancelFoc ? "cancelAction_pin_cancel_focused" : "cancelAction_pin_cancel_unfocused")

                        // Digit 0
                        let isZeroFoc = (config.focusedKey == 0)
                        keypadButton(digit: "0", isFocused: isZeroFoc, id: "collectionItem_keypad_0")

                        // Backspace icon button
                        let isDeleteFoc = (config.focusedKey == 11)
                        Image(systemName: "delete.left")
                            .font(.system(size: 26))
                            .foregroundColor(isDeleteFoc ? Color.black : Color.white)
                            .frame(width: 100, height: 68)
                            .background(isDeleteFoc ? Color.white : Color.white.opacity(0.12))
                            .cornerRadius(16)
                            .shadow(color: isDeleteFoc ? Color.white.opacity(0.35) : Color.clear, radius: 12)
                            .captureFrame(id: isDeleteFoc ? "collectionItem_keypad_delete_focused" : "collectionItem_keypad_delete_unfocused")
                    }
                }
            }
            .padding(48)
            .background(Color(red: 0.12, green: 0.12, blue: 0.16))
            .cornerRadius(32)
            .shadow(color: Color.black.opacity(0.7), radius: 40)
            .captureFrame(id: "sheet_pin_dialog")
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }

    @ViewBuilder
    private func keypadButton(digit: String, isFocused: Bool, id: String) -> some View {
        Text(digit)
            .font(.system(size: 32, weight: isFocused ? .bold : .medium))
            .foregroundColor(isFocused ? Color.black : Color.white)
            .frame(width: 100, height: 68)
            .background(isFocused ? Color.white : Color.white.opacity(0.12))
            .cornerRadius(16)
            .shadow(color: isFocused ? Color.white.opacity(0.35) : Color.clear, radius: 12)
            .captureFrame(id: isFocused ? "\(id)_focused" : "\(id)_unfocused")
    }
}
