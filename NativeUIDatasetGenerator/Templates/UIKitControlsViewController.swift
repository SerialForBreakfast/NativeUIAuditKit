// UIKitControlsViewController.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// UIKit template: controls showcase.
//
// Annotated elements:
//   navigationBar      (chrome — auto-detected)
//   slider             UISlider
//   segmentedControl   UISegmentedControl
//   activityIndicator  UIActivityIndicatorView
//   progressView       UIProgressView
//   pageControl        UIPageControl
//   toggle             UISwitch
//
// No tab bar — single-screen showcase with no bottom chrome.
//
// Layout: programmatic, vertical stack below the navigation bar.
// Control values vary based on seed to avoid always-same-state bias.

import UIKit

// MARK: - UIKitControlsViewController

@MainActor
public final class UIKitControlsViewController: UIViewController, UIKitAnnotatable {

    // MARK: - Configuration

    private let seed: UInt64
    private let runConfig: GeneratorRunConfig

    // MARK: - Annotated views

    private let navBar = UINavigationBar()
    private let slider = UISlider()
    private let segmentedControl = UISegmentedControl()
    private let activityIndicator = UIActivityIndicatorView(style: .medium)
    private let progressView = UIProgressView(progressViewStyle: .default)
    private let pageControl = UIPageControl()
    private let toggle = UISwitch()
    /// Password secure text field — annotated as secureField.
    private let secureTextField = UITextField()
    /// "Reset" secondary button at the bottom of the controls showcase.
    private let resetButton = UIButton(type: .system)

    // MARK: - Section labels (visual context only, not annotated)

    private let sliderLabel = UILabel()
    private let segmentLabel = UILabel()
    private let activityLabel = UILabel()
    private let progressLabel = UILabel()
    private let pageLabel = UILabel()
    private let toggleLabel = UILabel()
    private let secureLabel = UILabel()

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
            UIKitAnnotatedView(id: "slider",            elementType: "slider",            view: slider),
            UIKitAnnotatedView(id: "segmentedControl",  elementType: "segmentedControl",  view: segmentedControl),
            UIKitAnnotatedView(id: "activityIndicator", elementType: "activityIndicator", view: activityIndicator),
            UIKitAnnotatedView(id: "progressView",      elementType: "progressView",      view: progressView),
            UIKitAnnotatedView(id: "pageControl",       elementType: "pageControl",       view: pageControl),
            UIKitAnnotatedView(id: "toggle",            elementType: "toggle",            view: toggle),
            UIKitAnnotatedView(id: "secureTextField",   elementType: "secureField",       view: secureTextField),
            UIKitAnnotatedView(id: "resetButton",       elementType: "secondaryButton",   view: resetButton,
                               visibleText: resetButton.title(for: .normal)),
        ]
    }

    // MARK: - Setup

    private func setupAppearance() {
        overrideUserInterfaceStyle = runConfig.colorScheme == .dark ? .dark : .light
        view.backgroundColor = .systemGroupedBackground
    }

    private func configureSectionLabel(_ label: UILabel, text: String) {
        label.text = text.uppercased()
        label.font = .systemFont(ofSize: 12, weight: .medium)
        label.textColor = .secondaryLabel
    }

    private func setupViews() {
        var corpus = ContentCorpus(seed: seed)

        // Navigation bar
        let navItem = UINavigationItem(title: corpus.navigationTitle())
        navBar.items = [navItem]
        view.addSubview(navBar)

        // Section labels
        configureSectionLabel(sliderLabel,    text: "Slider")
        configureSectionLabel(segmentLabel,   text: "Segmented Control")
        configureSectionLabel(activityLabel,  text: "Activity Indicator")
        configureSectionLabel(progressLabel,  text: "Progress View")
        configureSectionLabel(pageLabel,      text: "Page Control")
        configureSectionLabel(toggleLabel,    text: "Toggle")

        // Slider — distribute values so equal representation across range
        slider.minimumValue = 0
        slider.maximumValue = 1
        slider.value = Float(seed % 5) * 0.25  // 0.0, 0.25, 0.50, 0.75, 1.0

        // Segmented control — 2–4 segments based on seed
        let segmentOptions: [[String]] = [
            ["All", "Active", "Done"],
            ["Day", "Week", "Month", "Year"],
            ["Light", "Dark"],
            ["S", "M", "L", "XL"],
        ]
        let segments = segmentOptions[Int(seed % UInt64(segmentOptions.count))]
        for (i, title) in segments.enumerated() {
            segmentedControl.insertSegment(withTitle: title, at: i, animated: false)
        }
        segmentedControl.selectedSegmentIndex = Int(seed % UInt64(segments.count))

        // Activity indicator — always animating so it's visually present
        activityIndicator.startAnimating()
        activityIndicator.color = .systemBlue

        // Progress view — value varies by seed
        progressView.progress = Float(seed % 4 + 1) * 0.25  // 0.25, 0.50, 0.75, 1.0
        progressView.progressTintColor = .systemBlue

        // Page control — 3–7 pages based on seed
        let pageCount = Int(seed % 5) + 3
        pageControl.numberOfPages = pageCount
        pageControl.currentPage = Int(seed % UInt64(pageCount))
        pageControl.currentPageIndicatorTintColor = .systemBlue
        pageControl.pageIndicatorTintColor = .systemFill

        // Toggle — state alternates by seed
        toggle.isOn = seed % 2 == 0

        // "Reset" secondary button at the bottom
        let resetLabels = ["Reset to Defaults", "Reset All", "Restore Defaults", "Clear Settings"]
        let resetLabel = resetLabels[Int(seed % UInt64(resetLabels.count))]
        resetButton.setTitle(resetLabel, for: .normal)
        resetButton.titleLabel?.font = .systemFont(ofSize: 17)
        resetButton.setTitleColor(.systemBlue, for: .normal)

        // Secure text field — password style
        configureSectionLabel(secureLabel, text: "Secure Input")
        secureTextField.isSecureTextEntry = true
        secureTextField.placeholder = "Password"
        secureTextField.borderStyle = .roundedRect
        secureTextField.font = .systemFont(ofSize: 17)
        secureTextField.text = String(repeating: "•", count: Int(seed % 8) + 6) // varies by seed

        // Add section labels to hierarchy
        for label in [sliderLabel, segmentLabel, activityLabel, progressLabel, pageLabel, toggleLabel, secureLabel] {
            view.addSubview(label)
        }

        // Add annotated controls to hierarchy
        for control in [slider, segmentedControl, activityIndicator, progressView, pageControl, toggle, secureTextField, resetButton] as [UIView] {
            view.addSubview(control)
        }
    }

    private func layoutViews() {
        let safeTop = runConfig.osProfile.safeAreaTopInset
        let width = view.bounds.width
        let height = view.bounds.height
        let hPad: CGFloat = 24
        let controlWidth = width - 2 * hPad
        let labelHeight: CGFloat = 16
        let controlSpacing: CGFloat = 8
        // Compact spacing on sub-700pt screens (e.g. ios17 iPhone SE / standard @2x)
        let rowSpacing: CGFloat = height < 700 ? 18 : 32

        // Navigation bar
        navBar.frame = CGRect(x: 0, y: 0, width: width, height: safeTop + 44)

        var y = navBar.frame.maxY + 28

        // Slider
        sliderLabel.frame = CGRect(x: hPad, y: y, width: controlWidth, height: labelHeight)
        y += labelHeight + controlSpacing
        slider.frame = CGRect(x: hPad, y: y, width: controlWidth, height: 31)
        y += 31 + rowSpacing

        // Segmented control
        segmentLabel.frame = CGRect(x: hPad, y: y, width: controlWidth, height: labelHeight)
        y += labelHeight + controlSpacing
        segmentedControl.frame = CGRect(x: hPad, y: y, width: controlWidth, height: 32)
        y += 32 + rowSpacing

        // Activity indicator
        activityLabel.frame = CGRect(x: hPad, y: y, width: controlWidth, height: labelHeight)
        y += labelHeight + controlSpacing
        let indicatorSize: CGFloat = 20
        activityIndicator.frame = CGRect(x: hPad, y: y, width: indicatorSize, height: indicatorSize)
        y += indicatorSize + rowSpacing

        // Progress view
        progressLabel.frame = CGRect(x: hPad, y: y, width: controlWidth, height: labelHeight)
        y += labelHeight + controlSpacing
        progressView.frame = CGRect(x: hPad, y: y, width: controlWidth, height: 4)
        y += 4 + rowSpacing

        // Page control
        pageLabel.frame = CGRect(x: hPad, y: y, width: controlWidth, height: labelHeight)
        y += labelHeight + controlSpacing
        pageControl.frame = CGRect(x: hPad, y: y, width: controlWidth, height: 26)
        y += 26 + rowSpacing

        // Toggle
        toggleLabel.frame = CGRect(x: hPad, y: y, width: controlWidth, height: labelHeight)
        y += labelHeight + controlSpacing
        toggle.frame = CGRect(x: hPad, y: y, width: 51, height: 31)
        y += 31 + rowSpacing

        // Secure text field
        secureLabel.frame = CGRect(x: hPad, y: y, width: controlWidth, height: labelHeight)
        y += labelHeight + controlSpacing
        secureTextField.frame = CGRect(x: hPad, y: y, width: controlWidth, height: 36)
        y += 36 + rowSpacing

        // "Reset" secondary button — centred, full-width tap target
        resetButton.frame = CGRect(x: 0, y: y, width: width, height: 44)
    }
}
