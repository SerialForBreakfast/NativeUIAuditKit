// UIKitFormViewController.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// UIKit template: sign-in / authentication form.
//
// Annotated elements:
//   navigationBar   (chrome — auto-detected by detectChromeFrames)
//   label_email     label        — "Email" / "Email Address"
//   textField       textField    — email input
//   label_password  label        — "Password"
//   secureField     secureField  — password input (isSecureTextEntry = true)
//   primaryButton   primaryButton — filled CTA button
//   secondaryButton secondaryButton — text-style link button
//
// Layout: fully programmatic (no AutoLayout). Frames are set in viewDidLayoutSubviews
// using config.osProfile.safeAreaTopInset so layout is deterministic regardless of
// the simulator's actual safe area insets.
//
// Appearance: overrideUserInterfaceStyle driven by config.colorScheme so dark/light
// mode is explicit and seed-reproducible.

import UIKit

// MARK: - UIKitFormViewController

@MainActor
public final class UIKitFormViewController: UIViewController, UIKitAnnotatable {

    // MARK: - Configuration

    private let seed: UInt64
    private let runConfig: GeneratorRunConfig

    // MARK: - Views

    private let navBar = UINavigationBar()
    private let emailLabel = UILabel()
    private let emailField = UITextField()
    private let passwordLabel = UILabel()
    private let passwordField = UITextField()
    private let signInButton = UIButton(type: .system)
    private let secondaryButton = UIButton(type: .system)

    // MARK: - Init

    public init(seed: UInt64, config: GeneratorRunConfig) {
        self.seed = seed
        self.runConfig = config
        super.init(nibName: nil, bundle: nil)
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) { fatalError("init(coder:) not used") }

    // MARK: - UIViewController

    public override func viewDidLoad() {
        super.viewDidLoad()
        UIView.setAnimationsEnabled(false)
        setupAppearance()
        setupViews()
    }

    public override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        layoutViews()
    }

    // MARK: - UIKitAnnotatable

    public var annotatedViews: [UIKitAnnotatedView] {
        [
            UIKitAnnotatedView(id: "label_email",     elementType: "label",         view: emailLabel,     visibleText: emailLabel.text),
            UIKitAnnotatedView(id: "textField",        elementType: "textField",     view: emailField,     visibleText: emailField.placeholder),
            UIKitAnnotatedView(id: "label_password",  elementType: "label",         view: passwordLabel,  visibleText: passwordLabel.text),
            UIKitAnnotatedView(id: "secureField",     elementType: "secureField",   view: passwordField),
            UIKitAnnotatedView(id: "primaryButton",   elementType: "primaryButton", view: signInButton,   visibleText: signInButton.title(for: .normal)),
            UIKitAnnotatedView(id: "secondaryButton", elementType: "secondaryButton", view: secondaryButton, visibleText: secondaryButton.title(for: .normal)),
        ]
    }

    // MARK: - Setup

    private func setupAppearance() {
        overrideUserInterfaceStyle = runConfig.colorScheme == .dark ? .dark : .light
        view.backgroundColor = .systemBackground
    }

    private func setupViews() {
        var corpus = ContentCorpus(seed: seed)

        // Navigation bar
        let navItem = UINavigationItem(title: corpus.navigationTitle())
        navBar.items = [navItem]
        view.addSubview(navBar)

        // Email label
        emailLabel.text = seed % 3 == 0 ? "Email Address" : "Email"
        emailLabel.font = .systemFont(ofSize: 13, weight: .medium)
        emailLabel.textColor = .secondaryLabel
        view.addSubview(emailLabel)

        // Email text field
        emailField.placeholder = corpus.email()
        emailField.borderStyle = .roundedRect
        emailField.keyboardType = .emailAddress
        emailField.autocapitalizationType = .none
        emailField.font = .systemFont(ofSize: 17)
        view.addSubview(emailField)

        // Password label
        passwordLabel.text = "Password"
        passwordLabel.font = .systemFont(ofSize: 13, weight: .medium)
        passwordLabel.textColor = .secondaryLabel
        view.addSubview(passwordLabel)

        // Password field
        passwordField.placeholder = "Required"
        passwordField.borderStyle = .roundedRect
        passwordField.isSecureTextEntry = true
        passwordField.font = .systemFont(ofSize: 17)
        view.addSubview(passwordField)

        // Primary CTA
        let primaryLabel: String = seed % 4 == 0 ? "Log In" : (seed % 4 == 1 ? "Continue" : "Sign In")
        signInButton.setTitle(primaryLabel, for: .normal)
        signInButton.backgroundColor = .systemBlue
        signInButton.setTitleColor(.white, for: .normal)
        signInButton.titleLabel?.font = .systemFont(ofSize: 17, weight: .semibold)
        signInButton.layer.cornerRadius = 12
        signInButton.clipsToBounds = true
        view.addSubview(signInButton)

        // Secondary action
        let secondaryLabel: String = seed % 2 == 0 ? "Forgot Password?" : "Create Account"
        secondaryButton.setTitle(secondaryLabel, for: .normal)
        secondaryButton.setTitleColor(.systemBlue, for: .normal)
        secondaryButton.titleLabel?.font = .systemFont(ofSize: 15)
        view.addSubview(secondaryButton)
    }

    private func layoutViews() {
        let safeTop = runConfig.osProfile.safeAreaTopInset
        let width = view.bounds.width
        let hPad: CGFloat = 24
        let fieldWidth = width - 2 * hPad

        // Navigation bar: covers status bar + standard 44pt bar height
        navBar.frame = CGRect(x: 0, y: 0, width: width, height: safeTop + 44)

        // Form content begins below nav bar
        var y = navBar.frame.maxY + 36

        emailLabel.frame = CGRect(x: hPad, y: y, width: fieldWidth, height: 18)
        y += 22

        emailField.frame = CGRect(x: hPad, y: y, width: fieldWidth, height: 44)
        y += 56

        passwordLabel.frame = CGRect(x: hPad, y: y, width: fieldWidth, height: 18)
        y += 22

        passwordField.frame = CGRect(x: hPad, y: y, width: fieldWidth, height: 44)
        y += 64

        signInButton.frame = CGRect(x: hPad, y: y, width: fieldWidth, height: 50)
        y += 62

        secondaryButton.frame = CGRect(x: hPad, y: y, width: fieldWidth, height: 44)
    }
}
