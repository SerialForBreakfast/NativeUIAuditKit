// tvOSSignInWithAppleTemplate.swift
// NativeUIDatasetGenerator — tvOS templates
//
// Parameterised tvOS Sign In with Apple / QR Code pairing modal template for OS UI detection.
// Models Apple TV setup and authentication modals:
// QR code badge, instruction text, pairing digits, secondary alternative button, and cancel action.
//
// Annotated elements:
//   sheet           — authentication modal card
//   imageView       — QR code graphic and Apple ID logo
//   label           — modal title, pairing instructions, code digits
//   link            — help / support web URL
//   secondaryButton — "Sign In with Remote" alternative button
//   cancelAction    — "Cancel" dismissal button

import SwiftUI

// MARK: - tvOSSignInWithAppleConfig

public struct tvOSSignInWithAppleConfig: Sendable {
    public var title: String
    public var subtitle: String
    public var pairingCode: String
    public var focusedTarget: Int // 0: Sign In with Remote, 1: Cancel
    public var showQRCode: Bool

    public init(
        title: String = "Sign In with iPhone",
        subtitle: String = "Open the Camera app on your iPhone or iPad and scan this QR code.",
        pairingCode: String = "834 - 192",
        focusedTarget: Int = 0,
        showQRCode: Bool = true
    ) {
        self.title = title
        self.subtitle = subtitle
        self.pairingCode = pairingCode
        self.focusedTarget = focusedTarget
        self.showQRCode = showQRCode
    }

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> tvOSSignInWithAppleConfig {
        var rng = SeededRNG(seed: seed)
        let titles = [
            ("Sign In with iPhone", "Bring your iPhone or iPad near this Apple TV to sign in automatically."),
            ("Authorize TVTestRig", "Scan the code with your registered developer device to permit automation."),
            ("Apple Account Setup", "Open Camera on an Apple device running iOS 17 or later and scan.")
        ]
        let item = titles[Int(rng.next() % UInt64(titles.count))]
        let code = String(format: "%03d - %03d", rng.next() % 1000, rng.next() % 1000)

        return tvOSSignInWithAppleConfig(
            title: item.0,
            subtitle: item.1,
            pairingCode: code,
            focusedTarget: Int(rng.next() % 2),
            showQRCode: true
        )
    }
}

// MARK: - tvOSSignInWithAppleTemplate View

public struct tvOSSignInWithAppleTemplate: View {
    public let config: tvOSSignInWithAppleConfig

    public init(config: tvOSSignInWithAppleConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack {
            Color.black.opacity(0.85).ignoresSafeArea()

            HStack(spacing: 64) {
                // QR Code Panel
                ZStack {
                    RoundedRectangle(cornerRadius: 24)
                        .fill(Color.white)
                    Image(systemName: "qrcode")
                        .font(.system(size: 200))
                        .foregroundColor(.black)
                }
                .frame(width: 320, height: 320)
                .captureFrame(id: "imageView_signin_qrcode")

                // Right Column: Details & Actions
                VStack(alignment: .leading, spacing: 20) {
                    HStack(spacing: 14) {
                        Image(systemName: "applelogo")
                            .font(.system(size: 32))
                            .foregroundColor(.white)
                            .captureFrame(id: "imageView_apple_logo")

                        Text(config.title)
                            .font(.system(size: 38, weight: .bold))
                            .foregroundColor(.white)
                            .captureFrame(id: "label_signin_title")
                    }

                    Text(config.subtitle)
                        .font(.system(size: 22))
                        .foregroundColor(.white.opacity(0.75))
                        .lineLimit(3)
                        .frame(maxWidth: 580, alignment: .leading)
                        .captureFrame(id: "label_signin_subtitle")

                    // Pairing Code Box
                    HStack(spacing: 12) {
                        Text("Code:")
                            .font(.system(size: 20, weight: .medium))
                            .foregroundColor(.white.opacity(0.5))
                            .captureFrame(id: "label_code_prefix")

                        Text(config.pairingCode)
                            .font(.system(size: 30, weight: .bold, design: .monospaced))
                            .foregroundColor(.white)
                            .captureFrame(id: "label_pairing_code")
                    }
                    .padding(.vertical, 8)

                    // Link
                    Text("apple.com/appleid")
                        .font(.system(size: 20))
                        .foregroundColor(Color.blue)
                        .underline()
                        .captureFrame(id: "link_appleid_help")

                    Spacer().frame(height: 12)

                    // Action Buttons Row
                    HStack(spacing: 24) {
                        let isSecFoc = (config.focusedTarget == 0)
                        Text("Use Remote Instead")
                            .font(.system(size: 22, weight: isSecFoc ? .bold : .medium))
                            .foregroundColor(isSecFoc ? Color.black : Color.white)
                            .padding(.horizontal, 28)
                            .frame(height: 60)
                            .background(isSecFoc ? Color.white : Color.white.opacity(0.12))
                            .cornerRadius(14)
                            .shadow(color: isSecFoc ? Color.white.opacity(0.35) : Color.clear, radius: 10)
                            .captureFrame(id: isSecFoc ? "secondaryButton_use_remote_focused" : "secondaryButton_use_remote_unfocused")

                        let isCancelFoc = (config.focusedTarget == 1)
                        Text("Cancel")
                            .font(.system(size: 22, weight: isCancelFoc ? .bold : .medium))
                            .foregroundColor(isCancelFoc ? Color.black : Color.white)
                            .padding(.horizontal, 28)
                            .frame(height: 60)
                            .background(isCancelFoc ? Color.white : Color.white.opacity(0.12))
                            .cornerRadius(14)
                            .shadow(color: isCancelFoc ? Color.white.opacity(0.35) : Color.clear, radius: 10)
                            .captureFrame(id: isCancelFoc ? "cancelAction_signin_cancel_focused" : "cancelAction_signin_cancel_unfocused")
                    }
                }
            }
            .padding(56)
            .background(Color(red: 0.12, green: 0.12, blue: 0.16))
            .cornerRadius(32)
            .shadow(color: Color.black.opacity(0.7), radius: 40)
            .captureFrame(id: "sheet_signin_modal")
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}
