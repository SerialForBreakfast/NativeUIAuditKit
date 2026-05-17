// UIKitGeneratorViewController.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// TASK-4-2: Comprehensive UIKit template VC.
//
// Renders a configurable vertical stack of UIKit controls and exports their frames
// via the UIKitAnnotatable protocol. This is the anti-overfitting counterpart to
// the SwiftUI templates — same element taxonomy, different rendering framework.
//
// Element classes covered (maps → NativeUIElementType.rawValue):
//   label              — UILabel (standalone) and UITextView (multiline, annotated as label)
//   textField          — UITextField
//   toggle             — UISwitch
//   slider             — UISlider
//   segmentedControl   — UISegmentedControl
//   primaryButton      — UIButton (filled style)
//   secondaryButton    — UIButton (plain style)
//   menuButton         — UIButton with .menu + showsMenuAsPrimaryAction
//   activityIndicator  — UIActivityIndicatorView
//   progressView       — UIProgressView
//   pageControl        — UIPageControl
//   imageView          — UIImageView (non-decorative, has content)
//   listRow            — UITableViewCell (4 styles: default/subtitle/value1/value2)
//   navigationBar      — UINavigationBar (standalone, auto-detected by detectChromeFrames)
//   tabBar             — UITabBar (standalone, auto-detected by detectChromeFrames)
//   tabBarItem         — per-item divisions within tabBar (auto-detected)
//
// Hidden-view guard: annotatedViews skips any view with isHidden = true or alpha ≤ 0.01.
// Canvas filter: annotatedViews skips any view whose frame doesn't intersect the canvas.
// These two rules together satisfy the TASK-4-2 AC for hidden UIButton exclusion.
//
// Layout: fully programmatic (no AutoLayout). Frames set in viewDidLayoutSubviews using
// config.osProfile.safeAreaTopInset. Same seed → same frames every time.
//
// Table cell annotation: cells are collected after tableView.layoutIfNeeded() in
// viewDidLayoutSubviews. Cells at rows 0–3 (all 4 styles) are annotated; the row-2
// and row-3 cells have non-zero y-offsets within the table, satisfying the
// "mid-table position" AC.

import UIKit

// MARK: - UIKitGeneratorViewController

@MainActor
public final class UIKitGeneratorViewController: UIViewController,
                                                  UIKitAnnotatable,
                                                  UITableViewDataSource,
                                                  UITableViewDelegate {

    // MARK: - Configuration

    private let seed: UInt64
    private let runConfig: GeneratorRunConfig

    // MARK: - Chrome views (auto-detected — NOT added to allAnnotations)

    private let navBar = UINavigationBar()
    private let tabBarView = UITabBar()

    // MARK: - Annotated controls

    private let emailLabel = UILabel()
    private let emailField = UITextField()
    private let bioTextView = UITextView()   // annotated as "label" (multiline)
    private let toggle = UISwitch()
    private let slider = UISlider()
    private let segmentedControl = UISegmentedControl()
    private let primaryButton = UIButton(type: .system)
    private let secondaryButton = UIButton(type: .system)
    private let menuButtonView = UIButton(type: .system)
    private let activityIndicator = UIActivityIndicatorView(style: .medium)
    private let progressView = UIProgressView(progressViewStyle: .default)
    private let pageControl = UIPageControl()
    private let photoImageView = UIImageView()

    /// UITableView for listRow annotations. Not scrollable — fixed height = rows × rowHeight.
    private let tableView = UITableView(frame: .zero, style: .plain)
    private let tableRowHeight: CGFloat = 44
    private let tableRowCount = 4    // one per UITableViewCell style

    /// Intentionally hidden button — must NOT appear in annotatedViews (TASK-4-2 AC).
    private let hiddenButton = UIButton(type: .system)

    // MARK: - Annotation state

    /// Populated in viewDidLayoutSubviews after table cells are available.
    private var allAnnotations: [UIKitAnnotatedView] = []
    /// Guards against re-entering buildAnnotations via table layout callbacks.
    private var annotationsBuildScheduled = false

    // MARK: - Content

    private var rowTitles: [String] = []
    private var rowSubtitles: [String] = []

    // MARK: - Init

    public init(seed: UInt64, config: GeneratorRunConfig) {
        self.seed = seed
        self.runConfig = config
        super.init(nibName: nil, bundle: nil)
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) { fatalError("init(coder:) not used") }

    // MARK: - UIViewController lifecycle

    public override func viewDidLoad() {
        super.viewDidLoad()
        UIView.setAnimationsEnabled(false)
        setupAppearance()
        setupViews()
        tableView.reloadData()
    }

    public override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        layoutViews()
        // Build annotations exactly once per layout pass (guard prevents re-entrance
        // if tableView.layoutIfNeeded() triggers a recursive viewDidLayoutSubviews).
        if !annotationsBuildScheduled {
            annotationsBuildScheduled = true
            tableView.layoutIfNeeded()
            buildAnnotations()
        }
    }

    // MARK: - UIKitAnnotatable

    public var annotatedViews: [UIKitAnnotatedView] {
        let canvasBounds = CGRect(origin: .zero, size: runConfig.osProfile.screenSize)
        return allAnnotations.compactMap { annotated -> UIKitAnnotatedView? in
            guard let v = annotated.view else { return nil }
            guard !v.isHidden, v.alpha > 0.01 else { return nil }
            let frame = v.convert(v.bounds, to: view)
            guard frame.width > 0, frame.height > 0 else { return nil }
            guard canvasBounds.intersects(frame) else { return nil }
            return annotated
        }
    }

    // MARK: - UITableViewDataSource

    public func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        tableRowCount
    }

    public func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        // Each row uses a distinct UITableViewCell style.
        // Created without reuse so the style is guaranteed per row.
        let styles: [UITableViewCell.CellStyle] = [.default, .subtitle, .value1, .value2]
        let style = styles[indexPath.row % styles.count]
        let cell = UITableViewCell(style: style, reuseIdentifier: nil)
        cell.textLabel?.text = rowTitles[safe: indexPath.row] ?? "Row \(indexPath.row)"
        cell.detailTextLabel?.text = rowSubtitles[safe: indexPath.row]
        return cell
    }

    public func tableView(_ tableView: UITableView, heightForRowAt indexPath: IndexPath) -> CGFloat {
        tableRowHeight
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

        // Tab bar with 4 items (detectChromeFrames yields tabBarItem_0..3)
        let tabItems = [
            UITabBarItem(title: "Home",     image: UIImage(systemName: "house"),           tag: 0),
            UITabBarItem(title: "Browse",   image: UIImage(systemName: "square.grid.2x2"), tag: 1),
            UITabBarItem(title: "Library",  image: UIImage(systemName: "books.vertical"),  tag: 2),
            UITabBarItem(title: "Profile",  image: UIImage(systemName: "person.circle"),   tag: 3),
        ]
        tabBarView.items = tabItems
        tabBarView.selectedItem = tabItems[0]
        view.addSubview(tabBarView)

        // Email label
        emailLabel.text = seed % 2 == 0 ? "Email Address" : "Email"
        emailLabel.font = .systemFont(ofSize: 13, weight: .medium)
        emailLabel.textColor = .secondaryLabel
        view.addSubview(emailLabel)

        // Email text field
        emailField.placeholder = corpus.email()
        emailField.borderStyle = .roundedRect
        emailField.keyboardType = .emailAddress
        emailField.autocapitalizationType = .none
        view.addSubview(emailField)

        // Bio text view (multiline, annotated as "label")
        bioTextView.text = "\(corpus.personName()) — \(corpus.companyName())"
        bioTextView.isEditable = false
        bioTextView.isScrollEnabled = false
        bioTextView.font = .systemFont(ofSize: 15)
        bioTextView.backgroundColor = .secondarySystemBackground
        bioTextView.layer.cornerRadius = 8
        view.addSubview(bioTextView)

        // Toggle
        toggle.isOn = seed % 2 == 0
        view.addSubview(toggle)

        // Slider
        slider.minimumValue = 0
        slider.maximumValue = 1
        slider.value = Float(seed % 5) * 0.25
        view.addSubview(slider)

        // Segmented control
        let segOptions: [[String]] = [
            ["All", "Active", "Done"],
            ["Day", "Week", "Month"],
            ["Light", "Dark"],
        ]
        let opts = segOptions[Int(seed % UInt64(segOptions.count))]
        for (i, t) in opts.enumerated() {
            segmentedControl.insertSegment(withTitle: t, at: i, animated: false)
        }
        segmentedControl.selectedSegmentIndex = Int(seed % UInt64(opts.count))
        view.addSubview(segmentedControl)

        // Primary button (filled)
        let primaryTitle = seed % 3 == 0 ? "Save Changes" : (seed % 3 == 1 ? "Continue" : "Submit")
        primaryButton.setTitle(primaryTitle, for: .normal)
        primaryButton.backgroundColor = .systemBlue
        primaryButton.setTitleColor(.white, for: .normal)
        primaryButton.titleLabel?.font = .systemFont(ofSize: 17, weight: .semibold)
        primaryButton.layer.cornerRadius = 12
        primaryButton.clipsToBounds = true
        view.addSubview(primaryButton)

        // Secondary button (plain)
        secondaryButton.setTitle("Cancel", for: .normal)
        secondaryButton.setTitleColor(.systemBlue, for: .normal)
        view.addSubview(secondaryButton)

        // Menu button
        menuButtonView.setTitle("Options ▾", for: .normal)
        menuButtonView.setTitleColor(.systemBlue, for: .normal)
        let menu = UIMenu(children: [
            UIAction(title: "Edit")   { _ in },
            UIAction(title: "Share")  { _ in },
            UIAction(title: "Delete", attributes: .destructive) { _ in },
        ])
        menuButtonView.menu = menu
        menuButtonView.showsMenuAsPrimaryAction = true
        view.addSubview(menuButtonView)

        // Activity indicator
        activityIndicator.startAnimating()
        activityIndicator.color = .systemBlue
        view.addSubview(activityIndicator)

        // Progress view
        progressView.progress = Float(seed % 4 + 1) * 0.25
        progressView.progressTintColor = .systemBlue
        view.addSubview(progressView)

        // Page control
        let pages = Int(seed % 4) + 3
        pageControl.numberOfPages = pages
        pageControl.currentPage = Int(seed % UInt64(pages))
        pageControl.currentPageIndicatorTintColor = .systemBlue
        pageControl.pageIndicatorTintColor = .systemFill
        view.addSubview(pageControl)

        // Image view (non-decorative — has tinted SF symbol content)
        photoImageView.image = UIImage(systemName: "photo.on.rectangle")
        photoImageView.tintColor = .systemBlue
        photoImageView.contentMode = .scaleAspectFit
        photoImageView.backgroundColor = .secondarySystemBackground
        photoImageView.layer.cornerRadius = 8
        photoImageView.clipsToBounds = true
        view.addSubview(photoImageView)

        // Table view — 4 rows with different cell styles
        rowTitles = (0..<tableRowCount).map { _ in corpus.listRowTitle() }
        rowSubtitles = (0..<tableRowCount).map { _ in corpus.listRowSubtitle() }
        tableView.dataSource = self
        tableView.delegate = self
        tableView.isScrollEnabled = false
        tableView.backgroundColor = .secondarySystemBackground
        view.addSubview(tableView)

        // Hidden button — must NOT appear in annotatedViews output (TASK-4-2 AC)
        hiddenButton.setTitle("Hidden Button", for: .normal)
        hiddenButton.isHidden = true
        view.addSubview(hiddenButton)
    }

    // MARK: - Layout

    private func layoutViews() {
        let safeTop = runConfig.osProfile.safeAreaTopInset
        let safeBottom = runConfig.osProfile.safeAreaBottomInset
        let w = view.bounds.width
        let h = view.bounds.height
        let hPad: CGFloat = 20
        let ctrlW = w - 2 * hPad
        let gap: CGFloat = 10

        // Chrome
        navBar.frame = CGRect(x: 0, y: 0, width: w, height: safeTop + 44)
        tabBarView.frame = CGRect(
            x: 0,
            y: h - safeBottom - 49,
            width: w,
            height: 49 + safeBottom
        )

        // Content area begins below nav bar
        var y = navBar.frame.maxY + 12

        emailLabel.frame = CGRect(x: hPad, y: y, width: ctrlW, height: 18)
        y += 22

        emailField.frame = CGRect(x: hPad, y: y, width: ctrlW, height: 44)
        y += 44 + gap

        bioTextView.frame = CGRect(x: hPad, y: y, width: ctrlW, height: 52)
        y += 52 + gap

        toggle.frame = CGRect(x: hPad, y: y, width: 51, height: 31)
        y += 31 + gap

        slider.frame = CGRect(x: hPad, y: y, width: ctrlW, height: 31)
        y += 31 + gap

        segmentedControl.frame = CGRect(x: hPad, y: y, width: ctrlW, height: 32)
        y += 32 + gap

        primaryButton.frame = CGRect(x: hPad, y: y, width: ctrlW, height: 50)
        y += 50 + gap / 2

        secondaryButton.frame = CGRect(x: hPad, y: y, width: ctrlW, height: 40)
        y += 40 + gap / 2

        menuButtonView.frame = CGRect(x: hPad, y: y, width: ctrlW, height: 40)
        y += 40 + gap

        activityIndicator.frame = CGRect(x: hPad, y: y, width: 20, height: 20)
        y += 20 + gap / 2

        progressView.frame = CGRect(x: hPad, y: y, width: ctrlW, height: 4)
        y += 4 + gap / 2

        pageControl.frame = CGRect(x: hPad, y: y, width: ctrlW, height: 26)
        y += 26 + gap

        photoImageView.frame = CGRect(x: hPad, y: y, width: ctrlW, height: 40)
        y += 40 + gap

        // Table: fixed height = row count × row height
        let tableH = CGFloat(tableRowCount) * tableRowHeight
        tableView.frame = CGRect(x: 0, y: y, width: w, height: tableH)
        y += tableH

        // Hidden button at a visible position — hidden flag means it won't appear in output
        hiddenButton.frame = CGRect(x: hPad, y: navBar.frame.maxY + 50, width: 120, height: 44)
    }

    // MARK: - Annotation collection

    private func buildAnnotations() {
        var annotations: [UIKitAnnotatedView] = [
            UIKitAnnotatedView(id: "label_email",    elementType: "label",    view: emailLabel,    visibleText: emailLabel.text),
            UIKitAnnotatedView(id: "textField",       elementType: "textField", view: emailField),
            UIKitAnnotatedView(id: "label_bio",       elementType: "label",    view: bioTextView,   visibleText: bioTextView.text),
            UIKitAnnotatedView(id: "toggle",          elementType: "toggle",   view: toggle),
            UIKitAnnotatedView(id: "slider",          elementType: "slider",   view: slider),
            UIKitAnnotatedView(id: "segmentedControl", elementType: "segmentedControl", view: segmentedControl),
            UIKitAnnotatedView(id: "primaryButton",   elementType: "primaryButton",  view: primaryButton,   visibleText: primaryButton.title(for: .normal)),
            UIKitAnnotatedView(id: "secondaryButton", elementType: "secondaryButton", view: secondaryButton, visibleText: secondaryButton.title(for: .normal)),
            UIKitAnnotatedView(id: "menuButton",      elementType: "menuButton",     view: menuButtonView,  visibleText: menuButtonView.title(for: .normal)),
            UIKitAnnotatedView(id: "activityIndicator", elementType: "activityIndicator", view: activityIndicator),
            UIKitAnnotatedView(id: "progressView",    elementType: "progressView",   view: progressView),
            UIKitAnnotatedView(id: "pageControl",     elementType: "pageControl",    view: pageControl),
            UIKitAnnotatedView(id: "imageView",       elementType: "imageView",      view: photoImageView),
        ]

        // Table cells — collected after tableView.layoutIfNeeded()
        for row in 0..<tableRowCount {
            if let cell = tableView.cellForRow(at: IndexPath(row: row, section: 0)) {
                annotations.append(UIKitAnnotatedView(
                    id: "listRow_\(row)",
                    elementType: "listRow",
                    view: cell,
                    visibleText: rowTitles[safe: row]
                ))
            }
        }

        // Note: hiddenButton is NOT in this list — it's intentionally excluded.
        // annotatedViews would also skip it (isHidden = true), but keeping it out of
        // allAnnotations makes the intent explicit for test verification.

        allAnnotations = annotations
    }
}

// MARK: - Array safe subscript (local to this file)

private extension Array {
    subscript(safe index: Int) -> Element? {
        indices.contains(index) ? self[index] : nil
    }
}
