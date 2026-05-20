// MultiSectionFormTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI multi-section form template (TASK-5b-22).
// Structural distinction: a single form combining textField, secureField, Picker
// (inline), Stepper, Toggle across multiple sections — more complex than LoginForm
// or FormValidation which each focus on a narrower element set.
//
// Annotated elements:
//   textField      — name / email inputs
//   secureField    — password input
//   picker         — inline date or option picker
//   stepperControl — quantity / count stepper
//   toggle         — notification preference toggles
//   primaryButton  — submit / save button
//   label          — section and field labels
//   navigationBar  — auto-detected
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - MultiSectionFormConfig

public struct MultiSectionFormConfig: Sendable {
    public var title: String
    public var nameValue: String
    public var emailValue: String
    public var passwordValue: String
    /// Inline picker options and selected index.
    public var pickerOptions: [String]
    public var pickerSelected: Int
    public var pickerLabel: String
    /// Stepper current value and range.
    public var stepperValue: Int
    public var stepperMin: Int
    public var stepperMax: Int
    public var stepperLabel: String
    /// Toggle states.
    public var notifyPush: Bool
    public var notifyEmail: Bool
    public var submitLabel: String
    public var colorScheme: ColorScheme

    public init(
        title: String,
        nameValue: String,
        emailValue: String,
        passwordValue: String,
        pickerOptions: [String],
        pickerSelected: Int,
        pickerLabel: String,
        stepperValue: Int,
        stepperMin: Int,
        stepperMax: Int,
        stepperLabel: String,
        notifyPush: Bool,
        notifyEmail: Bool,
        submitLabel: String,
        colorScheme: ColorScheme
    ) {
        self.title = title
        self.nameValue = nameValue
        self.emailValue = emailValue
        self.passwordValue = passwordValue
        self.pickerOptions = pickerOptions
        self.pickerSelected = pickerSelected
        self.pickerLabel = pickerLabel
        self.stepperValue = stepperValue
        self.stepperMin = stepperMin
        self.stepperMax = stepperMax
        self.stepperLabel = stepperLabel
        self.notifyPush = notifyPush
        self.notifyEmail = notifyEmail
        self.submitLabel = submitLabel
        self.colorScheme = colorScheme
    }

    private static let regionOptions = ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East"]
    private static let submitLabels  = ["Save Changes", "Create Account", "Submit", "Register", "Update Profile"]

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> MultiSectionFormConfig {
        var rng = SeededRNG(seed: seed)
        let dark   = rng.next() % 2 == 0
        let selIdx = Int(rng.next() % UInt64(regionOptions.count))
        let stepV  = 1 + Int(rng.next() % 9)   // 1–9
        return MultiSectionFormConfig(
            title: corpus.navigationTitle(),
            nameValue: corpus.personName(),
            emailValue: corpus.email(),
            passwordValue: "••••••••",
            pickerOptions: regionOptions,
            pickerSelected: selIdx,
            pickerLabel: "Region",
            stepperValue: stepV,
            stepperMin: 1,
            stepperMax: 10,
            stepperLabel: "Devices",
            notifyPush: rng.next() % 2 == 0,
            notifyEmail: rng.next() % 2 == 0,
            submitLabel: submitLabels[Int(rng.next() % UInt64(submitLabels.count))],
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - MultiSectionFormTemplate

public struct MultiSectionFormTemplate: View {
    public let config: MultiSectionFormConfig

    public init(config: MultiSectionFormConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack {
            Color(UIColor.systemGroupedBackground).ignoresSafeArea()

            NavigationStack {
                Form {
                    // Section 1: Identity
                    Section("Account") {
                        HStack {
                            Text("Name")
                                .captureFrame(id: "label_name")
                            Spacer()
                            Text(config.nameValue)
                                .foregroundStyle(.secondary)
                        }
                        .captureFrame(id: "textField_0")

                        HStack {
                            Text("Email")
                                .captureFrame(id: "label_email")
                            Spacer()
                            Text(config.emailValue)
                                .foregroundStyle(.secondary)
                        }
                        .captureFrame(id: "textField_1")

                        HStack {
                            Text("Password")
                                .captureFrame(id: "label_password")
                            Spacer()
                            Text(config.passwordValue)
                                .foregroundStyle(.secondary)
                        }
                        .captureFrame(id: "secureField_0")
                    }

                    // Section 2: Preferences (picker + stepper)
                    Section("Preferences") {
                        Picker(config.pickerLabel, selection: .constant(config.pickerSelected)) {
                            ForEach(Array(config.pickerOptions.enumerated()), id: \.offset) { idx, opt in
                                Text(opt).tag(idx)
                            }
                        }
                        .captureFrame(id: "picker_0")

                        HStack {
                            Text(config.stepperLabel)
                                .captureFrame(id: "label_stepper")
                            Spacer()
                            Stepper(
                                "\(config.stepperValue)",
                                value: .constant(config.stepperValue),
                                in: config.stepperMin...config.stepperMax
                            )
                            .captureFrame(id: "stepperControl_0")
                        }
                    }

                    // Section 3: Notifications (toggles)
                    Section("Notifications") {
                        Toggle(isOn: .constant(config.notifyPush)) {
                            Text("Push Notifications")
                                .captureFrame(id: "label_toggle_push")
                        }
                        .captureFrame(id: "toggle_0")

                        Toggle(isOn: .constant(config.notifyEmail)) {
                            Text("Email Notifications")
                                .captureFrame(id: "label_toggle_email")
                        }
                        .captureFrame(id: "toggle_1")
                    }

                    // Submit
                    Section {
                        Button(config.submitLabel) {}
                            .font(.body.bold())
                            .frame(maxWidth: .infinity, alignment: .center)
                            .foregroundStyle(Color.accentColor)
                            .captureFrame(id: "primaryButton_0")
                    }
                }
                .navigationTitle(config.title)
                .navigationBarTitleDisplayMode(.inline)
            }
        }
        .ignoresSafeArea(.all)
        .colorScheme(config.colorScheme)
    }
}
