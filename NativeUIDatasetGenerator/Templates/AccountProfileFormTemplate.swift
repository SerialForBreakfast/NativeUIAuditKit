// AccountProfileFormTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Train-family Form-in-List clone of MultiSectionForm (TASK-6a-8 / BP-32).
// MultiSectionForm is withheld; Run 007 matched its Form rows as listRow
// (textField 314/500, picker 133/200, secureField 100 miss + 100 listRow).
// This family stays in train/val so Form chrome is not zero-shot at test time.
//
// Annotated elements:
//   textField, secureField, picker, stepperControl, toggle, primaryButton, label
//   navigationBar — auto-detected
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - AccountProfileFormConfig

/// Parameterised inputs for a single AccountProfileForm rendering.
public struct AccountProfileFormConfig: Sendable {
    public var title: String
    public var displayName: String
    public var emailValue: String
    public var nickname: String
    public var passwordValue: String
    public var pickerOptions: [String]
    public var pickerSelected: Int
    public var pickerLabel: String
    public var stepperValue: Int
    public var stepperMin: Int
    public var stepperMax: Int
    public var stepperLabel: String
    public var privateAccount: Bool
    public var submitLabel: String
    public var colorScheme: ColorScheme

    public init(
        title: String,
        displayName: String,
        emailValue: String,
        nickname: String,
        passwordValue: String,
        pickerOptions: [String],
        pickerSelected: Int,
        pickerLabel: String,
        stepperValue: Int,
        stepperMin: Int,
        stepperMax: Int,
        stepperLabel: String,
        privateAccount: Bool,
        submitLabel: String,
        colorScheme: ColorScheme
    ) {
        self.title = title
        self.displayName = displayName
        self.emailValue = emailValue
        self.nickname = nickname
        self.passwordValue = passwordValue
        self.pickerOptions = pickerOptions
        self.pickerSelected = pickerSelected
        self.pickerLabel = pickerLabel
        self.stepperValue = stepperValue
        self.stepperMin = stepperMin
        self.stepperMax = stepperMax
        self.stepperLabel = stepperLabel
        self.privateAccount = privateAccount
        self.submitLabel = submitLabel
        self.colorScheme = colorScheme
    }

    private static let timezoneOptions = ["Pacific", "Mountain", "Central", "Eastern", "UTC"]
    private static let submitLabels = ["Save Profile", "Update Account", "Apply", "Continue"]

    /// Deterministic factory — same `seed` always produces the same config.
    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> AccountProfileFormConfig {
        var rng = SeededRNG(seed: seed)
        let dark = rng.next() % 2 == 0
        let selIdx = Int(rng.next() % UInt64(timezoneOptions.count))
        let stepV = 1 + Int(rng.next() % 9)
        return AccountProfileFormConfig(
            title: corpus.navigationTitle(),
            displayName: corpus.personName(),
            emailValue: corpus.email(),
            nickname: corpus.listRowTitle(),
            passwordValue: "••••••••",
            pickerOptions: timezoneOptions,
            pickerSelected: selIdx,
            pickerLabel: "Time Zone",
            stepperValue: stepV,
            stepperMin: 1,
            stepperMax: 10,
            stepperLabel: "Sessions",
            privateAccount: rng.next() % 2 == 0,
            submitLabel: submitLabels[Int(rng.next() % UInt64(submitLabels.count))],
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - AccountProfileFormTemplate

/// SwiftUI Form-in-List profile screen for train (not withheld).
///
/// **Platform scope:** iOS GeneratorRunner target only.
///
/// HStack value rows match MultiSectionForm holdout chrome. Real `TextField` /
/// `SecureField` inside `Form` also appear so the model sees both styles.
public struct AccountProfileFormTemplate: View {
    public let config: AccountProfileFormConfig

    public init(config: AccountProfileFormConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack {
            Color(UIColor.systemGroupedBackground).ignoresSafeArea()

            NavigationStack {
                Form {
                    Section("Profile") {
                        HStack {
                            Text("Name")
                                .captureFrame(id: "label_name")
                            Spacer()
                            Text(config.displayName)
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

                        TextField("Nickname", text: .constant(config.nickname))
                            .captureFrame(id: "textField_2")

                        HStack {
                            Text("Password")
                                .captureFrame(id: "label_password")
                            Spacer()
                            Text(config.passwordValue)
                                .foregroundStyle(.secondary)
                        }
                        .captureFrame(id: "secureField_0")

                        SecureField("Confirm password", text: .constant(""))
                            .captureFrame(id: "secureField_1")
                    }

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

                    Section("Privacy") {
                        Toggle(isOn: .constant(config.privateAccount)) {
                            Text("Private Account")
                                .captureFrame(id: "label_toggle_private")
                        }
                        .captureFrame(id: "toggle_0")
                    }

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
