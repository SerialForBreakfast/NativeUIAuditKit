// WizardStepFlowTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI multi-step wizard / onboarding flow template (TASK-5b-22).
// Structural distinction: shows a step-progress indicator at the top (distinct from
// OnboardingPageTemplate's hero + page dots pattern), with form-like content and
// Back/Next navigation buttons.
//
// Annotated elements:
//   progressView   — step progress bar at top (linear ProgressView used as step counter)
//   label          — step title, description, field labels
//   primaryButton  — "Next" / "Done" forward action
//   secondaryButton — "Back" backward action
//   textField      — input field on some steps
//   navigationBar  — auto-detected
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - WizardStepFlowConfig

public struct WizardStepFlowConfig: Sendable {
    public var title: String
    /// Total steps in the wizard (3–5).
    public var totalSteps: Int
    /// Currently displayed step (1-based).
    public var currentStep: Int
    /// Step title (heading on this step's screen).
    public var stepTitle: String
    /// Step body description.
    public var stepDescription: String
    /// Whether this step shows a text field (e.g., "Enter your name").
    public var showTextField: Bool
    public var fieldLabel: String
    public var fieldValue: String
    /// Labels for forward and back actions.
    public var nextLabel: String
    public var backLabel: String
    public var colorScheme: ColorScheme

    public init(
        title: String,
        totalSteps: Int,
        currentStep: Int,
        stepTitle: String,
        stepDescription: String,
        showTextField: Bool,
        fieldLabel: String,
        fieldValue: String,
        nextLabel: String,
        backLabel: String,
        colorScheme: ColorScheme
    ) {
        self.title = title
        self.totalSteps = totalSteps
        self.currentStep = currentStep
        self.stepTitle = stepTitle
        self.stepDescription = stepDescription
        self.showTextField = showTextField
        self.fieldLabel = fieldLabel
        self.fieldValue = fieldValue
        self.nextLabel = nextLabel
        self.backLabel = backLabel
        self.colorScheme = colorScheme
    }

    private static let stepTitles = [
        "Create Your Account", "Set Your Preferences", "Add Your Details",
        "Confirm Your Plan", "Verify Your Identity", "Choose a Username",
        "Set a Password", "Connect Your Devices",
    ]
    private static let stepDescriptions = [
        "Fill in the information below to get started. This only takes a minute.",
        "Customise your experience by setting your preferences for notifications and updates.",
        "Your details help us personalise the app for you.",
        "Review your selected plan before proceeding to checkout.",
        "We need to verify your identity to keep your account secure.",
    ]

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> WizardStepFlowConfig {
        var rng   = SeededRNG(seed: seed)
        let dark  = rng.next() % 2 == 0
        let total = 3 + Int(rng.next() % 3)   // 3–5 steps
        let cur   = 1 + Int(rng.next() % UInt64(total))
        let showF = rng.next() % 2 == 0
        let title = stepTitles[Int(rng.next() % UInt64(stepTitles.count))]
        let desc  = stepDescriptions[Int(rng.next() % UInt64(stepDescriptions.count))]
        let isLast = cur == total
        return WizardStepFlowConfig(
            title: "Setup",
            totalSteps: total,
            currentStep: cur,
            stepTitle: title,
            stepDescription: desc,
            showTextField: showF,
            fieldLabel: "Display Name",
            fieldValue: corpus.personName(),
            nextLabel: isLast ? "Done" : "Continue",
            backLabel: "Back",
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - WizardStepFlowTemplate

public struct WizardStepFlowTemplate: View {
    public let config: WizardStepFlowConfig

    public init(config: WizardStepFlowConfig) {
        self.config = config
    }

    private var stepFraction: Double {
        Double(config.currentStep) / Double(config.totalSteps)
    }

    public var body: some View {
        ZStack {
            Color(UIColor.systemBackground).ignoresSafeArea()

            NavigationStack {
                VStack(alignment: .leading, spacing: 0) {
                    // Step progress indicator
                    VStack(alignment: .leading, spacing: 6) {
                        HStack {
                            Text("Step \(config.currentStep) of \(config.totalSteps)")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                                .captureFrame(id: "label_step_counter")
                            Spacer()
                        }
                        ProgressView(value: stepFraction)
                            .tint(Color.accentColor)
                            .captureFrame(id: "progressView_step")
                    }
                    .padding(.horizontal, 24)
                    .padding(.top, 16)
                    .padding(.bottom, 32)

                    // Step content
                    VStack(alignment: .leading, spacing: 16) {
                        Text(config.stepTitle)
                            .font(.title2.bold())
                            .captureFrame(id: "label_step_title")

                        Text(config.stepDescription)
                            .font(.body)
                            .foregroundStyle(.secondary)
                            .captureFrame(id: "label_step_description")

                        if config.showTextField {
                            VStack(alignment: .leading, spacing: 6) {
                                Text(config.fieldLabel)
                                    .font(.caption)
                                    .foregroundStyle(.secondary)
                                    .captureFrame(id: "label_field")
                                ZStack(alignment: .leading) {
                                    RoundedRectangle(cornerRadius: 10)
                                        .fill(Color(UIColor.secondarySystemBackground))
                                        .frame(height: 48)
                                    Text(config.fieldValue)
                                        .font(.body)
                                        .padding(.horizontal, 14)
                                }
                                .captureFrame(id: "textField_0")
                            }
                            .padding(.top, 8)
                        }
                    }
                    .padding(.horizontal, 24)

                    Spacer()

                    // Navigation buttons
                    HStack(spacing: 12) {
                        if config.currentStep > 1 {
                            Button(config.backLabel) {}
                                .font(.body)
                                .frame(maxWidth: .infinity, minHeight: 50)
                                .background(Color.secondary.opacity(0.15))
                                .foregroundStyle(.primary)
                                .clipShape(RoundedRectangle(cornerRadius: 12))
                                .captureFrame(id: "secondaryButton_back")
                        }
                        Button(config.nextLabel) {}
                            .font(.body.bold())
                            .frame(maxWidth: .infinity, minHeight: 50)
                            .background(Color.accentColor)
                            .foregroundStyle(.white)
                            .clipShape(RoundedRectangle(cornerRadius: 12))
                            .captureFrame(id: "primaryButton_next")
                    }
                    .padding(.horizontal, 24)
                    .padding(.bottom, 48)
                }
                .navigationTitle(config.title)
                .navigationBarTitleDisplayMode(.inline)
            }
        }
        .ignoresSafeArea(.all)
        .colorScheme(config.colorScheme)
    }
}
