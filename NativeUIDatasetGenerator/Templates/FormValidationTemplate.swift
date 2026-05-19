// FormValidationTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI form-with-validation template (TASK-5b-4).
// Compiled exclusively into the iOS GeneratorRunner Xcode target.
//
// Annotated elements:
//   textField     — each text input field
//   secureField   — password / PIN field
//   toggle        — remember-me / consent toggles
//   primaryButton — submit / continue action
//   label         — field labels and inline validation error messages
//
// Validation error variant: ~25% of images show error states on one or more fields.
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - FormValidationConfig

/// Parameterised inputs for a single FormValidation rendering.
public struct FormValidationConfig: Sendable {
    /// Navigation bar title.
    public var title: String
    /// Placeholder / label for the main text field.
    public var fieldLabel: String
    /// Placeholder text for the text field.
    public var placeholder: String
    /// When true, show an inline validation error on the text field.
    public var textFieldError: Bool
    /// When true, show an inline validation error on the password field.
    public var passwordError: Bool
    /// Primary button label.
    public var primaryButtonLabel: String
    /// Whether the "remember me" toggle is on.
    public var rememberMeOn: Bool
    /// Whether a second "agree to terms" toggle is shown.
    public var showTermsToggle: Bool
    /// Color scheme applied to the view.
    public var colorScheme: ColorScheme

    public init(
        title: String,
        fieldLabel: String,
        placeholder: String,
        textFieldError: Bool,
        passwordError: Bool,
        primaryButtonLabel: String,
        rememberMeOn: Bool,
        showTermsToggle: Bool,
        colorScheme: ColorScheme
    ) {
        self.title = title
        self.fieldLabel = fieldLabel
        self.placeholder = placeholder
        self.textFieldError = textFieldError
        self.passwordError = passwordError
        self.primaryButtonLabel = primaryButtonLabel
        self.rememberMeOn = rememberMeOn
        self.showTermsToggle = showTermsToggle
        self.colorScheme = colorScheme
    }

    /// Deterministic factory — same `seed` always produces the same config.
    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> FormValidationConfig {
        var rng = SeededRNG(seed: seed)
        let dark        = rng.next() % 2 == 0
        let tfError     = rng.next() % 4 == 0   // ~25%
        let pwError     = rng.next() % 4 == 0   // ~25%
        let rememberMe  = rng.next() % 2 == 0
        let showTerms   = rng.next() % 2 == 0

        return FormValidationConfig(
            title: corpus.navigationTitle(),
            fieldLabel: corpus.listRowTitle(),
            placeholder: corpus.email(),
            textFieldError: tfError,
            passwordError: pwError,
            primaryButtonLabel: corpus.buttonLabel(),
            rememberMeOn: rememberMe,
            showTermsToggle: showTerms,
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - FormValidationTemplate

/// SwiftUI view rendering a multi-field form with inline validation errors.
///
/// **Platform scope:** iOS GeneratorRunner target only.
public struct FormValidationTemplate: View {
    public let config: FormValidationConfig

    public init(config: FormValidationConfig) {
        self.config = config
    }

    public var body: some View {
        NavigationStack {
            ZStack(alignment: .topLeading) {
                Color(UIColor.systemBackground).ignoresSafeArea()

                VStack(alignment: .leading, spacing: 0) {
                    // Text field label
                    Text(config.fieldLabel)
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                        .captureFrame(id: "label_field")
                        .padding(.leading, 20)
                        .padding(.top, 32)

                    // Text field
                    TextField(config.placeholder, text: .constant(""))
                        .keyboardType(.emailAddress)
                        .autocorrectionDisabled()
                        .padding(12)
                        .background(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(
                                    config.textFieldError ? Color.red : Color.secondary.opacity(0.4),
                                    lineWidth: config.textFieldError ? 2 : 1
                                )
                        )
                        .captureFrame(id: "textField_0")
                        .padding(.horizontal, 20)
                        .padding(.top, 6)

                    // Inline error for text field
                    if config.textFieldError {
                        Text("Please enter a valid value.")
                            .font(.caption)
                            .foregroundStyle(.red)
                            .captureFrame(id: "label_fieldError")
                            .padding(.leading, 20)
                            .padding(.top, 4)
                    }

                    // Password label
                    Text("Password")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                        .captureFrame(id: "label_password")
                        .padding(.leading, 20)
                        .padding(.top, 20)

                    // Secure field
                    SecureField("Password", text: .constant(""))
                        .textContentType(.password)
                        .padding(12)
                        .background(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(
                                    config.passwordError ? Color.red : Color.secondary.opacity(0.4),
                                    lineWidth: config.passwordError ? 2 : 1
                                )
                        )
                        .captureFrame(id: "secureField_0")
                        .padding(.horizontal, 20)
                        .padding(.top, 6)

                    if config.passwordError {
                        Text("Password must be at least 8 characters.")
                            .font(.caption)
                            .foregroundStyle(.red)
                            .captureFrame(id: "label_passwordError")
                            .padding(.leading, 20)
                            .padding(.top, 4)
                    }

                    // Remember me toggle
                    HStack {
                        Text("Remember me")
                            .font(.subheadline)
                            .captureFrame(id: "label_rememberMe")
                        Spacer()
                        Toggle("", isOn: .constant(config.rememberMeOn))
                            .labelsHidden()
                            .captureFrame(id: "toggle_rememberMe")
                    }
                    .padding(.horizontal, 20)
                    .padding(.top, 16)

                    // Terms toggle (conditional)
                    if config.showTermsToggle {
                        HStack {
                            Text("I agree to the Terms of Service")
                                .font(.subheadline)
                                .captureFrame(id: "label_terms")
                            Spacer()
                            Toggle("", isOn: .constant(false))
                                .labelsHidden()
                                .captureFrame(id: "toggle_terms")
                        }
                        .padding(.horizontal, 20)
                        .padding(.top, 12)
                    }

                    Spacer().frame(minHeight: 32)

                    // Primary button
                    Button(config.primaryButtonLabel) {}
                        .frame(maxWidth: .infinity, minHeight: 50)
                        .background(Color.accentColor)
                        .foregroundStyle(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                        .captureFrame(id: "primaryButton_0")
                        .padding(.horizontal, 20)
                        .padding(.bottom, 32)

                    Spacer()
                }
            }
            .ignoresSafeArea(.all)
            .navigationTitle(config.title)
            .navigationBarTitleDisplayMode(.large)
            .colorScheme(config.colorScheme)
        }
        .colorScheme(config.colorScheme)
    }
}
