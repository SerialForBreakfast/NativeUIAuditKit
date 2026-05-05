// LoginFormTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI login/signup form template.
// Compiled exclusively into the iOS GeneratorRunner Xcode target.
// No platform guards needed — this file never compiles on macOS.
//
// Annotated elements:
//   navigationBar, textField, secureField, label, primaryButton,
//   secondaryButton, link
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All element offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:)
//
// Parameter sweep: 2 color schemes × 3 DynamicType sizes × 2 device sizes = 12 variants minimum.

import SwiftUI
import UIKit

// MARK: - LoginFormConfig

/// Parameterised inputs for a single LoginForm rendering.
public struct LoginFormConfig: Sendable {
    /// Navigation bar title.
    public var title: String
    /// Email field placeholder text.
    public var emailPlaceholder: String
    /// Primary button label.
    public var primaryButtonLabel: String
    /// When `true`, a "Forgot password?" link is rendered below the password field.
    public var showForgotPassword: Bool
    /// When `true`, a "Sign up instead" secondary button is rendered below the primary button.
    public var showSignUpButton: Bool
    /// When `true`, the email field renders in an error state (red border + error label).
    public var emailErrorState: Bool
    /// Color scheme applied to the view.
    public var colorScheme: ColorScheme

    public init(
        title: String,
        emailPlaceholder: String,
        primaryButtonLabel: String,
        showForgotPassword: Bool,
        showSignUpButton: Bool,
        emailErrorState: Bool,
        colorScheme: ColorScheme
    ) {
        self.title = title
        self.emailPlaceholder = emailPlaceholder
        self.primaryButtonLabel = primaryButtonLabel
        self.showForgotPassword = showForgotPassword
        self.showSignUpButton = showSignUpButton
        self.emailErrorState = emailErrorState
        self.colorScheme = colorScheme
    }

    /// Deterministic factory — same `seed` always produces the same config.
    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> LoginFormConfig {
        var rng = SeededRNG(seed: seed)
        let showForgot    = rng.next() % 2 == 0
        let showSignUp    = rng.next() % 2 == 0
        let emailError    = rng.next() % 4 == 0   // ~25% show error state
        let dark          = rng.next() % 2 == 0

        return LoginFormConfig(
            title: corpus.navigationTitle(),
            emailPlaceholder: corpus.emailPlaceholder(),
            primaryButtonLabel: corpus.primaryButtonLabel(),
            showForgotPassword: showForgot,
            showSignUpButton: showSignUp,
            emailErrorState: emailError,
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - LoginFormTemplate

/// SwiftUI view rendering a login/signup screen and annotating UI elements
/// via `.captureFrame(id:)`.
///
/// **Platform scope:** iOS GeneratorRunner target only.
public struct LoginFormTemplate: View {
    public let config: LoginFormConfig

    public init(config: LoginFormConfig) {
        self.config = config
    }

    public var body: some View {
        NavigationStack {
            ZStack(alignment: .topLeading) {
                Color(UIColor.systemBackground).ignoresSafeArea()

                VStack(alignment: .leading, spacing: 0) {
                    // Email label
                    Text("Email")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                        .padding(.leading, 20)
                        .padding(.top, 32)
                        .captureFrame(id: "label_email")

                    // Email text field
                    TextField(config.emailPlaceholder, text: .constant(""))
                        .keyboardType(.emailAddress)
                        .autocorrectionDisabled()
                        .textContentType(.emailAddress)
                        .padding(12)
                        .background(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(
                                    config.emailErrorState ? Color.red : Color.secondary.opacity(0.4),
                                    lineWidth: config.emailErrorState ? 2 : 1
                                )
                        )
                        .padding(.horizontal, 20)
                        .padding(.top, 6)
                        .captureFrame(id: "textField_email")

                    // Error label (conditional)
                    if config.emailErrorState {
                        Text("Please enter a valid email address.")
                            .font(.caption)
                            .foregroundStyle(.red)
                            .padding(.leading, 20)
                            .padding(.top, 4)
                            .captureFrame(id: "label_emailError")
                    }

                    // Password label
                    Text("Password")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                        .padding(.leading, 20)
                        .padding(.top, 20)
                        .captureFrame(id: "label_password")

                    // Secure field
                    SecureField("Password", text: .constant(""))
                        .textContentType(.password)
                        .padding(12)
                        .background(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(Color.secondary.opacity(0.4), lineWidth: 1)
                        )
                        .padding(.horizontal, 20)
                        .padding(.top, 6)
                        .captureFrame(id: "secureField_password")

                    // Forgot password link (conditional)
                    if config.showForgotPassword {
                        Button("Forgot password?") {}
                            .font(.subheadline)
                            .padding(.leading, 20)
                            .padding(.top, 8)
                            .captureFrame(id: "link_forgotPassword")
                    }

                    Spacer().frame(minHeight: 32)

                    // Primary button
                    Button(config.primaryButtonLabel) {}
                        .frame(maxWidth: .infinity, minHeight: 50)
                        .background(Color.accentColor)
                        .foregroundStyle(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                        .padding(.horizontal, 20)
                        .captureFrame(id: "primaryButton_submit")

                    // Secondary button (conditional)
                    if config.showSignUpButton {
                        Button("Sign up instead") {}
                            .frame(maxWidth: .infinity, minHeight: 44)
                            .foregroundStyle(Color.accentColor)
                            .overlay(
                                RoundedRectangle(cornerRadius: 12)
                                    .stroke(Color.accentColor, lineWidth: 1)
                            )
                            .padding(.horizontal, 20)
                            .padding(.top, 12)
                            .captureFrame(id: "secondaryButton_signUp")
                    }

                    Spacer()
                }
            }
            .ignoresSafeArea(.all)
            .navigationTitle(config.title)
            .navigationBarTitleDisplayMode(.large)
            .colorScheme(config.colorScheme)
        }
        .captureFrame(id: "navigationBar")
    }
}
